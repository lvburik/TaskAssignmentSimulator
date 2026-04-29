def get_grid_neighbors(position, map_matrix):
    neighbors = []
    x, y = position
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # down, right, up, left
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < len(map_matrix[0]) and 0 <= new_y < len(map_matrix):
            if map_matrix[new_y][new_x] == 0:  # Check if it's not a wall
                neighbors.append((new_x, new_y))
                
    return neighbors