from planners.class_definition import Planner

from pathfinding.distancefinder import FindClosestGoal
from pathfinding.to_direction import ToDirection

class GreedyTaskSelector(Planner):
    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        super().__init__(pathfinding_algorithm, agent_id, messagebus)

        self.current_goal = None 
        

    def update_plan(self, observation: dict):
        self.tasks = observation["tasks"]
        self.agent_location = observation["agent_location"]
        self.world_map = observation["map"]

        task_locations = [task.location for task in self.tasks if not task.completed and task.spawn_time <= observation["time"]]

        goal, _ = FindClosestGoal(self.world_map, self.agent_location, task_locations)
        
        if not goal:
            return  # No available tasks to select
        
        self.current_goal =  goal
        

    def act(self):
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
        
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
        
        else: 
            path = self.pathfinding_algorithm(self.agent_location, self.current_goal, self.world_map)

        return ToDirection(self.agent_location, path[1])  # Convert the next step in the path to a direction

def _select_closest_goal(goal_distances):
    #sort by distance and task_id to ensure deterministic tie-breaking
    sorted_goals = sorted(goal_distances.items(), key=lambda x: (x[1], x[0]))
    if not sorted_goals:
        return []
        
    return sorted_goals[0][0]

        

