class Task:
    def __init__(self, id: int, spawn_time: int = 0):
        self.id = id
        self.location = None
        self.spawn_time = spawn_time
        self.spawned = False
        self.completed = False