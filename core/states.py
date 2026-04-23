from dataclasses import dataclass
from typing import Dict, Tuple

Position = Tuple[int, int]

@dataclass
class AgentState:
    id: int
    position: Position

@dataclass
class WorldState:
    Agents: Dict[int, AgentState]
    width: int
    height: int
    time: int = 0

    