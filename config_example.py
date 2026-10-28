from pathlib import Path

from communication.policies import AlwaysAllowPolicy


BASE_DIR = Path(__file__).resolve().parent

PATHS = {
    "maps_dir": BASE_DIR / "maps",
    "data_dir": BASE_DIR / "Data",
    "xgb_model": BASE_DIR / "models" / "XGBoost_best_1.pkl",
    "mlp_model": BASE_DIR / "models" / "MLP_best_1.pkl",
    "cnn_model": BASE_DIR / "models" / "CNN_best_1.pt",
}

SIMULATION_SETTINGS = {
    "number_of_agents": [40],
    "planner_algorithm": ["CNN"],
    "world_map": ["Map0.png"],
    "simulation_seeds": [1324, 132, 1372, 137234587],
    "simulation_timesteps": [500],
    "number_of_tasks": [1100],
    "visualization": False,
    "record": True,
    "message_policy": [AlwaysAllowPolicy()],
    "simrunner_max_fps": 120,
    "world_task_spawn_messages": False,
    "world_task_completion_messages": False,
    "world_status_updates": True,
    "world_random_close_spawns": True,
    "viewer_basic_sim_info": True,
    "viewer_debug_mode": True,
    "viewer_debug_mode_settings": [],
}
