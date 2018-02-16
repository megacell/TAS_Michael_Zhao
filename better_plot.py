from __future__ import division
import numpy as np
import argparse
from process_data import process_net, process_trips, extract_features, process_links, process_node, \
    geojson_link, construct_igraph, construct_od, join_node_demand, geojson_link_Scenario_Study, process_node_to_GPS_Coord
from frank_wolfe_2 import solver_3
from Social_Optimum import solver_social_optimum
from Demand_Study_HS import total_cost, load_network_data, frank_wolfe_ratio_study
import matplotlib.pyplot as plt
from math import *
from Speed_Util import get_results


###DATA

def get_ttime(name, demand):
    flows=get_results(name, demand)
    azf=np.loadtxt("data/"+name+"_net.csv", skiprows=1, delimiter=',')
    ttimes=[]
    for i in range(0, len(flows)):
        ttimes.append([])
        a0=azf[i][3]
        a4=azf[i][7]
	for j in range (0, int(20*demand)+1):
            traveltimeminut=a0+a4*flows[i][j]**4
            ttimes[i].append(traveltimeminut)
    return ttimes

flows=get_ttime("Toy", 1.5)
top=flows[:5]
mid=[flows[5]]+flows[7:9]
bot=[flows[6]]+flows[9:]

top=[top[0][i]+top[1][i]+top[2][i]+top[3][i]+top[4][i] for i in range(0,len(top[0]))]
mid=[mid[0][i]+mid[1][i]+mid[2][i] for i in range(0,len(mid[0]))]
bot=[bot[0][i]+bot[1][i]+bot[2][i]+bot[3][i]+bot[4][i] for i in range(0,len(bot[0]))]

mini=[4 for i in range(0, 24*3)]
for i in range (14*3+1, 18*3+1):
	mini[i]+=1
mini[17*3]-=1
for i in range(14*3+2,16*3+1):
	mini[i]+=1
maxi=[4 for i in range(0, 24*3)]
for i in range (14*3-1, 19*3+2):
	maxi[i]+=2
for i in range (14*3, 19*3):
	maxi[i]+=1
for i in range (14*3, 19*3-1):
	maxi[i]+=1
for i in range (14*3+1, 18*3+1):
	maxi[i]+=1
for i in range (14*3+2, 17*3+2):
	maxi[i]+=1
maxi[17*3]-=1
for i in range (14*3+1, 16*3+1):
	maxi[i]+=2
maxi[14*3+2]+=2

minn=[12 for i in range(0,24*3)]
minn[20]-=2
minn[0]+=2
minn[1]+=2
minn[17]+=2
for i in range (3,15):
	minn[i]+=2

maxn=[22 for i in range(0,24*3)]
for i in range (45,50):
	maxn[i]+=2
for i in range (17*3+1,18*3+2):
	maxn[i]+=2
for i in range (0,22):
	maxn[i]-=4
for i in range (60,len(maxn)):
	maxn[i]-=4
for i in range (0,20):
	maxn[i]-=2
for i in range (65,len(maxn)):
	maxn[i]-=2
for i in range (0,18):
	maxn[i]-=2
maxn[15]+=2
for i in range (9*3,11*3+2):
	maxn[i]-=2
maxn[39]-=2
maxn[59]-=2
maxn[len(maxn)-1],minn[len(maxn)-1]=14,14

mins=[12 for i in range(0,24*3)]
for i in range (18,34):
	mins[i]-=2
for i in range (46,71):
	mins[i]-=2
mins[41]-=2
mins[42]-=2

maxs=[12 for i in range(0,24*3)]
for i in range(17,len(maxs)-1):
	maxs[i]+=2
for i in range(19,68):
	maxs[i]+=2
maxs[19]+=2
for i in range(21,63):
	maxs[i]+=2
maxs[61]-=2
for i in range(24,59):
	maxs[i]+=2
maxs[27]+=2
for i in range(30,18*3+2):
	maxs[i]+=2
for i in range(32,35):
	maxs[i]-=2
maxs[40]+=2
maxs[41]+=2
maxs[43]+=2
maxs[45]+=2
maxs[46]+=2
maxs[47]+=2
maxs[48]+=2
maxs[49]+=2
maxs[51]+=2
maxs[53]+=2
maxs[54]+=2
maxs[52]+=4

time=[i/3 for i in range(0, len(maxi))]
x=[i for i in range(0,len(maxi))]
demands=[1.25*i for i in range(0, len(bot))]

###PLOT

x_values1=demands
y_values1=top
y_values2=mid
y_values3=bot

x_values2=time
y_values4=maxi
y_values5=mini



#fig=plt.figure()
#ax=fig.add_subplot(111, label="1")
#ax2=fig.add_subplot(111, label="2", frame_on=False)
fig, (ax,ax2)=plt.subplots(1,2, sharey=True)

ax.plot(x_values1, y_values1, color="c",label='North')
ax.set_xlabel("Demand (kVehicles/h)")
ax.set_ylabel("Travel Time (Min)")
#ax.tick_params(axis='x')
#ax.tick_params(axis='y')
ax.plot(x_values1, y_values2, color="r",label='Highway')
ax.plot(x_values1, y_values3, color="y",label='South')
ax.grid(True)
ax.set_title("Travel Time of each Itinerrary at User Equilibrium")
ax.set_xlim(xmax=30)

ax2.fill_between(time,minn, maxn, color='c', alpha=0.5)
ax2.fill_between(time,mins, maxs, color='y', alpha=0.5)
ax2.fill_between(time,y_values5, y_values4, color='r', alpha=0.5)
#ax2.xaxis.tick_top()
#ax2.yaxis.tick_right()
ax2.set_xlabel('Time of the day (h)') 
#ax2.set_ylabel('y label 2')       
#ax2.xaxis.set_label_position('top') 
#ax2.yaxis.set_label_position('right') 
#ax2.tick_params(axis='x')
#ax2.tick_params(axis='y')
ax2.grid(True)
ax2.set_title("Travel Time Forecast by Google Maps")
ax2.set_xlim(xmax=71/3)
#plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
ax.set_ylim(ymax=30)
ax.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
plt.show()
