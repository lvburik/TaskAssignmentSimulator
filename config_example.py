"""Default filesystem paths and settings used when no local config.py exists.

Copy this file to ``config.py`` to customize a run without changing defaults
tracked in the repository.
"""

from pathlib import Path

from communication.policies import * # import all message policies


BASE_DIR = Path(__file__).resolve().parent

PATHS = {
    "maps_dir": BASE_DIR / "maps",  # PNG world maps.
    "data_dir": BASE_DIR / "Data",  # JSON Lines simulation output.
    "xgb_model": BASE_DIR / "models" / "XGB.pkl",  # XGB planner checkpoint.
    "mlp_model": BASE_DIR / "models" / "MLP.pkl",  # MLP planner checkpoint.
    "cnn_model": BASE_DIR / "models" / "CNN.pt",  # CNN planner checkpoint.
}

SIMULATION_SETTINGS = {
    # Each list-valued setting contributes to the batch Cartesian product.
    "number_of_agents": [40],
    "planner_algorithm": ["CNN"],
    "world_map": ["Map0.png"],
    "simulation_seeds": [1324, 132, 1372, 137234587],
    "simulation_timesteps": [500],
    "number_of_tasks": [1100],
    # Runtime and console output.
    "visualization": False,
    "record": True,
    "message_policy": [AlwaysAllowPolicy()],
    "simrunner_max_fps": 120,
    "world_task_spawn_messages": False,
    "world_task_completion_messages": False,
    "world_status_updates": True,
    # World initialization and viewer overlays.
    "world_random_close_spawns": True,
    "viewer_basic_sim_info": True,
    "viewer_debug_mode": True,
    "viewer_debug_mode_settings": [],
}
