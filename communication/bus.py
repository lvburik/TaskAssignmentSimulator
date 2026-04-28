"""A small synchronous message bus for agent communication."""

from typing import Callable, Dict, List, Optional

from communication.messages import Message


class MessageBus:
	"""A very small in-process message bus.

	Subscribers register callbacks for topics or for a specific recipient id.
	When a `Message` is published, topic subscribers and recipient-specific
	subscribers are invoked synchronously in the publisher's thread.
	"""

	def __init__(self) -> None:
		# topic -> list of callbacks
		self._topics: Dict[str, List[Callable[[Message], None]]] = {}
		# recipient id -> list of callbacks
		self._recipients: Dict[str, List[Callable[[Message], None]]] = {}

	def subscribe(self, callback: Callable[[Message], None], *, topic: Optional[str] = None, recipient: Optional[str] = None) -> None:
		"""Subscribe a callback to a `topic` and/or a `recipient`.

		- `topic`: delivers messages where `Message.topic == topic`.
		- `recipient`: delivers messages where `Message.recipient == recipient`.

		The same callback may be subscribed to multiple topics/recipients.
		"""
		if topic is None and recipient is None:
			raise ValueError("either topic or recipient must be provided")

		if topic is not None:
			self._topics.setdefault(topic, []).append(callback)

		if recipient is not None:
			self._recipients.setdefault(recipient, []).append(callback)

	def unsubscribe(self, callback: Callable[[Message], None], *, topic: Optional[str] = None, recipient: Optional[str] = None) -> None:
		"""Unsubscribe a previously-registered callback.

		If neither `topic` nor `recipient` is provided, the callback is removed
		from all subscriptions.
		"""
		if topic is None and recipient is None:
			# remove from all
			for lst in list(self._topics.values()):
				if callback in lst:
					lst.remove(callback)
			for lst in list(self._recipients.values()):
				if callback in lst:
					lst.remove(callback)
			return

		if topic is not None:
			lst = self._topics.get(topic)
			if lst and callback in lst:
				lst.remove(callback)

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
			for cb in list(self._topics.get(message.topic, [])):
				cb(message)

		# deliver to recipient subscribers
		if message.recipient is not None:
			for cb in list(self._recipients.get(message.recipient, [])):
				cb(message)

	def clear(self) -> None:
		"""Remove all subscriptions."""
		self._topics.clear()
		self._recipients.clear()
