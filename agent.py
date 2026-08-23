import planners.class_definition as planner_def


class Agent:
    def __init__(self, id: int, planner: planner_def.Planner):
        self.id = id
        self.location = None
        self.planner = planner
        # Expose the owning agent id on the planner for communication policies.
        self.planner.agent_id = id
        self.plan = None
        
        

    def act(self, world):
        observation = self._sense(world)

        self.planner.update_plan(observation)
        
        return self.planner.act()
    
    def _sense(self, world):
        # Return the observation for the agent
        observation = {}

        agent_locations = [(a.id, a.location) for a in world.agents if a.id != self.id]
        tasks = [task for task in world.tasks if not task.completed and task.spawn_time <= world.time]
        world_map = world.map  # Assuming the world has a map attribute

        observation["time"] = world.time
        observation["agent_id"] = self.id
        observation["agent_location"] = self.location
        observation["other_agent_locations"] = agent_locations
        observation["tasks"] = tasks
        observation["map"] = world_map



        return observation


    