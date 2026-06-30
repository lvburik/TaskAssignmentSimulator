from abc import abstractmethod, ABC
from communication import bus as bus
from communication import messages as messages

class Planner(ABC):
    @abstractmethod
    def __init__(self, pathfinding_algorithm, Communication: tuple[bus.MessageBus, list[messages.Message]] | None =None):
        self.pathfinding_algorithm = pathfinding_algorithm
        self.message_bus = Communication[0] if Communication else None
        self.received_messages = Communication[1] if Communication else None

    @abstractmethod
    def update_plan(self, observation: dict):
        pass

    @abstractmethod
    def act(self):
        pass

    