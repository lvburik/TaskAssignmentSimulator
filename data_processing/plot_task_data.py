Data_folder_path = "/home/luc/Desktop/AfstudeerProject/Simulator/Data"
File_name = "world_log.json"

import json
from pathlib import Path

#open file and load json data
with open(Path(Data_folder_path) / File_name, "r", encoding="utf-8") as f:
    data = json.load(f)

import matplotlib.pyplot as plt

#extract data for plotting
times = [snapshot["time"] for snapshot in data["snapshots"]]
tasks_completed = [sum(1 for task in snapshot["tasks"].values() if not task["completed"]) for snapshot in data["snapshots"]]

#plotting
plt.figure(figsize=(10, 6))
plt.plot(times, tasks_completed, marker='o')
plt.title("Number of To do Tasks Over Time")
plt.xlabel("Time")
plt.ylabel("Number of To do Tasks")
plt.grid()
plt.show()

