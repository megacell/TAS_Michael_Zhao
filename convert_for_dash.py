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

start_time = time.time()

# whether or not to make link to lat/lng coordinate json file
make_link2coord = False


net = 'la'
# net = 'chicago'

# PUT ALL DATA IN A FOLDER NAMED 'dash_data_la' or 'dash_data_chicago'
dash_data = 'dash_data_{}'.format(net)
# Output will be put into 'dash_100_json_la' or 'dash_100_json_chicago'
out_data = 'dash_100_json_{}'.format(net)

if net == 'la':
    prefix = 'LA'

    graph = np.loadtxt("data/LA_net.csv", skiprows=1, delimiter=',')
    graph[10787,-1] = graph[10787,-1] / (1.5**4)
    graph[3348,-1] = graph[3348,-1] / (1.2**4)
    demand = np.loadtxt('data/LA_od_2.csv', delimiter=',', skiprows=1)
    demand[:,2] = 0.5*demand[:,2] / 4000
    od = construct_od(demand)

elif net == 'chicago':
    prefix = 'Chicago'

    graph = np.loadtxt("data/Chicago_net.csv", skiprows=1, delimiter=',')
    demand = np.loadtxt('data/Chicago_od.csv', delimiter=',', skiprows=1)
    demand[:,2] = 0.5*demand[:,2] / 4000
    od = construct_od(demand)

# make link to lat/lng coordinate json file
if make_link2coord:
    with open('{}/{}_net_od_2_alpha_0.{:02d}.txt'.format(dash_data, prefix, 50), 'r') as infile:
        run = pickle.loads(infile.read())
    fs = run['f']
    f = np.array([l[0] + l[1] for l in fs])
    if net == 'la':
        node = np.loadtxt('data/LA_node.csv', delimiter=',')
        features = np.zeros((f.shape[0], 4))
        features[:,:3] = extract_features('data/LA_net.txt')
    elif net == 'chicago':
        node = np.loadtxt('data/Chicago_node.csv', delimiter=',', skiprows=1)
        features = np.zeros((f.shape[0], 4))
        features[:,:3] = extract_features('data/ChicagoSketch_net.txt')
    f = np.divide(f*4000, features[:,0])
    features[:,3] = f
    links = process_links(graph, node, features, in_order=True)

    link2coord = {}
    for i in range(len(links)):
        link2coord[i] = {
            'origin': [links[i, 0], links[i, 1]],
            'destination': [links[i, 2], links[i, 3]],
        }
    with open('{}/link_coord.json'.format(out_data), 'w') as f:
        json.dump(link2coord, f, indent=0)

nds = []
index = 0
path2id = {}
id2path = {}
for alpha in range(0, 100):
    with open('{}/{}_net_od_2_alpha_0.{:02d}.txt'.format(dash_data, prefix, alpha), 'r') as infile:
        run = pickle.loads(infile.read())

    fs = run['f']
    f = np.array([l[0] + l[1] for l in fs])
    tt = (graph[:, 3] + graph[:, 7] * f**4) / 60

    # # make link to both flow json
    link2flow = {}
    for i in range(len(fs)):
      link2flow[i] = {
          'app_usr_flow': fs[i][0],
          'non_app_usr_flow': fs[i][1],
          'travel_time': tt[i]
      }
    with open('{}/link_flow/link_flow_0.{:02d}.json'.format(out_data, alpha), 'w') as f:
        json.dump(link2flow, f, indent=0)

    # # get nash distance
    g = construct_igraph(graph)
    L, grad, path_flows = search_direction(f, graph, g, od)
    nd = np.dot(tt, f-L)
    nds += [nd]
    # print 'alpha {}:'.format(alpha), nds
    # continue

    # make od to paths and path to links jsons
    od_paths = {}
    od2id = {}

    for k in run['h'].keys():
        # if run['h'][k] == 0:
        #     continue
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
            index = len(path2id)
            path2id[k[2]] = index
            id2path[index] = k[2]
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
    # for odid in od_paths:
    #     # print 'before', len(od_paths[odid]['app_user_path_flow']), len(od_paths[odid]['non_app_user_path_flow'])
    #     od_paths[odid]['app_user_path_flow'] = sorted(od_paths[odid]['app_user_path_flow'], key=lambda p: p['flow'])[-5:]
    #     od_paths[odid]['non_app_user_path_flow'] = sorted(od_paths[odid]['non_app_user_path_flow'], key=lambda p: p['flow'])[-5:]
    #     # print 'after', len(od_paths[odid]['app_user_path_flow']), len(od_paths[odid]['non_app_user_path_flow'])

    with open('{}/od/od_0.{:02d}.json'.format(out_data, alpha), 'w') as f:
        json.dump(od_paths, f, indent=0)

    # with open('{}/od/od_1.00.json'.format(out_data), 'w') as f:
        # json.dump(od_paths, f, indent=0)

    print 'alpha {}: {} sec'.format(alpha, time.time() - start_time)
    # print len(path2id), len(id2path), max(path2id.values())
    # break
with open('{}/path_info.json'.format(out_data), 'w') as f:
    json.dump(id2path, f, indent=0)






