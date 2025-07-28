# This script takes the backboning results and a csv with two columns: id and genre. 
# They correspond to the band id and the genre assigned to that band. It outputs the Genre assortativity.

import networkx as nx
import pandas as pd

genre = pd.read_csv("")
edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep="\t")

G = nx.Graph()

for band in genre.values:
    G.add_node(str(band[0]), genre=band[1])

for edge in edges.values:
    G.add_edge(str(int(edge[0])), str(int(edge[1])))

assortativity = nx.attribute_assortativity_coefficient(G, 'genre')
print(f"Genre assortativity: {assortativity:.3f}")