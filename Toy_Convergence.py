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

#print top
#print mid
#print bot



values=[(top[i],mid[i],bot[i]) for i in range (0, len(bot))]
demands=[1.25*i for i in range(0, len(bot))]
top, mid, bot=zip(*values)
colors_and_labels=((top, 'blue', 'North'),(mid, 'red', 'Highway'),(bot,'yellow','South'))
for time, color, label in colors_and_labels:
    plt.plot(demands, time, color=color,label=label)

plt.title("Travel Time of each Itinerrary at User Equilibrium")
plt.xlabel("Demand (k.vehicles/hour)")
plt.ylabel("Travel Time (minutes)")
plt.grid(True)
plt.legend()
plt.show()

