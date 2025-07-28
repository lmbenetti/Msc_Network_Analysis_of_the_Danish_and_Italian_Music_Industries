# This script takes the average year per band and the backboning results and outputs the year assortativity

import networkx as nx
import pandas as pd

years = pd.read_csv("outputs/danish_average_year.tsv", sep="\t")
edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep="\t")

G = nx.Graph()

for band in years.values:
    G.add_node(str(band[0]), year=band[1])

for edge in edges.values:
    G.add_edge(str(int(edge[0])), str(int(edge[1])))

assortativity = nx.numeric_assortativity_coefficient(G, 'year')
print(f"Year assortativity (numeric): {assortativity:.3f}")