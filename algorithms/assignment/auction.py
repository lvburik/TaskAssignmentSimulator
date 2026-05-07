from communication import Message, MessageBus
from algorithms.assignment.greedy import find_goal_distances_with_walls, select_closest_goal, find_task_id_from_location

bus = MessageBus()
received_messages = []

def on_task(message: Message) -> None:
	received_messages.append(message)
	#print(f"topic:{message.topic} from {message.sender} -> {message.payload}")
      
bus.subscribe(on_task, topic="bids")
bus.subscribe(on_task, topic="assignment")


def decentralized_auction_task_selector(agent_state, tasks):
    
    # check if uncompeted tasks are available using agent's observation of the world
    uncompleted_tasks = [task for task in tasks.values() if not task.state.completed]

    # check wich tasks are already being pursued by other agents using agent's the task topic in the message bus
    assigned_task_ids = check_assigned_tasks(received_messages).keys()

    available_task_ids = [task.id for task in uncompleted_tasks if task.id not in assigned_task_ids]

    # check best bid for each available task using the bids topic in the message bus
    bids = check_bids(received_messages)

    

    

    did_win = False
    won_task = None
    for task_id in available_task_ids:
        if did_i_win(agent_state.id, task_id, bids):
            assign_task(agent_state.id, task_id)
            won_task = task_id
            did_win = True
            
            break


    # remove won tasks from available tasks
    if did_win:
        available_task_ids.remove(won_task)

    if available_task_ids:
        goal_list = [tasks[task_id].state.location for task_id in available_task_ids]


        #find the final position of the agent after executing its current plan to use as the starting point for distance calculations
        
        final_position = tasks[agent_state.memory.task_queue[-1]].state.location if agent_state.memory.task_queue else agent_state.state.position

        goal_distances = find_goal_distances_with_walls(final_position, goal_list, agent_state.memory.world_observation.walls)

        closest_goal = select_closest_goal(goal_distances)

        closest_task_id = find_task_id_from_location(tasks, closest_goal)
        distance_to_closest = goal_distances[closest_goal]

        bid_value = calculate_total_queue_cost(agent_state, tasks) + distance_to_closest

        publish_bid(agent_state.id, closest_task_id, bid_value)
        

    if did_win:
        task_queue = agent_state.memory.task_queue
        task_queue.append(won_task)
        
        return task_queue
    else:
        return agent_state.memory.task_queue



def assign_task(agent_id, task_id):
      bus.publish(Message(sender=agent_id, topic="assignment", payload={"task_id": task_id}))
      
def publish_bid(agent_id, task_id, distance):
        bus.publish(Message(sender=agent_id, topic="bids", payload={"agent_id": agent_id, "task_id": task_id, "distance": distance}))   
      
def check_assigned_tasks(received_messages):
    #returns a dict of task_id to agent_id for tasks that have been assigned according to the messages in the message bus
    assigned_tasks = {}
    for msg in received_messages:
        if isinstance(msg, Message) and msg.topic == "assignment":
            assigned_tasks[msg.payload["task_id"]] = msg.sender
            
    return assigned_tasks

def check_bids(received_messages):
    #returns a dict of task_id to the lowest bid for that task and the corresponding agent_id
    bids = {}
    for msg in received_messages:
            if isinstance(msg, Message) and msg.topic == "bids":
                task_id = msg.payload["task_id"]
                agent_id = msg.payload["agent_id"]
                distance = msg.payload["distance"]
                if task_id not in bids or distance < bids[task_id]["distance"]:
                        bids[task_id] = {"agent_id": agent_id, "distance": distance}
    return bids
    
def did_i_win(agent_id, task_id, bids):
    #returns true if the agent has the lowest bid for the task
    return task_id in bids and bids[task_id]["agent_id"] == agent_id

def calculate_total_queue_cost(agent_state, tasks):
    total_cost = 0
    current_position = agent_state.state.position

    for task_id in agent_state.memory.task_queue:
        task_location = tasks[task_id].state.location
        total_cost += find_goal_distances_with_walls(current_position, [task_location], agent_state.memory.world_observation.walls).get(task_location, float('inf'))
        current_position = task_location

    return total_cost

