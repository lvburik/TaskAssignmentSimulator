from agents.agent import Agent
from simulation.map_loader import load_map_matrix
from world.grid import GridWorld
from world.task import Task

import random


def _free_positions(width, height, walls):
    positions = []
    for y in range(height):
        for x in range(width):
            if walls[y][x] == 0:
                positions.append((x, y))
    return positions


def _pick_position(available_positions):
    if not available_positions:
        raise ValueError("No free cells available for spawning agents or tasks")

    index = random.randrange(len(available_positions))
    return available_positions.pop(index)


def create_world(
    width=10,
    height=10,
    number_of_agents=2,
    number_of_tasks=0,
    map_name=None,
    movement_warnings=True,
):
    """Create the world and spawn agents and tasks."""
    if map_name is not None:
        walls = load_map_matrix(map_name)
        height = len(walls)
        width = len(walls[0]) if height else 0
    else:
        walls = [[0 for _ in range(width)] for _ in range(height)]

    world = GridWorld(width, height, walls=walls, movement_warnings=movement_warnings)
    available_positions = _free_positions(width, height, walls)

    for ii in range(number_of_agents):
        agent = Agent(id=ii, position=_pick_position(available_positions))
        world.add_agent(agent)

    for ii in range(number_of_tasks):
        task = Task(id=ii, location=_pick_position(available_positions))
        world.add_task(task)

    return world