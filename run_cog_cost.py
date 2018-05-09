import numpy as np
from process_data import extract_features
from utils import multiply_cognitive_cost, heterogeneous_demand
from frank_wolfe_heterogeneous import fw_heterogeneous_1
import cPickle as pickle

#Profiling the code
import timeit
from collections import defaultdict


for alpha in np.linspace(0, 1, 101):
    print "ALPHA:", alpha
    start_time = timeit.default_timer()

    graph = np.loadtxt('data/LA_net.csv', delimiter=',', skiprows=1)
    demand = np.loadtxt('data/LA_od_2.csv', delimiter=',', skiprows=1)
    graph[10787,-1] = graph[10787,-1] / (1.5**4)
    graph[3348,-1] = graph[3348,-1] / (1.2**4)
    node = np.loadtxt('data/LA_node.csv', delimiter=',')
    features = extract_features('data/LA_net.txt')

    # graph = np.loadtxt('data/Chicago_net.csv', delimiter=',', skiprows=1)
    # demand = np.loadtxt('data/Chicago_od.csv', delimiter=',', skiprows=1)
    # node = np.loadtxt('data/Chicago_node.csv', delimiter=',', skiprows=1)
    # features = extract_features('data/ChicagoSketch_net.txt')

    # features = table in the format [[capacity, length, FreeFlowTime]]

    # alpha = .2 # also known as r
    thres = 1000.
    cog_cost = 3000.

    demand[:,2] = 0.5*demand[:,2] / 4000
    g_nr, small_capacity = multiply_cognitive_cost(graph, features, thres, cog_cost)
    d_nr, d_r = heterogeneous_demand(demand, alpha)
    fs, hs, n_d = fw_heterogeneous_1([graph, g_nr], [d_r,d_nr], alpha, max_iter=30, display=1)
    # print n_d

    output = {
        'f': fs,
        'h': hs,
        'n_d': n_d
    }

    with open('graph_stuff/LA_net_od_2_alpha_{}.txt'.format(alpha), 'w') as outfile:
    # with open('graph_stuff/Chicago_net_od_2_alpha_{}.txt'.format(alpha), 'w') as outfile:
        outfile.write(pickle.dumps(output))

    #end of timer
    elapsed = timeit.default_timer() - start_time

    print ("Execution took %s seconds" % elapsed)