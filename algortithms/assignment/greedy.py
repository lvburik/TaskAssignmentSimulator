def greedy_task_selector(agent_state, tasks):
    """Select the closest uncompleted task for the agent."""
    best_task = None
    best_distance = float('inf')

    for task in tasks.values():
        if not task.state.completed:

            #compute manhattan distance
            distance = abs(agent_state.position[0] - task.state.location[0]) + abs(agent_state.position[1] - task.state.location[1])

            if distance < best_distance:
                best_distance = distance
                best_task = task.id

    return best_task