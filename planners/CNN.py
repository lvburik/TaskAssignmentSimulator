from pathlib import Path, PosixPath
import pathlib
import os

import torch
from torch import Tensor, nn

from pathfinding.to_direction import ToDirection

from planners.model_input import available_tasks, cnn_inputs


class AssignmentCNN(nn.Module):
    def __init__(
        self,
        input_channels: int,
        image_height: int,
        image_width: int,
        base_channels: int,
        convolutional_blocks: int,
        kernel_size: int,
        classifier_width: int,
        dropout: float,
    ) -> None:
        super().__init__()
        if input_channels != 3:
            raise ValueError("AssignmentCNN requires exactly three input channels")
        self.branch_specs = tuple(
            (channel, pooling_type)
            for channel in range(input_channels)
            for pooling_type in ("max", "average")
        )
        self.pool_size = 4
        self.branches = nn.ModuleList(
            self._make_branch(
                base_channels, convolutional_blocks, kernel_size, pooling_type
            )
            for _, pooling_type in self.branch_specs
        )
        self.image_width = image_width
        self.image_height = image_height
        final_channels = base_channels * 2 ** (convolutional_blocks - 1)
        feature_size = (
            len(self.branch_specs)
            * final_channels
            * self.pool_size
            * self.pool_size
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(feature_size + 3, classifier_width),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(classifier_width, 1),
        )

    def _make_branch(
        self,
        base_channels: int,
        convolutional_blocks: int,
        kernel_size: int,
        pooling_type: str,
    ) -> nn.Sequential:
        layers: list[nn.Module] = []
        input_size = 1
        for block in range(convolutional_blocks):
            output_size = base_channels * 2**block
            layers.extend(
                [
                    nn.Conv2d(
                        input_size,
                        output_size,
                        kernel_size,
                        padding=kernel_size // 2,
                    ),
                    nn.BatchNorm2d(output_size),
                    nn.ReLU(),
                    self._pooling_layer(pooling_type),
                ]
            )
            input_size = output_size
        layers.append(self._pooling_layer(pooling_type, (self.pool_size, self.pool_size)))
        return nn.Sequential(*layers)

    @staticmethod
    def _pooling_layer(
        pooling_type: str, adaptive_size: tuple[int, int] | None = None
    ) -> nn.Module:
        if adaptive_size is not None:
            if pooling_type == "max":
                return nn.AdaptiveMaxPool2d(adaptive_size)
            if pooling_type == "average":
                return nn.AdaptiveAvgPool2d(adaptive_size)
        elif pooling_type == "max":
            return nn.MaxPool2d(2)
        elif pooling_type == "average":
            return nn.AvgPool2d(2)
        raise ValueError(f"Unsupported pooling type: {pooling_type}")

    def forward(self, inputs: Tensor) -> Tensor:
        features = torch.cat(
            [
                branch(inputs[:, channel : channel + 1])
                for (channel, _), branch in zip(self.branch_specs, self.branches)
            ],
            dim=1,
        ).flatten(start_dim=1)
        task = self._marker_positions(inputs[:, 1])
        agent = self._marker_positions(inputs[:, 2])
        delta = task - agent
        scale = inputs.new_tensor((self.image_width, self.image_height))
        relation = torch.cat(
            (
                delta / scale,
                torch.linalg.vector_norm(delta, dim=1, keepdim=True)
                / max(scale),
            ),
            dim=1,
        )
        return self.classifier(torch.cat((features, relation), dim=1)).squeeze(1)

    @staticmethod
    def _marker_positions(channel: Tensor) -> Tensor:
        height, width = channel.shape[-2:]
        index = channel.flatten(start_dim=1).argmax(dim=1)
        y = torch.div(index, width, rounding_mode="floor")
        x = index.remainder(width)
        return torch.stack((x.float(), y.float()), dim=1)


