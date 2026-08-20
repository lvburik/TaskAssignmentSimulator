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
from communication.policies import LimitedRangePolicy

from world import World
from datalogger import DataLogger

max_fps = 30

def _resolve_planner(planner_algorithm):
    if isinstance(planner_algorithm, str):
        planners = {
            "Random": RandomMovesPlanner,
            "Greedy": GreedyTaskSelector,
            "Tom": TheoryOfMindPlanner,
            "Auction": AuctionPlanner,
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

def _resolve_messagepolicies(message_policy):
    if isinstance(message_policy, str):
        policies = {
            "range": LimitedRangePolicy,
        }
        if message_policy not in policies:
            raise ValueError(f"Unsupported message policy: {message_policy}")
        return policies[message_policy]
    return message_policy

def init(world_map, number_of_agents, number_of_tasks, planner_algorithm, pathfinding_algorithm, steps, message_policy = "range"):
    planner_cls = _resolve_planner(planner_algorithm)
    pathfinding_method = _resolve_pathfinding(pathfinding_algorithm)
    message_plcy = _resolve_messagepolicies(message_policy)

    world = World(world_map)

    message_bus = MessageBus()
    message_bus.add_world(world)
    message_bus.add_policy(message_plcy)
    
    for ii in range(number_of_agents):
        planner = planner_cls(pathfinding_method, agent_id = ii, messagebus = message_bus)
        world.add_agent(agent.Agent(id=ii, planner=planner))

    
    for ii in range(number_of_tasks):
        world.add_task(task.Task(id=ii, spawn_time=random.randint(0, steps - 1)))

    return world
    
def engine(steps, visualization, logger: DataLogger, world):
    
    if visualization:
        viewer = PygameViewer(world)
        viewer.run(step_callback=lambda _step: world.step(logger), max_steps=steps, fps=max_fps)
        return

    for _ in range(steps):
        world.step(logger)
        
        

