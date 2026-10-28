"""Task state and scheduled spawn time for a single world objective."""

class Task:
    """A task that becomes available at ``spawn_time`` and can be completed."""

    def __init__(self, id: int, spawn_time: int = 0):
        """Initialize an unspawned, incomplete task with no assigned location."""
        self.id = id
        self.location = None
        self.spawn_time = spawn_time
        self.spawned = False
        self.completed = False