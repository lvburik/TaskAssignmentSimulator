from core.states import AgentState
import random


class Agent:
    def __init__(self, id, position):
        self.id = id
        self.state = AgentState(position=position)
    
    def decide(self):
        #simple random movement logic for demonstration
        moves = [(0,1), (0,-1), (1,0), (-1,0)]
        move = random.choice(moves)
        return (self.state.position[0] + move[0], self.state.position[1] + move[1])