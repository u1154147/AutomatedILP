#!/usr/bin/python 

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
        temp_graph = nx.read_weighted_edgelist(edgelist_path)

    except FileNotFoundError:
        print("Unable to locate edge list. Please enter correct file location.")
        sys.exit()

    #print(list(G.edges(data=True)))

    G = nx.DiGraph()
    for (u, v, data) in temp_graph.edges(data=True):
        G.add_edge(u, v, weight=data['weight'])


    options = {
        'node_size': 1500,
        'arrowstyle': '-|>',
        'arrowsize': 12,
    }


    edge_labels=dict([((u,v,),int(d['weight'])) for u,v,d in G.edges(data=True)]) # Mainly used to get only the weight out of the 'weight' dict. 

    pos = nx.spring_layout(G)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
    nx.draw(G, pos=pos, with_labels=True, **options)
    plt.show()
    


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