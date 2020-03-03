import networkx as nx
G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4, 5, 6])
G.add_weighted_edges_from([(1, 2, 5.0), (1, 3, 7.0),
                           (2, 3, 6.0), (2, 4, 3.0), (2, 5, 4.0), (3, 4, 8.0),
                           (3, 5, 2.0), (4, 5, 1.0), (4, 6, 10.0), (5, 6, 9.0)])
T = nx.minimum_spanning_tree(G)
print(T.edges(data=True))
