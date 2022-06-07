from utils import *
from SybilRank import SybilRank
from Integro import Integro
import random
import networkx as nx
import time
import matplotlib.pyplot as plt



def main(start_time, se, am):
    c = load_config("config.json")
    graph = load_graph(c['graph_file'], c['user_file'], c['trust_score'],
                       c['select_from_top'], c['total_select'], c['attack_num'], seed_select=se, attack_method=am)
    ranker = SybilRank(graph)
    ranker.rank(start_time)

    return ranker


def main2(start_time, se, am):
    c = load_config("config.json")
    graph = load_graph(c['graph_file'], c['user_file'], c['trust_score'],
                       c['select_from_top'], c['total_select'], c['attack_num'], seed_select=se, attack_method=am)
    ranker = Integro(graph)
    ranker.classify_potential_victim('Data/new_potential_victim.csv')
    ranker.rank(start_time)

    return ranker


def log_output_graph(output_graph, algo):
    user_score = {}
    score_list = []
    for node in output_graph.graph:
        # name : [score, type, predict_type]
        user_score[node.name] = [node.rank, node.node_type]
        score_list.append(node.rank)
    c = sorted(score_list)[int(len(score_list)*critical_value)]
    print(f'{algo} Critical value is {score_list[int(len(score_list)*critical_value)]}')
    for key in user_score.keys():
        predict = 'human' if user_score[key][0] > c else 'faker'
        user_score[key].append(predict)

    return user_score


def plot(graph):
    t = list()
    r = list()
    for i in graph.graph:
        r.append(i.rank)
        t.append(i.node_type)
    plt.scatter(t, r)
    plt.show()
    return


if __name__ == "__main__":
    critical_value = 0.5
    random.seed(123)
    seed_select = 2
    attack_method = 3

    start = time.time()
    G1 = main(start, seed_select, attack_method)
    print(f'Total spending time {time.time() - start}')
    user_score1 = log_output_graph(G1, 'SybilRank')
    plot(G1)


    start = time.time()
    G2 = main2(start, 3, attack_method)
    print(f'Total spending time {time.time() - start}')
    user_score2 = log_output_graph(G2, 'Integro')
    plot(G2)



    with open('predict_user1.json', 'w') as f1:
        f1.write(json.dumps(user_score1))


    with open('predict_user2.json', 'w') as f2:
        f2.write(json.dumps(user_score2))