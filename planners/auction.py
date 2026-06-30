from planners.class_definition import Planner
from communication import messages
from pathfinding.distancefinder import FindClosestGoal
from pathfinding.to_direction import ToDirection

from task import Task

#based on CBBA?

class AuctionPlanner(Planner):
    def __init__(self, pathfinding_algorithm=None, communication=None):
        super().__init__(pathfinding_algorithm, communication)

        self.message_bus.subscribe(self._on_task, topic = "auction")
        self.received_messages = []

        self.task_bids = {}

        self.my_bids = {}

        self.current_queue = []
        self.current_goal = None
        
        

    def update_plan(self, observation: dict):
        self.agent_location = observation["agent_location"]
        self.world_map = observation["map"]
        self.agent_id = observation["agent_id"]

        incomplete_tasks = [task for task in observation["tasks"] if not task.completed]

        self._update_distance_to_first_task_in_queue()

        self._create_greedy_queue(incomplete_tasks)

        self._insert_tasks_into_queue(incomplete_tasks)

        self._configure_bids(observation["time"])

        self._publish_bids()

        self._process_received_messages()

        self._clean_up_queue(incomplete_tasks)

        pass

    def act(self):
        if self.current_goal is None:
            return None  # Placeholder action when no goal is selected
        
        if self.agent_location == self.current_goal:
            return "perform_task"  # Placeholder action when at the goal
        
        else: 
            path = self.pathfinding_algorithm(self.agent_location, self.current_goal, self.world_map)

        return ToDirection(self.agent_location, path[1])  # Convert the next step in the path to a direction
        
    def _update_distance_to_first_task_in_queue(self):
        if self.current_queue:
            first_task, _ = self.current_queue[0]
            distance_to_first_task = FindClosestGoal(self.world_map, self.agent_location, [first_task.location])[1]

            self.current_queue[0] = (first_task, distance_to_first_task + 1)  # add 1 to distance to account for the time it takes to perform the task

    def _create_greedy_queue(self, uncompleted_tasks):
        new_task_locations = {task.location: task for task in uncompleted_tasks if task.id not in [t.id for t, _ in self.current_queue]}
        while len(self.current_queue) < 5 or len(self.current_queue) < len(new_task_locations):
            if not new_task_locations:
                break  # No more tasks to add

            #find closest task to the last task in the queue or to the agent's location if the queue is empty
            last_location = self.current_queue[-1][0].location if self.current_queue else self.agent_location

            closest_goal, distance_to_closest_goal = FindClosestGoal(self.world_map, last_location, list(new_task_locations.keys()))

            if closest_goal is None:
                break  # No reachable tasks

            closest_task = new_task_locations[closest_goal]

            #check if a lower bid for the task already exists, if so, don't add it to the queue
            if self.task_bids.get(closest_task.id) and self.task_bids[closest_task.id][1] < distance_to_closest_goal + 1:
                del new_task_locations[closest_goal]
                continue  # Skip adding this task to the queue

            self.current_queue.append((closest_task, distance_to_closest_goal + 1)) # add 1 to distance to account for the time it takes to perform the task

            #remove this task from the new_task_locations to avoid adding it again
            del new_task_locations[closest_goal]

    def _insert_tasks_into_queue(self, uncompleted_tasks):
        new_task_locations = {task.location: task for task in uncompleted_tasks if task.id not in [t.id for t, _ in self.current_queue]}
        start_location = self.agent_location
        
        for ii, queue_entry in enumerate(self.current_queue):
            task, distance = queue_entry

            canidate_goal_location, distance = FindClosestGoal(self.world_map, start_location, list(new_task_locations.keys()), max_distance=distance - 1)

            if canidate_goal_location is not None:
                canidate_task = new_task_locations[canidate_goal_location]
                #check if a lower bid for the task already exists, if so, don't add it to the queue

                if self.task_bids.get(canidate_task.id) and self.task_bids[canidate_task.id][1] < distance + 1:
                    continue  # Skip adding this task to the queue

                #insert task into the queue at the current position and remove all entries after it, as they are no longer valid
                self.current_queue[ii] = (canidate_task, distance + 1) # add 1 to distance to account for the time it takes to perform the task
                self.current_queue = self.current_queue[:ii] # remove all entries after the inserted task

                return

            start_location = task.location  # Update the start location for the next task

    def _clean_up_queue(self, uncompleted_tasks):
        # Remove tasks from the queue that are no longer in the uncompleted_tasks list
        uncompleted_task_ids = {task.id for task in uncompleted_tasks}
        self.current_queue = [(task, distance) for task, distance in self.current_queue if task.id in uncompleted_task_ids]

        # Update current_goal to the first task in the queue if it exists
        if self.current_queue:
            self.current_goal = self.current_queue[0][0].location
        else:
            self.current_goal = None

        

    def _configure_bids(self, time):
        
        total_distance = 0
        for task, distance in self.current_queue:
            total_distance += distance
            self.my_bids[task.id] = total_distance + time

    def _publish_bids(self):
        queue_task_ids = [task.id for task, _ in self.current_queue]
        for task_id, bid_value in self.my_bids.items():
            if task_id in queue_task_ids:
                self._publish_bid(task_id, bid_value)
            else:
                # If the task is no longer in the queue, publish a high bid to indicate disinterest
                self._release_bid(task_id)        

    def _on_task(self, message: messages.Message) -> None:
        self.received_messages.append(("topic", message.sender, message.topic, message.payload))

    def _publish_bid(self, task_id, bid_value):
        self.message_bus.publish(messages.Message(
            sender=self.agent_id,
            topic="aucion",
            payload={"type":"bid", "task_id": task_id, "agent_id": self.agent_id, "completion_time": bid_value}
        ))
                  
    def _release_bid(self, task_id):
        self.message_bus.publish(messages.Message(
            sender=self.agent_id,
            topic="auction",
            payload={"type": "release", "task_id": task_id, "agent_id": self.agent_id}
        ))

    def _process_received_messages(self):
        recieved_bids = [msg for msg in self.received_messages if msg[2] == "auction" and msg[3]["type"] == "bid"]
        recieved_releases = [msg for msg in self.received_messages if msg[2] == "auction" and msg[3]["type"] == "release"]

        for bid_msg in recieved_bids:
            task_id = bid_msg[3]["task_id"]
            agent_id = bid_msg[3]["agent_id"]
            completion_time = bid_msg[3]["completion_time"]

            if not self.task_bids[task_id]:
                self.task_bids[task_id] = [agent_id, completion_time]
            else:
                _, current_best_time = self.task_bids[task_id]
                if completion_time < current_best_time:
                    self.task_bids[task_id] = [agent_id, completion_time]

        for release_msg in recieved_releases:
            task_id = release_msg[3]["task_id"]
            agent_id = release_msg[3]["agent_id"]

            if self.task_bids.get(task_id) and self.task_bids[task_id][0] == agent_id:
                del self.task_bids[task_id]

        #clear the received messages after processing
        self.received_messages.clear()