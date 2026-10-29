"""Abstract planner interface used by simulation agents."""

from abc import abstractmethod, ABC
from communication import bus as bus
from communication import messages as messages
from pathfinding.to_direction import ToDirection

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

    def act(self):
        """Move toward the current goal or perform the task when at its location."""
        if self.current_goal is None:
            return None  # No goal selected

        if self.agent_location == self.current_goal:
            self._on_task_reached()
            return "perform_task"

        next_location = self.pathfinding_algorithm.next_step(self.agent_location, self.current_goal)
        return ToDirection(self.agent_location, next_location)

    def _on_task_reached(self):
        """Hook called when the agent is at its goal, before performing the task."""
        pass

    