__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

'''
This is another way of computing the hybrid model on LA
Unfortunately, it gives the same, bad results
'''

###Libraries
from __future__ import division
import numpy as np
import argparse
from math import ceil
#Functions
from process_data import process_net, process_trips, extract_features, process_links, process_node, \
    geojson_link, construct_igraph, construct_od, join_node_demand, geojson_link_Scenario_Study, process_node_to_GPS_Coord
from frank_wolfe_heterogeneous import fw_heterogeneous_1,fw_heterogeneous_2
from Social_Optimum import solver_social_optimum
from AoN_igraph import all_or_nothing
from frank_wolfe_2 import total_free_flow_cost, search_direction, line_search, solver_3
from process_data import construct_igraph, construct_od
from utils import multiply_cognitive_cost, heterogeneous_demand
from heterogeneous_construct import toy_heterogeneous, LAfix_heterogeneous

###Code

#Extract Data
nodes = np.loadtxt('data/iod_node.csv', delimiter=',', skiprows=1)
links = np.loadtxt('data/iod_net.csv', delimiter=',', skiprows=1)
flows= np.loadtxt('data/flow_allocation.csv', delimiter=',', skiprows=1)
flauws= np.loadtxt('data/flow_allocation_non_users.csv', delimiter=',', skiprows=1)

#Usual /4000 division because 'flow_allocation' has been computed with another algorithm
for i in range(0, len(flows)):
    flows[i,1]=flows[i,1]/4000
for i in range(0, len(flauws)):
    flauws[i,1]=flauws[i,1]/4000

#results output
for j in range(1,101):   #From 0 to 100% with a step of 1%
    print  j
    lounch=np.copy(links)
    demand=np.loadtxt('data/LAfix_od.csv',skiprows=1, delimiter=',')
    for d in demand:
        d[2]=(j/100)*d[2] /4000
    for link in lounch:
        i=int(link[0])
        a0=link[3]
        a4=link[7]
        f=flows[i][1]+(1-j/100)*flauws[i][1]
        p=[a0+a4*(f**4), a4*4*(f**3), 6*a4*(f**2), 4*a4*f, a4]
        link[3:8]=p
    for i in range(0, len(lounch)):
        lounch[i][0]=i
    frank=solver_3(lounch, demand, max_iter=1000, q=50, display=1, stop=1e-2)
    fritz=[0]*(len(flows))
    for i in range(0, len(frank)):
        link=int(links[i][0])
        fritz[link]=frank[i]
    result=[fritz[i]+flows[i,1]+(1-j/100)*flauws[i,1] for i in range(0, len(fritz))]
    name='data/output/iod_output_ratio_1_perc_'+str(j/100)+'.csv
    np.savetxt(name, result , delimiter=',')
