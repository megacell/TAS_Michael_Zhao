__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

'''
Same principle as traveltimes, compute travel times for different paths and plot them
The method to compute flow data is not the same
Paths are not the Same
This is the one used for the TRB paper
'''

###Libraries
from __future__ import division
import argparse
import csv
import numpy as np
import igraph
import matplotlib.pyplot as plt
from math import *
#Functions
from utils import digits, spaces, areInside
from pyproj import Proj, transform

#Extract Paths
highway=np.loadtxt('data/highway_links.csv')
dev1=np.loadtxt('data/Paths/Green_South.csv', delimiter=',')
dev2=np.loadtxt('data/Paths/Yellow_All.csv', delimiter=',')


azf=np.loadtxt("data/LA_net.csv", skiprows=1, delimiter=',')

traveltimes=[]
td1=[]
td2=[]

###Compute travel times on paths
tflows= np.loadtxt('data/flow_allocation.csv', delimiter=',', skiprows=1)
for i in range (1,101):
    #print i
    #print i/10
        ###SHORTEST PATH
    #dubflows=np.loadtxt('data/output/LAfix_output_ratio_1_routed_perc_'+str(i/100)+'.csv', delimiter=',')                #same, uncomment the one you want
    dubflows=np.loadtxt('data/output/New_FW_Heterogeneous_Demand_1/LA_output_ratio_1.0_routed_perc_'+str(i/100)+'.csv', delimiter=',')


    #totflows=[dubflows[i][0]+dubflows[i][1]+(tflows[i][1]/4000) for i in range(0,len(dubflows))]
    totflows=[link[0]+link[1] for link in dubflows]
    ttime=0
    for j in highway:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    traveltimes.append(ttime)
    ttime=0
    for j in dev1:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    td1.append(ttime)
    ttime=0
    for j in dev2:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    td2.append(ttime)




#This is data collected another way, to show the equalization in travel times
nu=np.loadtxt('data/output/Travel_time_equalization.csv', skiprows=1, delimiter=',',usecols=4)
u=np.loadtxt('data/output/Travel_time_equalization.csv', skiprows=1, delimiter=',',usecols=3)

#########plot

#g1 represents the paths, g2 the equalization

fig,(g1, g2)= plt.subplots(1,2, sharey=True)
#a, g1=plt.subplots(1,1)
g1.plot(traveltimes, c="r", label="I-210", lw=2)
g1.plot(td1, c="lightgreen", label="Path 2", lw=2)
g1.plot(td2, c="purple", label="Path 1", lw=2)

g2.plot(nu, c='r', lw=2, label="Non-Routed Users")
g2.plot(u, c='turquoise', lw=2, label="Routed Users")

g1.legend()
g1.grid(True)
g2.legend()
g2.grid(True)
g1.set_xlabel('Percentage of Routed Users (%)')
g1.set_ylabel('Travel Time (min)')


g2.set_xlabel('Percentage of Routed Users (%)')
g2.set_ylabel('Travel Time (min)')

plt.show()
