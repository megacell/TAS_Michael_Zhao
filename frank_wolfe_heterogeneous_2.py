__author__ = 'Jerome Thai'
__email__ = 'jerome.thai@berkeley.edu'


'''
This module is frank-wolfe algorithm using an all-or-nothing assignment
based on igraph package
'''

import numpy as np
from process_data import construct_igraph, construct_od
from AoN_igraph import all_or_nothing
#Profiling the code
import timeit
from collections import defaultdict
from utils import heterogeneous_demand


def potential(graph ,f):
    # this routine is useful for doing a line search
    # computes the potential at flow assignment f
    #print np.max(graph[:,0])+1)
    links = int(np.max(graph[:,0])+1)
    g = graph.dot(np.diag([1.,1.,1.,1.,1/2.,1/3.,1/4.,1/5.]))
    x = np.power(f.reshape((links,1)), np.array([1,2,3,4,5]))
    return np.sum(np.einsum('ij,ij->i', x, g[:,3:]))


def line_search(f, res=20):
    # on a grid of 2^res points bw 0 and 1, find global minimum
    # of continuous convex function
    d = 1./(2**res-1)
    l, r = 0, 2**res-1
    while r-l > 1:
        if f(l*d) <= f(l*d+d): return l*d
        if f(r*d-d) >= f(r*d): return r*d
        # otherwise f(l) > f(l+d) and f(r-d) < f(r)
        m1, m2 = (l+r)/2, 1+(l+r)/2
        if f(m1*d) < f(m2*d): r = m1
        if f(m1*d) > f(m2*d): l = m2
        if f(m1*d) == f(m2*d): return m1*d
    return l*d


def total_free_flow_cost(g, od):
    return np.array(g.es['weight']).dot(all_or_nothing(g, od)[0])

#Calculates the total travel cost/time
def total_cost(graph, f, grad):
    #g.es['weight'] = grad.tolist()
    #return np.array(g.es['weight']).dot(f)
    #Since the cost function equals to t(f) = a0+a1*f+a2*f^2+a3*f^3+a4*f^4 (where f is the flow)
    #the travel cost, f*t(f) = a0*f+ a1*f^2 + a2*f^3+ a3*f^4 + a4*f^5
    x = np.power(f.reshape((f.shape[0],1)), np.array([1,2,3,4,5]))  # x is a matrix containing f,f^2, f^3, f^4, f^5
    tCost = np.sum(np.einsum('ij,ij->i', x, graph[:,3:]))    # Multply matrix x with coefficients a0, a1, a2, a3 and a4
    return tCost
    #g.es['weight'] = grad.tolist()


def search_direction(f, graph, g, od):
    # computes the Frank-Wolfe step
    # g is just a canvas containing the link information and to be updated with
    # the most recent edge costs
    x = np.power(f.reshape((f.shape[0],1)), np.array([0,1,2,3,4]))
    grad = np.einsum('ij,ij->i', x, graph[:,3:])
    g.es['weight'] = grad.tolist()

    #start timer
    #start_time1 = timeit.default_timer()

    L, path_flows = all_or_nothing(g, od)

    print len(path_flows)
    # for k in path_flows:
    #     print k, path_flows[k]
    #     exit(1)

    #end of timer
    #elapsed1 = timeit.default_timer() - start_time1
    #print ('all_or_nothing took  %s seconds' % elapsed1)

    return L, grad, path_flows
    #return all_or_nothing(g, od), grad

def search_direction_with_fixed(f, f_fixed, graph, g, od):
    # computes the Frank-Wolfe step
    # g is just a canvas containing the link information and to be updated with
    # the most recent edge costs
    f_total = f + f_fixed

    x = np.power(f_total.reshape((f_total.shape[0],1)), np.array([0,1,2,3,4]))
    grad = np.einsum('ij,ij->i', x, graph[:,3:])
    g.es['weight'] = grad.tolist()

    #start timer
    #start_time1 = timeit.default_timer()

    # L_total, path_flows = all_or_nothing(g, od)
    # L = L_total - f_fixed

    L, path_flows = all_or_nothing(g, od)

    print len(path_flows)
    # for k in path_flows:
    #     print k, path_flows[k]
    #     exit(1)

    #end of timer
    #elapsed1 = timeit.default_timer() - start_time1
    #print ('all_or_nothing took  %s seconds' % elapsed1)

    return L, grad, path_flows
    #return all_or_nothing(g, od), grad


