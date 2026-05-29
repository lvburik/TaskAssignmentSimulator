from algorithms.assignment.random import random_task_assignment

def bayesian_delagation_assignment(agent_state, tasks):
    uncompleted_tasks = [task for task in tasks.values() if not task.state.completed]

    
    if not agent_state.memory.planning_memory:
        agent_state.memory = _initialize_planning_memory(agent_state, uncompleted_tasks)

    

    if agent_state.memory.world_observation.time > agent_state.memory.planning_memory['world_time']:
        if uncompleted_tasks != agent_state.memory.planning_memory['last_task_set'] or agent_state.memory.world_observation.time == 0:
            agent_state.memory = _initialize_beliefs(agent_state, uncompleted_tasks)
        else:
            _update_beliefs(agent_state, uncompleted_tasks)

        _normalise_beliefs(agent_state)
        
    


    #for now use random task assignment
    return agent_state.memory
    

def _initialize_planning_memory(agent_state, uncompleted_tasks):
    # Initialize any necessary planning memory for the agent here
    print("Initializing planning memory for agent", agent_state.id)
    
    agent_state.memory.planning_memory = {
        'world_time': agent_state.memory.world_observation.time,
        'last_task_set': uncompleted_tasks,
    }

    return agent_state.memory

def _initialize_beliefs(agent_state, uncompleted_tasks):
    print("Initializing beliefs for agent", agent_state.id)

def _update_beliefs(agent_state, uncompleted_tasks):
    print("Updating beliefs for agent", agent_state.id)

def _normalise_beliefs(agent_state):
    print("Normalizing beliefs for agent", agent_state.id)

    





    
    
    
    
    