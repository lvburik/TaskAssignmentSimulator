import heapq

from algorithms.other.neighbors import get_grid_neighbors

def simple_greedy_task_selector(agent, tasks):
    """Return Closest incomplete task."""
    
    closest_task = None
    min_distance = float('inf')

    for task in tasks.values():
        if task.state.completed:
            continue

        distance = abs(agent.state.position[0] - task.state.location[0]) + abs(agent.state.position[1] - task.state.location[1])
        if distance < min_distance:
            min_distance = distance
            closest_task = task

    return [closest_task.id] if closest_task is not None else []

def greedy_task_selector(agent, tasks):
    """Return Closest incomplete task."""

    goal_list = [task.state.location for task in tasks.values() if not task.state.completed]
    
    goal_distances = find_closest_goal_with_walls(agent.state.position, goal_list, agent.memory.world_observation.walls)

    #sort by distance and task_id to ensure deterministic tie-breaking
    sorted_goals = sorted(goal_distances.items(), key=lambda x: (x[1], x[0]))
    if not sorted_goals:
        return []
    
    closest_goal = sorted_goals[0][0]
    # Find the task corresponding to the closest goal
    for task in tasks.values():
        if task.state.location == closest_goal:
            return [task.id]


def find_closest_goal_with_walls(start, goal_list, map_matrix):
    goal_distances = {}

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in goal_list:
            goal_distances[current] = g_score[current]
        
        for neighbor in get_grid_neighbors(current, map_matrix):
            tentative = g_score[current] + 1  # Assuming uniform cost for moving to a neighbor

            if neighbor not in g_score or tentative < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative


                if neighbor not in [ii[1] for ii in open_set]:
                    heapq.heappush(open_set, (g_score[neighbor], neighbor))

    if not goal_distances:
        return None
    
    return goal_distances 


