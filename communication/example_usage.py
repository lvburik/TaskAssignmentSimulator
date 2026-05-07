"""Example of agent-to-agent messaging.

Run from the project root with:

    python -m communication.example_usage

Or directly as a file:

    python communication/example_usage.py
"""

from pathlib import Path
import sys

# Support direct file execution by ensuring the project root is importable.
if __package__ in (None, ""):
	project_root = Path(__file__).resolve().parents[1]
	if str(project_root) not in sys.path:
		sys.path.insert(0, str(project_root))

from communication import Message, MessageBus


def main() -> None:
	bus = MessageBus()
	received = []

	def on_task(message: Message) -> None:
		received.append(("topic", message.sender, message.topic, message.payload))
		print(f"topic:{message.topic} from {message.sender} -> {message.payload}")

	def on_agent_1(message: Message) -> None:
		received.append(("recipient", message.sender, message.recipient, message.payload))
		print(f"recipient:{message.recipient} from {message.sender} -> {message.payload}")

	bus.subscribe(on_task, topic="task")
	bus.subscribe(on_agent_1, recipient="agent_1")

	bus.publish(
		Message(
			sender="agent_0",
			topic="task",
			payload={"task_id": 42, "action": "pickup"},
		)
	)
	bus.publish(
		Message(
			sender="agent_0",
			recipient="agent_1",
			payload={"text": "hello"},
		)
	)

	serialized = Message(sender="bridge", topic="task", payload={"x": 1}).to_json()
	print(serialized)

	assert len(received) == 2


if __name__ == "__main__":
	main()
