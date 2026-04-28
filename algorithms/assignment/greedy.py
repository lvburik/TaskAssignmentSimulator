from algorithms.planning.Astar import a_star_planner, path_cost

def simple_greedy_task_selector(agent, tasks):
    """Return Closest incomplete task."""
    candidates = []

    min_distance = float('inf')
    best_task_id = None

    for task in tasks.values():
        if task.state.completed:
            continue

        distance = abs(agent.state.position[0] - task.state.location[0]) + abs(agent.state.position[1] - task.state.location[1]) #ignoring walls
        
        if distance < min_distance:
            min_distance = distance
            best_task_id = task.id

    return [best_task_id] if best_task_id is not None else []

def greedy_task_selector(agent, tasks):
    """Return Closest incomplete task."""
    candidates = []

    min_distance = float('inf')
    best_task_id = None

    
    for task in tasks.values():
        
        if task.state.completed:
            continue

        distance = find_distance_with_walls(agent.state.position, task.state.location, agent.memory.world_observation.walls)
        
        abs(agent.state.position[0] - task.state.location[0]) + abs(agent.state.position[1] - task.state.location[1])
        if distance < min_distance:
            min_distance = distance
            best_task_id = task.id

    return [best_task_id] if best_task_id is not None else []

def find_distance_with_walls(start, end, walls):
    
    path = a_star_planner(start, end, walls)
    if path is None:
        
        return float('inf')  # No path available
    return path_cost(path)

