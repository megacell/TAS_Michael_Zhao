__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

'''
'''

###Libraries
from __future__ import division
import numpy as np
import argparse
import matplotlib.pyplot as plt
from math import *

###Files
from process_data import process_net, process_trips, extract_features, process_links, process_node, \
    geojson_link, construct_igraph, construct_od, join_node_demand, geojson_link_Scenario_Study, process_node_to_GPS_Coord
from frank_wolfe_2 import solver_3
from Social_Optimum import solver_social_optimum
from Demand_Study_HS import total_cost, load_network_data, frank_wolfe_ratio_study
from Speed_Util import get_results_h

###Definitions
def get_ttime(name, demand):
    '''
    Computes travel times for all links of the network for different demands (of 'get_results'). For Toy, also computes flow on the three paths
    input/name (string) name of the network
    input/demand (float) max demand ratio
    output/ttimes ([[float]]) travel times on each link (rows) for each demand (columns)
    output/h ([float]) flow on highway of Toy network for 20 different demands
    output/n ([float]) flow on north arterial of Toy network for 20 different demands
    output/s ([float]) flow on south arterial of Toy network for 20 different demands
    '''
    r, nr=get_results_h(name, demand)
    h=[]
    n=[]
    s=[]
    flows=[[r[i][j]+nr[i][j] for j in range(0,len(r[i]))] for i in range(0,len(r))]
    for i in range(0, len(flows[0])):
        h.append(20*flows[5][i])
        n.append(20*flows[1][i])
        s.append(20*flows[6][i])
    azf=np.loadtxt("data/"+name+"_net.csv", skiprows=1, delimiter=',')
    ttimes=[]
    for i in range(0, len(flows)):
        ttimes.append([])
        a0=azf[i][3]
        a4=azf[i][7]
	for j in range (0, len(flows[0])):
            traveltimeminut=a0+a4*flows[i][j]**4
            ttimes[i].append(traveltimeminut)
    return ttimes, h, n, s

###Four packs of computations, can be set to comment if not needed

#flows8,r8,nr8=get_ttime("Toy", 0.1)
#top8=flows8[:5]
#mid8=[flows8[5]]+flows8[7:9]
#bot8=[flows8[6]]+flows8[9:]
#top8=[top8[0][i]+top8[1][i]+top8[2][i]+top8[3][i]+top8[4][i] for i in range(0,len(top8[0]))]
#mid8=[mid8[0][i]+mid8[1][i]+mid8[2][i] for i in range(0,len(mid8[0]))]
#bot8=[bot8[0][i]+bot8[1][i]+bot8[2][i]+bot8[3][i]+bot8[4][i] for i in range(0,len(bot8[0]))]
#routed8=[((top8[i])*(r8[0][i])+(mid8[i])*(r8[5][i])+(bot8[i])*(r8[6][i]))/(r8[0][i]+r8[5][i]+r8[6][i]) for i in range(0,len(top8))]
#nrouted8=[(top8[i]*nr8[0][i]+mid8[i]*nr8[5][i]+bot8[i]*nr8[6][i])/(nr8[0][i]+nr8[5][i]+nr8[6][i]) for i in range(0,len(top8))]

#flows9,r9,nr9=get_ttime("Toy", 1.4)
#top9=flows9[:5]
#mid9=[flows9[5]]+flows9[7:9]
#bot9=[flows9[6]]+flows9[9:]
#top9=[top9[0][i]+top9[1][i]+top9[2][i]+top9[3][i]+top9[4][i] for i in range(0,len(top9[0]))]
#mid9=[mid9[0][i]+mid9[1][i]+mid9[2][i] for i in range(0,len(mid9[0]))]
#bot9=[bot9[0][i]+bot9[1][i]+bot9[2][i]+bot9[3][i]+bot9[4][i] for i in range(0,len(bot9[0]))]
#routed9=[(top9[i]*r9[0][i]+mid9[i]*r9[5][i]+bot9[i]*r9[6][i])/(r9[0][i]+r9[5][i]+r9[6][i]) for i in range(0,len(top9))]
#nrouted9=[(top9[i]*nr9[0][i]+mid9[i]*nr9[5][i]+bot9[i]*nr9[6][i])/(nr9[0][i]+nr9[5][i]+nr9[6][i]) for i in range(0,len(top9))]

