from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict, List, Tuple


Position = Tuple[int, int]


@dataclass(frozen=True)
class TaskSnapshot:
	id: int
	location: Position
	completed: bool


@dataclass(frozen=True)
class WorldSnapshot:
	time: int
	agent_locations: Dict[int, Position]
	agent_task_queues: Dict[int, List[int]]
	tasks: Dict[int, TaskSnapshot]


@dataclass
class WorldLogger:
	walls: List[List[int]] | None = None
	snapshots: List[WorldSnapshot] = field(default_factory=list)

	def record(self, world):
		if self.walls is None:
			self.walls = [row[:] for row in world.state.walls]

		snapshot = WorldSnapshot(
			time=world.state.time,
			agent_locations={agent_id: tuple(agent.state.position) for agent_id, agent in world.state.agents.items()},
			agent_task_queues={agent_id: list(agent.memory.task_queue) for agent_id, agent in world.state.agents.items()},
			tasks={
				task_id: TaskSnapshot(
					id=task_id,
					location=tuple(task.state.location),
					completed=task.state.completed,
				)
				for task_id, task in world.state.tasks.items()
			},
		)
		self.snapshots.append(snapshot)
		return snapshot

	def to_dict(self):
		return {
			"walls": self.walls,
			"snapshots": [
				{
					"time": snapshot.time,
					"agent_locations": {
						str(agent_id): list(position)
						for agent_id, position in snapshot.agent_locations.items()
					},
					"agent_task_queues": {
						str(agent_id): list(task_queue)
						for agent_id, task_queue in snapshot.agent_task_queues.items()
					},
					"tasks": {
						str(task_id): {
							"id": task_snapshot.id,
							"location": list(task_snapshot.location),
							"completed": task_snapshot.completed,
						}
						for task_id, task_snapshot in snapshot.tasks.items()
					},
				}
				for snapshot in self.snapshots
			],
		}

	def save(self, file_path):
		path = Path(file_path)
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def capture_world_state(world):
	logger = WorldLogger()
	logger.record(world)
	return logger


def save_world_log(world_logger, file_path):
	world_logger.save(file_path)
