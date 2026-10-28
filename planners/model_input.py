"""Build model inputs from the simulator's live agent observation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


TABULAR_COLUMNS = (
    "task_x",
    "task_y",
    "agent_x",
    "agent_y",
    "manhattan_distance",
    "team_size",
    "closer_agents_count",
    "closest_teammate_manhattan_distance",
    "world_width",
    "world_height",
)


def available_tasks(observation: dict[str, Any]) -> list[Any]:
    """Return the active tasks in a deterministic order."""
    return sorted(
        (
            task
            for task in observation["tasks"]
            if not task.completed
            and task.spawn_time <= observation["time"]
            and task.location is not None
        ),
        key=lambda task: task.id,
    )


def tabular_inputs(
    observation: dict[str, Any], tasks: list[Any] | None = None
) -> pd.DataFrame:
    """Create the feature rows used by the XGBoost and MLP dataset builders."""
    tasks = available_tasks(observation) if tasks is None else tasks
    agent_x, agent_y = observation["agent_location"]
    other_locations = [
        location for _, location in observation["other_agent_locations"] if location is not None
    ]
    team_size = len(other_locations) + 1
    world_map = observation["map"]
    world_height = len(world_map)
    world_width = len(world_map[0]) if world_height else 0

    rows = []
    for task in tasks:
        task_x, task_y = task.location
        distance = abs(agent_x - task_x) + abs(agent_y - task_y)
        teammate_distances = [
            abs(other_x - task_x) + abs(other_y - task_y)
            for other_x, other_y in other_locations
        ]
        rows.append(
            {
                "task_x": task_x,
                "task_y": task_y,
                "agent_x": agent_x,
                "agent_y": agent_y,
                "manhattan_distance": distance,
                "team_size": team_size,
                "closer_agents_count": sum(
                    teammate_distance < distance
                    for teammate_distance in teammate_distances
                ),
                "closest_teammate_manhattan_distance": min(
                    teammate_distances, default=distance
                ),
                "world_width": world_width,
                "world_height": world_height,
            }
        )
    return pd.DataFrame(rows, columns=TABULAR_COLUMNS)


def cnn_inputs(
    observation: dict[str, Any], tasks: list[Any] | None = None
) -> np.ndarray:
    """Create NHWC uint8 images matching ``CNN_dataset_builder.py``."""
    tasks = available_tasks(observation) if tasks is None else tasks
    map_channel = np.asarray(observation["map"], dtype=np.float32)
    if map_channel.ndim != 2 or map_channel.size == 0:
        raise ValueError("Observation map must be a non-empty two-dimensional matrix")
    height, width = map_channel.shape
    map_channel = np.clip(map_channel * 255, 0, 255)

    task_channel = np.full((height, width), 128, dtype=np.float32)
    for task in tasks:
        x, y = task.location
        _validate_position((x, y), width, height, "task")
        task_channel[y, x] = 192

    agent_channel = np.full((height, width), 128, dtype=np.float32)
    agent_locations = [
        location
        for _, location in observation["other_agent_locations"]
        if location is not None
    ]
    for location in [observation["agent_location"], *agent_locations]:
        _validate_position(location, width, height, "agent")
        x, y = location
        agent_channel[y, x] = 192

    images = []
    for task in tasks:
        task_x, task_y = task.location
        image = np.stack((map_channel, task_channel, agent_channel), axis=-1).copy()
        image[task_y, task_x, 1] = 255
        agent_x, agent_y = observation["agent_location"]
        image[agent_y, agent_x, 2] = 255
        images.append(image)
    return np.asarray(images, dtype=np.uint8).reshape((-1, height, width, 3))


def _validate_position(
    position: Any, width: int, height: int, item_name: str
) -> None:
    if not isinstance(position, (tuple, list)) or len(position) < 2:
        raise ValueError(f"{item_name} position must contain x and y coordinates")
    x, y = position[:2]
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"{item_name} position {(x, y)} is outside the map")
