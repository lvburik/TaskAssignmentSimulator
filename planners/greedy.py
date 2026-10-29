"""Nearest-reachable-task planner with no inter-agent coordination."""

from planners.class_definition import Planner


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
        


        
