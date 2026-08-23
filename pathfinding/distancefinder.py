import numpy as np
import heapq

class DistanceFinder:
    def __init__(self, map_matrix):
        
        self._create_connection_graph(map_matrix)
        
        self._cache_distances()   

    def _create_connection_graph(self, map_matrix):
        map_matrix = np.matrix(map_matrix)

        
        self.map_shape = np.shape(map_matrix)

        self.location_dict = {}
        self.node_locations = []

        for x in range(self.map_shape[0]):
            for y in range(self.map_shape[1]):
                if map_matrix[x, y] == 0: #node is walkable
                    self.location_dict[(x, y)] = y*x + x
                    self.node_locations.append(np.array([x, y]))
                    
        self.number_of_nodes = len(self.node_locations)

        graph_matrix = np.zeros((self.number_of_nodes, self.number_of_nodes), int)

        for start_node in range(self.number_of_nodes):
            for end_node in range(self.number_of_nodes):
                graph_matrix[start_node][end_node] = np.linalg.norm(self.node_locations[end_node] - self.node_locations[start_node]) == 1

        self.connection_graph = graph_matrix

    

    def _cache_distances(self):
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


                
map = [[0, 0, 0, 0],[1, 1, 0, 1],[0, 1, 0, 0],[1, 1, 1, 0], [0, 0, 0, 0]]            

    



A = DistanceFinder(map)
print(A.location_dict)

        
