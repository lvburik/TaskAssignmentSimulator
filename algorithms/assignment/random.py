import random

from algorithms.other.task_queue_to_action_queue import task_queue_to_action_queue

def random_task_assignment(agent_state, tasks):
    
    if not tasks:
        
        return task_queue_to_action_queue(agent_state)
    
    
    
    if agent_state.memory.task_queue!=[]:
        return task_queue_to_action_queue(agent_state)
    
    incomplete_tasks = [task.id for task in tasks.values() if not task.state.completed]
    
    
    agent_state.memory.task_queue = [random.choice(incomplete_tasks)] if incomplete_tasks else []
    return task_queue_to_action_queue(agent_state)