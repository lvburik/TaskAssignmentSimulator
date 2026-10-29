"""Task selection using simple beliefs about other agents' task choices."""

from planners.class_definition import Planner



class TheoryOfMindPlanner(Planner):
    """Update task beliefs from proximity and competing-agent observations."""

    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        super().__init__(pathfinding_algorithm, agent_id, messagebus)

        self.beliefs = {}  # Placeholder for beliefs about other agents
        self.current_queue = []
        self.current_goal = None
        self.previous_task_set = None
        self.world_time = None
        self.world_map = None
        self.agent_location = None  # Placeholder for the agent's current location
        

    def update_plan(self, observation: dict):
        """Update beliefs and choose the task with the highest current belief."""

        current_time = observation["time"]
        self.agent_location = observation["agent_location"]
        self.world_map = observation["map"]
        tasks = [task for task in observation["tasks"]]
        uncompleted_tasks = [task for task in observation["tasks"] if not task.completed]

        #if self.previous_task_set != tasks or (current_time != self.world_time and current_time == 0):
        if (current_time != self.world_time and current_time == 0):
            self._initialize_beliefs(uncompleted_tasks)
            self._normalise_beliefs()

        
        elif current_time > self.world_time:
            self._update_beliefs(uncompleted_tasks, observation)
            self._normalise_beliefs()

        self.world_time = current_time
        self.previous_task_set = tasks

        best_task = max(uncompleted_tasks, key=lambda task: self.beliefs.get(task.id, 0), default=None) #different to previous version

        if best_task is not None:
            self.current_goal = best_task.location
            self.current_queue = [best_task]
    
    def _on_task_reached(self):
        """Clear beliefs once the task is reached."""
        self.beliefs.clear()

    def _initialize_beliefs(self, uncompleted_tasks: list):
        """Assign an initially uniform belief across available tasks."""
        if not uncompleted_tasks:
            self.beliefs.clear()  # No tasks to initialize beliefs for
            return  # No tasks to initialize beliefs for
        
        prior = 1.0/len(uncompleted_tasks)
        
        for task in uncompleted_tasks:
            if task.id not in self.beliefs.keys():
                self.beliefs[task.id] = prior  # Initialize with uniform prior
        

    def _update_beliefs(self, uncompleted_tasks:list, observations: dict):
        """Reweight task beliefs using estimated agent competition."""
        if not uncompleted_tasks:
            self.beliefs.clear()  # No tasks to update beliefs for
            return  # No tasks to update beliefs for

        likelihoods = self._compute_likelihoods(uncompleted_tasks, observations)

        for task in uncompleted_tasks:
            prior = self.beliefs.get(task.id, 1/max(1, len(uncompleted_tasks)))  # Default to uniform prior if not present
            likelihood = likelihoods.get(task.id, 0.01)
            self.beliefs[task.id] = prior * likelihood  # Update belief with new likelihood
        
    
    def _normalise_beliefs(self):
        """Scale beliefs so their total is one when the total is nonzero."""
        total_belief = sum(self.beliefs.values())
        if total_belief == 0:
            return  # Avoid division by zero; beliefs remain unchanged
        
        for task_id in self.beliefs:
            self.beliefs[task_id] /= total_belief  # Normalize beliefs to sum to 1
    
    def _compute_likelihoods(self, uncompleted_tasks: list, observations: dict):
        """Estimate task likelihood from distance, queue, and teammate positions."""
        likelihoods = {}
        if not uncompleted_tasks:
            return likelihoods  # No tasks to compute likelihoods for

        other_agent_locations = observations["other_agent_locations"]

        first_task_in_queue = self.current_queue[0] if self.current_queue else None

        for task in uncompleted_tasks:
            distance_to_task = self.pathfinding_algorithm.get_distance(self.agent_location, task.location)
            distance_factor = 1 / (distance_to_task + 1)  # Avoid division by zero

            competing_support = 0.0
            for _, competeting_location in other_agent_locations:
                other_distance_to_task = self.pathfinding_algorithm.get_distance(competeting_location, task.location)
                if other_distance_to_task < distance_to_task:
                    competing_support += 1 / (other_distance_to_task + 1) # Increment support if another agent is closer

            queue_support = 1 if first_task_in_queue and first_task_in_queue.id == task.id else 0.0

            likelihood = max(0.01, (distance_factor + queue_support) / (competing_support + 1))
            likelihoods[task.id] = likelihood  

        return likelihoods
