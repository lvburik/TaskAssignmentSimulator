from planners.class_definition import Planner
from pathfinding.to_direction import ToDirection
from pathlib import Path
from task import Task

import pandas as pd
import pickle


class LearnedPlanner:
    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        self.pathfinding_algorithm = pathfinding_algorithm

        MODEL_DIR = Path("/home/luc/Desktop/AfstudeerProject/TaskAssignmentLearner/models/MLP.pkl")
        self.model = pickle.load(open(MODEL_DIR, 'rb'))

        self.current_queue = []
        self.current_goal = None

    def update_plan(self, observation: dict):
        #clear task list
        self.current_queue = []

        #process observation
        self.agent_location = observation["agent_location"]
        
        tasks = [task for task in observation["tasks"] if (not task.completed and task.spawned)]

        team_locations = [pos[1] for pos in observation["other_agent_locations"] if pos[1] != self.agent_location]

        #prepare for model input
        input_data = []
        for task in tasks:
            row = {"task_x": task.location[0],
                "task_y": task.location[1],
                "agent_x": self.agent_location[0],
                "agent_y": self.agent_location[1],
                "team_count": len(team_locations),
                }
            for teammate_index, location in enumerate(team_locations):
                            
                            row[f"teammate_{teammate_index}_x"] = location[0]
                            row[f"teammate_{teammate_index}_y"] = location[1]
            input_data.append(row)

        X = pd.DataFrame(input_data).fillna(0)

        #predict
        predictions = self.model.predict(X)

        #add predicted tasks to queue
        for ii, prediction in enumerate(predictions):
            if prediction == True:
                self.current_queue.append([tasks[ii], self.pathfinding_algorithm.get_distance(self.agent_location, tasks[ii].location)])

        #sort predicted task queue by current distance to task:
        if self.current_queue:
            if len(self.current_queue) > 1:
                # Sorts the list in-place by the second element (distance)
                self.current_queue.sort(key=lambda x: x[1])

            self.current_goal = self.current_queue[0][0].location

    def act(self):
            
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
            
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
    
        else: 
            next_location = self.pathfinding_algorithm.next_step(self.agent_location, self.current_goal)
            
        return ToDirection(self.agent_location, next_location)  # Convert the next step in the path to a direction
           


        



          

            









        
