
    
def track_tasks(world_state):
    #check if log file exists, if not create it and write header
    if not os.path.exists("task_log.csv"):
        with open("task_log.csv", "w") as f:
            f.write("time,agent_id,task_id,event_type\n")

    # Log task assignments, completions, and queue lengths for each agent
    log_task_assignments(world_state)
    log_task_completions(world_state)
    log_task_queues(world_state)

def log_task_assignments(world_state):


def log_task_completions(world_state):

def log_task_queues(world_state):