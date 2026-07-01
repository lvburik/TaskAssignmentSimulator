import agent
import task
import random

from visualization.pygame_viewer import PygameViewer

from planners.random_moves import RandomMovesPlanner
from planners.greedy import GreedyTaskSelector
from planners.tom import TheoryOfMindPlanner
from planners.auction import AuctionPlanner

from pathfinding.Double_Dijkstra import DoubleDijkstraPlanner
from pathfinding.AStar import AStarPlanner

from communication.bus import MessageBus

from world import World
from datalogger import DataLogger

max_fps = 30
status_updates = True # Set to True to enable status updates during simulation

def _resolve_planner(planner_algorithm):
    if isinstance(planner_algorithm, str):
        planners = {
            "RandomMovesPlanner": RandomMovesPlanner,
            "GreedyTaskSelector": GreedyTaskSelector,
            "TheoryOfMindPlanner": TheoryOfMindPlanner,
            "AuctionPlanner": AuctionPlanner,
        }
        if planner_algorithm not in planners:
            raise ValueError(f"Unsupported planner algorithm: {planner_algorithm}")
        return planners[planner_algorithm]
    return planner_algorithm


def _resolve_pathfinding(pathfinding_algorithm):
    if isinstance(pathfinding_algorithm, str):
        pathfinders = {
            "DoubleDijkstra": DoubleDijkstraPlanner,
            "AStar": AStarPlanner,
        }
        if pathfinding_algorithm not in pathfinders:
            raise ValueError(f"Unsupported pathfinding algorithm: {pathfinding_algorithm}")
        return pathfinders[pathfinding_algorithm]
    return pathfinding_algorithm

def init(world_map, number_of_agents, number_of_tasks, planner_algorithm, pathfinding_algorithm, steps):
    planner_cls = _resolve_planner(planner_algorithm)
    pathfinding_method = _resolve_pathfinding(pathfinding_algorithm)

    bus = MessageBus()
    recieved_messages = []

    agents = []
    for ii in range(number_of_agents):
        planner = planner_cls(pathfinding_method, (bus, recieved_messages))
        agents.append(agent.Agent(id=ii, planner=planner))

    tasks = []
    for ii in range(number_of_tasks):
        tasks.append(task.Task(id=ii, spawn_time=random.randint(0, steps - 1)))
    


    return World(world_map, agents, tasks)
    
def engine(steps, visualization, logger: DataLogger, world):
    
    if visualization:
        viewer = PygameViewer(world)
        viewer.run(step_callback=lambda _step: world.step(logger), max_steps=steps, fps=max_fps)
        return

    for _ in range(steps):
        world.step(logger)
        
        