#This function allow each user to account for their impact on the global travel cost
#thus allowing to measure the price of anarchy
def price_of_anarchy(f, graph, g, od):
    # computes the Frank-Wolfe step
    # g is just a canvas containing the link information and to be updated with
    # the most recent edge costs
    x = np.power(f.reshape((f.shape[0],1)), np.array([0,1,2,3,4]))
    #import pdb; pdb.set_trace()
    #When we add the price of anarchy, the cost function becomes a0+ 2*a2*x+ 3*a3*x^2+ 4*a4*x^3+ 5*a5*x^4
    #Matrix coefficients saves the 1, 2, 3, 4, and 5 coefficients in front of the ai*x terms
    coefficients = np.array([1,2,3,4,5])
    onesArray = np.ones((f.shape[0],5))
    import pdb; pdb.set_trace()
    coefficients = onesArray * coefficients.transpose()
    #y stands for the flow multiplied by the coefficients
    #import pdb; pdb.set_trace()
    y = np.einsum('ij, ij->ij', x, coefficients)
    grad = np.einsum('ij,ij->i', y, graph[:,3:])
    g.es['weight'] = grad.tolist()

    #Calculating All_or_nothing
    L = all_or_nothing(g, od)

    return L, grad


def solver(graph, demand, demand_fixed, g=None, od=None, od_fixed=None, max_iter=100, eps=1e-8, q=None, \
    display=0, past=None, stop=1e-8):

    if g is None: g = construct_igraph(graph)
    if od is None: od = construct_od(demand)
    if od_fixed is None: od_fixed = construct_od(demand_fixed)
    f = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
    h = defaultdict(np.float64) # initial path flow assignment is null
    f_fixed, _, h_fixed = search_direction(f, graph, g, od_fixed)
    K = total_free_flow_cost(g, od)
    if K < eps:
        K = np.sum(demand[:,2])
    elif display >= 1:
        print 'average free-flow travel time', K / np.sum(demand[:,2])

    start_time = timeit.default_timer()
    for i in range(max_iter):
        if display >= 1:
            if i <= 1:
                print 'iteration: {}'.format(i+1)
            else:
                print 'iteration: {}, error: {}'.format(i+1, error)
        # construct weighted graph with latest flow assignment
        L, grad, path_flows = search_direction_with_fixed(f, f_fixed, graph, g, od)
        if i >= 1:
            error = grad.dot(f - L) / K
            if error < stop: return f, h
        f = f + 2.*(L-f)/(i+2.)
        for k in set(h.keys()).union(set(path_flows.keys())):
            h[k] = h[k] + 2.*(path_flows[k]-h[k])/(i+2.)
        print 'iteration', i
        print 'time(sec):', timeit.default_timer() - start_time;
        print 'num path flows:', len(h)

        f_h = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
        for k in h:
            flow = h[k]
            for link in k[2]:
                f_h[link] += flow
        print "path vs link flow diff:", np.sum(np.abs(f_h - f)), f.shape

    f += f_fixed
    for k in set(h.keys()).union(set(h_fixed.keys())):
        h[k] += h_fixed[k]

    print 'added in fixed flows'
    print 'num path flows:', len(h)
    f_h = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
    for k in h:
        flow = h[k]
        for link in k[2]:
            f_h[link] += flow
    print "[total] path link flow total:", np.sum(np.abs(f_h)), f.shape
    print "[total] link link flow total:", np.sum(np.abs(f)), f.shape
    print "[total] path vs link flow diff:", np.sum(np.abs(f_h - f)), f.shape

    # find how many paths each od pair really has
    od_paths = defaultdict(int)
    most_paths = 0
    for k in h.keys():
        od_paths[(k[:2])] += 1
        most_paths = max(most_paths, od_paths[(k[:2])])
    path_counts = [0 for i in range(most_paths + 1)]
    for k in od_paths.keys():
        path_counts[od_paths[k]] += 1
    for i in range(len(path_counts)):
        print i, path_counts[i]
    return f, h


