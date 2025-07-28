# This script takes the backboning results and a csv with two columns: id and genre. 
# They correspond to the band id and the genre assigned to that band. It outputs the Genre modularity.


import pandas as pd
import networkx as nx
from networkx.algorithms.community import modularity
from collections import defaultdict

edges_df = pd.read_csv("danish_network/danish_backboning_result.tsv")
clusters_df = pd.read_csv("")

edges_df = edges_df.drop(columns=['nij','score','sdev_cij'])
edges = list(edges_df.itertuples(index=False, name=None))

G = nx.Graph()
G.add_edges_from(edges)

cluster_dict = defaultdict(set)
for node_id, genre in zip(clusters_df['id'], clusters_df['genre']):
    cluster_dict[genre].add(node_id)
communities = list(cluster_dict.values())

mod = modularity(G, communities)
print(f"Modularity: {mod:.4f}")