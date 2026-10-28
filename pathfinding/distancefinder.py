"""Precompute shortest paths between all walkable map cells."""

import numpy as np

class DistanceFinder:
    """Four-neighbor grid graph with cached all-pairs shortest-path distances."""

    def __init__(self, map_matrix):
        """Build the walkable-cell graph and cache distances from every cell."""
        print("precalculating paths")
        
        self._create_connection_graph(map_matrix)
        print("caching distances")
        
        self._cache_distances()   
        print("Pathing Initialized")

    def get_distance(self, start, goal):
        """Return the cached number of moves between two walkable coordinates."""
        start_node_id = self.location_dict[start]
        goal_node_id = self.location_dict[goal]

        return self.distances[start_node_id][goal_node_id]

    def get_distances(self, start, goals):
        """Return the distance from ``start`` to each goal, preserving order."""
        return [self.get_distance(start, goal) for goal in goals]

    def next_step(self, agent_location, goal_location):
        """Return a neighboring coordinate that decreases distance to the goal."""

        agent_node_id = self.location_dict[agent_location]
        goal_node_id = self.location_dict[goal_location]

        neighbor_nodes = np.where(self.connection_graph[agent_node_id] != 0)[0]

        current_distance = self.distances[agent_node_id][goal_node_id]

        for node in neighbor_nodes:
            if self.distances[node][goal_node_id] == current_distance-1:
                return self.node_locations[node]
                

    def findclosestgoal(self, start, goals, max_distance=float("inf")):
        """Return the nearest goal within the limit and its distance, if any."""
        if not goals:
            return None, float("inf")

        closest_goal = None
        min_distance = float("inf")

        for goal in goals:
            distance = self.get_distance(start, goal)
            if distance < min_distance:
                closest_goal = goal
                min_distance = distance

        if closest_goal is not None and min_distance <= max_distance:
            return closest_goal, min_distance

        return None, float("inf")

    def _create_connection_graph(self, map_matrix):
        """Index walkable cells and connect cardinal neighbors in a dense graph."""
        map_matrix = np.matrix(map_matrix)

        
        self.map_shape = np.shape(map_matrix)

        self.location_dict = {}
        self.node_locations = []

        for y in range(self.map_shape[0]):
            for x in range(self.map_shape[1]):
                if map_matrix[y, x] == 0: #node is walkable
                    self.location_dict[(x, y)] = len(self.node_locations)
                    self.node_locations.append(np.array([x, y]))
                    
        self.number_of_nodes = len(self.node_locations)

        graph_matrix = np.zeros((self.number_of_nodes, self.number_of_nodes), int)

        for start_node in range(self.number_of_nodes):
            for end_node in range(self.number_of_nodes):
                graph_matrix[start_node][end_node] = np.linalg.norm(self.node_locations[end_node] - self.node_locations[start_node]) == 1

        self.connection_graph = graph_matrix

    def _cache_distances(self):
        """Run breadth-first search from each node to cache shortest distances."""
        distances = np.zeros((self.number_of_nodes, self.number_of_nodes), int)

        for node in range(self.number_of_nodes):
            open_set = [node]
            
            while len(open_set) != 0:
                current = open_set[0]
                open_set.pop(0)

                neighbors = np.where(self.connection_graph[current])[0]

                for neighbor in neighbors:
                    if neighbor == node: #node is start node
                        continue

                    if distances[node][neighbor]!=0: #node already explored
                        continue

                    distances[node][neighbor] = distances[node][current] + self.connection_graph[current][neighbor]

                    open_set.append(neighbor)          
                
        self.distances = distances

        
