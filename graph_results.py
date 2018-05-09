import cPickle as pickle
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn

from AoN_igraph import all_or_nothing
from frank_wolfe_2 import search_direction
from process_data import construct_igraph, construct_od, extract_features, process_links, geojson_link

import time

from collections import defaultdict

plt.style.use("seaborn-darkgrid")

start_time = time.time()

compile_od_data = True
# number of percentage points we love at, (x+1) means we look at every 100/x percent
granularity = 21
# folder with input path flow, link flow data
in_folder = 'max_iters_100'
# calculate nash distance for each run (needed when my earlier implementations didn't return nash distance from frank-wolfe algorithm)
calculate_nd = False
# whether or not to produce jsons for the dashboard
make_dash_data = False
# whether or not to produce graphs
graph = False
# whether or not to plot specific graphs
graph_path_flow_vs_app_usage = True
graph_travel_time_vs_app_usage = True
graph_total_path_flow_vs_app_usage = True

# compile path flow data into single file focused on one OD pair
if compile_od_data:
    graph = np.loadtxt("data/LA_net.csv", skiprows=1, delimiter=',')
    graph[10787,-1] = graph[10787,-1] / (1.5**4)
    graph[3348,-1] = graph[3348,-1] / (1.2**4)
    demand = np.loadtxt('data/LA_od_2.csv', delimiter=',', skiprows=1)
    demand[:,2] = 0.5*demand[:,2] / 4000
    # most_demand = np.argmax(demand[:, 2])
    od = construct_od(demand)

    # sort ODs based demand
    argsorted = np.argsort(demand[:, 2])
    # print 'most_demand', argsorted[-1]

    # pick an OD to aggregate path data on, -1 is highest demand
    sorted_od = demand[argsorted[-3]]

    # nash distances
    nds = []
    # path flows for app users
    path_flows_x = defaultdict(lambda : np.array([0. for _ in range(granularity)]))
    # path flows for non app users
    path_flows_y = defaultdict(lambda : np.array([0. for _ in range(granularity)]))
    # path flows for all users
    path_flows_total = defaultdict(lambda : np.array([0. for _ in range(granularity)]))
    # link travel times
    tts = []

    # used to keep track of iteration for indexing in path_flow_* default dicts
    index = 0
    for alpha in np.linspace(0, 1, granularity):
        with open('{}/LA_net_od_2_alpha_{}.txt'.format(in_folder, alpha), 'r') as infile:
            run = pickle.loads(infile.read())

        fs = run['f']
        f = np.array([l[0] + l[1] for l in fs])
        tt = (graph[:, 3] + graph[:, 7] * f**4) / 60

        tts += [tt]

        if calculate_nd:
            g = construct_igraph(graph)
            L, grad, path_flows = search_direction(f, graph, g, od)
            nd = np.dot(tt, f-L)
            nds += [nd]
            print nd

        # produce OD data json needed for dashboard
        if make_dash_data:
            od_paths = {}
            od2id = {}
            path2id = {}

            for k in run['h'].keys():
                odp = (k[0], k[1])
                if odp not in od2id:
                    od2id[odp] = len(od2id)
                if od2id[odp] not in od_paths:
                    od_paths[od2id[odp]] = {
                        'O': k[0],
                        'D': k[1],
                        'app_user_path_flow': [],
                        'non_app_user_path_flow': [],
                    }
                if k[2] not in path2id:
                    path2id[k[2]] = len(path2id)
                if k[3] == 0:
                    od_paths[od2id[odp]]['app_user_path_flow'] += [{
                        'links': path2id[k[2]],
                        'flow': run['h'][k],
                    }]
                else:
                    od_paths[od2id[odp]]['non_app_user_path_flow'] += [{
                        'links': path2id[k[2]],
                        'flow': run['h'][k],
                    }]
            for odid in od_paths:
                # print 'before', len(od_paths[odid]['app_user_path_flow']), len(od_paths[odid]['non_app_user_path_flow'])
                od_paths[odid]['app_user_path_flow'] = sorted(od_paths[odid]['app_user_path_flow'], key=lambda p: p['flow'])[-5:]
                od_paths[odid]['non_app_user_path_flow'] = sorted(od_paths[odid]['non_app_user_path_flow'], key=lambda p: p['flow'])[-5:]
                # print 'after', len(od_paths[odid]['app_user_path_flow']), len(od_paths[odid]['non_app_user_path_flow'])
            with open('json/od_{}.json'.format(alpha), 'w') as f:
                json.dump(od_paths, f, indent=None)

        # put paths in proper path_flows_* dict
        for k in run['h'].keys():
            if k[0] == sorted_od[0] and k[1] == sorted_od[1]:
                # k[3]: 0 means app user, and 1 means non app user
                if k[3] == 0:
                    path_flows_x[k[2]][index] = run['h'][k]
                elif k[3] == 1:
                    path_flows_y[k[2]][index] = run['h'][k]
                path_flows_total[k[2]][index] += run['h'][k]

        index += 1
        print 'alpha {}: {} sec'.format(alpha, time.time() - start_time)

    # sort all path flows by descending path flow
    sorted_path_flows_x = sorted(path_flows_x.items(), key=lambda p: max(p[1]))[::-1]
    sorted_path_flows_y = sorted(path_flows_y.items(), key=lambda p: max(p[1]))[::-1]
    sorted_path_flows_total = sorted(path_flows_total.items(), key=lambda p: max(p[1]))[::-1]

    path_flows = {
        'x': sorted_path_flows_x,
        'y': sorted_path_flows_y,
        't': sorted_path_flows_total
    }

    with open('path_flows.pkl', 'w') as outfile:
        outfile.write(pickle.dumps((path_flows, tts, nds)))

