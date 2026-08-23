"""A small synchronous message bus for agent communication."""

from typing import Any, Callable, Dict, List, Optional

from communication.messages import Message
from communication.policies import MessagePolicy


class MessageBus:
	"""A very small in-process message bus.

	Subscribers register callbacks for topics or for a specific recipient id.
	When a `Message` is published, topic subscribers and recipient-specific
	subscribers are invoked synchronously in the publisher's thread.
	"""

	def __init__(self) -> None:
		# topic -> list of (callback, subscriber id used for policy checks)
		self._topics: Dict[str, List[tuple[Callable[[Message], None], Optional[Any]]]] = {}
		# recipient id -> list of callbacks
		self._recipients: Dict[Any, List[Callable[[Message], None]]] = {}
		# delivery policies evaluated before each callback invocation
		self._policies: List[MessagePolicy] = []

	def add_world(self, world):
		self.world = world

	def add_policy(self, policy: MessagePolicy) -> None:
		"""Register a delivery policy.

		All registered policies must allow delivery for a callback to be invoked.
		"""
		self._policies.append(policy)

	def remove_policy(self, policy: MessagePolicy) -> None:
		"""Unregister a previously added policy."""
		if policy in self._policies:
			self._policies.remove(policy)

	def clear_policies(self) -> None:
		"""Remove all registered policies."""
		self._policies.clear()

	def _delivery_allowed(self, message: Message, recipient: Optional[Any]) -> bool:
		for policy in self._policies:
			if not policy(message, recipient, self.world):
				return False
		return True

	@staticmethod
	def _infer_callback_recipient(callback: Callable[[Message], None]) -> Optional[Any]:
		"""Try to infer a receiver id from a bound method callback."""
		receiver = getattr(callback, "__self__", None)
		if receiver is None:
			return None

		for attr in ("agent_id", "id"):
			value = getattr(receiver, attr, None)
			if value is not None:
				return value

		return None

	def subscribe(
		self,
		callback: Callable[[Message], None],
		*,
		topic: Optional[str] = None,
		recipient: Optional[Any] = None,
		subscriber_id: Optional[Any] = None,
	) -> None:
		"""Subscribe a callback to a `topic` and/or a `recipient`.

		- `topic`: delivers messages where `Message.topic == topic`.
		- `recipient`: delivers messages where `Message.recipient == recipient`.
		- `subscriber_id`: receiver identity for topic deliveries, used by
		  policies that need sender/receiver context (for example range checks).

		The same callback may be subscribed to multiple topics/recipients.
		"""
		if topic is None and recipient is None:
			raise ValueError("either topic or recipient must be provided")

		if topic is not None:
			self._topics.setdefault(topic, []).append((callback, subscriber_id))

		if recipient is not None:
			self._recipients.setdefault(recipient, []).append(callback)

	def unsubscribe(
		self,
		callback: Callable[[Message], None],
		*,
		topic: Optional[str] = None,
		recipient: Optional[Any] = None,
	) -> None:
		"""Unsubscribe a previously-registered callback.

		If neither `topic` nor `recipient` is provided, the callback is removed
		from all subscriptions.
		"""
		if topic is None and recipient is None:
			# remove from all
			for lst in list(self._topics.values()):
				for ii in range(len(lst) - 1, -1, -1):
					if lst[ii][0] == callback:
						lst.pop(ii)
			for lst in list(self._recipients.values()):
				if callback in lst:
					lst.remove(callback)
			return

		if topic is not None:
			lst = self._topics.get(topic)
			if lst:
				for ii in range(len(lst) - 1, -1, -1):
					if lst[ii][0] == callback:
						lst.pop(ii)

		if recipient is not None:
			lst = self._recipients.get(recipient)
			if lst and callback in lst:
				lst.remove(callback)

	def publish(self, message: Message) -> None:
		"""Publish a message to matching subscribers.

		Delivery is synchronous and best-effort: exceptions in subscriber
		callbacks are propagated to the publisher. If you need isolation,
		wrap callbacks or run the bus in a worker thread.
		"""
		# deliver to topic subscribers
		if message.topic is not None:
			for cb, subscriber_id in list(self._topics.get(message.topic, [])):
				recipient = message.recipient
				if recipient is None:
					recipient = subscriber_id
				if self._delivery_allowed(message, recipient):
					cb(message)

		# deliver to recipient subscribers
		if message.recipient is not None:
			for cb in list(self._recipients.get(message.recipient, [])):
				if self._delivery_allowed(message, message.recipient):
					cb(message)

	def clear(self) -> None:
		"""Remove all subscriptions."""
		self._topics.clear()
		self._recipients.clear()
