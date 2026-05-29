from simulation.initialization import create_world
from visualization.pygame_viewer import PygameViewer

from algorithms.assignment.greedy import greedy_task_selector, simple_greedy_task_selector
from algorithms.assignment.none import none_task_selector
from algorithms.assignment.random import random_task_assignment
from algorithms.assignment.tom import bayesian_delagation_assignment
from algorithms.planning.Astar import a_star_planner
from algorithms.planning.random import random_movement_planner
from algorithms.assignment.auction import decentralized_auction_task_selector
import threading


ASSIGNMENT_ALGORITHMS = {
    "greedy": greedy_task_selector,
    "greedy_simple": simple_greedy_task_selector,
    "auction": decentralized_auction_task_selector,
    "none": none_task_selector,
    "random": random_task_assignment,
    "tom": bayesian_delagation_assignment,
}

PATHFINDING_ALGORITHMS = {
    "astar": a_star_planner,
    "random": random_movement_planner,
}


def _advance_one_step(world, pathfinding_algorithm):
    actions = {}

    # Have each agent sense the current world state to get a snapshot of the environment
    for agent in world.state.agents.values():
        agent.sense(world.state)

    # Have each agent decide on an action based on the current world state and the provided algorithms
    for agent in world.state.agents.values():
        action = agent.act(pathfinding_algorithm)
        if action is not None:
            actions[agent.id] = action

    # Execute the decided actions in the world, which will update the world state for the next step
    world.step(actions)


def _allocation_loop(world, assignment_algorithm, stop_event, interval=0.1):
    """Continuously run task-allocation for agents in parallel with execution loop.

    - `assignment_algorithm` should be callable (agent_state, tasks) -> assignment
    - `stop_event` is a threading.Event used to stop the loop cleanly
    - `interval` is seconds to wait between allocation iterations
    """
    while not stop_event.is_set():
        # Plan tasks for each agent; plan_tasks will update each agent's memory under lock
        for agent in world.state.agents.values():
            try:
                agent.plan_tasks(assignment_algorithm)
            except Exception:
                # Keep allocation loop alive even if one agent fails planning
                continue
            

        # Wait before next allocation round (interruptible)
        stop_event.wait(interval)


def run_simulation(
    width=10,
    height=10,
    number_of_agents=2,
    number_of_tasks=0,
    steps=10,
    view=False,
    fps=4,
    map_name=None,
    movement_warnings=True,
    assignment_name="greedy",
    pathfinding_name="astar",
    seed=None,
):
    """Run the simulation loop in console mode or pygame view mode."""
    world = create_world(
        width=width,
        height=height,
        number_of_agents=number_of_agents,
        number_of_tasks=number_of_tasks,
        map_name=map_name,
        movement_warnings=movement_warnings,
        seed=seed,
    )

    assignment_algorithm = ASSIGNMENT_ALGORITHMS[assignment_name]
    pathfinding_algorithm = PATHFINDING_ALGORITHMS[pathfinding_name]

    if view:
        viewer = PygameViewer(world)

        def step_callback(step):
            _advance_one_step(world, pathfinding_algorithm)

        # Start allocation thread while the viewer runs
        stop_event = threading.Event()
        alloc_thread = threading.Thread(
            target=_allocation_loop,
            args=(world, assignment_algorithm, stop_event),
            daemon=True,
        )
        alloc_thread.start()

        viewer.run(step_callback=step_callback, max_steps=steps, fps=fps)

        # Stop allocation thread after viewer stops
        stop_event.set()
        alloc_thread.join()

        return world


    # Non-view (console) mode: start allocation thread and run discrete steps
    stop_event = threading.Event()
    alloc_thread = threading.Thread(target=_allocation_loop, args=(world, assignment_algorithm, stop_event), daemon=True)
    alloc_thread.start()

    for step in range(steps):
        _advance_one_step(world, pathfinding_algorithm)

        print(f"Step {step}:")
        for agent_id, agent in world.state.agents.items():
            print(f"  Agent {agent_id} at position {agent.state.position}")

    # Stop allocation thread and wait for it to finish
    stop_event.set()
    alloc_thread.join()

    return world


def available_assignment_algorithms():
    return sorted(ASSIGNMENT_ALGORITHMS.keys())


def available_pathfinding_algorithms():
    return sorted(PATHFINDING_ALGORITHMS.keys())