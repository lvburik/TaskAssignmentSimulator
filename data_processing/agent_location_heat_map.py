import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DATA_FILE = Path(__file__).resolve().parents[1] / "Data" / "world_log.json"


def load_world_log(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_visit_counts(data: dict) -> tuple[np.ndarray, np.ndarray]:
    walls = np.array(data["walls"], dtype=int)
    visit_counts = np.zeros_like(walls, dtype=int)

    for snapshot in data.get("snapshots", []):
        for location in snapshot.get("agent_locations", {}).values():
            x, y = location
            if 0 <= y < visit_counts.shape[0] and 0 <= x < visit_counts.shape[1]:
                visit_counts[y, x] += 1

    return walls, visit_counts


def plot_visit_heat_map(walls: np.ndarray, visit_counts: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(8, 7))

    # Draw visit frequency as a heat map.
    heat = ax.imshow(visit_counts, cmap="YlOrRd", origin="upper")

    # Overlay walls as dark cells so the world layout stays visible.
    wall_mask = np.ma.masked_where(walls == 0, walls)
    ax.imshow(wall_mask, cmap="Greys", alpha=0.8, origin="upper")

    ax.set_title("Agent Location Visit Heat Map")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    ax.set_xticks(np.arange(visit_counts.shape[1]))
    ax.set_yticks(np.arange(visit_counts.shape[0]))
    ax.set_xticks(np.arange(-0.5, visit_counts.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, visit_counts.shape[0], 1), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=0.5, alpha=0.25)

    cbar = plt.colorbar(heat, ax=ax)
    cbar.set_label("Visit Count")

    plt.tight_layout()
    plt.show()


def main() -> None:
    data = load_world_log(DATA_FILE)
    walls, visit_counts = compute_visit_counts(data)

    print("Visit count matrix (rows=y, cols=x):")
    print(visit_counts)

    plot_visit_heat_map(walls, visit_counts)


if __name__ == "__main__":
    main()
