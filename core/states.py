from dataclasses import dataclass
from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.task import Task


Position = Tuple[int, int]


@dataclass
class AgentState:
    position: Position


@dataclass
class WorldState:
    agents: Dict[int, "Agent"]
    tasks: Dict[int, "Task"]
    width: int
    height: int
    walls: List[List[int]]
    time: int = 0


@dataclass
class TaskState:
    location: Position
    completed: bool = False