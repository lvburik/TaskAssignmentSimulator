"""Nearest-reachable-task planner with no inter-agent coordination."""

from planners.class_definition import Planner

from pathfinding.to_direction import ToDirection

class GreedyTaskSelector(Planner):
    """Choose the closest active task and follow a shortest path to it."""

    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        super().__init__(pathfinding_algorithm, agent_id, messagebus)

        self.current_goal = None 
        self.current_queue = []
        

    def update_plan(self, observation: dict):
        """Select the closest reachable task from the current observation."""
        self.tasks = observation["tasks"]
        self.agent_location = observation["agent_location"]
        self.world_map = observation["map"]

        task_locations = [task.location for task in self.tasks if not task.completed and task.spawn_time <= observation["time"]]

        if not task_locations:
            return
        
        goal, _ = self.pathfinding_algorithm.findclosestgoal(self.agent_location, task_locations)
        
        if not goal:
            return  # No available tasks to select
        
        self.current_goal =  goal
        

    def act(self):
        """Move toward the selected task or perform it when at its location."""
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
        
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
        
        else: 
            next_location = self.pathfinding_algorithm.next_step(self.agent_location, self.current_goal)

        return ToDirection(self.agent_location, next_location)  # Convert the next step in the path to a direction

        
