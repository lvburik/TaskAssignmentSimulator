"""Planner that selects an unconditioned random cardinal movement."""

from planners.class_definition import Planner
import random

class RandomMovesPlanner(Planner):
    """Choose one of the four movement directions at random each step."""

    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        super().__init__(pathfinding_algorithm, agent_id, messagebus)
        self.current_queue = []
        self.current_goal = None

    def update_plan(self, observation: dict):
        """Accept the observation; this planner does not build a task plan."""
        # Implement the logic to update the plan based on the world state
        # This is a placeholder implementation
        self.current_plan = "Random moves plan based on world state"
        
        if observation["agent_id"] == 0:
            print(f"time: {observation['time']}, Agent {observation['agent_id']} at location: {observation['agent_location']}")

    def act(self):
        """Return a random cardinal movement action."""
        # Implement the action execution based on the current plan
        return random.choice(["up", "down", "left", "right"])  # Randomly choose an action