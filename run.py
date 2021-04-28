#!/usr/bin/env python3

import matplotlib.pyplot as plt
import os
import sys
import getopt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph



def main(argv):
    args = sys.argv

    edgelist_path = ''
    mem_usage = 0
    objective = ''
    opts = []
    try:
        opts, args = getopt.getopt(argv, "hi:m:o:", ["ifile=", "memory-usage=", "objective="]) # Get command-line inputs
    
    except getopt.GetoptError:
        print ('usage: ' + sys.argv[0] + '-i <input edgelist file> -m <max memory usage allowed> -o <objective>')
        return

    for opt, arg in opts: # Check command-line inputs
        if opt == '-h':
            print ('usage: ' + sys.argv[0] + '-i <input edgelist file> -m <max memory usage allowed> -o <objective>')
            sys.exit()

        elif opt in ("-i", "--ifile"):
            edgelist_path = arg

        elif opt in ("-m", "--memory-usage"):
            mem_usage = arg

        elif opt in ('-o', '--objective'):
            objective = arg

    # check_inputs(edgelist_path, mem_usage, objective) 

    try:  
        G = nx.read_weighted_edgelist(edgelist_path, create_using=nx.DiGraph)

    except FileNotFoundError:
        print("Unable to locate edge list. Please enter correct file location.")
        sys.exit()

    options = {
        'node_size': 1500,
        'arrowstyle': '-|>',
        'arrowsize': 12,
    }


    crit_path_len = find_crit_path(G)
    gen = nx.algorithms.dag.all_topological_sorts(G)

    source, sink = create_src_sink_nodes(G) # Adding nodes no longer makes the graph a DAG (acyclic) anymore, for some reason.

    all_paths = nx.all_simple_paths(G, source='SRC', target='SINK')

    crit_paths = []
    non_crit_paths = []
    for path in all_paths:
        path = path[1:-1]
        if len(path) == crit_path_len:
            crit_paths.append(path)

        else:
            non_crit_paths.append(path)

    # edge_labels=dict([((u,v,),int(d['weight'])) for u,v,d in G.edges(data=True)]) # Mainly used to get only the weight out of the 'weight' dict. 
    # pos = nx.spiral_layout(G)
    # nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
    # nx.draw(G, pos=pos, with_labels=True, **options)
    # plt.show()

def check_edge_weight(G: nx.DiGraph, max_mem: int):
    for edge in G.edges(data=True):
        weight = edge[:-1]

        if weight > max_mem:
            return edge, False

    return True


    
# Create source and sink nodes.
def create_src_sink_nodes(G: nx.DiGraph):
    src = G.add_node('SRC')
    sink = G.add_node('SINK')
    for node in G.nodes:
        iter_pre = G.predecessors(node)
        iter_suc = G.successors(node)
        l_pre = list(iter_pre)
        l_suc = list(iter_suc)

        if len(l_pre) == 0:
            G.add_edge('SRC', node, weight=0)

        elif len(l_suc) == 0:
            G.add_edge(node, 'SINK', weight=0)

    return src, sink

def find_crit_path(G: nx.DiGraph):
    path = nx.algorithms.dag.dag_longest_path_length(G, weight=None, default_weight=1)
    return path + 1


def generate_dependency_graph(G: nx.DiGraph):
    NotImplemented

def generate_ILP(G: nx.DiGraph):
    NotImplemented


def check_inputs(edgelist_path, mem_usage, objective):
    if edgelist_path == '':
        print('Please specify path to edge list.')
        sys.exit()

    if mem_usage == 0:
        print('Please specify maximum memory usage.')
        sys.exit()

    if objective == '':
        print('Please specify an objective.')
        sys.exit()
    

if __name__ == "__main__":
    main(sys.argv[1:])