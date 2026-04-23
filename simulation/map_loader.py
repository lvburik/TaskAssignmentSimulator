from pathlib import Path

import pygame


def load_map_matrix(map_name):
    map_path = Path(__file__).resolve().parent.parent / "maps" / map_name
    if not map_path.exists():
        raise FileNotFoundError(f"Map file not found: {map_path}")

    surface = pygame.image.load(str(map_path))
    width, height = surface.get_size()

    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            red, green, blue, _ = surface.get_at((x, y))
            brightness = (red + green + blue) / 3
            row.append(1 if brightness < 128 else 0)
        matrix.append(row)

    return matrix