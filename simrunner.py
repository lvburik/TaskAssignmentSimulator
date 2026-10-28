import agent
import task
import random

from planners.random_moves import RandomMovesPlanner
from planners.greedy import GreedyTaskSelector
from planners.tom import TheoryOfMindPlanner
from planners.auction import AuctionPlanner
from planners.XGBoost import XGBPlanner
from planners.MLP import MLPPlanner
from planners.CNN import CNNPlanner

from pathfinding.distancefinder import DistanceFinder

from communication.bus import MessageBus


from world import World
from datalogger import DataLogger

max_fps = 120

def _resolve_planner(planner_algorithm):
    if isinstance(planner_algorithm, str):
        planners = {
            "Random": RandomMovesPlanner,
            "Greedy": GreedyTaskSelector,
            "Tom": TheoryOfMindPlanner,
            "Auction": AuctionPlanner,
            "XGB": XGBPlanner,
            "MLP": MLPPlanner,
            "CNN": CNNPlanner,
        }
        if planner_algorithm not in planners:
            raise ValueError(f"Unsupported planner algorithm: {planner_algorithm}")
        return planners[planner_algorithm]
    return planner_algorithm

def init(world_map, number_of_agents, number_of_tasks, planner_algorithm, steps, message_policy):
    planner_cls = _resolve_planner(planner_algorithm) 

    print("initializing world")
    world = World(world_map)

    message_bus = MessageBus()
    message_bus.add_world(world)
    
    message_bus.add_policy(message_policy)
    
    distancefinder = DistanceFinder(world.map)

    print("initializing agents")
    for ii in range(number_of_agents):
        planner = planner_cls(distancefinder, agent_id = ii, messagebus = message_bus)
        world.add_agent(agent.Agent(id=ii, planner=planner))

    print("initializing tasks")
    for ii in range(number_of_tasks):
        world.add_task(task.Task(id=ii, spawn_time=random.randint(-number_of_agents-10, steps - 1)))

    print("ready")
    return world
    
def engine(steps, visualization, logger: DataLogger, world):
    
    if visualization:
        from visualization.pygame_viewer import PygameViewer

        viewer = PygameViewer(world)
        viewer.run(step_callback=lambda _step: world.step(logger), max_steps=steps, fps=max_fps)
        return

    for _ in range(steps):
        world.step(logger)
        
        
