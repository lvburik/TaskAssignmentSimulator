from core.states import AgentState, AgentMemory
from algorithms.planning.random import random_movement_planner


class Agent:
    def __init__(self, id, position):
        self.id = id
        self.state = AgentState(position=position)
        self.memory = AgentMemory()

    def _drop_completed_or_missing_tasks(self, world_state):
        filtered = []
        with self.memory.lock:
            for task_id in self.memory.task_queue:
                task = world_state.tasks.get(task_id)
                if task is not None and not task.state.completed:
                    filtered.append(task_id)
            self.memory.task_queue = filtered

    def sense(self, world_state):
        # For now, agent has perfect information about the world.
        with self.memory.lock:
            self.memory.world_observation = world_state

    def plan_tasks(self, assignment_algorithm):
        # assignment_algorithm expected signature: (agent_state, tasks_dict) -> list|int|None
        updated_memory_state = assignment_algorithm(self, self.memory.world_observation.tasks)
        
        
        with self.memory.lock:
            self.memory = updated_memory_state
    
    def act(self, pathfinding_algorithm):
        def to_displacement(next_position):
            return (
                next_position[0] - self.state.position[0],
                next_position[1] - self.state.position[1],
            )

        # Clean up task queue under lock
        self._drop_completed_or_missing_tasks(self.memory.world_observation)

        # Snapshot current task and observation without holding the lock during planning
        with self.memory.lock:
            if not self.memory.task_queue:
                return
            current_task_id = self.memory.task_queue[0]
            task_location = self.memory.world_observation.tasks[current_task_id].state.location

        # Run path planner (may be relatively expensive) without holding the memory lock
        planned_path = pathfinding_algorithm(self.state.position, task_location, self.memory.world_observation.walls) or []

        with self.memory.lock:
            self.memory.path = planned_path

            # If planner returned no path, skip this task and retry next turn.
            if not self.memory.path:
                if self.memory.task_queue:
                    self.memory.task_queue.pop(0)
                return

            # Follow path.
            if self.memory.path[0] == self.state.position:
                self.memory.path.pop(0)
            elif len(self.memory.path) > 1 and self.memory.path[1] == self.state.position:
                # If we advanced outside expected sequence, drop stale first waypoint.
                self.memory.path.pop(0)
                if self.memory.path:
                    self.memory.path.pop(0)
            else:
                # Agent likely got blocked; force replanning next step and jitter now.
                self.memory.path = []
                fallback = random_movement_planner(self.state.position, self.state.position, self.memory.world_observation.walls) or []
                if fallback:
                    return to_displacement(fallback[0])
                return 

            if self.memory.path:
                return to_displacement(self.memory.path[0])

        return
    
    


