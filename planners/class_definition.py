from abc import abstractmethod, ABC
from communication import bus as bus
from communication import messages as messages

class Planner(ABC):
    @abstractmethod
    def __init__(self, pathfinding_algorithm):
        self.pathfinding_algorithm = pathfinding_algorithm

    @abstractmethod
    def update_plan(self, observation: dict):
        pass

    @abstractmethod
    def act(self):
        pass

    