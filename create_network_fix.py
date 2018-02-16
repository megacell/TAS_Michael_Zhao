__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

'''
This file creates the network LAfix, which is the LA network on which the flow of flow_allocation is added
'''

###Libraries
import argparse
import csv
import numpy as np
import igraph
from pyproj import Proj, transform

###Files
from utils import digits, spaces, areInside
from process_data import extract_features

###Code

#LAfix_node.csv
nodes = np.loadtxt('data/LA_node.csv', delimiter=',')
np.savetxt('data/LAfix_node.csv', nodes, delimiter=',', header='node,lat,lon', comments='')

#LAfix_net.csv
links = np.loadtxt('data/LA_net.csv', delimiter=',', skiprows=1)
flows= np.loadtxt('data/flow_allocation.csv', delimiter=',', skiprows=1)
for i in range(0,len(links)):
    a0=links[i][3]
    a4=links[i][7]
    f=flows[i][1]/4000
    p=[a0+a4*f**4, a4*4*f**3, 6*a4*f**2, 4*a4*f, a4]
    links[i][3:]=p
np.savetxt('data/LAfix_net.csv', links, delimiter=',', header='LINK,O,D,a0,a1,a2,a3,a4', comments='')
