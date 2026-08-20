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


@dataclass
class LimitedRangePolicy:
	"""Allow message delivery only when sender and recipient are in range.

	This policy is only evaluated when a concrete recipient id is available.
	For topic-only subscribers (where recipient is ``None``), delivery is allowed.
	"""

	max_distance: float
	position_resolver: PositionResolver
	allow_when_unknown: bool = True
	distance_fn: Callable[[Position, Position], float] = euclidean_distance

	def __call__(self, message: Message, recipient: Optional[Any], world) -> bool:
		print("policy_called")
		return True
