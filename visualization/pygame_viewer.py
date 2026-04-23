import pygame

CELL_SIZE= 20
GRID_COLOR = (45, 45, 45)
BACKGROUND_COLOR = (18, 18, 18)
WALL_COLOR = (95, 95, 95)

AGENT_COLOR = (0, 200, 255)

TASK_COLOR = (255, 100, 0)

class PygameViewer:
    def __init__(self, world):
        self.world = world

        pygame.init()

        self.width = world.state.width * CELL_SIZE
        self.height = world.state.height * CELL_SIZE

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Agent Simulation")

        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for x in range(0, self.world.state.width):
            pygame.draw.line(
                self.screen, 
                GRID_COLOR, 
                (x*CELL_SIZE, 0), 
                (x*CELL_SIZE, self.height)
                )
            
        for y in range(0, self.world.state.height):
            pygame.draw.line(
                self.screen, 
                GRID_COLOR, 
                (0, y*CELL_SIZE), 
                (self.width, y*CELL_SIZE)
                )

    def draw_walls(self):
        for y, row in enumerate(self.world.state.walls):
            for x, cell in enumerate(row):
                if cell == 1:
                    pygame.draw.rect(
                        self.screen,
                        WALL_COLOR,
                        (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    )
            
    def draw_agents(self):
        for agent in self.world.state.agents.values():
            x, y = agent.state.position


            pygame.draw.circle(
                self.screen, 
                AGENT_COLOR, 
                (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2), 
                CELL_SIZE//2 - 2
                )
            
    def draw_tasks(self):
        for task in self.world.state.tasks.values():
            x, y = task.state.location

            color = TASK_COLOR if not task.state.completed else (100, 50, 0)

            pygame.draw.rect(
                self.screen, 
                color, 
                (x*CELL_SIZE + 4, y*CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8)
                )
            
    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_walls()
        self.draw_grid()
        self.draw_agents()
        self.draw_tasks()
        pygame.display.flip()
    
    def run(self, step_callback, max_steps=100, fps=10):
        running = True
        step = 0

        # Show initial state before first step.
        self.render()

        while running and step < max_steps:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            step_callback(step)
            self.render()
            self.clock.tick(fps)
            step += 1

        pygame.quit()
        
