from Planners.class_definition import Planner
import random

class RandomMovesPlanner(Planner):
    def __init__(self, pathfinding_algorithm=None, communication = None):
        super().__init__(pathfinding_algorithm, communication)

    def update_plan(self, observation: dict):
        # Implement the logic to update the plan based on the world state
        # This is a placeholder implementation
        self.current_plan = "Random moves plan based on world state"
        
        if observation["agent_id"] == 0:
            print(f"time: {observation['time']}, Agent {observation['agent_id']} at location: {observation['agent_location']}")

    def act(self):
        # Implement the action execution based on the current plan
        return random.choice(["up", "down", "left", "right"])  # Randomly choose an action