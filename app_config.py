"""Load user configuration, falling back to the checked-in example."""

try:
    from config import PATHS, SIMULATION_SETTINGS
except ImportError:
    from config_example import PATHS, SIMULATION_SETTINGS
