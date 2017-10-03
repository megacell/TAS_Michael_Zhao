__author__ = "Hippolyte Signargout"
__email__ = "signargout@berkeley.edu"

'''
Construction of rnr graphs and demand for heterogeneous Frank-Wolfe algorithm
'''
###Libraries and Functions
from process_data import extract_features
import numpy as np


def toy_heterogeneous(demand_r):
    ''' generate heteregenous game on Toy network '''
    g2 = np.loadtxt('data/Toy_net.csv', delimiter=',', skiprows=1)
    g1 = np.copy(g2)
    for i in range(0,13):
        for j in [3,7]:
            if i<5 or i>8 or i==6:                      #Non highway links
                g1[i,j]*=3000                               #3000 is the cognitive cost
    d1 = np.loadtxt('data/Toy_od.csv', delimiter=',', skiprows=1)
    d2 = np.copy(d1)
    d1[0,2] *= (1-demand_r)
    d2[0,2] *= demand_r
    return g1, g2, d1, d2                    #1 for nr, 2 for r, graph and demand

def LA_heterogeneous(demand_r, capacity):
    '''generate heterogeneous game on LA network
    demand_r is the ratio of routed users
    capacity is the max capacity for which a road is considered arterial'''
    g2 = np.loadtxt('data/LA_net.csv', delimiter=',', skiprows=1)
    g1 = np.copy(g2)
    features = extract_features('data/LA_net.txt')
    for i in range(0,len(features)):
        if features[i][0]<=capacity:
            g1[i,3:7]*=3000
    d1 = np.loadtxt('data/LA_od.csv', delimiter=',', skiprows=1)
    d2 = np.copy(d1)
    #print d1
    d1[:,2] *= (1-demand_r)
    d2[:,2] *= demand_r
    return g1, g2, d1, d2

def LAfix_heterogeneous(demand_r, capacity):                  #demand_nr=1-demand_r
    '''generate heterogeneous game on LAfix network
    demand_r is the ratio of routed users
    capacity is the max capacity for which a road is considered low-capacity'''
    g2 = np.loadtxt('data/LAfix_net.csv', delimiter=',', skiprows=1)
    g1 = np.copy(g2)
    features = extract_features('data/LAfix_net.txt')
    for i in range(0,len(features)):
        if features[i][0]<=capacity:
            g1[i,3:7]*=3000
    d1 = np.loadtxt('data/LA_od.csv', delimiter=',', skiprows=1)
    d2 = np.copy(d1)
    d1[:,2] *= (1-demand_r)
    d2[:,2] *= demand_r
    return g1, g2, d1, d2
