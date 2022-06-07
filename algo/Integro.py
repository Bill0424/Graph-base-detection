import math
import csv
import time


class Integro:
    def __init__(self, graph, options=None):
        self.graph = graph
        self.options = options if options else {}

    def classify_potential_victim(self, predict_model, beta=2, threshold=0.5):
        victim = {}
        real = {}
        victim_set = []
        """model omitted here, csv data format = {id, 1 or 0, potential score<-(0, 1)}"""
        with open(predict_model, newline='') as file:
            rows = csv.reader(file)
            for i in rows:
                if int(i[1]):
                    victim_set.append(i[0])
                    victim[i[0]] = float(i[-1])
                else:
                    real[i[0]] = float(i[-1])
        for edge in self.graph.edges:
            edge0 = edge[0].name
            edge1 = edge[1].name
            if edge0 == edge1 and self.graph.degree(edge[0], weight='weight') < 1:
                # degree normalization for self-loop
                self.graph[edge[0]][edge[1]]['weight'] = (1-self.graph.degree(edge[0], weight='weight'))/2
                continue
            if edge0 in victim_set and edge1 in victim_set:
                p0 = victim[edge0]
                p1 = victim[edge1]
                self.graph[edge[0]][edge[1]]['weight'] = min(1, beta*(1-max(p0, p1)))
            elif edge0 in victim_set:
                p0 = victim[edge0]
                self.graph[edge[0]][edge[1]]['weight'] = min(1, beta*(1-p0))
            elif edge1 in victim_set:
                p1 = victim[edge1]
                self.graph[edge[0]][edge[1]]['weight'] = min(1, beta*(1-p1))
        print('Adjust weight successfully!')

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
