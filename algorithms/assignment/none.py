def none_task_selector(agent, tasks):
    """A task selector that does not assign any tasks."""
    del agent_state, tasks
    return []