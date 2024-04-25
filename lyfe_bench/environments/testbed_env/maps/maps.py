import json
import os

import networkx as nx

# Get the directory of the current module
module_dir = os.path.dirname(os.path.abspath(__file__))

# Build the full path by joining the module directory and relative path

def uniform_edges(G, edge_weight=1):
    """
    add common edge weights to a graph
    """
    for u, v in G.edges():
        G[u][v]["travel_time"] = edge_weight
    return G

def json_to_complete_graph(path, edge_weight=1):
    """
    create a complete graph from a list of nodes
    """
    absolute_path = os.path.join(module_dir, path)
    nodes = json.load(open(absolute_path, "r"))
    G = nx.complete_graph(nodes)
    return uniform_edges(G, edge_weight=edge_weight)


# Function to calculate L1 distance
def L1_distance(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

def create_L1_graph(vertices):
    """
    Create a graph with L1 distance as edge weights.
    Input: list of tuples of the form (label, coordinates)
    Output: networkx graph
    """
    # Create an empty graph
    G = nx.Graph()

    # Add vertices to the graph
    for label, coords in vertices:
        G.add_node(label, coordinates=coords)


    # Add edges with L1 distance as weight
    for i in range(len(vertices)):
        for j in range(i+1, len(vertices)):
            label1, coords1 = vertices[i]
            label2, coords2 = vertices[j]
            distance = L1_distance(coords1, coords2)
            G.add_edge(label1, label2, weight=distance)

    return G

