# the original code can be found here: http://www.xl-optim.com/python-traffic-assignment/

__author__ = "Jerome Thai"
__email__ = "jerome.thai@berkeley.edu"


import numpy as np
import os, sys
import AoN
from scipy.sparse import csr_matrix


def all_or_nothing(graph, od, display=0):
    '''do all or nothing assignment given numpy arrays of graph and OD flow
    '''
    #Characteristics of the graph
    zones=int(np.max(od[:,0:2])+1)
    links=int(np.max(graph[:,0])+1)
    #print 'graph', graph
    #print graph.dtype
    #print 'zones', zones
    #print 'links', links
    #Builds the matrix on a sparse format because the matrix is too big and too sparse
    matrix=csr_matrix((od[:,2],(od[:,0].astype(int),od[:,1].astype(int))), shape=(zones,zones), dtype="float64")
    #print 'matrix', matrix
    #Prepares arrays for assignment
    L=np.zeros(links,dtype="float64")
    demand=np.zeros(zones,dtype="float64")
    
    #import pdb; pdb.set_trace()

    for i in range(int(zones)): #We assign all zones
        #print i
        if matrix.indptr[i+1]>matrix.indptr[i]: #Only if there are flows for that particular zone
            demand.fill(0) #We erase the previous matrix array for assignment
            demand[matrix.indices[matrix.indptr[i]:matrix.indptr[i+1]]]=matrix.data[matrix.indptr[i]:matrix.indptr[i+1]] #Fill it in with the new information
            #print 'demand', demand
            #print demand.dtype
            #print np.sum(demand > 0.)
            zones, loads=AoN.AllOrNothing(graph,demand,i)  #And assign
            #print 'loads', loads
            L=L+loads
            if display>=1: print 'Origin ' + str(zones)+' assigned'
            #print 'Origin ' + str(zones)+' assigned'
    #print L.dot(graph[:,3])
    # np.savetxt('data/I210/graph.csv', graph, delimiter=',')
    # np.savetxt('data/I210/od.csv', od, delimiter=',')
    return L


def main(graph='data/graph.csv', matrix='data/matrix.csv', display=0):

    #dire_data=os.getcwd()
    #dire=os.getcwd()

    #We load the data
    graph=np.loadtxt(graph, delimiter=',', skiprows=1)
    od=np.loadtxt(matrix, delimiter=',', skiprows=1)

    #Characteristics of the graph
    #zones=int(np.max(od[:,0:2])+1)
    #links=int(np.max(graph[:,0])+1)

    #Do all or nothing assignment
    print all_or_nothing(graph, od, display=display)
    # w=open('RESULT.CSV','w')
    # print >> w, 'Link,NodeA,NodeB,LOAD'
    # for i in range(links-1):
    #     if L[i]>0:
    #         print >> w, i,',', graph[i,1],',', graph[i,2],',',L[i]
    # w.flush()
    # w.close()

    # print "DONE"



if __name__ == '__main__':
    # main('data/braess_graph.csv', 'data/braess_od.csv')
    main(display=1)