#flows10,r10,nr10=get_ttime("Toy", 0.95)
#top10=flows10[:5]
#mid10=[flows10[5]]+flows10[7:9]
#bot10=[flows10[6]]+flows10[9:]
#top10=[top10[0][i]+top10[1][i]+top10[2][i]+top10[3][i]+top10[4][i] for i in range(0,len(top10[0]))]
#mid10=[mid10[0][i]+mid10[1][i]+mid10[2][i] for i in range(0,len(mid10[0]))]
#bot10=[bot10[0][i]+bot10[1][i]+bot10[2][i]+bot10[3][i]+bot10[4][i] for i in range(0,len(bot10[0]))]
#routed10=[(top10[i]*r10[0][i]+mid10[i]*r10[5][i]+bot10[i]*r10[6][i])/(r10[0][i]+r10[5][i]+r10[6][i]) for i in range(0,len(top10))]
#nrouted10=[(top10[i]*nr10[0][i]+mid10[i]*nr10[5][i]+bot10[i]*nr10[6][i])/(nr10[0][i]+nr10[5][i]+nr10[6][i]) for i in range(0,len(top10))]

flows11,h, n, s = get_ttime("Toy3", 1)
top11=flows11[:5]
mid11=[flows11[5]]+flows11[7:9]
bot11=[flows11[6]]+flows11[9:]
top11=[top11[0][i]+top11[1][i]+top11[2][i]+top11[3][i]+top11[4][i] for i in range(0,len(top11[0]))]
mid11=[mid11[0][i]+mid11[1][i]+mid11[2][i] for i in range(0,len(mid11[0]))]
bot11=[bot11[0][i]+bot11[1][i]+bot11[2][i]+bot11[3][i]+bot11[4][i] for i in range(0,len(bot11[0]))]
#routed11=[(top11[i]*r11[0][i]+mid11[i]*r11[5][i]+bot11[i]*r11[6][i])/(r11[0][i]+r11[5][i]+r11[6][i]) for i in range(0,len(top11))]
#nrouted11=[(top11[i]*nr11[0][i]+mid11[i]*nr11[5][i]+bot11[i]*nr11[6][i])/(nr11[0][i]+nr11[5][i]+nr11[6][i]) for i in range(0,len(top11))]

percs=[0.1*i for i in range(0, len(bot11))]

####File Output

#fileName1 = 'data/output/Toy_Travel_Times_H_Highway.csv'
#print(fileName1)
#np.savetxt(fileName1, mid11, delimiter=',')
#fileName2 = 'data/output/Toy_Travel_Times_H_South.csv'
#print(fileName2)
#np.savetxt(fileName2, bot11, delimiter=',')
#fileName3 = 'data/output/Toy_Travel_Times_H_North.csv'
#print(fileName3)
#np.savetxt(fileName3, top11, delimiter=',')
#print h, s, n
np.savetxt('TT_perc_I210', mid11, delimiter=',')
np.savetxt('TT_perc_AR1', top11, delimiter=',')
np.savetxt('TT_perc_AR2', bot11, delimiter=',')
np.savetxt('Flow_perc_I210', h, delimiter=',')
np.savetxt('Flow_perc_AR1', n, delimiter=',')
np.savetxt('Flow_perc_AR2', s, delimiter=',')

'''
####Plot####
#A lot of things, most of it in comment
#Can plot a lot of different and nice graphs, just uncomment what you need
'''

fig, (ax22, ax1, ax2)=plt.subplots(3,1,sharex=True, gridspec_kw = {'height_ratios':[5, 2,1.4]})
#fig,(ax11,ax21,ax22)=plt.subplots(3,1,sharex=True, sharey=True)
#ax11.plot(percs,routed8, color='green', lw=3, label="Average Routed User")
#ax11.plot(percs,nrouted8, color='brown',  lw=3, label="Average Non-Routed User")
#ax11.plot(percs,top8, lw=1.5,color="c",label='North')
#ax11.plot(percs,mid8, lw=1.5,color="r",label='Highway')
#ax11.plot(percs,bot8, lw=1.5,color="y",label='South')

