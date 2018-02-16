# This is the analytical model that is going to inherit from the Traffic_Model
import numpy as np
import csv
from Traffic_Model import Traffic_Model_class

class Analytical_Model_class(Traffic_Model_class):
    def __init__(self, type, name):
        Traffic_Model_class.__init__(self, type)
        # The folder locations of all the input files
        graphLocation = 'data/' + name + '_net.csv'
        demandLocation = 'data/' + name + '_od.csv'
        nodeLocation = 'data/' + name + '_node.csv'
        featureLocation = 'data/' + name + '_net.txt'

        self.graph = np.loadtxt(graphLocation, delimiter=',', skiprows=1)
        self.demand = np.loadtxt(demandLocation, delimiter=',', skiprows=1)
        self.features = extract_features(featureLocation)

        # LA network has a different way of processing the nodes file
        if (name == "LA"):
            self.node = np.loadtxt(nodeLocation, delimiter=',')
            self.features[10787, 0] = self.features[10787, 0] * 1.5
            self.graph[10787, -1] = self.graph[10787, -1] / (1.5 ** 4)
            self.features[3348, :] = self.features[3348, :] * 1.2
            self.graph[3348, -1] = self.graph[3348, -1] / (1.2 ** 4)
        else:
            self.node = np.loadtxt(nodeLocation, delimiter=',', skiprows=1)

#Function useful to extract features used in loading other graph data
def extract_features(input):
    # features = table in the format [[capacity, length, FreeFlowTime]]
    flag = False
    out = []
    with open(input, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0:
                if flag == False:
                    if row[0].split()[0] == '~': flag = True
                else:
                    out.append([float(e) for e in row[0].split()[2:5]])
    return np.array(out)

