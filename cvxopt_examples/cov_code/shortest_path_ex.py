import networkx as nx
G = nx.DiGraph()
G.add_nodes_from(['v1', 'v2', 'v3', 'v4', 'v5'])
G.add_weighted_edges_from([('v1', 'v2', 40.0),
                           ('v1', 'v3', 20.0), ('v2', 'v4', 10.0),
                           ('v2', 'v5', 25.0), ('v3', 'v2', 15.0),
                           ('v3', 'v5', 35.0), ('v4', 'v5', 20.0)])
print(nx.dijkstra_path(G, 'v1', 'v4'))
