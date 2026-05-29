from core.states import AgentState, AgentMemory, WorldObservation
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
            

            self.memory.world_observation = WorldObservation(
                agent_locations = {agent_id: agent.state.position for agent_id, agent in world_state.agents.items()},
                walls = world_state.walls,
                time = world_state.time,
                tasks = world_state.tasks,
            )


    def plan_tasks(self, assignment_algorithm):
        # assignment_algorithm expected signature: (agent_state, tasks_dict) -> list|int|None
        updated_memory_state = assignment_algorithm(self, self.memory.world_observation.tasks)
        
        
        with self.memory.lock:
            self.memory = updated_memory_state
    
    def act(self):
        if self.memory.action_queue:
            next_action = self.memory.action_queue[0]
            
            #remuve action from queue
            self.memory.action_queue = self.memory.action_queue[1:]
            return next_action
        
    
        
    
    