#ax11.set_xlabel("Percentage of Routed Users (%)")
#ax11.set_ylabel("Travel Time (Min)")
#ax11.grid(True)
#ax11.set_title("Travel Time for I210E Through Pasadena Depending On Percentage Of App-Users \n Demand = 2,500 vehicles/h")
#ax11.set_ylim(0,30)

#ax12.plot(percs,top9, color="c",label='North')
#ax12.plot(percs,mid9, color="r",label='Highway')
#ax12.plot(percs,bot9, color="y",label='South')
#ax12.plot(percs,routed9, color='brown',  lw=2, label="Average Routed User")
#ax12.plot(percs,nrouted9, color='green',  lw=2, label="Average Non-Routed User")
#ax12.set_xlabel("Percentage of Routed Users (%)")
#ax12.set_ylabel("Travel Time (Min)")
#ax12.grid(True)
#ax12.set_title("Demand=1.4")
#ax12.set_ylim(0,30)
#ax21.plot(percs,routed10, color='green',  lw=3, label="Average Routed User")
#ax21.plot(percs,nrouted10, color='brown',  lw=3, label="Average Non-Routed User")
#ax21.plot(percs,top10, lw=1.5,color="c",label='North')
#ax21.plot(percs,mid10, lw=1.5,color="r",label='Highway')
#ax21.plot(percs,bot10, lw=1.5,color="y",label='South')

#ax21.set_xlabel("Percentage of Routed Users (%)")
#ax21.set_ylabel("Travel Time (Min)")
#ax21.grid(True)
#ax21.set_title("Demand = 25,000 vehicles/h")
#ax21.set_ylim(0,30)
#ax22.plot(percs,routed11, color='green',  lw=3, label="Average Routed User")
#ax22.plot(percs,nrouted11, color='brown',  lw=3, label="Average Non-Routed User")


ax22.plot(percs,mid11, lw=4,color="r",label='I210')
ax22.plot(percs,top11, lw=4,color="b",label='Arterial Road 1')
ax22.plot(percs,bot11, lw=4,color="g",label='Arterial Road 2')

ax2.set_xlabel("Percentage of Routed Users (%)")
ax22.set_ylabel("Travel Time (Min)")
ax22.grid(True)
#ax22.set_title("Demand = 27,500 vehicles/h")
ax22.set_xlim(0,24)
ax22.set_ylim(10,31)

ax1.plot(percs, h, lw=4, color="r")
ax1.plot(percs, n, lw=4, color="b")
ax1.plot(percs, s, lw=4, color="g")


ax2.plot(percs, h, lw=4, color="r")
ax2.plot(percs, n, lw=4, color="b")
ax2.plot(percs, s, lw=4, color="g")

ax1.set_yticks([5*i for i in range(1,20)])
ax2.set_yticks([5*i for i in range(1,20)])
ax1.yaxis.grid(True)
ax2.yaxis.grid(True)
ax1.xaxis.grid(True)
ax2.xaxis.grid(True)

ax1.set_ylim(80,100)
ax2.set_ylim(0,14)
ax1.set_ylabel("Flow (% of total)")

ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop='off')  # don't put tick labels at the top
ax2.xaxis.tick_bottom()

d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

#
#top10, mid10, bot10=zip(*values)
#colors_and_labels=((top10, 'blue', 'North'),(mid10, 'red', 'Highway'),(bot10,'yellow','South'))
#for time, color, label in colors_and_labels:
#    plt.plot(percs, time, color=color,label=label)

#plt.title("Travel Time of each Itinerrary at User Equilibrium")
#plt.xlabel("Percentage of routed users (%)")
#plt.ylabel("Travel Time (minutes)")
#plt.grid(True)
#plt.legend()

ax22.legend()
plt.show()
