import csv
import json
import random
import numpy as np
import networkx as nx
from community import community_louvain


def collect_community(graph, human_user):
    comms = community_louvain.best_partition(graph)
    com_id = dict()
    for _, v in comms.items():
        if _ in human_user:
            try:
                com_id[v] += 1
            except KeyError:
                com_id[v] = 1
    o = []
    for key in com_id.keys():
        o.append((key, com_id[key]))
    o.sort(key=lambda x: x[1], reverse=True)
    user_com = dict()
    for i in o:
        if i[1] >= 30:
            user_com[i[0]] = []
    for user in comms.items():
        try:
            user_com[user[1]].append(user[0])
        except KeyError:
            pass
    return user_com


def generate_community_edge(user, num_com=5, r=0.6):
    node1 = list()
    node2 = list()
    for _ in range(num_com):
        com_node_num = random.randrange(100, 200, 1)
        edge_num = int(r*(com_node_num**2))
        node = [random.choice(user) for _ in range(com_node_num)]
        for _ in range(edge_num):
            node1.append(random.choice(node))
            node2.append(random.choice(node))
    for _ in range(2000):
        node1.append(random.choice(user))
        node2.append(random.choice(user))
    return zip(node1, node2)


def generate_edge(user, num=30000):
    node1 = [random.choice(user) for _ in range(num)]
    node2 = [random.choice(user) for _ in range(num)]
    return zip(node1, node2)


def collect_user(path):
    """Collect known user"""
    global data
    user_d = dict()
    n = 0
    for p in path:
        node_type = 'human' if name[n] == 'TFP' or name[n] == 'E13' else 'faker'
        with open(p, newline='') as user:
            rows = csv.reader(_.replace('\x00', '') for _ in user)
            next(rows)
            for i in rows:
                user_d[i[0]] = 1
                user_data[node_type].append(i[0])
                data['nodes'].append({
                    'name': i[0],
                    'node_type': node_type,
                    'groups': name[n],
                    'rank': 0,
                })
        n += 1
    return user_d


def collect_edge(path, weight=1, method='dense'):
    """Collect desired edges (edge of (u, v) where u, v both in user_dic)"""
    global data, user_dic
    f = open('Data/original_edge_set.txt', 'w')
    for path1, path2 in path:
        with open(path1, newline='') as followers:
            rows = csv.reader(followers)
            next(rows)
            for i in rows:
                try:
                    l = user_dic[i[0]]
                    ll = user_dic[i[1]]
                    data['edges'].append((i[0], i[1], weight))
                    print(f'{i[0]},{i[1]}', file=f)
                except KeyError:
                    pass
        with open(path2, newline='') as friends:
            rows = csv.reader(friends)
            next(rows)
            for i in rows:
                try:
                    l = user_dic[i[0]]
                    ll = user_dic[i[1]]
                    data['edges'].append((i[0], i[1], weight))
                    print(f'{i[0]},{i[1]}', file=f)
                except KeyError:
                    pass
    """Generate edge to complete the graph"""
    gen_edge = generate_edge(user_data['human']) if method == 'dense' else generate_community_edge(user_data['human'])
    for edge in gen_edge:
        data['edges'].append((edge[0], edge[1], weight))
        print(f'{edge[0]},{edge[1]}', file=f)
    """End"""

    f.close()
    # collect top degree human node
    G = nx.read_edgelist('Data/original_edge_set.txt', delimiter=",")
    top_node = collect_top_node(G)
    user_data['top_node'] = [node[0] for node in top_node]
    print(f'Original {G}')
    print(f'Top 10 human node list = {top_node}')
    return collect_community(G, user_data['human'])


def collect_top_node(graph, top=10):
    degree_list = []
    for node in graph:
        if node in user_data['human']:
            degree_list.append((node, graph.degree(node)))
    degree_list.sort(key=lambda x: x[1], reverse=True)
    return degree_list[:top]


data = {'nodes': [], 'edges': []}
user_data = {'human': [], 'faker': []}
name = ['TFP', 'E13', 'INT', 'FSF', 'TWT']
path_set = ['/Users/bill/Desktop/Fake_project_dataset_csv/TFP.csv/users.csv',
            '/Users/bill/Desktop/Fake_project_dataset_csv/E13.csv/users.csv',
            '/Users/bill/Desktop/Fake_project_dataset_csv/INT.csv/users.csv',
            '/Users/bill/Desktop/Fake_project_dataset_csv/FSF.csv/users.csv',
            '/Users/bill/Desktop/Fake_project_dataset_csv/TWT.csv/users.csv']

user_dic = collect_user(path_set)

edge_path = [('/Users/bill/Desktop/Fake_project_dataset_csv/TFP.csv/followers.csv',
              '/Users/bill/Desktop/Fake_project_dataset_csv/TFP.csv/friends.csv'),
             ('/Users/bill/Desktop/Fake_project_dataset_csv/E13.csv/followers.csv',
              '/Users/bill/Desktop/Fake_project_dataset_csv/E13.csv/friends.csv'),
             ('/Users/bill/Desktop/Fake_project_dataset_csv/INT.csv/followers.csv',
              '/Users/bill/Desktop/Fake_project_dataset_csv/INT.csv/friends.csv'),
             ('/Users/bill/Desktop/Fake_project_dataset_csv/FSF.csv/followers.csv',
              '/Users/bill/Desktop/Fake_project_dataset_csv/FSF.csv/friends.csv'),
             ('/Users/bill/Desktop/Fake_project_dataset_csv/TWT.csv/followers.csv',
              '/Users/bill/Desktop/Fake_project_dataset_csv/TWT.csv/friends.csv')]
community_data = collect_edge(edge_path, method='community')

with open('Data/graph_data.json', 'w') as f1:
    f1.write(json.dumps(data))

with open('Data/user_data.json', 'w') as f2:
    f2.write(json.dumps(user_data))

with open('Data/community_data.json', 'w') as f3:
    f3.write(json.dumps(community_data))

print(f"Number of human node = {len(user_data['human'])}")
print(f"Number of faker node = {len(user_data['faker'])}")
print(f"Number of edge = {len(data['edges'])}")


