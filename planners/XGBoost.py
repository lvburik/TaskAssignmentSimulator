from pathfinding.to_direction import ToDirection
from pathlib import Path
import pickle

from planners.model_input import available_tasks, tabular_inputs


class XGBPlanner:
    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        self.pathfinding_algorithm = pathfinding_algorithm

        MODEL_DIR = Path("D:\\afstuderen\\TaskAssignmentLearner\\models\\XGBoost_best_1.pkl")
        self.model = pickle.load(open(MODEL_DIR, 'rb'))

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

    def act(self):
            
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
            
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
    
        else: 
            next_location = self.pathfinding_algorithm.next_step(self.agent_location, self.current_goal)
            
        return ToDirection(self.agent_location, next_location)  # Convert the next step in the path to a direction
           


        



          

            









        
