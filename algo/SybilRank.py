import math
import time


class SybilRank:
    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options if options else {}

    def rank(self, now):
        num_iterations = int(math.ceil(math.log(self.graph.order())))
        nodes_rank = {node: node.init_rank for node in self.graph}
        for i in range(num_iterations):
            nodes_rank = self.spread_nodes_rank(nodes_rank)
            print(f'Iteration {i+1}/{num_iterations}, spending time = {time.time()-now}')
            now = time.time()
        for node in self.graph:
            node.rank = nodes_rank[node]
            node_degree = self.graph.degree(node, weight='weight')
            if node_degree > 0:
                node.rank /= node_degree  # degree-normalized trust
        return self.graph

    def spread_nodes_rank(self, nodes_rank):
        """Power iteration"""
        new_nodes_rank = {}
        for node in nodes_rank:
            new_trust = 0
            neighbors = self.graph.neighbors(node)
            for neighbor in neighbors:
                neighbor_degree = self.graph.degree(neighbor, weight='weight')
                edge_weight = self.graph[node][neighbor].get('weight', 1)
                if neighbor_degree > 0:
                    new_trust += nodes_rank[neighbor] * \
                        edge_weight / neighbor_degree
            new_nodes_rank[node] = new_trust
        return new_nodes_rank
