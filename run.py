#!/usr/bin/env python3

import matplotlib.pyplot as plt
import os
import sys
import getopt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph


line_start = '  '


def main(argv):
    args = sys.argv

    edgelist_path, max_memory, objective, max_latency = read_args(argv)

    check_inputs(edgelist_path, max_memory, objective) 

    try:  
        G = nx.read_weighted_edgelist(edgelist_path, create_using=nx.DiGraph)

    except FileNotFoundError:
        print("Unable to locate edge list. Please enter correct file location.")
        sys.exit(2)

    # options = {
    #     'node_size': 1500,
    #     'arrowstyle': '-|>',
    #     'arrowsize': 12,
    # }

    crit_path_len = find_crit_path(G)
    gen = nx.algorithms.dag.all_topological_sorts(G)
    write_ILP_file(G, max_latency)

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

    # sys.exit(0)

    # edge_labels=dict([((u,v,),int(d['weight'])) for u,v,d in G.edges(data=True)]) # Mainly used to get only the weight out of the 'weight' dict. 
    # pos = nx.spiral_layout(G)
    # nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
    # nx.draw(G, pos=pos, with_labels=True, **options)
    # plt.show()

def read_args(argv):
    edgelist_path = ''
    max_memory = 0
    objective = ''
    opts = []
    latency = 0
    try:
        opts, args = getopt.getopt(argv, "hi:m:o:l:", ["ifile=", "memory-usage=", "objective=", "latency="]) # Get command-line inputs
    
    except getopt.GetoptError:
        print ('usage: ' + sys.argv[0] + '-i <input edgelist file> -m <max memory usage allowed> -o <objective> -l <latency>')
        return

    for opt, arg in opts: # Check command-line inputs
        if opt == '-h':
            print ('usage: ' + sys.argv[0] + '-i <input edgelist file> -m <max memory usage allowed> -o <objective> -l <latency>')
            sys.exit(1)

        elif opt in ("-i", "--ifile"):
            edgelist_path = arg

        elif opt in ("-m", "--memory-usage"):
            max_memory = arg

        elif opt in ('-o', '--objective'):
            objective = arg

        elif opt in ('-l', '--latency'):
            latency = arg

    print(objective)
    return edgelist_path, max_memory, objective, latency


def check_edge_weight(G: nx.DiGraph, max_mem: int):
    for edge in G.edges(data=True):
        weight = edge[:-1]

        if weight > max_mem:
            return edge, False

    return True

def write_ILP_file(G: nx.DiGraph, max_latency: int, name = 'ilp_output.lp'):
    with open(name, 'w') as f:
        to_write = []

        nodes, variables_generated = generate_ILP_nodes(G, max_latency)

        header = generate_ILP_header(variables_generated, None)

        edges = generate_ILP_edges(G, max_latency)

        floor = generate_ILP_floor(variables_generated)

        footer = generate_ILP_footer(variables_generated)

        to_write.append(header)
        to_write.append(nodes)
        to_write.append(edges)
        to_write.append(floor)
        to_write.append(footer)

        for l in to_write:
            for line in l:
                f.write(line)


def generate_ILP_header(variables: set, objective: str):
    lines = []
    lines.append('Minimize\n')

    line = line_start # + 'obj: '

    for variable in variables:
        line += variable[-1] + variable + ' + '

    line = line[:-3] + '\n'
    lines.append(line)

    lines.append('Subject to\n')

    return lines


def generate_ILP_nodes(G: nx.DiGraph, max_latency):
    lines = [] 
    variables = set() 
    line_count = 0
    for node in G.nodes:
        line = line_start + 'c' + str(line_count) + ': '
        for i in range(1, int(max_latency) + 1):
            string = ('x' + str(node) + '_' +  str(i) + ' + ')
            variables.add(string[:-3])

            line += string

        line_count += 1
        line = line[:-3] + ' = 1\n' 
        lines.append(line)

    return lines, variables

def generate_ILP_edges(G: nx.DiGraph, max_latency):
    lines = []
    line_count = 0
    for u, v in G.edges:
        line = line_start + 'e' + str(line_count) + ': '
        for i in range(1, int(max_latency) + 1):
            string = (str(i) + 'x' + str(v) + '_' + str(i) + ' + ' )
            line += string

        line = line[:-2]

        for i in range(1, int(max_latency) + 1):
            string = '- ' + str(i) + 'x' + str(u) + '_' + str(i) + ' '
            line += string

        line += '>= 1\n'
        lines.append(line)
        line_count += 1

    return lines

def generate_ILP_floor(variables: set):
    lines = []
    i = 0
    for var in variables:
        line = line_start + 'f' + str(i) +': ' + str(var) + ' >= 0\n'
        lines.append(line)
        i += 1
    
    return lines

def generate_ILP_footer(variables: set):
    lines = []

    lines.append('Integer\n')

    line = '\t'
    for var in variables:
        line += var + ' '
    line += '\n'
    lines.append(line)

    return lines

    
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


def check_inputs(edgelist_path, mem_usage, objective):
    if edgelist_path == '':
        print('Please specify path to edge list.')
        sys.exit(1)

    if mem_usage == 0:
        print('Please specify maximum memory usage.')
        sys.exit(1)

    if objective == '' or (objective != 'latency' and objective != 'memory'):
        print('Please specify an objective.')
        sys.exit(1)
    

if __name__ == "__main__":
    main(sys.argv[1:])