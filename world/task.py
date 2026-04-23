from core.states import TaskState

class Task:
    def __init__(self, id, location):
        self.id = id
        self.state = TaskState(location=location, completed=False)

    def complete(self):
        self.state.completed = True
