import csv
import json
import random
import networkx as nx


class Node:
    def __init__(self, name, node_type, initial_rank, groups, rank=None):
        self.name = name
        self.node_type = node_type
        self.init_rank = initial_rank
        self.rank = rank
        self.groups = groups if groups else {}

    def __repr__(self):
        return 'Node(user id): {}'.format(self.name)


def load_config(file):
    with open(file, 'r') as f:
        data = f.read()
        return json.loads(data)


def choose_seed1(group_top, group_normal, top, total):
    trust_seed = set(random.sample(group_top, top))
    while len(trust_seed) != total:
        trust_seed.add(random.choice(group_normal))
    print(f'Trust seed = {list(trust_seed)}')
    return list(trust_seed)


def choose_seed2(total):
    with open('Data/community_data.json', 'r') as f:
        data = f.read()
        data = json.loads(data)
    each_num = int(total / len(data))
    trust_seed = list()
    for k in data.keys():
        trust_seed += random.sample(data[k], each_num)
    print(f'Trust seed = {trust_seed}')
    return trust_seed


def choose_seed3(total):
    victim = list()
    with open('Data/new_potential_victim.csv', newline='') as file:
        rows = csv.reader(file)
        for i in rows:
            if int(i[1]):
                victim.append(i[0])
    with open('Data/community_data.json', 'r') as f:
        data = f.read()
        data = json.loads(data)
    each_num = int(total / len(data))
    trust_seed = list()
    for k in data.keys():
        select = list()
        for i in data[k]:
            if i not in victim:
                select.append(i)
        trust_seed += random.sample(select, each_num)
    print(f'Trust seed = {trust_seed}')
    return trust_seed


def attack0(G, nodes, human, faker, attack_num):
    G.add_weighted_edges_from([(nodes[edge[0]], nodes[edge[1]], 1)
                                   for edge in zip([random.choice(human) for _ in range(attack_num)],
                                                   [random.choice(faker) for _ in range(attack_num)])])

    return G


def attack1(G, nodes, human, faker, attack_num, attack_ratio=0.7):
    victim = list()
    with open('Data/new_potential_victim.csv', newline='') as file:
        rows = csv.reader(file)
        for i in rows:
            if int(i[1]):
                victim.append(i[0])
    attack_victim = int(attack_num * attack_ratio)
    G.add_weighted_edges_from([(nodes[edge[0]], nodes[edge[1]], 1)
                                   for edge in zip([random.choice(victim) for _ in range(attack_victim)],
                                                   [random.choice(faker) for _ in range(attack_victim)])])
    G.add_weighted_edges_from([(nodes[edge[0]], nodes[edge[1]], 1)
                                   for edge in zip([random.choice(human) for _ in range(attack_num - attack_victim)],
                                                   [random.choice(faker) for _ in range(attack_num - attack_victim)])])

    return G


def attack2(G, nodes, seed, faker, k, attack_num):
    victim = set()
    for source in seed:
        source_path_lengths = nx.single_source_dijkstra_path_length(G, nodes[source])
        for v in source_path_lengths.keys():
            if source_path_lengths[v] == k:
                victim.add(v)
    victim = list(victim)
    G.add_weighted_edges_from([(edge[0], nodes[edge[1]], 1)
                                   for edge in zip([random.choice(victim) for _ in range(attack_num)],
                                                   [random.choice(faker) for _ in range(attack_num)])])
    return G


def attack3(G, nodes, faker, known_seed, k, attack_num):
    seed = random.sample(known_seed, k)
    G.add_weighted_edges_from([(nodes[edge[0]], nodes[edge[1]], 1)
                                   for edge in zip([random.choice(seed) for _ in range(attack_num)],
                                                   [random.choice(faker) for _ in range(attack_num)])])
    return G


def load_graph(graph_file, user_file, total_trust, select_top10, select_total, num_attack_edge, seed_select=2, attack_method=2):
    with open(graph_file, 'r') as f1:
        data1 = f1.read()
    with open(user_file, 'r') as f2:
        data2 = f2.read()
    return from_json(data1, data2, total_trust, select_top10, select_total, num_attack_edge, seed_select, attack_method)


def from_json(data1, data2, trust, top, total, attack, seed_select, attack_method):
    data = json.loads(data1)
    user = json.loads(data2)

    if seed_select == 1:
        # 1. num top from top node, num total-top from human node
        trust_seed = choose_seed1(user['top_node'], user['human'], top, total)
    elif seed_select == 2:
        # 2. seed distribute evenly in community (community def |community| >= 30)
        trust_seed = choose_seed2(total)
    else:
        # 3. same method of 2. , but skip victim node
        trust_seed = choose_seed3(total)
    trust /= total
    graph = nx.Graph()
    nodes = {}
    for node in data['nodes']:
        groups = node['groups'] if node['groups'] else None
        rank = trust if node['name'] in trust_seed else node['rank']
        nodes[node['name']] = Node(node['name'], node['node_type'], rank, groups)
        graph.add_node(nodes[node['name']])
    # existing edge
    graph.add_weighted_edges_from([(nodes[edge[0]], nodes[edge[1]], edge[2])
                                    for edge in data['edges']])
    print(f'Original graph summary:{graph}')

    # attack edge (remark : weight of attack edge is 1)
    if attack_method == 0:
        # 0 attack randomly on human
        graph = attack0(graph, nodes, user['human'], user['faker'], attack)

    elif attack_method == 1:
        # 1 attack edge with (attack ratio) on victim, (1-attack ratio) on human
        graph = attack1(graph, nodes, user['human'], user['faker'], attack)

    elif attack_method == 2:
        # 2. distant-seed attack : attacker targets accounts that are k nodes away from all trusted accounts.
        k = 3
        graph = attack2(graph, nodes, trust_seed, user['faker'], k, attack)

    elif attack_method == 3:
        # 3 random-seed attack : attackers have only a partial knowledge and target k trusted accounts picked at random.
        k = 10
        know_ration = 0.8
        known = int(len(trust_seed) * know_ration)
        known_seed = random.sample(trust_seed, known)
        k = k if k < len(known_seed) else len(known_seed)

        graph = attack3(graph, nodes, user['faker'], known_seed, k, attack)

    print(f'Adding attack edge graph summary:{graph}')
    return graph



