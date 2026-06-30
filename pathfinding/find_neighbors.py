def get_neighbors(world_map, location: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = location
        neighbors = [
            (x, y - 1),  # Up
            (x, y + 1),  # Down
            (x - 1, y),  # Left
            (x + 1, y),  # Right
        ]
        return [n for n in neighbors if is_valid_location(world_map, n)]

def is_valid_location(world_map, location: tuple[int, int]) -> bool:
    x, y = location
    if x < 0 or x >= len(world_map[0]) or y < 0 or y >= len(world_map):
        return False
    return world_map[y][x] == 0  # Assuming 0 is walkable and 1 is a wall