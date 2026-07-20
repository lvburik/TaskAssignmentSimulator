number_of_agents = [10]
planner_algorithm = ["TheoryOfMindPlanner"]
pathfinding_algorithm = ["DoubleDijkstra"]
world_map = ["Map14.png"]
number_of_tasks = [1000]
Simulation_seeds = [3876428754]
simulation_timesteps = [1000]

visualization = True

record = False
data_folder_dir = "data/"


import simrunner
import random
import os

from datalogger import DataLogger


def _resolve_world_map_path(map_name: str) -> str:
    return os.path.join(os.path.dirname(__file__), "maps", map_name)

def main():
    number_of_simulations = len(number_of_agents) * len(planner_algorithm) * len(pathfinding_algorithm) * len(world_map) * len(number_of_tasks) * len(Simulation_seeds) * len(simulation_timesteps)

    for ii in range(number_of_simulations):
        # Calculate the indices for each parameter based on the current simulation index
        idx_agents = ii % len(number_of_agents)
        idx_planner = (ii // len(number_of_agents)) % len(planner_algorithm)
        idx_pathfinding = (ii // (len(number_of_agents) * len(planner_algorithm))) % len(pathfinding_algorithm)
        idx_map = (ii // (len(number_of_agents) * len(planner_algorithm) * len(pathfinding_algorithm))) % len(world_map)
        idx_tasks = (ii // (len(number_of_agents) * len(planner_algorithm) * len(pathfinding_algorithm) * len(world_map))) % len(number_of_tasks)
        idx_seed = (ii // (len(number_of_agents) * len(planner_algorithm) * len(pathfinding_algorithm) * len(world_map) * len(number_of_tasks))) % len(Simulation_seeds)
        idx_timesteps = (ii // (len(number_of_agents) * len(planner_algorithm) * len(pathfinding_algorithm) * len(world_map) * len(number_of_tasks) * len(Simulation_seeds))) % len(simulation_timesteps)

        # Get the current parameters for this simulation
        current_number_of_agents = number_of_agents[idx_agents]
        current_planner_algorithm = planner_algorithm[idx_planner]
        current_pathfinding_algorithm = pathfinding_algorithm[idx_pathfinding]
        current_world_map = _resolve_world_map_path(world_map[idx_map])
        current_number_of_tasks = number_of_tasks[idx_tasks]
        current_simulation_seed = Simulation_seeds[idx_seed]
        current_simulation_timesteps = simulation_timesteps[idx_timesteps]

        random.seed(current_simulation_seed)  # Set the random seed for reproducibility

        # Initialize the simulation with the current parameters
        sim_world = simrunner.init(
            current_world_map,
            current_number_of_agents,
            current_number_of_tasks,
            current_planner_algorithm,
            current_pathfinding_algorithm,
            current_simulation_timesteps,
        )

        logger = None
        if record:
            logger = DataLogger({
                "number_of_agents": current_number_of_agents,
                "planner_algorithm": current_planner_algorithm,
                "pathfinding_algorithm": current_pathfinding_algorithm,
                "world_map": world_map[idx_map],
                "number_of_tasks": current_number_of_tasks,
                "simulation_seed": current_simulation_seed,
                "simulation_timesteps": current_simulation_timesteps
            }, world_info = sim_world.get_world_map_info(), output_dir=data_folder_dir)

        
        simrunner.engine(current_simulation_timesteps, visualization, logger, sim_world)


if __name__ == "__main__":
    main()


    

