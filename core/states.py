from dataclasses import dataclass, field
from typing import Dict, List, Tuple, TYPE_CHECKING
from threading import Lock

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.task import Task


Position = Tuple[int, int]



@dataclass
class AgentState:
    position: Position

@dataclass
class AgentMemory:
    action_queue: List[str] = field(default_factory=list)
    task_queue: List[int] = field(default_factory=list)
    path: List[Position] = field(default_factory=list)
    world_observation: "WorldState" = None 
    lock: Lock = field(default_factory=Lock, repr=False, compare=False)
    planning_memory: any = None  # Placeholder for any additional planning-related memory


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