def solver_2(graph, demand, demand_fixed, g=None, od=None, od_fixed=None, max_iter=100, eps=1e-8, q=10, \
    display=0, past=None, stop=1e-8):

    if g is None: g = construct_igraph(graph)
    if od is None: od = construct_od(demand)
    if od_fixed is None: od_fixed = construct_od(demand_fixed)
    f = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
    h = defaultdict(np.float64) # initial path flow assignment is null
    f_fixed, _, h_fixed = search_direction(f, graph, g, od_fixed)
    ls = max_iter/q # frequency of line search
    K = total_free_flow_cost(g, od)
    if K < eps:
        K = np.sum(demand[:,2])
    elif display >= 1:
        print 'average free-flow travel time', K / np.sum(demand[:,2])

    start_time = timeit.default_timer()
    for i in range(max_iter):
        if display >= 1:
            if i <= 1:
                print 'iteration: {}'.format(i+1)
            else:
                print 'iteration: {}, error: {}'.format(i+1, error)
        # construct weighted graph with latest flow assignment
        L, grad, path_flows = search_direction_with_fixed(f, f_fixed, graph, g, od)
        
        if i >= 1:
            # w = f - L
            # norm_w = np.linalg.norm(w,1)
            # if norm_w < eps: return f, h
            error = grad.dot(f - L) / K
            if error < stop: return f, h
        # s = line_search(lambda a: potential(graph, (1.-a)*f+a*L)) if i>max_iter-q \
        #     else 2./(i+2.)
        s = line_search(lambda a: potential(graph, (1.-a)*f+a*L)) if i%ls==(ls-1) \
            else 2./(i+2.)
        if s < eps: return f, h
        f = (1.-s) * f + s * L
        for k in set(h.keys()).union(set(path_flows.keys())):
            h[k] = (1.-s) * h[k] + s * path_flows[k]
        print 'iteration', i
        print 'time(sec):', timeit.default_timer() - start_time;
        print 'num path flows:', len(h)

        f_h = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
        for k in h:
            flow = h[k]
            for link in k[2]:
                f_h[link] += flow
        print "path vs link flow diff:", np.sum(np.abs(f_h - f)), f.shape

    f += f_fixed
    for k in set(h.keys()).union(set(h_fixed.keys())):
        h[k] += h_fixed[k]

    print 'added in fixed flows'
    print 'num path flows:', len(h)
    f_h = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
    for k in h:
        flow = h[k]
        for link in k[2]:
            f_h[link] += flow
    print "[total] path link flow total:", np.sum(np.abs(f_h)), f.shape
    print "[total] link link flow total:", np.sum(np.abs(f)), f.shape
    print "[total] path vs link flow diff:", np.sum(np.abs(f_h - f)), f.shape

    # find how many paths each od pair really has
    od_paths = defaultdict(int)
    most_paths = 0
    for k in h.keys():
        od_paths[(k[:2])] += 1
        most_paths = max(most_paths, od_paths[(k[:2])])
    path_counts = [0 for i in range(most_paths + 1)]
    for k in od_paths.keys():
        path_counts[od_paths[k]] += 1
    for i in range(len(path_counts)):
        print i, path_counts[i]
    return f, h


def solver_3(graph, demand, demand_fixed, g=None, od=None, od_fixed=None, past=10, max_iter=100, eps=1e-16, \
    q=50, display=0, stop=1e-8):
    '''
    this is an adaptation of Fukushima's algorithm
    graph:    numpy array of the format [[link_id from to a0 a1 a2 a3 a4]]
    demand:   mumpy arrau of the format [[o d flow]]
    g:        igraph object constructed from graph
    od:       od in the format {from: ([to], [rate])}
    past:     search direction is the mean over the last 'past' directions
    max_iter: maximum number of iterations
    esp:      used as a stopping criterium if some quantities are too close to 0
    q:        first 'q' iterations uses open loop step sizes 2/(i+2)
    display:  controls the display of information in the terminal
    stop:     stops the algorithm if the error is less than 'stop'
    '''

    assert past <= q, "'q' must be bigger or equal to 'past'"
    if g is None:
        g = construct_igraph(graph)
    if od is None:
        od = construct_od(demand)
    if od_fixed is None:
        od_fixed = construct_od(demand_fixed)
    f = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
    fs = np.zeros((graph.shape[0],past),dtype='float64') #not sure what fs does
    h = defaultdict(np.float64) # initial path flow assignment is null
    hs = defaultdict(lambda : [0. for _ in range(past)]) # initial path flow assignment is null
    f_fixed, _, h_fixed = search_direction(f, graph, g, od_fixed)
    K = total_free_flow_cost(g, od)

    # why this?
    if K < eps:
        K = np.sum(demand[:,2])
    elif display >= 1:
        print 'average free-flow travel time', K / np.sum(demand[:,2])

    #import pdb; pdb.set_trace()
    start_time = timeit.default_timer()
    for i in range(max_iter):

