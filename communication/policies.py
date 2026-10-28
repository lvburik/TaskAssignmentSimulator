"""Policies used to decide whether a message should be delivered."""

from dataclasses import dataclass
from math import dist
from typing import Any, Callable, Optional, Protocol, Sequence

from communication.messages import Message


Position = Sequence[float]
PositionResolver = Callable[[Any], Optional[Position]]


class MessagePolicy(Protocol):
	"""Interface for delivery policies used by :class:`communication.bus.MessageBus`."""

	def __call__(self, message: Message, recipient: Optional[Any]) -> bool:
		"""Return ``True`` when delivery is allowed for this recipient."""


def euclidean_distance(a: Position, b: Position) -> float:
	"""Compute Euclidean distance between two positions."""
	return dist(a, b)

def position_resolver(agent_id, world):
	"""Look up an agent's current position by identifier."""
	for agent in world.agents:
		if agent.id == agent_id:
			return agent.location
	

@dataclass
class LimitedRangePolicy:
	"""Allow message delivery only when sender and recipient are in range.

	This policy is only evaluated when a concrete recipient id is available.
	For topic-only subscribers (where recipient is ``None``), delivery is allowed.
	"""

	max_distance: float
	
	
	allow_when_unknown: bool = True
	

	def __init__(self, max_distance: float, allow_when_unknown: bool = True, distance_fn: Callable[[Position, Position], float] = euclidean_distance):
		"""Initialize the maximum separation at which messages may be delivered."""
		self.max_distance = max_distance
		self.allow_when_unknown = allow_when_unknown
		self.distance_fn = distance_fn

		self.name = f"LimitedRange_{max_distance}"

	def __call__(self, message: Message, recipient: Optional[Any], world) -> bool:
		"""Allow delivery only when sender and recipient are closer than the limit."""
		sender = message.sender
		sender_location = position_resolver(sender, world)

		recipient_location = position_resolver(recipient, world)

		#print(f"policy called for message sent by {sender} at {sender_location} to {recipient} at {recipient_location}")

		distance = euclidean_distance(sender_location, recipient_location)


		return distance < self.max_distance

class AlwaysAllowPolicy:
	"""Always allow message delivery."""

	name = "AlwaysAllow"

	def __call__(self, message: Message, recipient: Optional[Any], _) -> bool:
		return True

class PartlyBrokenPolicy:
	"""Block messages when both sender and recipient are in the broken group."""

	def __init__(self, number_of_agents, broken_fraction):
		"""Mark the first fraction of agent IDs as the communication-limited group."""
		self.broken_fraction = broken_fraction
		self.broken_agents = set(range(int(number_of_agents * broken_fraction)))
		self.name = f"{broken_fraction*100}%_Broken"

	def __call__(self, message: Message, recipient: Optional[Any], _) -> bool:
		"""Return whether this sender-recipient pair can communicate."""
		if message.sender in self.broken_agents and recipient in self.broken_agents:
			return False
		return True
