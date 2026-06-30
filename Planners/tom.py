from Planners.class_definition import Planner

from pathfinding.to_direction import ToDirection
from pathfinding.distancefinder import BulkDistanceFinder

class TheoryOfMindPlanner(Planner):
    def __init__(self, pathfinding_algorithm=None, communication = None):
        super().__init__(pathfinding_algorithm, communication)

        self.beliefs = {}  # Placeholder for beliefs about other agents
        self.current_task_queue = None
        self.current_goal = None
        self.previous_task_set = None
        self.world_time = None
        self.world_map = None
        self.agent_location = None  # Placeholder for the agent's current location

    def update_plan(self, observation: dict):

        current_time = observation["time"]
        self.agent_location = observation["agent_location"]
        self.world_map = observation["map"]
        tasks = [task for task in observation["tasks"]]
        uncompleted_tasks = [task for task in observation["tasks"] if not task.completed]

        #if self.previous_task_set != tasks or (current_time != self.world_time and current_time == 0):
        if (current_time != self.world_time and current_time == 0):
            self._initialize_beliefs(uncompleted_tasks)
        elif current_time > self.world_time:
            self._update_beliefs(uncompleted_tasks, observation)
            self._normalise_beliefs()

        self.world_time = current_time
        self.previous_task_set = tasks

        best_task = max(uncompleted_tasks, key=lambda task: self.beliefs.get(task.id, 0), default=None) #different to previous version

        if best_task is not None:
            self.current_goal = best_task.location
            self.current_task_queue = [best_task]
    
    def act(self):
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
        
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
        
        else: 
            path = self.pathfinding_algorithm(self.agent_location, self.current_goal, self.world_map)

        return ToDirection(self.agent_location, path[1])  # Convert the next step in the path to a direction
    
    def _initialize_beliefs(self, uncompleted_tasks: list):
        if not uncompleted_tasks:
            self.beliefs.clear()  # No tasks to initialize beliefs for
            return  # No tasks to initialize beliefs for
        
        prior = 1.0/len(uncompleted_tasks)
        self.beliefs.clear()  # Clear existing beliefs

        for task in uncompleted_tasks:
            self.beliefs[task.id] = prior  # Initialize with uniform prior
        

    def _update_beliefs(self, uncompleted_tasks:list, observations: dict):
        if not uncompleted_tasks:
            self.beliefs.clear()  # No tasks to update beliefs for
            return  # No tasks to update beliefs for

        likelihoods = self._compute_likelihoods(uncompleted_tasks, observations)

        for task in uncompleted_tasks:
            prior = self.beliefs.get(task.id, 1/max(1, len(uncompleted_tasks)))  # Default to uniform prior if not present
            likelihood = likelihoods.get(task.id, 0.01)
            self.beliefs[task.id] = prior * likelihood  # Update belief with new likelihood
        
    
    def _normalise_beliefs(self):
        total_belief = sum(self.beliefs.values())
        if total_belief == 0:
            return  # Avoid division by zero; beliefs remain unchanged
        
        for task_id in self.beliefs:
            self.beliefs[task_id] /= total_belief  # Normalize beliefs to sum to 1
    
    def _compute_likelihoods(self, uncompleted_tasks: list, observations: dict):
        likelihoods = {}
        if not uncompleted_tasks:
            return likelihoods  # No tasks to compute likelihoods for
        
        my_location = observations["agent_location"]

        my_distances = BulkDistanceFinder(self.world_map, my_location, [task.location for task in uncompleted_tasks])

        other_agent_locations = observations["other_agent_locations"]
        other_agent_distances = {}
        
        for agent_id, agent_location in other_agent_locations:
            distances = BulkDistanceFinder(self.world_map, agent_location, [task.location for task in uncompleted_tasks])
            other_agent_distances[agent_id] = distances

        first_task_in_queue = self.current_task_queue[0] if self.current_task_queue else None

        for task in uncompleted_tasks:
            distance_to_task = my_distances.get(task.location, float('inf'))
            distance_factor = 1 / (distance_to_task + 1)  # Avoid division by zero

            competing_support = 0.0
            for agent_id, distances in other_agent_distances.items():
                other_distance_to_task = distances.get(task.location, float('inf'))
                if other_distance_to_task < distance_to_task:
                    competing_support += 1.0  # Increment support if another agent is closer

            queue_support = 1.0 if first_task_in_queue and first_task_in_queue.id == task.id else 0.0

            likelihood = max(0.01, (distance_factor + queue_support) / (competing_support + 1))
            likelihoods[task.id] = likelihood  

        return likelihoods

