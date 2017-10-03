__author__ = "Jerome Thai, Nicolas Laurent-Brouty, Juliette Ugirumurera, Hippolyte Signargout"
__email__ = "jerome.thai@berkeley.edu, nicolas.lb@berkeley.edu, Ugirumurera@lbl.gov, signargout@berkeley.edu"

'''
This is another 'Demand_Study'-like files
The arguments are the demand ratio, the percentage of routed users, and the step for which the reduction of capacity has to be used
It runs an iteration loop to compute UE for all capacity reductions between 0 and 1
The network is Toy, it has been used in the TRB paper
'''

###Libraries
import numpy as np
import argparse
from math import ceil
#Functions
from process_data import process_net, process_trips, extract_features, process_links, process_node, \
    geojson_link, construct_igraph, construct_od, join_node_demand, geojson_link_Scenario_Study, process_node_to_GPS_Coord
from frank_wolfe_heterogeneous import fw_heterogeneous_1,fw_heterogeneous_2
from Social_Optimum import solver_social_optimum
from AoN_igraph import all_or_nothing
from frank_wolfe_2 import total_free_flow_cost, search_direction, line_search, solver_3
from process_data import construct_igraph, construct_od
from utils import multiply_cognitive_cost, heterogeneous_demand
from heterogeneous_construct import toy_heterogeneous, LAfix_heterogeneous

#Profiling the code
import timeit

#Funtion to calculate the total travel time
def total_cost(graph, f):
    x = np.power(f.reshape((f.shape[0],1)), np.array([1,2,3,4,5]))  # x is a matrix containing f,f^2, f^3, f^4, f^5
    tCost = np.sum(np.einsum('ij,ij->i', x, graph[:,3:]))    # Multply matrix x with coefficients a0, a1, a2, a3 and a4
    return tCost


#load the network data:

def load_network_data(name):
    #import pdb; pdb.set_trace()

    #The folder locations of all the input files
    graphLocation = 'data/' + name + '_net.csv'
    demandLocation = 'data/' + name + '_od.csv'
    nodeLocation = 'data/' + name + '_node.csv'
    featureLocation = 'data/' + name + '_net.txt'

    graph = np.loadtxt(graphLocation, delimiter=',', skiprows=1)
    demand = np.loadtxt(demandLocation, delimiter=',', skiprows=1)
    features = extract_features(featureLocation)
    #import pdb; pdb.set_trace()

    #LA network has a different way of processing the nodes file
    if(name == "LA"):
    	node = np.loadtxt(nodeLocation, delimiter=',')
	print features.shape
	features[10787,0] = features[10787,0] * 1.5
	graph[10787,-1] = graph[10787,-1] / (1.5**4)
	features[3348,:] = features[3348,:] * 1.2
	graph[3348,-1] = graph[3348,-1] / (1.2**4)
    else:
    	node = np.loadtxt(nodeLocation, delimiter=',', skiprows=1)
    return graph, demand, node, features


#This function runs frank-wolfe algorithm on a particular network with demand modified as ratio X demand
def frank_wolfe_ratio_study_hc(ratio, perc, capacity):
    '''
    This function runs heterogeneous frank-wolfe algorithm on a particular network with demand modified as ratio X demand and ratio of routed users being 'perc'
    input/ratio (float) demand ratio
    input/perc (float) percentage of routed users
    input/capacity is the capacity reduction of the Highway
    '''
    g1, g2, d1, d2 = toy_heterogeneous(perc)                     #Only for Toy
    d1[:,2] =ratio*(  d1[:,2] /4000)
    d2[:,2] =ratio*(  d2[:,2] /4000)
    g1[7,7]= g1[7,7]/((1-capacity)**4)
    g2[7,7]= g2[7,7]/((1-capacity)**4)
    #print "dnr=", d1, "dr=",d2


       #start timer for frank-wolfe
    start_time1 = timeit.default_timer()

       #Run Frank-Wolfe
    f = fw_heterogeneous_1([g1,g2], [d1,d2], max_iter=10000, q=50, display=0, stop=1e-5)
       #end of timer

    elapsed1 = timeit.default_timer() - start_time1
    #print ("Frank-Wolfe took  %s seconds" % elapsed1)

    #total_travel_time = total_cost(graph, f)
    #avg_travel_time = total_travel_time/np.sum(d[:,2])
    #print ("Average travel time %3f " % avg_travel_time)

    fileName = 'data/output/Toy_output_ratio_' + str(ratio) + '_perc_'+ str(perc) +'_capdec_'+str(capacity)+'.csv'
    print(fileName)
    np.savetxt(fileName, f, delimiter=',')
    #Call visualize with filename where output is
    #visualize_result_ratio_study(fileName, ratio, network_name, mode)

#Visualize the results from the scenario study
def visualize_result_ratio_study(fileName, ratio, name, mode):
    net, demand, node, features = load_network_data(name)
    #Loading the flow per link resulting from frank-wolfe
    f = np.loadtxt(fileName, delimiter=',', skiprows=0)

    #Location of the features
    featureLocation = 'data/' + name + '_net.txt'
    features = np.zeros((f.shape[0], 4))
    features[:,:3] = extract_features(featureLocation)

    #Multiply the flow obtained by 4000 since we initially divided by 4000 before frank-wolfs
    f = np.divide(f*4000, features[:,0])
    features[:,3] = f
    links = process_links(net, node, features, in_order=True)

    #creates color array used to visulized the links
    #values useful in differenciating links based of flow on links
    color = 2.0*f + 1.0

    #Keeping track of the percentage of congestion
    links_congested = len(color[np.where(color >= 3)])
    percentage_of_congestion = float(links_congested) / float(len(color))
    print("congestion is at %3f " % percentage_of_congestion)

    geojson_link_Scenario_Study(ratio,links, ['capacity', 'length', 'fftt', 'flow_over_capacity'], color, name, mode)

def main():
    pass
    parser = argparse.ArgumentParser(description='Process network name and demand ratio')
    #parser.add_argument("name", type = str, help = "name of network")
    parser.add_argument("ratio", type = float, help = "demand ratio")
    parser.add_argument("routed", type = float, help = "percentage of routed users")
    parser.add_argument("capacity", type = float, help= "reduction of capacity")
    #frank-wolfe algorithm can operate in two modes: User Equilibrium (UE) or Social Optimum (SO)
    #parser.add_argument("mode", type = str, help = "frank wolfe mode")
    args = parser.parse_args()
    for i in range (0,int(ceil(1/args.capacity)+1)):              #Loop on the capacity reduction
        frank_wolfe_ratio_study_hc(args.ratio, args.routed, args.capacity*i)


if __name__ == '__main__':
    main()
