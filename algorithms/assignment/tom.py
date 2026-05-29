import heapq
from algorithms.other.task_queue_to_action_queue import task_queue_to_action_queue
from algorithms.other.neighbors import get_grid_neighbors


def bayesian_delagation_assignment(agent_state, tasks):
    """Select the most likely task using a light Bayesian delegation model.

    The original paper-level algorithm keeps beliefs over which task each agent
    will pursue, updates those beliefs from observations, and then picks the
    task with the highest posterior. The simulator currently has no explicit
    communication model, so this implementation infers task ownership from
    visible agent queues and relative distance.
    """

    if agent_state.memory.world_observation is None:
        return agent_state.memory

    uncompleted_tasks = [task for task in tasks.values() if not task.state.completed]

    if not agent_state.memory.planning_memory:
        _initialize_planning_memory(agent_state, uncompleted_tasks)

    planning_memory = agent_state.memory.planning_memory
    current_time = agent_state.memory.world_observation.time
    task_ids = tuple(task.id for task in uncompleted_tasks)

    if planning_memory["last_task_set"] != task_ids or (
        current_time == 0 and planning_memory["world_time"] != current_time
    ):
        _initialize_beliefs(agent_state, uncompleted_tasks)
    elif current_time > planning_memory["world_time"]:
        _update_beliefs(agent_state, uncompleted_tasks)
        _normalise_beliefs(agent_state)

    planning_memory["world_time"] = current_time
    planning_memory["last_task_set"] = task_ids

    best_task_id = _select_best_task(agent_state, uncompleted_tasks)
    if best_task_id is None:
        agent_state.memory.task_queue = []
        agent_state.memory.action_queue = []
        return agent_state.memory

    current_task_id = agent_state.memory.task_queue[0] if agent_state.memory.task_queue else None
    if current_task_id != best_task_id:
        agent_state.memory.task_queue = [best_task_id]

    return task_queue_to_action_queue(agent_state)


def _initialize_planning_memory(agent_state, uncompleted_tasks):
    agent_state.memory.planning_memory = {
        "world_time": agent_state.memory.world_observation.time,
        "last_task_set": tuple(task.id for task in uncompleted_tasks),
        "task_beliefs": {},
    }
    _initialize_beliefs(agent_state, uncompleted_tasks)
    return agent_state.memory


def _initialize_beliefs(agent_state, uncompleted_tasks):
    task_beliefs = agent_state.memory.planning_memory.setdefault("task_beliefs", {})

    if not uncompleted_tasks:
        task_beliefs.clear()
        return

    prior = 1.0 / len(uncompleted_tasks)
    task_beliefs.clear()
    for task in uncompleted_tasks:
        task_beliefs[task.id] = prior


def _update_beliefs(agent_state, uncompleted_tasks):
    task_beliefs = agent_state.memory.planning_memory.setdefault("task_beliefs", {})
    world_observation = agent_state.memory.world_observation

    if not uncompleted_tasks:
        task_beliefs.clear()
        return

    likelihoods = _task_likelihoods(agent_state, uncompleted_tasks, world_observation)
    for task in uncompleted_tasks:
        prior = task_beliefs.get(task.id, 1.0 / max(1, len(uncompleted_tasks)))
        likelihood = likelihoods.get(task.id, 0.05)
        task_beliefs[task.id] = prior * likelihood


def _normalise_beliefs(agent_state):
    task_beliefs = agent_state.memory.planning_memory.setdefault("task_beliefs", {})
    total = sum(task_beliefs.values())

    if total <= 0:
        return

    for task_id in list(task_beliefs.keys()):
        task_beliefs[task_id] /= total


def _select_best_task(agent_state, uncompleted_tasks):
    if not uncompleted_tasks:
        return None

    task_beliefs = agent_state.memory.planning_memory.get("task_beliefs", {})

    scored_tasks = []
    distances = _distances(agent_state.state.position, uncompleted_tasks, agent_state.memory.world_observation.walls)
    for task in uncompleted_tasks:
        belief = task_beliefs.get(task.id, 0.0)
        distance = distances[task.id] if distances and task.id in distances else float('inf')
        score = (belief, -distance, -task.id)
        scored_tasks.append((score, task.id))

    scored_tasks.sort(reverse=True)
    return scored_tasks[0][1] if scored_tasks else None


def _task_likelihoods(agent_state, tasks, world_observation):
    # Return a dict of {task.id: likelihood}
    likelihoods = {}
    if not tasks:
        return likelihoods

    my_pos = agent_state.state.position
    
    # compute path distances from self to all goals
    my_distances = _distances(my_pos, tasks, world_observation.walls) or {}

    # get other agent locations from observation (backwards-compatible keys)
    loc_map = getattr(world_observation, "agent_locations", None) or getattr(world_observation, "agents_locations", None) or {}

    # precompute other agents distances to goals
    others_distances = {}
    for aid, loc in loc_map.items():
        if aid == agent_state.id:
            continue
        d = _distances(loc, tasks, world_observation.walls) or {}
        others_distances[aid] = d

    my_queue_first = agent_state.memory.task_queue[0] if agent_state.memory.task_queue else None

    for task in tasks:
        dist = my_distances.get(task.state.location, float('inf'))
        distance_factor = 1.0 / (dist + 1.0)

        competing_support = 0.0
        for aid, dmap in others_distances.items():
            other_dist = dmap.get(task.state.location, float('inf'))
            if other_dist < dist:
                competing_support += 1.0

        queue_support = 1.0 if my_queue_first == task.id else 0.0

        likelihood = max(0.05, (distance_factor + queue_support) / (1.0 + competing_support))
        likelihoods[task.id] = likelihood

    return likelihoods


def _distances(start, tasks, walls):
    
    # tasks: list of goal locations
    goal_distances = {}
    goal_set = set(task.state.location for task in tasks)

    open_set = []
    heapq.heappush(open_set, (0, start))

    g_score = {start: 0}

    while open_set and goal_set:
        _, current = heapq.heappop(open_set)

        if current in goal_set:

            #find task id from location
            for task in tasks:
                if task.state.location == current:
                    goal_distances[task.id] = g_score[current]
                    break

            goal_set.remove(current)

        for neighbor in get_grid_neighbors(current, walls):
            tentative = g_score[current] + 1
            if neighbor not in g_score or tentative < g_score[neighbor]:
                g_score[neighbor] = tentative
                if neighbor not in [ii[1] for ii in open_set]:
                    heapq.heappush(open_set, (g_score[neighbor], neighbor))

    return goal_distances

    
    
    
    
    





