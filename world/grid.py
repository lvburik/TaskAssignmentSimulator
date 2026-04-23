from core.states import WorldState


class GridWorld:
    def __init__(self, width, height, walls=None, movement_warnings=True):
        if walls is None:
            walls = [[0 for _ in range(width)] for _ in range(height)]
        self.movement_warnings = movement_warnings

        self.state = WorldState(
            agents={},
            tasks={},
            width=width,
            height=height,
            walls=walls,
            time=0,
        )

    def add_agent(self, agent):
        self.state.agents[agent.id] = agent

    def add_task(self, task):
        self.state.tasks[task.id] = task

    def move_agent(self, agent_id, new_position):
        if not self._in_bounds(new_position):
            self._warn(f"Agent {agent_id} attempted to move out of bounds to {new_position}, Ignoring.")
            return

        if self._is_wall(new_position):
            self._warn(f"Agent {agent_id} attempted to move into a wall at {new_position}, Ignoring.")
            return

        if self._agent_at_position(new_position):
            self._warn(f"Agent {agent_id} attempted to move to occupied position {new_position}, Ignoring.")
            return

        self.state.agents[agent_id].state.position = new_position

    def _warn(self, message):
        if self.movement_warnings:
            print(message)

    def _is_wall(self, pos):
        x, y = pos
        return self.state.walls[y][x] == 1

    def _agent_at_position(self, position):
        for agent in self.state.agents.values():
            if agent.state.position == position:
                return agent
        return None

    def _in_bounds(self, pos):
        x, y = pos
        return 0 <= x < self.state.width and 0 <= y < self.state.height

    def check_task_completion(self):
        for task in self.state.tasks.values():
            if not task.state.completed:
                if self._agent_at_position(task.state.location):
                    task.complete()
                    print(f"Task {task.id} completed at time {self.state.time}!")

    def step(self, actions):
        for agent_id, position in actions.items():
            self.move_agent(agent_id, position)

        for task in self.state.tasks.values():
            if not task.state.completed:
                self.check_task_completion()

        self.state.time += 1