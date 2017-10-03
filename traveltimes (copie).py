from __future__ import division
import argparse
import csv
import numpy as np
from utils import digits, spaces, areInside
from pyproj import Proj, transform
import igraph
import matplotlib.pyplot as plt
from math import *

highway=np.loadtxt('data/highway_links.csv')
dev1=np.loadtxt('data/Paths/Green_South.csv', delimiter=',')
dev2=np.loadtxt('data/Paths/Yellow_All.csv', delimiter=',')
dev3=np.loadtxt('data/Paths/Path1.csv', delimiter=',')
dev4=np.loadtxt('data/Paths/Path2.csv', delimiter=',')
dev5=np.loadtxt('data/Paths/Path3.csv', delimiter=',')

azf=np.loadtxt("data/LA_net.csv", skiprows=1, delimiter=',')

traveltimes=[]
td1=[]
td4=[]
td3=[]
td2=[]
td5=[]

sraveltimes=[]
sd1=[]
sd4=[]
sd3=[]
sd2=[]
sd5=[]
for i in range (1,101):
    #print i
    #print i/10
        ###SHORTEST PATH
    #dubflows=np.loadtxt('data/output/LAfix_output_ratio_1_routed_perc_'+str(i/100)+'.csv', delimiter=',')
    dubflows=np.loadtxt('data/output/New_FW_Heterogeneous_Demand_1/LA_output_ratio_1.0_routed_perc_'+str(i/100)+'.csv', delimiter=',')

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
    ttime=0
    for j in dev3:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    td3.append(ttime)
    ttime=0
    for j in dev4:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    td4.append(ttime)
    ttime=0
    for j in dev5:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    td5.append(ttime)


    #if (i/5)==floor(i/5):

            ###WHOLE NETWORK
    #dubflows=np.loadtxt('data/output/FW_Heterogeneous_Demand_1/LA_output_ratio_1.0_routed_perc_'+str(i/100)+'.csv', delimiter=',')
    #totflows=np.loadtxt('data/output/iod_output_ratio_1_perc_'+str(i/100)+'.csv', delimiter=',')
    totflows=np.loadtxt('data/output/LAfix_output_ratio_1_perc_'+str(i/100)+'.csv', delimiter=',')
    #totflows=[link[0]+link[1] for link in dubflows]
    ttime=0
    for j in highway:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    sraveltimes.append(ttime)
    ttime=0
    for j in dev1:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    sd1.append(ttime)
    ttime=0
    for j in dev2:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    sd2.append(ttime)
    ttime=0
    for j in dev3:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    sd3.append(ttime)
    ttime=0
    for j in dev4:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    sd4.append(ttime)
    ttime=0
    for j in dev5:
        j=int(j)
        a0=azf[j][3]
        a4=azf[j][7]
        traveltimeminut=(a0+a4*totflows[j]**4)/60
        ttime+=traveltimeminut
    sd5.append(ttime)

nu=np.loadtxt('data/output/Travel_time_equalization.csv', skiprows=1, delimiter=',',usecols=3)


#fig,(g1, g2)= plt.subplots(1,2, sharey=True)
a, g1=plt.subplots(1,1)
g1.plot(traveltimes, c="r", label="I210")
g1.plot(td1, c="g", label="2")
g1.plot(td2, c="cyan", label="1")
g1.plot(td3, c="darkblue", label="1a")
g1.plot(td4, c="violet", label="1b")
g1.plot(td5, c="turquoise", label="1c")
g1.plot(nu, c='black', lw=2, label="Shortest Path")

g1.legend()
g1.grid(True)
g1.set_xlabel('Percentage of Routed Users (%)')
g1.set_ylabel('Travel Time (min)')

#g2.plot(sraveltimes, c="r")
#g2.plot(sd1, c="g")
#g2.plot(sd2, c="y")
#g2.plot(sd3, c="b")
#g2.plot(sd4, c="pink")
#g2.plot(sd5, c="brown")

#g2.grid(True)
#g2.set_xlabel('Percentage of Routed Users (%)')
#g2.set_ylabel('Travel Time (min)')

plt.show()
