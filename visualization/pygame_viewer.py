import pygame

CELL_SIZE= 16
GRID_COLOR = (45, 45, 45)
BACKGROUND_COLOR = (18, 18, 18)
WALL_COLOR = (95, 95, 95)

AGENT_COLOR = (0, 200, 255)

TASK_COLOR = (255, 100, 0)

TEXT_COLOR = (0, 255, 0)

class PygameViewer:
    def __init__(self, world):
        self.world = world
        

        pygame.init()

        self.width = world.width * CELL_SIZE
        self.height = world.height * CELL_SIZE

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Agent Simulation")

        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for x in range(0, self.world.width):
            pygame.draw.line(
                self.screen, 
                GRID_COLOR, 
                (x*CELL_SIZE, 0), 
                (x*CELL_SIZE, self.height)
                )
            
        for y in range(0, self.world.height):
            pygame.draw.line(
                self.screen, 
                GRID_COLOR, 
                (0, y*CELL_SIZE), 
                (self.width, y*CELL_SIZE)
                )

    def draw_walls(self):
        for y, row in enumerate(self.world.map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pygame.draw.rect(
                        self.screen,
                        WALL_COLOR,
                        (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    )
            
    def draw_agents(self):
        for agent in self.world.agents:
            x, y = agent.location


            pygame.draw.circle(
                self.screen, 
                AGENT_COLOR, 
                (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2), 
                CELL_SIZE//2 - 2
                )
            
    def draw_tasks(self):
        for task in self.world.tasks:
            if not task.spawned or task.completed:
                continue

            x, y = task.location

            color = TASK_COLOR

            pygame.draw.rect(
                self.screen, 
                color, 
                (x*CELL_SIZE + 4, y*CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8)
                )
            
    def add_text_info(self):
        time = self.world.time
        number_of_active_incomplete_tasks = len([task for task in self.world.tasks if task.spawned and not task.completed])

        #add the text to the top right corner of the screen in green color
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Time: {time} | Active Incomplete Tasks: {number_of_active_incomplete_tasks}", True, TEXT_COLOR)
        self.screen.blit(text, (self.width - text.get_width() - 10, 10))

            
    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_walls()
        self.draw_grid()
        self.draw_tasks()
        self.draw_agents()
        self.add_text_info()
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
        
