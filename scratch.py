#!/usr/bin/env python3
import networkx as nx

def main():
    G = nx.DiGraph()
    G.add_node(1)
   # G.add_nodes_from([1, 2])
    #G.add_edge(1, 2, weight=2)

    print(G.number_of_nodes())




if __name__ == '__main__':
    main()