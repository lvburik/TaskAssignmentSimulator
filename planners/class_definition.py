"""Abstract planner interface used by simulation agents."""

from abc import abstractmethod, ABC
from communication import bus as bus
from communication import messages as messages

class Planner(ABC):
    """Base contract for planners that update plans and return world actions."""

    @abstractmethod
    def __init__(self, pathfinding_algorithm, agent_id, messagebus):
        """Store shared pathfinding and identity context for a planner."""
        self.pathfinding_algorithm = pathfinding_algorithm
        self.agent_id = agent_id
        

    @abstractmethod
    def update_plan(self, observation: dict):
        """Update planner state from the agent's current observation."""
        pass

    @abstractmethod
    def act(self):
        """Return one movement, task-completion, or idle action."""
        pass

    