# Task Assignment Simulator

Task Assignment Simulator is a grid-world simulation of agents that move around
obstacles and complete tasks as they appear. Each agent observes the world,
chooses a plan, and takes one action per time step. The project includes
rule-based, communication-based, and learned planners, optional Pygame
visualization, and JSON Lines simulation logs.

## Requirements

- Python 3.12 or newer
- Python packages listed in `requirements.txt`:

  ```bash
  python -m pip install -r requirements.txt
  ```

- `XGB` and `MLP` planners load Python pickle files and need versions of their
  training libraries compatible with those files. The `CNN` planner needs a
  compatible PyTorch checkpoint.

Pretrained model files are included in `models/`: `XGB.pkl`, `MLP.pkl`, and
`CNN.pt`. The example configuration points to these files by default, so the
learned planners can be selected without downloading separate checkpoints.
Only load pickle model files from trusted sources.

## Run a simulation

From the repository root, create a local configuration from the example:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp config_example.py config.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

Edit `config.py` if you want to change the defaults. The default `CNN` planner
uses the included `models/CNN.pt` checkpoint; `XGB` and `MLP` use
`models/XGB.pkl` and `models/MLP.pkl`. The built-in `Greedy` planner is also
available and does not need a model. Then run:

```bash
python main.py
```

`config.py` is intentionally ignored by Git; edit `config_example.py` if you
want to change the checked-in defaults instead. The model path entries in
`PATHS` can be changed if you replace or relocate a checkpoint.

For a small, headless run, for example, set the following values in
`config.py`:

```python
SIMULATION_SETTINGS["number_of_agents"] = [3]
SIMULATION_SETTINGS["planner_algorithm"] = ["Greedy"]
SIMULATION_SETTINGS["world_map"] = ["Map0.png"]
SIMULATION_SETTINGS["simulation_seeds"] = [1324]
SIMULATION_SETTINGS["simulation_timesteps"] = [50]
SIMULATION_SETTINGS["number_of_tasks"] = [20]
SIMULATION_SETTINGS["visualization"] = False
SIMULATION_SETTINGS["record"] = True
```

Map filenames are resolved under `PATHS["maps_dir"]`. A map is a PNG image:
pixels darker than 128 on a grayscale conversion are blocked, and all other
pixels are walkable. Coordinates are `(x, y)`, with `(0, 0)` at the top-left.
The bundled `maps/Map0.png` through `Map9.png` are ready-to-use examples.

## Configuration reference

`app_config.py` imports `PATHS` and `SIMULATION_SETTINGS` from a local
`config.py`, falling back to `config_example.py` when no local configuration
exists. `PATHS` contains filesystem locations; `SIMULATION_SETTINGS` contains
the simulation parameters and runtime options.

### Paths (`PATHS`)

| Key | Purpose |
| --- | --- |
| `maps_dir` | Directory containing the map PNG files named by `world_map`. |
| `data_dir` | Directory where recorded simulation logs are written. |
| `xgb_model` | Pickle checkpoint loaded by the `XGB` planner; defaults to `models/XGB.pkl`. |
| `mlp_model` | Pickle checkpoint loaded by the `MLP` planner; defaults to `models/MLP.pkl`. |
| `cnn_model` | PyTorch checkpoint loaded by the `CNN` planner; defaults to `models/CNN.pt`. |

### Simulation settings (`SIMULATION_SETTINGS`)

