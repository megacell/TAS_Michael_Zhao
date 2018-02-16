__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

'''
From the La network, create the network iod which is just a subnetwork conaining only nodes and arc in the rectangle defined by the coordinates
'''

#Libraries
import argparse
import csv
import numpy as np
import igraph
from pyproj import Proj, transform
#Files
from utils import digits, spaces, areInside
from process_data import extract_features

#Select Nodes
nodes = np.loadtxt('data/LA_node.csv', delimiter=',')
ondes=[]
spnd=14617*[[0,0,0]]
for i  in range(0,len(nodes)):
    if nodes[i][1]<34.248503 and nodes[i][1]>34.108762 and nodes[i][2]>-118.271624 and nodes[i][2]<-117.692782:
        ondes.append(nodes[i])
        spnd[i]=nodes[i]
np.savetxt('data/iod_node.csv', spnd, delimiter=',', header='node,lat,lon', comments='')                         #Node ID is equal to node index: the file is sparse
np.savetxt('data/iod_node_dense.csv', ondes, delimiter=',', header='node,lat,lon', comments='')                  #The file is densified and there are no blank lines
nodes=[el[0] for el in ondes]

#Select Links
links = np.loadtxt('data/LA_net.csv', delimiter=',', skiprows=1)
features = extract_features('data/LA_net.txt')
lniks=[]
faetures=[]
for i in range(0,len(links)):
    if links[i][1] in nodes and links[i][2] in nodes:                       #Check if both nodes of the link are in the zone
        lniks.append(links[i])
        arr=np.concatenate((np.array([0,0]),features[i]))
        faetures.append(arr)
np.savetxt('data/iod_net.csv', lniks, delimiter=',', header='LINK,O,D,a0,a1,a2,a3,a4', comments='')
np.savetxt('data/iod_net.txt', faetures, delimiter='\t', header ='~',comments='')
