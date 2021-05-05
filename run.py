#!/usr/bin/env python3

import os
import sys
import getopt
import networkx as nx


line_start = '  '

# The main function that reads in the given file as a Directed Acyclic Graph(DAG), calls functions to build and finally write to a LP file
def main(argv):
    args = sys.argv

    edgelist_path, max_memory, objective, max_latency = read_args(argv)

    check_inputs(edgelist_path, max_memory, objective) 

    try:  
        G = nx.read_weighted_edgelist(edgelist_path, create_using=nx.DiGraph)

    except FileNotFoundError:
        print("Unable to locate edge list. Please enter correct file location.")
        sys.exit(2)

    # Perform checks if graph is obviously not feasible.
    # Reports to user issue found.
    feasible, val = is_feasible(G, max_memory, max_latency)    
    if feasible == 'mem':
        print('Given memory constraints are not feasible.')
        print('Found edge with memory requirements: ' + str(val))
        sys.exit(3)

    elif feasible == 'lat':
        print('Given latency constraints are not feasible.')
        print('Found longest path length: ' + str(val))
        sys.exit(3)

    gen = nx.algorithms.dag.all_topological_sorts(G)
    write_ILP_file(G, max_latency, max_memory, objective=objective)

    # sys.exit(0)

# Read_args reads in the arguments given by the command line, returning them to be used in other functions.
def read_args(argv):
    edgelist_path = ''
    max_memory = -1
    objective = ''
    opts = []
    latency = 0
    try:
        opts, args = getopt.getopt(argv, "hi:m:o:l:", ["ifile=", "memory-usage=", "objective=", "latency="]) # Get command-line inputs
    
    except getopt.GetoptError:
        print ('usage: ' + sys.argv[0] + '-i <input edgelist file> -m <max memory usage allowed> -o <objective> -l <latency>')
        return

    for opt, arg in opts: # Parse command-line inputs
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

    return edgelist_path, max_memory, objective, latency


# is_feasible checks if the given graph can be minimized using the given constraints
# It checks the largest sum of all edges of a single node against the largest memory constraint.
# It also checks the longest path against the maximum latency.
def is_feasible(G: nx.DiGraph, max_mem: int, max_latency: int):
    out_edges = G.out_edges(data=True)

    if max_mem != -1:
        for i in range(1, int(max_latency) + 1):
            line = '' 
            for node in G.nodes:
                total = 0
                for u, v, w in out_edges:
                    if u == node:
                        total +=  int(w['weight'])

                if total > int(max_mem):

                    return 'mem', int(total) 

    # Latency check
    # Have to add 1 to the return value as it's counting edges, not the actual number of nodes which is what we need
    longest_path = nx.dag_longest_path_length(G, weight=None, default_weight=1) + 1
    if int(max_latency) < longest_path:
        return 'lat', longest_path

    return 'feasible', None

# write_ILP_file writes all the lists generated into an actual lp format file for GLPK to solve.
def write_ILP_file(G: nx.DiGraph, max_latency = None, mem_constraint = -1, objective = 'latency', name = 'ilp_output.lp'):
    with open(name, 'w') as f:
        to_write = []

        nodes, variables_generated = generate_ILP_nodes(G, max_latency)

        header = generate_ILP_header(variables_generated, objective=objective)

        if (max_latency is not None):
            edges = generate_ILP_edges(G, max_latency)

        if (mem_constraint != -1):
            weights = generate_ILP_memconstraint(G, mem_constraint, max_latency, objective)

        floor = generate_ILP_floor(variables_generated)

        footer = generate_ILP_footer(variables_generated)


        to_write.append(header)
        to_write.append(nodes)

        if (max_latency is not None):
            to_write.append(edges)

        to_write.append(floor)
        if (mem_constraint != -1):
            to_write.append(weights)

        to_write.append(footer)

        for l in to_write:
            for line in l:
                f.write(line)

