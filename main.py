import argparse

from simulation.engine import (
    available_assignment_algorithms,
    available_pathfinding_algorithms,
    run_simulation,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run the agent simulation")
    assignment_choices = available_assignment_algorithms()
    pathfinding_choices = available_pathfinding_algorithms()

    parser.add_argument("--width", type=int, default=10, help="Grid width")
    parser.add_argument("--height", type=int, default=10, help="Grid height")
    parser.add_argument("--agents", type=int, default=2, help="Number of agents")
    parser.add_argument("--tasks", type=int, default=5, help="Number of tasks")
    parser.add_argument("--steps", type=int, default=10, help="Number of simulation steps")
    parser.add_argument("--view", action="store_true", help="Enable pygame visualization")
    parser.add_argument("--fps", type=int, default=4, help="Viewer FPS when --view is enabled")
    parser.add_argument("--map", dest="map_name", default=None, help="PNG map name from the maps folder")
    parser.add_argument(
        "--assignment",
        choices=assignment_choices,
        default="greedy",
        help=f"Task assignment algorithm ({', '.join(assignment_choices)})",
    )
    parser.add_argument(
        "--pathfinding",
        choices=pathfinding_choices,
        default="astar",
        help=f"Pathfinding algorithm ({', '.join(pathfinding_choices)})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_simulation(
        width=args.width,
        height=args.height,
        number_of_agents=args.agents,
        number_of_tasks=args.tasks,
        steps=args.steps,
        view=args.view,
        fps=args.fps,
        map_name=args.map_name,
        assignment_name=args.assignment,
        pathfinding_name=args.pathfinding,
    )