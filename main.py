
import simrunner
import random
from pathlib import Path

from datalogger import DataLogger

from app_config import PATHS, SIMULATION_SETTINGS


number_of_agents = SIMULATION_SETTINGS["number_of_agents"]
planner_algorithm = SIMULATION_SETTINGS["planner_algorithm"]
world_map = SIMULATION_SETTINGS["world_map"]

Simulation_seeds = SIMULATION_SETTINGS["simulation_seeds"]
simulation_timesteps = SIMULATION_SETTINGS["simulation_timesteps"]
number_of_tasks = SIMULATION_SETTINGS["number_of_tasks"]

visualization = SIMULATION_SETTINGS["visualization"]

record = SIMULATION_SETTINGS["record"]
data_folder_dir = str(PATHS["data_dir"])

message_policy = SIMULATION_SETTINGS["message_policy"]

def _resolve_world_map_path(map_name: str) -> str:
    return str(Path(PATHS["maps_dir"]) / map_name)

def main():
    if message_policy:
        number_of_simulations = len(number_of_agents) * len(planner_algorithm) * len(world_map) * len(number_of_tasks) * len(Simulation_seeds) * len(simulation_timesteps) * len(message_policy)
    else: 
        number_of_simulations = len(number_of_agents) * len(planner_algorithm) * len(world_map) * len(number_of_tasks) * len(Simulation_seeds) * len(simulation_timesteps)
    for ii in range(number_of_simulations):
        # Calculate the indices for each parameter based on the current simulation index
        idx_agents = ii % len(number_of_agents)
        idx_planner = (ii // len(number_of_agents)) % len(planner_algorithm)
       
        idx_map = (ii // (len(number_of_agents) * len(planner_algorithm))) % len(world_map)
        idx_tasks = (ii // (len(number_of_agents) * len(planner_algorithm) * len(world_map))) % len(number_of_tasks)
        idx_seed = (ii // (len(number_of_agents) * len(planner_algorithm) * len(world_map) * len(number_of_tasks))) % len(Simulation_seeds)
        idx_timesteps = (ii // (len(number_of_agents) * len(planner_algorithm) * len(world_map) * len(number_of_tasks) * len(Simulation_seeds))) % len(simulation_timesteps)
        if message_policy:
            idx_policies =  (ii // (len(number_of_agents) * len(planner_algorithm) * len(world_map) * len(number_of_tasks) * len(Simulation_seeds) * len(simulation_timesteps))) % len(message_policy)

        # Get the current parameters for this simulation
        current_number_of_agents = number_of_agents[idx_agents]
        current_planner_algorithm = planner_algorithm[idx_planner]
        current_world_map = _resolve_world_map_path(world_map[idx_map])
        current_number_of_tasks = number_of_tasks[idx_tasks]
        current_simulation_seed = Simulation_seeds[idx_seed]
        current_simulation_timesteps = simulation_timesteps[idx_timesteps]
        if message_policy:
            current_message_policy = message_policy[idx_policies]
        else: 
            current_message_policy = None

        random.seed(current_simulation_seed)  # Set the random seed for reproducibility

        
        # Initialize the simulation with the current parameters
        sim_world = simrunner.init(
            current_world_map,
            current_number_of_agents,
            current_number_of_tasks,
            current_planner_algorithm,
            current_simulation_timesteps,
            current_message_policy
        )

        logger = None
        if record:
            logger = DataLogger({
                "number_of_agents": current_number_of_agents,
                "planner_algorithm": current_planner_algorithm,
                "world_map": world_map[idx_map],
                "number_of_tasks": current_number_of_tasks,
                "simulation_seed": current_simulation_seed,
                "simulation_timesteps": current_simulation_timesteps,
                "policies": current_message_policy.name
            }, world_info = sim_world.get_world_map_info(), output_dir=data_folder_dir)

        
        simrunner.engine(current_simulation_timesteps, visualization, logger, sim_world)


if __name__ == "__main__":
    
    main()


    
