from core.states import AgentState, AgentMemory
from algorithms.planning.random import random_movement_planner

class Agent:
    def __init__(self, id, position):
        self.id = id
        self.state = AgentState(position=position)
        self.memory = AgentMemory()

    def _normalize_task_queue(self, assignment_result):
        if assignment_result is None:
            return []

        if isinstance(assignment_result, list):
            return assignment_result

        if isinstance(assignment_result, tuple):
            return list(assignment_result)

        return [assignment_result]

    def _drop_completed_or_missing_tasks(self, world_state):
        filtered = []
        for task_id in self.memory.task_queue:
            task = world_state.tasks.get(task_id)
            if task is not None and not task.state.completed:
                filtered.append(task_id)
        self.memory.task_queue = filtered
    
    def decide(self, world_state, assignment_algorithm, pathfinding_algorithm):
        def to_displacement(next_position):
            return (
                next_position[0] - self.state.position[0],
                next_position[1] - self.state.position[1],
            )

        self._drop_completed_or_missing_tasks(world_state)

        # Select a queue of tasks when queue is empty.
        if not self.memory.task_queue:
            assignment_result = assignment_algorithm(self.state, world_state.tasks)
            self.memory.task_queue = self._normalize_task_queue(assignment_result)
            self._drop_completed_or_missing_tasks(world_state)
            self.memory.path_queue = []

        if not self.memory.task_queue:
            return

        current_task_id = self.memory.task_queue[0]
        task_location = world_state.tasks[current_task_id].state.location

        # Plan path if no planned movement exists.
        if not self.memory.path_queue:
            planned_path = pathfinding_algorithm(self.state.position, task_location, world_state.walls) or []
            self.memory.path_queue = planned_path

        # If planner returned no path, skip this task and retry next turn.
        if not self.memory.path_queue:
            self.memory.task_queue.pop(0)
            return

        # Follow path.
        if self.memory.path_queue[0] == self.state.position:
            self.memory.path_queue.pop(0)
        elif len(self.memory.path_queue) > 1 and self.memory.path_queue[1] == self.state.position:
            # If we advanced outside expected sequence, drop stale first waypoint.
            self.memory.path_queue.pop(0)
            self.memory.path_queue.pop(0)
        else:
            # Agent likely got blocked; force replanning next step and jitter now.
            self.memory.path_queue = []
            fallback = random_movement_planner(self.state.position, self.state.position, world_state.walls) or []
            if fallback:
                return to_displacement(fallback[0])
            return 

        if self.memory.path_queue:
            return to_displacement(self.memory.path_queue[0])

        return




