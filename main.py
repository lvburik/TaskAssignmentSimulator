
number_of_agents = [40]
planner_algorithm = ["CNN"]
world_map = ["Map0.png"]

Simulation_seeds = [1324, 132, 1372, 137234587]
#Simulation_seeds = [1724, 5001, 10, 172, 17, 8, 2, 4]
simulation_timesteps = [500]
number_of_tasks = [1100]  # Set number_of_tasks equal to simulation_timesteps

visualization = False

record = True
data_folder_dir = "Data/"


import simrunner
import random
import os

from datalogger import DataLogger

from communication.policies import LimitedRangePolicy, AlwaysAllowPolicy, PartlyBrokenPolicy
#message_policy = [PartlyBrokenPolicy(number_of_agents = 30, broken_fraction=10), PartlyBrokenPolicy(number_of_agents = 30, broken_fraction=20), PartlyBrokenPolicy(number_of_agents = 30, broken_fraction=30), PartlyBrokenPolicy(number_of_agents = 30, broken_fraction=40), PartlyBrokenPolicy(number_of_agents = 30, broken_fraction=50)]  # Example: 50% of agents are broken
message_policy = [AlwaysAllowPolicy()]

def _resolve_world_map_path(map_name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "maps", map_name)

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


    

