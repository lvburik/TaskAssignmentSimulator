from core.states import AgentState


class Agent:
    def __init__(self, id, position):
        self.id = id
        self.state = AgentState(position=position)
        self.task = None
        self.path = []
    
    def decide(self, world_state, assignment_algorithm, pathfinding_algorithm):
        if self.task is not None and world_state.tasks[self.task].state.completed:
            self.task = None
            self.path = []

        #select task if not already assigned
        if self.task is None:
            #select task using assignment algorithm
            self.task = assignment_algorithm(self.state, world_state.tasks)

        #plan path to task if assigned
        if not self.path and self.task is not None:
            task_location = world_state.tasks[self.task].state.location
            self.path = pathfinding_algorithm(self.state.position, task_location, world_state.walls) or []

        #follow path
        if self.path:
            if self.path[0] == self.state.position:
                self.path.pop(0)  #remove current position from path

            if self.path:
                return self.path[0]

            


