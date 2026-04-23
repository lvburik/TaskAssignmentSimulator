from simulation.initialization import create_world
from visualization.pygame_viewer import PygameViewer


def _advance_one_step(world):
    actions = {}
    for agent in world.state.agents.values():
        action = agent.decide()
        actions[agent.id] = action

    world.step(actions)


def run_simulation(
    width=10,
    height=10,
    number_of_agents=2,
    number_of_tasks=0,
    steps=10,
    view=False,
    fps=4,
    map_name=None,
):
    """Run the simulation loop in console mode or pygame view mode."""
    world = create_world(
        width=width,
        height=height,
        number_of_agents=number_of_agents,
        number_of_tasks=number_of_tasks,
        map_name=map_name,
    )

    if view:
        viewer = PygameViewer(world)

        def step_callback(step):
            _advance_one_step(world)

        viewer.run(step_callback=step_callback, max_steps=steps, fps=fps)
        return world

    for step in range(steps):
        _advance_one_step(world)

        print(f"Step {step}:")
        for agent_id, agent in world.state.agents.items():
            print(f"  Agent {agent_id} at position {agent.state.position}")

    return world