class _LegacyAssignmentCNN(nn.Module):
    def __init__(self, channels: int, height: int, width: int, config: dict) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(channels, 24, 3, padding=1),
            nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(24, 48, 3, padding=1),
            nn.BatchNorm2d(48),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(48, 96, 3, padding=1),
            nn.BatchNorm2d(96),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((height // 4, width // 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(96 * (height // 4) * (width // 4) + 3, 128),
            nn.ReLU(),
            nn.Dropout(float(config.get("dropout", 0.4))),
            nn.Linear(128, 1),
        )
        self.image_width = width
        self.image_height = height

    def forward(self, inputs: Tensor) -> Tensor:
        features = self.features(inputs)
        task = AssignmentCNN._marker_positions(inputs[:, 1])
        agent = AssignmentCNN._marker_positions(inputs[:, 2])
        delta = task - agent
        scale = inputs.new_tensor((self.image_width, self.image_height))
        relation = torch.cat(
            (
                delta / scale,
                torch.linalg.vector_norm(delta, dim=1, keepdim=True)
                / max(self.image_width, self.image_height),
            ),
            dim=1,
        )
        return self.classifier(
            torch.cat((features.flatten(start_dim=1), relation), dim=1)
        ).squeeze(1)


def _load_model(path: Path, device: torch.device) -> tuple[nn.Module, float]:
    # Checkpoints trained on Windows may contain pathlib.WindowsPath metadata.
    original_posix_path = pathlib.PosixPath
    original_windows_path = pathlib.WindowsPath
    if os.name == "nt":
        pathlib.PosixPath = pathlib.WindowsPath
    else:
        pathlib.WindowsPath = PosixPath
    try:
        checkpoint = torch.load(path, map_location=device, weights_only=False)
    finally:
        pathlib.PosixPath = original_posix_path
        pathlib.WindowsPath = original_windows_path

    if not isinstance(checkpoint, dict) or "model_state_dict" not in checkpoint:
        raise ValueError(f"{path} is not a supported CNN checkpoint")
    config = checkpoint.get("config", {})
    input_shape = checkpoint.get("input_shape")
    if not isinstance(input_shape, (tuple, list)) or len(input_shape) != 3:
        raise ValueError(f"{path} does not contain a valid CNN input shape")

    state_dict = checkpoint["model_state_dict"]
    if any(key.startswith("features.") for key in state_dict):
        model = _LegacyAssignmentCNN(
            int(input_shape[0]), int(input_shape[1]), int(input_shape[2]), config
        )
    else:
        model = AssignmentCNN(
            input_channels=int(input_shape[0]),
            image_height=int(input_shape[1]),
            image_width=int(input_shape[2]),
            base_channels=int(config.get("base_channels", 24)),
            convolutional_blocks=int(config.get("convolutional_blocks", 3)),
            kernel_size=int(config.get("kernel_size", 3)),
            classifier_width=int(config.get("classifier_width", 128)),
            dropout=float(config.get("dropout", 0.3)),
        )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model, float(checkpoint.get("threshold", 0.5))


class CNNPlanner:
    _model_cache: dict[tuple[Path, torch.device], tuple[nn.Module, float]] = {}

    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        self.pathfinding_algorithm = pathfinding_algorithm

        MODEL_DIR = Path("D:\\afstuderen\\TaskAssignmentLearner\\models\\CNN_best_1.pt")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        cache_key = (MODEL_DIR, self.device)
        if cache_key not in self._model_cache:
            self._model_cache[cache_key] = _load_model(MODEL_DIR, self.device)
        self.model, self.threshold = self._model_cache[cache_key]

        self.current_queue = []
        self.current_task_queue = []
        self.current_goal = None

    def update_plan(self, observation: dict):
        self.agent_location = observation["agent_location"]
        tasks = available_tasks(observation)
        self.current_task_queue = []
        self.current_goal = None
        if not tasks:
            return

        images = torch.from_numpy(cnn_inputs(observation, tasks))
        images = images.permute(0, 3, 1, 2).float().div_(255.0).to(self.device)
        with torch.inference_mode():
            probabilities = torch.sigmoid(self.model(images))
        predictions = probabilities.ge(self.threshold).tolist()

        #add predicted tasks to queue
        for ii, prediction in enumerate(predictions):
            if prediction == True:
                self.current_task_queue.append([tasks[ii], self.pathfinding_algorithm.get_distance(self.agent_location, tasks[ii].location)])

        #sort predicted task queue by current distance to task:
        if self.current_task_queue:
            if len(self.current_task_queue) > 1:
                # Sorts the list in-place by the second element (distance)
                self.current_task_queue.sort(key=lambda x: x[1])

            self.current_goal = self.current_task_queue[0][0].location

            self.current_queue = [entry[0] for entry in self.current_task_queue]

    def act(self):
            
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
            
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
    
        else: 
            next_location = self.pathfinding_algorithm.next_step(self.agent_location, self.current_goal)
            
        return ToDirection(self.agent_location, next_location)  # Convert the next step in the path to a direction
           