#        if display >= 1:
#            if i <= 1:
#                print 'iteration: {}'.format(i+1)
#            else:
#                print 'iteration: {}, error: {}'.format(i+1, error)

    #start timer
        #start_time2 = timeit.default_timer()

        # construct weighted graph with latest flow assignment
        L, grad, path_flows = search_direction_with_fixed(f, f_fixed, graph, g, od)
        
        fs[:,i%past] = L
        for k in set(h.keys()).union(set(path_flows.keys())):
            hs[k][i%past] = path_flows[k]
        w = L - f
        w_h = defaultdict(np.float64)
        for k in set(h.keys()).union(set(path_flows.keys())):
            w_h[k] = path_flows[k] - h[k]
        if i >= 1:
            error = -grad.dot(w) / K
            # if error < stop and error > 0.0:
            if error < stop:
                if display >= 1: print 'stop with error: {}'.format(error)
                return f, h
        if i > q:
            # step 3 of Fukushima
            v = np.sum(fs,axis=1) / min(past,i+1) - f
            v_h = np.defaultdict(np.float64)
            for k in set(hs.keys()).union(set(path_flows.keys())):
                v_h[k] = sum(hs[k]) / min(past,i+1) - h[k]
            norm_v = np.linalg.norm(v,1)
            if norm_v < eps:
                if display >= 1: print 'stop with norm_v: {}'.format(norm_v)
                return f, h
            norm_w = np.linalg.norm(w,1)
            if norm_w < eps:
                if display >= 1: print 'stop with norm_w: {}'.format(norm_w)
                return f, h
            # step 4 of Fukushima
            gamma_1 = grad.dot(v) / norm_v
            gamma_2 = grad.dot(w) / norm_w
            if gamma_2 > -eps:
                if display >= 1: print 'stop with gamma_2: {}'.format(gamma_2)
                return f, h
            d = v if gamma_1 < gamma_2 else w
            d_h = v_h if gamma_1 < gamma_2 else w_h
            # step 5 of Fukushima
            s = line_search(lambda a: potential(graph, f+a*d))
            lineSearchResult = s
            if s < eps:
                if display >= 1: print 'stop with step_size: {}'.format(s)
                return f, h
            f = f + s*d
            for k in set(hs.keys()).union(set(path_flows.keys())):
                h[k] = h[k] + s*d_h[k]
        else:
            f = f + 2. * w/(i+2.)
            for k in set(h.keys()).union(set(path_flows.keys())):
                h[k] = h[k] + 2.*(w_h[k])/(i+2.)
        print 'iteration', i
        print 'time(sec):', timeit.default_timer() - start_time;
        print 'num path flows:', len(h)

        f_h = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
        for k in h:
            flow = h[k]
            for link in k[2]:
                f_h[link] += flow
        print "path vs link flow diff:", np.sum(np.abs(f_h - f)), f.shape

    f += f_fixed
    for k in set(h.keys()).union(set(h_fixed.keys())):
        h[k] += h_fixed[k]

    print 'added in fixed flows'
    print 'num path flows:', len(h)
    f_h = np.zeros(graph.shape[0],dtype='float64') # initial flow assignment is null
    for k in h:
        flow = h[k]
        for link in k[2]:
            f_h[link] += flow
    print "[total] path link flow total:", np.sum(np.abs(f_h)), f.shape
    print "[total] link link flow total:", np.sum(np.abs(f)), f.shape
    print "[total] path vs link flow diff:", np.sum(np.abs(f_h - f)), f.shape

    # find how many paths each od pair really has
    od_paths = defaultdict(int)
    most_paths = 0
    for k in h.keys():
        od_paths[(k[:2])] += 1
        most_paths = max(most_paths, od_paths[(k[:2])])
    path_counts = [0 for i in range(most_paths + 1)]
    for k in od_paths.keys():
        path_counts[od_paths[k]] += 1
    for i in range(len(path_counts)):
        print i, path_counts[i]

    return f, h


def single_class_parametric_study(factors, output, net, demand, \
    max_iter=100, display=1):
    '''
    parametric study where the equilibrium flow is computed under different
    demand levels alpha*demand for alpha in factors
    '''
    g = construct_igraph(net)  #constructs an igraph object given the network information
    d = np.copy(demand)     #makes a copy of the demand array
    fs = np.zeros((net.shape[0], len(factors)))  #An array with all zeros of num-link by num-fact,
                         #where num-link is the number of links and num-fact is the number of factors

    #creates a header with Xi for each i index of factor in array
    header = ','.join(['X{}'.format(i) for i in range(len(factors))])
    for i,alpha in enumerate(factors):
        if display >= 1:
            print 'computing equilibrium {}/{}'.format(i+1, len(factors))
        print ('Factor is: %.3f' % factors[i]);
        d[:,2] = alpha * demand[:,2]
        f = solver_3(net, d, g=g, past=20, q=50, stop=1e-3, display=display, \
            max_iter=max_iter)
        fs[:,i] = f
    np.savetxt(output, fs, delimiter=',', header=header, comments='')


def main():
    start_time2 = timeit.default_timer()
    graph = np.loadtxt('data/LA_net.csv', delimiter=',', skiprows=1)
    demand = np.loadtxt('data/LA_od_2.csv', delimiter=',', skiprows=1)
    graph[10787,-1] = graph[10787,-1] / (1.5**4)
    graph[3348,-1] = graph[3348,-1] / (1.2**4)

    alpha = .2

    demand[:,2] = 0.5*demand[:,2] / 4000
    d_nr, d_r = heterogeneous_demand(demand, alpha)
    f, h = solver_3(graph, d_nr, d_r, max_iter=10, display=1)

    #end of timer
    elapsed2 = timeit.default_timer() - start_time2;
    print ("Execution took %s seconds" % elapsed2)
    visualize_LA()


if __name__ == '__main__':
    main()