if graph:
    with open('path_flows.pkl', 'r') as infile:
        path_flows, tts, nds = pickle.loads(infile.read())

    # max number of app user or non app user paths to consider
    paths = 5

    # sum of all path flows for this OD pair at each percentage point for app users (x) and non app users (y)
    total_pfs_x = np.zeros((21,))
    total_pfs_y = np.zeros((21,))

    # colors to user
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    color_index = 0

    # dict for keeping paths color consistent
    path2color = {}

    for i in range(len(path_flows['x'])):
        total_pfs_x += np.array(path_flows['x'][i][1])
    for i in range(len(path_flows['y'])):
        total_pfs_y += np.array(path_flows['y'][i][1])

    # simple function to create unique but deterministic identifier for path based on links
    def hash_path(path):
        h = 1
        for l in path:
            h = (h * l + 5) % 997
        return h

    if graph_path_flow_vs_app_usage:
        plt.figure(figsize=[10, 5])
        plt.ylabel('App User Percentage Path Flow')
        plt.xlabel('App Usage (%)')
        for i in range(min(paths, len(path_flows['x']))):
            if path_flows['x'][i][0] not in path2color:
                path2color[path_flows['x'][i][0]] = colors[color_index]
                color_index += 1
                if color_index >= len(colors):
                    print 'ran out of colors'
                    exit(-1)
            plt.plot(np.linspace(.05, 1, 20), np.divide(path_flows['x'][i][1], np.maximum(total_pfs_x, 1e-15))[1:], label='Path {}'.format(hash_path(path_flows['x'][i][0])), color=path2color[path_flows['x'][i][0]])
        plt.legend()
        plt.savefig('app_user_path_flow.png')
        plt.show()

        plt.figure(figsize=[10, 5])
        plt.ylabel('Nonapp User Percentage Path Flow')
        plt.xlabel('App Usage (%)')
        for i in range(min(paths, len(path_flows['y']))):
            if path_flows['y'][i][0] not in path2color:
                path2color[path_flows['y'][i][0]] = colors[color_index]
                color_index += 1
                if color_index >= len(colors):
                    print 'ran out of colors'
                    exit(-1)
            plt.plot(np.linspace(0, .95, 20), np.divide(path_flows['y'][i][1], np.maximum(total_pfs_y, 1e-15))[:-1], label='Path {}'.format(hash_path(path_flows['y'][i][0])), color=path2color[path_flows['y'][i][0]])
        plt.legend()
        plt.savefig('nonapp_user_path_flow.png')
        plt.show()


    if graph_travel_time_vs_app_usage:
        plt.figure(figsize=[10, 5])
        plt.ylabel('Path Travel Time (min)')
        plt.xlabel('App Usage (%)')
        for i in range(min(paths, len(path_flows['x']))):
            # if i >= 3:
            #     continue
            if path_flows['x'][i][0] not in path2color:
                path2color[path_flows['x'][i][0]] = colors[color_index]
                color_index += 1
                if color_index >= len(colors):
                    print 'ran out of colors'
                    exit(-1)
            plt.plot(np.linspace(.05, 1, 20), [sum([tts[r][l] for l in path_flows['x'][i][0]]) for r in range(21)][1:], label='Path {}'.format(hash_path(path_flows['x'][i][0])), color=path2color[path_flows['x'][i][0]])
        plt.legend()
        plt.savefig('app_user_path_tt.png')
        plt.show()

        plt.figure(figsize=[10, 5])
        plt.ylabel('Path Travel Time (min)')
        plt.xlabel('App Usage (%)')
        for i in range(min(paths, len(path_flows['y']))):
            if path_flows['y'][i][0] not in path2color:
                path2color[path_flows['y'][i][0]] = colors[color_index]
                color_index += 1
                if color_index >= len(colors):
                    print 'ran out of colors'
                    exit(-1)
            plt.plot(np.linspace(0, .95, 20), [sum([tts[r][l] for l in path_flows['y'][i][0]]) for r in range(21)][:-1], label='Travel Time {}'.format(hash_path(path_flows['y'][i][0])), color=path2color[path_flows['y'][i][0]])
        plt.legend()
        plt.savefig('nonapp_user_path_tt.png')
        plt.show()

    if graph_total_path_flow_vs_app_usage:
        plt.figure(figsize=[10, 5])
        plt.ylabel('Total Path Flow')
        plt.xlabel('App Usage (%)')
        for i in range(min(paths, len(path_flows['t']))):
            if path_flows['t'][i][0] not in path2color:
                path2color[path_flows['t'][i][0]] = colors[color_index]
                color_index += 1
                if color_index >= len(colors):
                    print 'ran out of colors'
                    exit(-1)
            plt.plot(np.linspace(0, 1, 21), path_flows['t'][i][1], label='Path {}'.format(hash_path(path_flows['t'][i][0])), color=path2color[path_flows['t'][i][0]])
        plt.legend()
        plt.savefig('total_path_flow.png')
        plt.show()
