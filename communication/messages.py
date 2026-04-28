"""Message primitives for agent communication.

The bus lives in :mod:`communication.bus`; this module only defines the
payload object and its JSON helpers so it can be reused by a future ROS bridge.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import json
import time


@dataclass
class Message:
	sender: str
	topic: Optional[str] = None
	recipient: Optional[str] = None
	payload: Any = field(default_factory=dict)
	timestamp: float = field(default_factory=time.time)
	type: Optional[str] = None

	def to_dict(self) -> Dict[str, Any]:
		return {
			"sender": self.sender,
			"topic": self.topic,
			"recipient": self.recipient,
			"payload": self.payload,
			"timestamp": self.timestamp,
		}

	def to_json(self) -> str:
		return json.dumps(self.to_dict())

	@staticmethod
	def from_json(s: str) -> "Message":
		d = json.loads(s)
		return Message(**d)




