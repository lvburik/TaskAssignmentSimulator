import json
import os
import datetime



class DataLogger:
    def __init__(self, simulation_paramaters, world_info, output_dir="data/"):
        
        self.simulation_paramaters = simulation_paramaters
        self.world_info = world_info
        
        self.output_dir = output_dir

        self._create_log_file()

        self._log_world_info()

    
    def log(self, world_state):        
        self.datafile.write(json.dumps(world_state) + "\n")
        
    
    def _create_log_file(self):
        self.file_name = self._parse_file_name(self.simulation_paramaters)

        print(f"Creating log file: {self.file_name}")

        #create the full path to the output directory (including root directory)
        self.output_dir = os.path.join(os.path.dirname(__file__), self.output_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.file_path = os.path.join(self.output_dir, self.file_name)

        self.datafile = open(self.file_path, "w", encoding="utf-8")



    def _parse_file_name(self, simulation_paramaters):
        planning_algorithm = simulation_paramaters.get("planner_algorithm", "unknown_planner")
        number_of_agents = simulation_paramaters.get("number_of_agents", "unknown_agents")
        number_of_tasks = simulation_paramaters.get("number_of_tasks", "unknown_tasks")
        map_name = simulation_paramaters.get("world_map", "unknown_map")

        #remove file extension from map_name
        map_name = os.path.splitext(map_name)[0]

        return f"TASim_{planning_algorithm}_{number_of_agents}A_{number_of_tasks}T_{map_name}_{datetime.datetime.now().strftime("%Y-%m-%d_%H%M-%S")}.json"
    
    def _log_world_info(self):
        self.datafile.write(json.dumps({"simulation_paramaters": self.simulation_paramaters}) + "\n")
        self.datafile.write(json.dumps({"world_info": self.world_info}) + "\n")
        