"""Planner that selects tasks with a saved multilayer-perceptron classifier."""

from planners.class_definition import Planner
from pathlib import Path
import pickle

from planners.model_input import available_tasks, tabular_inputs
from app_config import PATHS


class MLPPlanner(Planner):
    """Load an MLP pickle and route to tasks it predicts for this agent."""

    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        self.pathfinding_algorithm = pathfinding_algorithm

        MODEL_DIR = Path(PATHS["mlp_model"])
        self.model = pickle.load(open(MODEL_DIR, 'rb'))

        self.current_queue = []
        self.current_task_queue = []
        self.current_goal = None

    def update_plan(self, observation: dict):
        """Score active tasks and queue positive classifier predictions."""
        self.agent_location = observation["agent_location"]
        tasks = available_tasks(observation)
        self.current_task_queue = []
        self.current_goal = None
        if not tasks:
            return

        features = tabular_inputs(observation, tasks)
        predictions = self.model.predict(features)

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
           