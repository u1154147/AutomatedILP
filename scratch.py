#!/usr/bin/env python3
import networkx as nx
import run

def main():
    G = nx.DiGraph()
    G.add_node(1)
    G.add_node(2)
   # G.add_nodes_from([1, 2])
    #G.add_edge(1, 2, weight=2)

    G = nx.read_weighted_edgelist('rand_DFG_s10_1.edgelist', create_using=nx.DiGraph)
    
    l = run.generate_ILP_edges(G)

    print(l)


if __name__ == '__main__':
    main()