import os
import random

import agent
import task

from datalogger import DataLogger

class World:
    def __init__(self, map_file_name, agents: list[agent.Agent], tasks: list[task.Task]):
        self.agents = agents
        self.tasks = tasks
        self.time = 0

        self.map_file_name = map_file_name
        self.map = self._load_map(map_file_name)
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height > 0 else 0

        free_cells = self._free_cells()
        if len(free_cells) < len(self.agents) + len(self.tasks):
            raise ValueError("Map does not have enough free cells for agents and tasks.")

        random.shuffle(free_cells)
        for idx, sim_agent in enumerate(self.agents):
            sim_agent.location = free_cells[idx]

        for idx, sim_task in enumerate(self.tasks):
            sim_task.location = free_cells[len(self.agents) + idx]

    def step(self, logger: DataLogger | None = None):
        self._update_tasks(self.time)

        for sim_agent in self.agents:
            action = sim_agent.act(self)
            self._apply_action(sim_agent, action)

        if isinstance(logger, DataLogger):
            logger.log(self.get_state())

        self.time += 1

    def _load_map(self, map_file_name):
        if not os.path.isabs(map_file_name):
            workspace_root = os.path.dirname(os.path.dirname(__file__))
            map_file_name = os.path.join(workspace_root, "maps", map_file_name)

        if not os.path.exists(map_file_name):
            raise FileNotFoundError(f"Map file not found: {map_file_name}")

        try:
            from PIL import Image
        except ImportError as exc:
            raise ImportError(
                "Pillow is required to read PNG maps. Install with: pip install pillow"
            ) from exc

        image = Image.open(map_file_name).convert("L")
        width, height = image.size
        pixels = image.load()

        # 0 = free space, 1 = blocked cell
        map_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(1 if pixels[x, y] < 128 else 0)
            map_matrix.append(row)

        return map_matrix

    def _apply_action(self, sim_agent: agent.Agent, action: str | None):
        if action in ["up", "down", "left", "right"]:
            self._move_agent(sim_agent, action)
        elif action == "perform_task":
            self._complete_task(sim_agent)
        elif action == None:
            # No action taken
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
            pass

    def _complete_task(self, sim_agent: agent.Agent):
        for sim_task in self.tasks:
            if sim_task.location == sim_agent.location and not sim_task.completed:
                sim_task.completed = True
                print(f"Task {sim_task.id} completed at time {self.time}.")
                return
        print(f"No task to complete for agent {sim_agent.id} at location {sim_agent.location}.")

    def _move_agent(self, sim_agent: agent.Agent, action: str):
        if action == "up":
            next_location = (sim_agent.location[0], sim_agent.location[1] - 1)
        elif action == "down":
            next_location = (sim_agent.location[0], sim_agent.location[1] + 1)
        elif action == "left":
            next_location = (sim_agent.location[0] - 1, sim_agent.location[1])
        elif action == "right":
            next_location = (sim_agent.location[0] + 1, sim_agent.location[1])

        if self._is_valid_location(next_location):
            sim_agent.location = next_location

    def _is_valid_location(self, location: tuple[int, int]) -> bool:
        x, y = location

        if x < 0 or x >= self.width:
            return False
        if y < 0 or y >= self.height:
            return False

        if self.map[y][x] == 1:
            return False

        for sim_agent in self.agents:
            if sim_agent.location == location:
                return False

        return True
    
    def _update_tasks(self, current_time: int):
        for task in self.tasks:
            if not task.spawned and task.spawn_time <= current_time:
                task.spawned = True

                self._spawn_task(task)
                print(f"Task {task.id} spawned at time {current_time}.")
        
    def _spawn_task(self, sim_task: task.Task):
        free_cells = self._free_cells()
        if not free_cells:
            raise ValueError("No free cells available to spawn the task.")

        sim_task.location = random.choice(free_cells)

    def _free_cells(self):
        free_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] == 0:
                    occupied = False
                    for sim_agent in self.agents:
                        if sim_agent.location == (x, y):
                            occupied = True
                            break
                    for sim_task in self.tasks:
                        if sim_task.location == (x, y) and not sim_task.completed:
                            occupied = True
                            break
                    if not occupied:
                        free_cells.append((x, y))
        return free_cells

    def get_state(self):
       
        entry = {}
        entry["agents"] = {sim_agent.id: sim_agent.location for sim_agent in self.agents}
        
        entry["tasks"] = {sim_task.id: (sim_task.location, {"C": sim_task.completed, "S": sim_task.spawned}) for sim_task in self.tasks}
        
        return {self.time: entry}

    def get_world_map_info(self):
        return {
            "map_matrix": self.map,
            "map_width": self.width,
            "map_height": self.height,
        }
        
    