import heapq

from pathfinding.find_neighbors import get_neighbors as get_neighbors

def BulkDistanceFinder(map, start, goals):
    
    goal_distances = {}

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in goals:
            goal_distances[current] = g_score[current]
        
        for neighbor in get_neighbors(map, current):
            tentative = g_score[current] + 1  # Assuming uniform cost for moving to a neighbor

            if neighbor not in g_score or tentative < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative


                if neighbor not in [ii[1] for ii in open_set]:
                    heapq.heappush(open_set, (g_score[neighbor], neighbor))

    if not goal_distances:
        return None
    
    return goal_distances 





     

