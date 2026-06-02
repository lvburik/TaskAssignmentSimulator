from algorithms.planning.Astar import a_star_planner as pathfinding_algorithm

def task_queue_to_action_queue(agent):
    
    if not agent.memory.task_queue:
        return agent.memory

    current_task_id = agent.memory.task_queue[0]

    #check if tasks is completed
    if agent.memory.world_observation.tasks[current_task_id].state.completed:
        #remove task from queue if completed
        agent.memory.task_queue = agent.memory.task_queue[1:]
        return agent.memory



    task_location = agent.memory.world_observation.tasks[current_task_id].state.location

    path = pathfinding_algorithm(agent.state.position, task_location, agent.memory.world_observation.walls)

    if path is None:
        # No path found, clear the task queue to avoid getting stuck
        agent.memory.task_queue = []
        return agent.memory

    # Convert path to action queue (assuming actions are "up", "down", "left", "right")
    action_queue = []
    for i in range(1, len(path)):
        dx = path[i][0] - path[i-1][0]
        dy = path[i][1] - path[i-1][1]
        if dx == 1:
            action_queue.append("right")
        elif dx == -1:
            action_queue.append("left")
        elif dy == 1:
            action_queue.append("down")
        elif dy == -1:
            action_queue.append("up")

    agent.memory.action_queue = action_queue
    return agent.memory