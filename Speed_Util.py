__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

###Libraries###
from __future__ import division          #reals division with '/'
import numpy as np
import argparse
import matplotlib.pyplot as plt
from math import *
###Other files###
from process_data import process_net, process_trips, extract_features, process_links, process_node, \
    geojson_link, construct_igraph, construct_od, join_node_demand, geojson_link_Scenario_Study, process_node_to_GPS_Coord
from frank_wolfe_2 import solver_3
from Social_Optimum import solver_social_optimum
from Demand_Study_HS import total_cost, load_network_data, frank_wolfe_ratio_study
import matplotlib.pyplot as plt
from math import *

#This file contains utility functions to read outputs of function like frank_wolfe_ratio_study and output concatenated python matrices
#Other utility functions compute speeds and average speeds on links, and one plots a graph

###Functons###
def get_results(network_name, demand):
	'''Demand_Study network_name [i/20 for i in [|0,demand|]] UE, puts results in a python matrix (one line is a link, flows for each demand)
    Input: network_name is the name of the network, demand is the highest demand you want
    Output: tab is a matrix, one line is a link (all links in the network), one column is a demand ratio (20 steps from 0 to demand), filled with the flow on the link at UE for this demand ratio'''
	for i in range (0,int(20*demand)+1):
		frank_wolfe_ratio_study(network_name , i/20 , "UE")                          #This line can be put in comment if the output files are already computed
		vector=np.loadtxt("data/output/"+network_name+"_output_ratio_"+str(i/20)+"_UE.csv")
		if i==0:             #Create tab if i==0
			tab=[]
			for el in vector:
				tab.append([el])
		else:                #Fill tab afterwards
			for j in range (0, len(vector)):
				tab[j].append(vector[j])
	return tab

def get_results_h(network_name):
	'''Demand_Study_Heterogeneous network_name 1 [i/1000 for i in [|0,250|]], puts results in two python matrices (one line is a link, flows for each demand)
    Input: network_name is the name of the network in the files
    Output: r (nr) is the flow of routed users (non-routed users) on eahc link (line) for a demand ratio of 1, and ratios of routed users varying from 0% to 25% by steps of 0.1% (column), in a 2D matrix
    /!\Output files have to be already computed/!\ '''
	for i in range (0,251):                 #251=25/0.1+1   can be changed for more/less precision, other scale...
		if i==0:       #create matrices
			vector=np.loadtxt("data/output/"+network_name+"_output_ratio_1.0_perc_0.0.csv", delimiter=',')
			nr=[]
			r=[]
			for el in vector:                  #These files are composed of two columns with flows of nr and r users for all links
				nr.append([el[0]])
				r.append([el[1]])
		else:                      #Fill matrices
			vector=np.loadtxt("data/output/"+network_name+'_output_ratio_1.0_perc_'+str(i/1000)+".csv", delimiter=',')
			for j in range (0, len(vector)):
				nr[j].append(vector[j][0])
				r[j].append(vector[j][1])
	return r, nr

def get_results_hc(network_name, demand, ratio):
	'''Demand_Study_Heterogeneous network_name demand ratio for capacity decreases [i/1000 for i in [|0,1000|]], puts results in a python matrix (one line is a link, flows )
    Input: network_name is the name of the network in the files, demand is the demand ratio, ratio is the ratio of routed users
    Output: r (nr) is the flow of routed users (non-routed users) on eahc link (line) for a capacity decrease from 0% to 100% by steps of 0.1% (column), in a 2D matrix
    /!\Output files have to be already computed/!\Only works for the Toy network/!\ '''
	for i in range (0,1000):
		if i==0:
			vector=np.loadtxt("data/output/"+network_name+"_output_ratio_"+str(demand)+"_perc_"+str(ratio)+"_capdec_0.0.csv", delimiter=',')
			nr=[]
			r=[]
			for el in vector:
				nr.append([el[0]])
				r.append([el[1]])
		else:
			vector=np.loadtxt("data/output/"+network_name+'_output_ratio_'+str(demand)+'_perc_'+str(ratio)+'_capdec_'+str(i/1000)+".csv", delimiter=',')
			for j in range (0, len(vector)):
				nr[j].append(vector[j][0])
				r[j].append(vector[j][1])
	return r, nr

def get_speed(network_name, demand):
	'''use get_results to get the speed on each link and each demand
    network_name name of the network in the files
    demand demand ratio maximum
    Output matrix representing the speed of the flow on each link of the network (row) for demand ratios between 0 and the maximum in 20 steps'''
	flows=get_results(network_name, demand)
	azf=np.loadtxt("data/"+network_name+"_net.csv", skiprows=1, delimiter=',')
	lengths=np.loadtxt("data/"+network_name+"_net.txt", skiprows=7, usecols=(3))
	speeds=[]
	for i in range(0, len(flows)):
		speeds.append([])
		a0=azf[i][3]
		a4=azf[i][7]
		length=lengths[i]
		for j in range (0, 20*demand+1):
			traveltimeminut=a0+a4*flows[i][j]**4
			speed=60*length/traveltimeminut
			speeds[i].append(speed)
	return speeds

def avg_speeds(network_name, demand, steps):
    '''
    For 20 different demand ratios, compute the average speeds of links with a certain capacity
    input/network_name = name of the network in the file names
    input/demand = maximum demand ratio studied
    input/steps = number of capacity steps to distinguish
    output/cap = matrix representing average speeds on links of different categories of capacities (rows) for different demands (columns)
    '''
	speeds=get_speed(network_name, demand)
	capacities=np.loadtxt("data/"+network_name+"_net.txt", skiprows=7, usecols=(2))
	cap=[[0]*(1+20*demand)]*steps
	caps=[0]*steps
	for i in range(0, len(speeds)):
		step=int(ceil(steps*capacities[i]/10000)-1)
		caps[step]+=1
		cap[step]=[cap[step][j]+speeds[i][j] for j in range(0, 1+20*demand)]
	for step in range(0,steps):
		cap[step]=[el/caps[step] for el in cap[step]]
	return cap

def plot(network_name, demand,steps):
    '''
    Function to be able to plot on pyplot the evolution of average speed on links of different capacities depending on the demand ratio
    '''
	avg=avg_speeds(network_name,demand,steps)
	avg2=[]
	for i in range(0,1+demand*20):
		avg2.append([avg[j][i] for j in range (0,len(avg))])
	plt.title("Average Speed of Vehicles at User Equilibrium")
	plt.xlabel("Demand (*2500 vehicles/hour)")
	plt.ylabel("Speed (minutes)")
	plt.plot(avg2)
	plt.show()
