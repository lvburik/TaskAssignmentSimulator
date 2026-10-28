import os
import random

import agent
import task


from datalogger import DataLogger
from app_config import SIMULATION_SETTINGS

task_spawn_messages = SIMULATION_SETTINGS["world_task_spawn_messages"] # Set to True to enable warnings for task spawn issues
task_completion_messages = SIMULATION_SETTINGS["world_task_completion_messages"] # Set to True to enable warnings for task completion issues
status_updates = SIMULATION_SETTINGS["world_status_updates"] # Set to True to enable status updates during simulation
random_close_spawns = SIMULATION_SETTINGS["world_random_close_spawns"]

class World:
    def __init__(self, map_file_name):
        self.time = 0
        self.agents = []
        self.tasks = []
        self.map_file_name = map_file_name
        self.map = self._load_map(map_file_name)
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height > 0 else 0

    def add_agent(self, agent):
        #put agent in a random position

        #random chance of spawning next to another agent
        if random_close_spawns:
            if random.randint(0, 1) == 1:
                if self.agents:
                    neighboragent = random.choice(self.agents)
                    direction = random.choice([(0, 1),(1, 0),(0, -1),(-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)])
                    spawn_loc = (neighboragent.location[0] + direction[0], neighboragent.location[1] + direction[1])
                    if self._is_valid_location(spawn_loc):
                        agent.location = spawn_loc
                        self.agents.append(agent)
                        return
                    
        
        agent.location = self._random_empty_cell()

        self.agents.append(agent)
        


    def add_task(self, task):
        self.tasks.append(task)

    def _random_empty_cell(self):
        free_cells = self._free_cells()

        if not free_cells:
            raise ValueError("Map does not have free cells")

        return random.choice(free_cells)

        

    def step(self, logger: DataLogger | None = None):
        self._update_tasks(self.time)

        actions = []
        for sim_agent in self.agents:
            actions.append((sim_agent, sim_agent.act(self)))

        for (agent, action) in actions:
            self._apply_action(agent, action)

        if isinstance(logger, DataLogger):
            logger.log(self.get_state())

        status_update(self, self.time)
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
                if task_completion_messages: print(f"Task {sim_task.id} completed at time {self.time}.")
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
                self._spawn_task(task)
                task.spawned = True
                if task_spawn_messages: print(f"Task {task.id} spawned at time {current_time}.")
        
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
        entry["agents"] = {sim_agent.id: {"pos": sim_agent.location, "tasks": [task.id for task in sim_agent.planner.current_queue]} for sim_agent in self.agents}
        
        entry["tasks"] = {sim_task.id: (sim_task.location) for sim_task in self.tasks if (sim_task.spawned and not sim_task.completed)}
        
        return {self.time: entry}

    def get_world_map_info(self):
        return {
            "map_matrix": self.map,
            "map_width": self.width,
            "map_height": self.height,
        }
        
def status_update(world, step):
    if status_updates:
        if step % 10 == 0:
            print(f"Simulation progress: {step} steps completed. Number_of_incomplete_tasks: {len([task for task in world.tasks if not task.completed and task.spawned])}")
    