| Setting | Meaning |
| --- | --- |
| `number_of_agents` | List of agent counts to run. |
| `planner_algorithm` | List of planner names: `Random`, `Greedy`, `Tom`, `Auction`, `XGB`, `MLP`, or `CNN`. |
| `world_map` | List of map filenames, resolved relative to `maps_dir`. |
| `simulation_seeds` | List of Python random seeds; each run resets the random generator to its selected seed. |
| `simulation_timesteps` | Number of world steps in each run. |
| `number_of_tasks` | Number of tasks created for each run. Each spawn time is chosen randomly from `-number_of_agents - 10` through `simulation_timesteps - 1`, inclusive. |
| `visualization` | When true, display the simulation in a Pygame window. |
| `record` | When true, write the run metadata, map information, and world state after each step as JSON Lines. |
| `message_policy` | List of message-delivery policy objects used as scenarios. Built-ins are `AlwaysAllowPolicy()`, `LimitedRangePolicy(max_distance)`, and `PartlyBrokenPolicy(number_of_agents, broken_fraction)`. An empty list means no delivery policy. |
| `simrunner_max_fps` | Maximum visualization update rate; it does not change headless simulation speed. |
| `world_task_spawn_messages` | Print a message whenever a task spawns. |
| `world_task_completion_messages` | Print a message when an agent successfully completes a task. |
| `world_status_updates` | Print progress and active incomplete task counts every ten steps. |
| `world_random_close_spawns` | Give each added agent a 50% chance of attempting to spawn next to an existing agent before choosing a random free cell. |
| `viewer_basic_sim_info` | Show the time and active incomplete task count in the Pygame window. |
| `viewer_debug_mode` | Enable the configured Pygame debug overlays. |
| `viewer_debug_mode_settings` | List of overlays: `1` agent IDs, `2` agent goal locations, `3` task IDs, `4` agent task queues. |

The list-valued parameters (`number_of_agents`, `planner_algorithm`,
`world_map`, `simulation_seeds`, `simulation_timesteps`, `number_of_tasks`,
and `message_policy`) are combined as a Cartesian product. For example, two
agent counts and three seeds produce six runs when the other lists each
contain one value. Use a one-element list for a single value. The example
defaults perform four runs because they specify four seeds and one value for
each other parameter.

To disable message filtering, use `message_policy = []`. With the `Auction`
planner, agents still exchange their bids through the message bus; without
policies, delivery is unrestricted.

## How a simulation works

1. `main.py` enumerates every combination of the list-valued settings, seeds
   Python's `random` generator, and asks `simrunner` to create the world.
2. `World` reads the map, creates agents and tasks, and initializes
   `DistanceFinder`, which builds a four-direction movement graph and caches
   shortest-path distances.
3. At the start of each time step, eligible tasks spawn in unoccupied walkable
   cells. Each agent receives an observation containing its location, other
   agent locations, the map, and tasks that have reached their spawn time.
4. Each planner updates its plan and returns an action: move `up`, `down`,
   `left`, or `right`; `perform_task`; or no action. The world collects agents'
   actions and then applies them in agent order. Moves into walls, outside the
   map, or another agent's occupied cell are ignored.
5. A task is completed when an agent performs it while on its cell. If
   recording is enabled, the state after the actions is appended to the run's
   log. In headless mode, steps execute as quickly as possible; visualization
   uses `simrunner_max_fps`.

The available planners are:

- `Random`: chooses a random direction without task assignment.
- `Greedy`: moves toward the closest reachable active task.
- `Tom`: selects tasks using beliefs informed by task distance and observed
  competing agents.
- `Auction`: maintains a task queue and exchanges bids with other agents.
- `XGB` and `MLP`: use a supplied tabular classifier to select tasks.
- `CNN`: uses a supplied PyTorch classifier to select tasks from map images.

## Outputs

When `record` is enabled, a timestamped `TASim_...json` file is written under
`data_dir`. Each line is a separate JSON object: the first two lines contain
the simulation parameters and map dimensions/matrix; subsequent lines contain
one time step's agent positions and queues, plus active task positions. The
default data directory is `Data/`, which is ignored by Git.

## Source layout

- `main.py`, `simrunner.py`: configuration-driven batches and simulation loop.
- `world.py`, `agent.py`, `task.py`: grid-world state, observations, and task
  lifecycle.
- `planners/`: planner interface, built-in strategies, and model input/model
  loading code.
- `pathfinding/`: grid graph, shortest-path cache, and movement directions.
- `communication/`: messages, delivery bus, and message policies.
- `visualization/`: optional Pygame rendering.
- `datalogger.py`: JSON Lines output.
