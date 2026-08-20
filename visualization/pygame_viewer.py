import pygame

CELL_SIZE= 16
GRID_COLOR = (45, 45, 45)
BACKGROUND_COLOR = (18, 18, 18)
WALL_COLOR = (75, 75, 75)

AGENT_COLOR = (0, 100, 155)

TASK_COLOR = (155, 50, 0)

TEXT_INFO_COLOR = (150, 150, 0)
DEBUG_TEXT_COLOR = (255, 255, 255)

basic_sim_info = True
debug_mode = True
debug_mode_settings = [] #1 = show agent ids, 2 = show agent goal locations, 3 = show task ids, 4 = show agent task queues

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
        text = font.render(f"Time: {time} | Active Incomplete Tasks: {number_of_active_incomplete_tasks}", True, TEXT_INFO_COLOR)
        self.screen.blit(text, (self.width - text.get_width() - 10, 10))

    def add_debug_info(self):
        font = pygame.font.SysFont(None, 20)
        if 1 in debug_mode_settings: 
            #show agent ids

            #draw numbers on top of each agent and task to show their id
            agent_id_locations = [(agent.id, agent.location) for agent in self.world.agents]
            for agent_id, location in agent_id_locations:
                x, y = location
                text = font.render(str(agent_id), True, DEBUG_TEXT_COLOR)
                self.screen.blit(text, (x*CELL_SIZE + 2, y*CELL_SIZE + 2))

        if 2 in debug_mode_settings:
            #draw numbers  on top of each agents goal location to show their current goal
            agent_id_goal_locations = [(agent.id, agent.planner.current_goal) for agent in self.world.agents if agent.planner.current_goal is not None]
            for agent_id, goal_location in agent_id_goal_locations:
                x, y = goal_location
                text = font.render(str(agent_id), True, DEBUG_TEXT_COLOR)
                self.screen.blit(text, (x*CELL_SIZE + 2, y*CELL_SIZE + 2))

        if 3 in debug_mode_settings:
            #show the task ids on top of each task
            task_id_locations = [(task.id, task.location) for task in self.world.tasks if task.spawned and not task.completed]
            for task_id, location in task_id_locations:
                x, y = location
                text = font.render(str(task_id), True, DEBUG_TEXT_COLOR)
                self.screen.blit(text, (x*CELL_SIZE + 2, y*CELL_SIZE + 2))

        if 4 in debug_mode_settings:
            #show a list of all agents and their current task_queues in the top left corner of the screen
            agent_task_queues = []
            for agent in self.world.agents:
                if agent.planner.current_queue:
                    agent_task_queues.append((agent.id, agent.planner.current_queue))
                else: 
                    agent_task_queues.append((agent.id, []))

            for agent_id, task_queue in agent_task_queues:
                task_ids = [task.id for task, _ in task_queue]
                text = font.render(f"Agent {agent_id}: {task_ids}", True, DEBUG_TEXT_COLOR)
                self.screen.blit(text, (10, 30 + agent_id * 20))
            
            

            
    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_walls()
        self.draw_tasks()
        self.draw_agents()
        if basic_sim_info:
            self.add_text_info()
        if debug_mode:
            self.add_debug_info()
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
        
