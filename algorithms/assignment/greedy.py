def greedy_task_selector(agent_state, tasks):
    """Return Closest incomplete task."""
    candidates = []

    min_distance = float('inf')
    best_task_id = None

    for task in tasks.values():
        if task.state.completed:
            continue

        distance = abs(agent_state.position[0] - task.state.location[0]) + abs(agent_state.position[1] - task.state.location[1])
        if distance < min_distance:
            min_distance = distance
            best_task_id = task.id

    return [best_task_id] if best_task_id is not None else []