"""
Declarative configuration for the simulator.

This file contains simple variable assignments only. Use these values
directly from other modules (for example, `import config`).

The comments list typical/available options for each setting so it's
easy to change behavior without touching code.
"""

# Grid size
# Possible: any positive integer
WIDTH = 10
HEIGHT = 10

# Simulation entities
# NUMBER_OF_AGENTS: integer >= 0
# NUMBER_OF_TASKS: integer >= 0
NUMBER_OF_AGENTS = 4
NUMBER_OF_TASKS = 50

# Simulation runtime
# STEPS: integer >= 0 (0 may mean run until tasks complete depending on engine)
STEPS = 200

# Visualization
# VIEW: True to enable pygame viewer, False to disable
# FPS: integer frames-per-second when viewer is enabled
VIEW = True
FPS = 4

# Map
# MAP_NAME: None to generate an empty/random map, or a filename
# Example: 'office.png' (must exist in the maps folder)
MAP_NAME = "Map4.png"

# Warnings and logging
# MOVEMENT_WARNINGS: True/False
MOVEMENT_WARNINGS = True

# Algorithms defaults
# ASSIGNMENT_DEFAULT: one of ('greedy', 'auction', 'random', 'none', 'tom')
# PATHFINDING_DEFAULT: one of ('astar', 'random')
ASSIGNMENT_DEFAULT = "greedy"
PATHFINDING_DEFAULT = "astar"

# Random seed (None for non-deterministic behavior, or an integer for reproducibility)
SEED = None

# Engine selection
# ENGINE: 'single' for single-threaded engine, 'dual' for dual-threaded engine
ENGINE = "single"

# World logging
# LOG_WORLD: True to record world snapshots via algorithms.assignment.metrics.log_world.WorldLogger
# WORLD_LOG_PATH: output file path for the saved log
LOG_WORLD = True
WORLD_LOG_PATH = "Data/world_log.json"

