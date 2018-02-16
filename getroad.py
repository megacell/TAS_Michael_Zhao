from __future__ import division
import argparse
import csv
import numpy as np
from utils import digits, spaces, areInside
from pyproj import Proj, transform
import igraph
import matplotlib.pyplot as plt

def extract_features(input):
    '''features = table in the format [[capacity, length, FreeFlowTime]]'''
    flag = False
    out = []
    with open(input, 'rb') as f:
	reader = csv.reader(f)
        for row in reader:
            if len(row)>0:
                if flag == False:
                    if row[0].split()[0] == '~': flag = True
                else:
                    out.append([float(e) for e in row[0].split()[0:5]])
    return np.array(out)

def find_next_link(node, net):
    outlinks=[]
    for i in range (0, len(net)):
        if net[i][0]==node:
            outlink=np.concatenate([net[i],np.array([i])])
            #print net[i]
            #print i
            #print outlink
            outlinks.append(outlink)
    next_link=0
    capacity=0
    #print outlinks
    for outlink in outlinks:
        if outlink[2]>capacity:
            next_link=int(outlink[-1])
            capacity=outlink[2]
    #print ('next_link: '+str(next_link))
    return next_link

net=extract_features('data/LA_net.txt')  #not sure name
node=13499
links=[]
nodes=np.loadtxt('data/LA_node.csv', delimiter=',')   #not sure bout the name
iteration=0

while nodes[node-1][2]<-117.943260 and iteration<1000:    #might be completely different
    #print ("node: "+str(node))
    next_link=find_next_link(node, net)
    links.append(next_link)
    node=int(net[next_link][1])
    iteration+=1
    #print nodes[node-1]
print links

np.savetxt('data/highway_links.csv',links[:-1])

traveltimes=[]
for i in range (1,99):
    #print i
    #print i/10
    dubflows=np.loadtxt('data/output/New_FW_Heterogeneous_Demand_1/LA_output_ratio_1.0_routed_perc_'+str(i/100)+'.csv', delimiter=',')
    totflows=[link[0]+link[1] for link in dubflows]
    azf=np.loadtxt("data/LA_net.csv", skiprows=1, delimiter=',')
	#lengths=np.loadtxt("data/LA_net.txt", skiprows=7, usecols=(3))
    ttime=0
    for j in links:
        a0=azf[j][3]
        a4=azf[j][7]
		#length=lengths[i]
		#for j in range (0, 20*demand+1):
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        #print traveltimeminut
			#speed=60*length/traveltimeminut
			#speeds[i].append(speed)
        ttime+=traveltimeminut
    traveltimes.append(ttime)
print traveltimes

plt.plot(traveltimes)
plt.show()
