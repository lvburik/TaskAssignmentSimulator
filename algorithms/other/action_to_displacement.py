def action_to_displacement(action):
    """Convert queued action values into (dx, dy) displacements."""
    if action is None:
        return None

    if isinstance(action, tuple) and len(action) == 2:
        return action

    action_map = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
    }
    return action_map.get(action)
