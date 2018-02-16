import numpy as np
import csv
from Analytical_Model import Analytical_Model_class

class Analytical_BPR(Analytical_Model_class):
    #Initalization
    def __init__(self, type, name):
        Analytical_Model_class.__init__(self, type,name)

    #Cost function given BPR
    def cost_function(self, graph, f):
        x = np.power(f.reshape((f.shape[0], 1)), np.array([0, 1, 2, 3, 4]))
        grad = np.einsum('ij,ij->i', x, graph[:, 3:])
        return grad

    #Gradient function given BPR
    def gradient_function(self,graph, f):
        links = int(np.max(graph[:, 0]) + 1)
        g = graph.dot(np.diag([1., 1., 1., 1., 1 / 2., 1 / 3., 1 / 4., 1 / 5.]))
        x = np.power(f.reshape((links, 1)), np.array([1, 2, 3, 4, 5]))
        return np.sum(np.einsum('ij,ij->i', x, g[:, 3:]))

