from Planners.class_definition import Planner
from communication import messages
from pathfinding.distancefinder import BulkDistanceFinder
from pathfinding.to_direction import ToDirection

class AuctionPlanner(Planner):
    def __init__(self, pathfinding_algorithm=None, communication=None):
        super().__init__(pathfinding_algorithm, communication)

        self.message_bus.subscribe(self.on_task, topic = "bids")
        self.message_bus.subscribe(self.on_task, topic = "task_assignments")

        self.my_bids = {}
        self.current_task_queue = []
        self.current_goal = None
        self.recieved_messages = []

        self.agent_location = None
        self.world_map = None
        

    def update_plan(self, observation: dict):
        self.agent_location= observation["agent_location"]
        self.world_map = observation["map"]


        recieved_bids = self.check_bids()

        won_auctions = self.what_did_I_win(recieved_bids)
        #sort won auctions by completion time
        won_auctions.sort(key=lambda x: x[1])

        tasks = [task for task in observation["tasks"] if not task.completed]

        # update the current task queue based on the won auctions
        self.current_task_queue.clear()
        for win in won_auctions:
            task_id = win[0]
            for task in tasks:
                if task.id == task_id:
                    self.current_task_queue.append(task)
                    break

        tasks_not_assigned_to_me = [task for task in tasks if task not in self.current_task_queue]

        self.calculate_and_publish_bids(tasks_not_assigned_to_me, observation)

        self.current_goal = self.current_task_queue[0].location if self.current_task_queue else None



    def act(self):
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
        
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
        
        else: 
            path = self.pathfinding_algorithm(self.agent_location, self.current_goal, self.world_map)

        return ToDirection(self.agent_location, path[1])  # Convert the next step in the path to a direction
        
    def calculate_and_publish_bids(self, tasks, observation):
        distances = BulkDistanceFinder(observation["map"], observation["agent_location"], [task.location for task in tasks])

        for task in tasks:
            if task.completed:
                continue  # Skip completed tasks

            # Calculate the bid based on your own criteria (e.g., distance, time, etc.)
            current_queue_cost = 0
            if self.current_task_queue:
                current_queue_cost = max(self.my_bids.get(t.id, 0) for t in self.current_task_queue)
            bid_value = observation["time"] + distances.get(task.location, float('inf')) + 1 + current_queue_cost

            # Store the bid in a dictionary for later reference
            self.my_bids[task.id] = bid_value

            # Send the bid to the message bus
            self.message_bus.publish(messages.Message(
                sender = observation["agent_id"],
                topic="bids",
                payload={"task_id": task.id, "agent_id": observation["agent_id"], "completion_time": bid_value}
            ))
        
    def check_bids(self):
        
        #returns a dict of task_id to the lowest bid for that task and the corresponding agent_id
        bids = {}
        for msg in self.received_messages:
                if isinstance(msg, messages.Message) and msg.topic == "bids":
                    task_id = msg.payload["task_id"]
                    agent_id = msg.payload["agent_id"]
                    if agent_id == self.agent_id:
                        continue  # Skip own bids

                    completion_time = msg.payload["completion_time"]
                    if task_id not in bids or completion_time < bids[task_id]["completion_time"]:
                            bids[task_id] = {"agent_id": agent_id, "completion_time": completion_time}
        return bids

    def what_did_I_win(self, recieved_bids):
        my_wins = []
        
        for task_id, my_bid in self.my_bids.items():
            if task_id in recieved_bids:
                lowest_bid = recieved_bids[task_id]
                if my_bid < lowest_bid["completion_time"]:
                    my_wins.append((task_id, my_bid))

                    #if lost to another, forget all my own bids with a higher completion time than the winning bid
                    for t_id, bid in list(self.my_bids.items()):
                        if bid > lowest_bid["completion_time"]:
                            del self.my_bids[t_id]
            else:
                # If no other bids were received for this task, consider it a win
                my_wins.append((task_id, my_bid))

        return my_wins

    def on_task(self, message: messages.Message) -> None:
        self.received_messages.append(("topic", message.sender, message.topic, message.payload))
                  

