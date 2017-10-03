__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"
'''
This file uses the hybrid model on the LA network.
The network LAfix has been created with another file, it is the LA network with users with demand not interesting to us fixed to their shortest paths
Then, users with interesting demands are plit between routed and non-routed with different ratios (same for all demands)
Non routed are set to their shortest Paths
Routed set themselves to user equilibrium
'''

####Libraries
from __future__ import division
import numpy as np
import argparse
from math import ceil
#Files
from process_data import process_net, process_trips, extract_features, process_links, process_node, \
    geojson_link, construct_igraph, construct_od, join_node_demand, geojson_link_Scenario_Study, process_node_to_GPS_Coord
from frank_wolfe_heterogeneous import fw_heterogeneous_1,fw_heterogeneous_2
from Social_Optimum import solver_social_optimum
from AoN_igraph import all_or_nothing
from frank_wolfe_2 import total_free_flow_cost, search_direction, line_search, solver_3
from process_data import construct_igraph, construct_od
from utils import multiply_cognitive_cost, heterogeneous_demand
from heterogeneous_construct import toy_heterogeneous, LAfix_heterogeneous

###code

#Extract Data
nodes = np.loadtxt('data/LA_node.csv', delimiter=',')
links = np.loadtxt('data/LA_net.csv', delimiter=',', skiprows=1)
flows= np.loadtxt('data/flow_allocation.csv', delimiter=',', skiprows=1)
flows[:,1]=flows[:,1]/4000                     #The usual /4000
flauws= np.loadtxt('data/flow_allocation_non_users.csv', delimiter=',', skiprows=1)
flauws[:,1]=flauws[:,1]/4000

#Step of 1% from 0 to 100%
for j in range(0,101):
    print  j
    lounch=np.copy(links)
    demand=np.loadtxt('data/LAfix_od.csv',skiprows=1, delimiter=',')
    demand[:,2]=(j/100)*demand[:,2] /4000   #Routed demand
    for i in range(0,len(links)):
        a0=lounch[i][3]
        a4=lounch[i][7]
        f=flows[i][1]+(1-j/100)*flauws[i][1]    #Flows from other OD pairs and nonrouted users
        p=[a0+a4*f**4, a4*4*f**3, 6*a4*f**2, 4*a4*f, a4]
        lounch[i][3:]=p
    frank=solver_3(lounch, demand, max_iter=1000, q=50, display=1, stop=1e-2)
    result=[frank[i]+flows[i,1]+(1-j/100)*flauws[i,1] for i in range(0, len(frank))]
    name='data/output/LAfix_output_ratio_1_perc_'+str(j/100)+'.csv'
    np.savetxt(name, result , delimiter=',')
