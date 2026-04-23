from simulation.initialization import create_world
from visualization.pygame_viewer import PygameViewer

from algortithms.assignment.greedy import greedy_task_selector
from algortithms.assignment.none import none_task_selector
from algortithms.planning.Astar import a_star_planner
from algortithms.planning.random import random_movement_planner


ASSIGNMENT_ALGORITHMS = {
    "greedy": greedy_task_selector,
    "none": none_task_selector,
}

PATHFINDING_ALGORITHMS = {
    "astar": a_star_planner,
    "random": random_movement_planner,
}


def _advance_one_step(world, assignment_algorithm, pathfinding_algorithm):
    actions = {}
    for agent in world.state.agents.values():
        action = agent.decide(world.state, assignment_algorithm, pathfinding_algorithm)
        if action is not None:
            actions[agent.id] = action

    world.step(actions)


def run_simulation(
    width=10,
    height=10,
    number_of_agents=2,
    number_of_tasks=0,
    steps=10,
    view=False,
    fps=4,
    map_name=None,
    assignment_name="greedy",
    pathfinding_name="astar",
):
    """Run the simulation loop in console mode or pygame view mode."""
    world = create_world(
        width=width,
        height=height,
        number_of_agents=number_of_agents,
        number_of_tasks=number_of_tasks,
        map_name=map_name,
    )

    assignment_algorithm = ASSIGNMENT_ALGORITHMS[assignment_name]
    pathfinding_algorithm = PATHFINDING_ALGORITHMS[pathfinding_name]

    if view:
        viewer = PygameViewer(world)

        def step_callback(step):
            _advance_one_step(world, assignment_algorithm, pathfinding_algorithm)

        viewer.run(step_callback=step_callback, max_steps=steps, fps=fps)
        return world

    for step in range(steps):
        _advance_one_step(world, assignment_algorithm, pathfinding_algorithm)

        print(f"Step {step}:")
        for agent_id, agent in world.state.agents.items():
            print(f"  Agent {agent_id} at position {agent.state.position}")

    return world


def available_assignment_algorithms():
    return sorted(ASSIGNMENT_ALGORITHMS.keys())


def available_pathfinding_algorithms():
    return sorted(PATHFINDING_ALGORITHMS.keys())