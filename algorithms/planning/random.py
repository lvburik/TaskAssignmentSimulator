import random


def random_movement_planner(position, goal, map_matrix):
    del goal, map_matrix
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    move = random.choice(moves)
    return [(position[0] + move[0], position[1] + move[1])]