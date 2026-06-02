import config

from simulation.engine_dual_thread import (
    available_assignment_algorithms,
    available_pathfinding_algorithms,
)
from simulation.engine_dual_thread import run_simulation as run_dual_thread_simulation
from simulation.engine_single_thread import run_simulation as run_single_thread_simulation
from algorithms.assignment.metrics.log_world import WorldLogger


if __name__ == "__main__":
    # Note: argparse has been removed. Use `config.py` to change defaults.
    # If you need runtime overrides, alter `config.py` or call the relevant
    # simulation runner directly from another script.
    selected_runner = run_single_thread_simulation if config.ENGINE == "single" else run_dual_thread_simulation
    world_logger = WorldLogger() if config.LOG_WORLD else None
    selected_runner(
        width=config.WIDTH,
        height=config.HEIGHT,
        number_of_agents=config.NUMBER_OF_AGENTS,
        number_of_tasks=config.NUMBER_OF_TASKS,
        steps=config.STEPS,
        view=config.VIEW,
        fps=config.FPS,
        map_name=config.MAP_NAME,
        movement_warnings=config.MOVEMENT_WARNINGS,
        assignment_name=config.ASSIGNMENT_DEFAULT,
        pathfinding_name=config.PATHFINDING_DEFAULT,
        seed=config.SEED,
        world_logger=world_logger,
    )

    if world_logger is not None:
        world_logger.save(config.WORLD_LOG_PATH)