# generate_ILP_header creates the LP format headers of Minimize depending
# on the given objective and creates the Subject To section for the constraints
def generate_ILP_header(variables: set, objective = 'latency'):
    lines = []
    lines.append('Minimize\n')

    line = line_start # + 'obj: '

    if objective == 'latency':
        for variable in variables:
            line += variable[-1] + variable + ' + '

        line = line[:-3] + '\n'

    elif objective == 'memory':
        line += 'min_memory\n'

    lines.append(line)

    lines.append('Subject to\n')

    return lines

# generate_ILP_nodes iterates through all nodes to generate a LP constraint like:
# c1: x1_1 + x1_2 + x1_3 = 1 . This ensures that a node only exists once in the entire 
# solution when GLPK solves it.
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

# generate_ILP_edges iterates through all edges to generate a LP constraint like:
# e1: x2_1 + x_2_2 - x1_1 - x1_2 >= 1 . This ensures that dependent nodes come after
# their dependencies. 
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

# generate_ILP_memconstraint iterates through all the edges of all individual nodes to 
# generate a LP constraint for ML-RC like: 
# w1: 3x1_1 + 4x2_1 <= 7  

# or LP constraints for MR-LC:
# w1: mem1 - 3x1_1 - 4x2_1 = 0
# m1: mem1 - min_memory <= 0;

# In the former case this ensures that the sum of all edges coming from one node do not exceed
# the maximum memory constraint. In the latter case it optimizes to find the minimum memory for
# a latency constraint.
def generate_ILP_memconstraint(G: nx.DiGraph, mem_constraint, max_latency, objective):
    lines = []
    line_count = 0
    out_edges = G.out_edges(data=True)

    for i in range(1, int(max_latency) + 1):
        line = '' 
        for node in G.nodes:
            total = 0
            for u, v, w in out_edges:
                if u == node:
                    total +=  int(w['weight'])

            if objective == 'latency':
                var = str(total) + 'x' + node + '_' + str(i)
                line += var + ' + '

            elif objective == 'memory':
                var = str(total) + 'x' + node + '_' + str(i)
                line += var + ' - '

        final = line_start + 'w' + str(i) + ': '
        if objective == 'latency':
            final += line[:-2] + '<= ' + str(mem_constraint) + '\n'

        elif objective == 'memory':
            # final = line[:-2] + '= ' + 'mem' + str(i) + '\n'
            final += 'mem' + str(i) + ' - ' + line[:-2] + '= 0\n'

        lines.append(final)

    if objective == 'memory':
        for i in range(1, int(max_latency) + 1):
            line = line_start + 'm' + str(i) + ': '

            line += 'mem' + str(i) + ' - min_memory <= 0\n'
            lines.append(line)

    return lines

# generate_ILP_floor iterates through all the generated variables from the
# other functions to create LP constraints like:
# x1_1 >= 0
# x1_2 >= 0

# This is to make sure that these variables only take on positive values or zero
# as negative values would not be meaningful.
def generate_ILP_floor(variables: set):
    lines = []
    i = 0
    for var in variables:
        line = line_start + 'f' + str(i) +': ' + str(var) + ' >= 0\n'
        lines.append(line)
        i += 1
    
    return lines

# generate_ILP_footer iterates through all the variables created by the other
# functions and adds them to the bottom as integers, this is to ensure we do not
# get fractional answers from GLPK, only integers.
def generate_ILP_footer(variables: set):
    lines = []

    lines.append('Integer\n')

    line = '\t'
    for var in variables:
        line += var + ' '
    line += '\n'
    lines.append(line)

    return lines

# This checks if we have valid inputs, as in that we have a file path
# an objective, latency and (if needed) memory constraints.
def check_inputs(edgelist_path, mem_usage, objective):
    if edgelist_path == '':
        print('Please specify path to edge list.')
        sys.exit(1)

    # if mem_usage == 0:
    #     print('Please specify maximum memory usage.')
    #     sys.exit(1)

    if objective == '' or (objective != 'latency' and objective != 'memory'):
        print('Please specify an objective. Allowed objectives:')
        print('latency\nmemory')
        sys.exit(1)
    
# Allows running the python script through a shell or other means.
if __name__ == "__main__":
    main(sys.argv[1:])