"""Distributed task-queue planner using message-based bids."""

from planners.class_definition import Planner
from communication import messages

from task import Task

class AuctionPlanner(Planner):
    """Construct a short task queue and exchange bids to resolve ownership."""

    def __init__(self, pathfinding_algorithm=None, agent_id = None, messagebus = None):
        super().__init__(pathfinding_algorithm, agent_id, messagebus)

        
        self.message_bus = messagebus

        self.received_messages = []

        self.message_bus.subscribe(self._on_task, topic = "auction", subscriber_id = agent_id)

        self.task_bids = {}
        self.current_queue = []
        self.current_task_queue = []
        self.current_goal = None
        
    def update_plan(self, observation: dict):
        """Incorporate bids, maintain the queue, and publish this agent's bids."""
        self.agent_location = observation["agent_location"]
        self.agent_id = observation["agent_id"]
        self.world_time = observation["time"]

        incomplete_tasks = [task for task in observation["tasks"] if not task.completed]

        self._process_received_messages()

        self._remove_lost_tasks_from_queue()

        self._clean_up_queue(incomplete_tasks)

        self._update_distance_to_first_task_in_queue()

        self._create_greedy_queue(incomplete_tasks)

        self._insert_tasks_into_queue(incomplete_tasks)

        self._configure_bids()

        self._clean_up_bid_database(observation)

        self._send_bid_database()

        if self.current_task_queue:
            self.current_goal = self.current_task_queue[0][0].location

            self.current_queue = [entry[0] for entry in self.current_task_queue]

        

    def _update_distance_to_first_task_in_queue(self):
        """Refresh the first queue entry's travel-and-service cost."""
        if self.current_task_queue:
            first_task, _ = self.current_task_queue[0]
            distance_to_first_task = self.pathfinding_algorithm.get_distance(self.agent_location, first_task.location)

            self.current_task_queue[0] = (first_task, distance_to_first_task + 1)  # add 1 to distance to account for the time it takes to perform the task

    def _create_greedy_queue(self, uncompleted_tasks):
        """Extend the queue with nearby tasks not already claimed more cheaply."""
        new_task_locations = {task.location: task for task in uncompleted_tasks if task.id not in [t.id for t, _ in self.current_task_queue]}
        while len(self.current_task_queue) < 5 or len(self.current_task_queue) < len(new_task_locations):
            if not new_task_locations:
                break  # No more tasks to add

            #find closest task to the last task in the queue or to the agent's location if the queue is empty
            last_location = self.current_task_queue[-1][0].location if self.current_task_queue else self.agent_location

            closest_goal, distance_to_closest_goal = self.pathfinding_algorithm.findclosestgoal(last_location, list(new_task_locations.keys()))

            if closest_goal is None:
                break  # No reachable tasks

            closest_task = new_task_locations[closest_goal]

            #check if a lower bid for the task already exists, if so, don't add it to the queue
            if not self._should_insert_task(closest_task, closest_task, distance_to_closest_goal):
                del new_task_locations[closest_goal]
                continue  # Skip adding this task to the queue

            self.current_task_queue.append((closest_task, distance_to_closest_goal + 1)) # add 1 to distance to account for the time it takes to perform the task

            #remove this task from the new_task_locations to avoid adding it again
            del new_task_locations[closest_goal]

    def _remove_lost_tasks_from_queue(self):
        """Discard queue entries after the first task won by another agent."""
        # remove tasks that agent got outbid on from the queue
        for ii, (task, distance) in enumerate(self.current_task_queue):
            if self.task_bids.get(task.id) and self.task_bids[task.id][0] != self.agent_id:
                #remove all tasks from the queue after this one, as they are no longer valid
                self.current_task_queue = self.current_task_queue[:ii]
                break  # Exit the loop after modifying the list

    def _insert_tasks_into_queue(self, uncompleted_tasks):
        """Insert a profitable task before a later queued task when possible."""
        new_task_locations = {task.location: task for task in uncompleted_tasks if task.id not in [t.id for t, _ in self.current_task_queue]}
        start_location = self.agent_location
        task = None
        for ii, queue_entry in enumerate(self.current_task_queue):
            distance = queue_entry[1]

            canidate_goal_location, distance = self.pathfinding_algorithm.findclosestgoal(start_location, list(new_task_locations.keys()), max_distance = distance - 1)

            if canidate_goal_location is not None:
                canidate_task = new_task_locations[canidate_goal_location]
                #check if a lower bid for the task already exists, if so, don't add it to the queue

                if not self._should_insert_task(task, canidate_task, distance):
                    task = queue_entry[0]
                    start_location = task.location  # Update the start location for the next task
                    continue  # Skip adding this task to the queue

                #insert task into the queue at the current position and remove all entries after it, as they are no longer valid

                self.current_task_queue = self.current_task_queue[:ii] + [(canidate_task, distance + 1)]  # add 1 to distance to account for the time it takes to perform the task

                
            task = queue_entry[0]
            start_location = task.location  # Update the start location for the next task

    def _should_insert_task(self, prior_task, canidate_task, canidate_distance):
        """Return whether this candidate's bid beats the currently recorded bid."""
        #check if the task has already been caimed by another agent
        if canidate_task.id not in self.task_bids:
            return True

        #calculate bid and check if ours is lower
        if self._compute_bid(prior_task, canidate_distance) < self.task_bids[canidate_task.id][2]:
            return True
        
        return False

    def _clean_up_queue(self, uncompleted_tasks):
        """Remove completed or otherwise unavailable tasks from the queue."""
        # Remove tasks from the queue that are no longer in the uncompleted_tasks list
        uncompleted_task_ids = {task.id for task in uncompleted_tasks}
        self.current_task_queue = [(task, distance) for task, distance in self.current_task_queue if task.id in uncompleted_task_ids]

        # Update current_goal to the first task in the queue if it exists
        if self.current_task_queue:
            self.current_goal = self.current_task_queue[0][0].location
        else:
            self.current_goal = None


    def _configure_bids(self):
        """Update bids for queued tasks and release bids for removed tasks."""
        prior_task = None

        #update bids
        for task, distance in self.current_task_queue:
            bid = (task.id, self.agent_id, self._compute_bid(prior_task, distance), self.world_time)
            
            if self._is_this_bid_better(bid):
                self.task_bids[task.id] = bid

            prior_task = task

        #update releases
        for (task_id, winner_id, _, _) in self.task_bids.values():
            if winner_id == self.agent_id:
                task_in_queue = False
                for task, _ in self.current_task_queue:
                    if task.id == task_id:
                        task_in_queue = True
                        break

                if task_in_queue == False:
                    #release this bid
                    self.task_bids[task_id] = (task_id, self.agent_id, float('inf'), self.world_time)
                
    def _on_task(self, message: messages.Message) -> None:
        """Buffer auction topic messages for processing during planning."""
        self.received_messages.append(("topic", message.sender, message.topic, message.payload))
             
    def _send_bid_database(self):
        """Broadcast the current bid database to auction subscribers."""
        task_database = self.task_bids

        self.message_bus.publish(messages.Message(
            sender=self.agent_id,
            topic="auction",
            payload={"task_db": task_database, "current_t": self.world_time}
        ))
        

    def _process_received_messages(self):
        """Merge newer or better bids from received auction messages."""
        for message in self.received_messages:
            for bid in message[3]["task_db"].values():
                if self._is_this_bid_better(bid):
                    self.task_bids[bid[0]] = bid
        
        #clear the received messages after processing
        self.received_messages.clear()

    def _is_this_bid_better(self, bid):
        """Compare a candidate bid with the current winning bid for its task."""
        (task_id, bid_publisher, bid_value, bid_time) = bid

        if task_id not in self.task_bids.keys():
            return True #no bid yet so automatic win
        
        (_, current_winner, current_winning_bid, current_bid_time) = self.task_bids[task_id]

        if current_winning_bid > bid_value:
            return True #new bid is better

        if current_winner == bid_publisher:
            if bid_time > current_bid_time:
                return True #same owner, bid can be updated
        
        return False

    def _compute_bid(self, prior_task: Task | None, canidate_distance: int):
        """Calculate travel, service, and time cost for a candidate task."""
        bid = 0.001 * self.agent_id

        if prior_task:
            for task, dist in self.current_task_queue:
                bid += dist
                if task.id == prior_task.id:
                    break

        return bid + canidate_distance + self.world_time
    
    def _clean_up_bid_database(self, observation):
        """Remove bids for tasks that have already been completed."""
        tasks = observation["tasks"]

        for task in tasks:
            if task.completed == True:
                if task.id in self.task_bids.keys():
                    #remove from the list
                    self.task_bids.pop(task.id)
