

def decentralized_auction_task_selector(agent_state, tasks):
    # check if uncompeted tasks are available
    uncompleted_tasks = [task for task in tasks.values() if not task.state.completed]
    if not uncompleted_tasks:
        return []
    
    # TO:DO set up a service calling it get the current tasks allocated to each agent
    unallocated_tasks = uncompleted_tasks # for now, assume all uncompleted tasks are unallocated

    while unallocated_tasks:

    # update currently unallocated tasks

    
    
    if not unallocated_tasks:
        return self.memory.task_queue  # no new tasks to consider, stick with current queue
    
    # TO:DO implement a service to have every agent bid on the unassigned tasks based on thier current task queue and position

    # To:DO assign       


