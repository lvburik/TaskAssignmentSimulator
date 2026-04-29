import heapq

from algorithms.other.neighbors import get_grid_neighbors
    

def a_star_planner(start, goal, map_matrix):
    """A* pathfinding algorithm to find the shortest path from start to goal on a grid."""
    
    def heuristic(a, b):
        """Calculate the Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_grid_neighbors(current, map_matrix):
            tentative = g_score[current] + 1  # Assuming uniform cost for moving to a neighbor

            if neighbor not in g_score or tentative < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative

                f_score[neighbor] = tentative + heuristic(neighbor, goal)

                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None # No path found
        
def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path
    
def path_cost(path):
    return len(path) - 1  # Assuming uniform cost for each step