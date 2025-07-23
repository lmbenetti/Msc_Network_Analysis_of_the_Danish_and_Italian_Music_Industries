# This script takes the genre matrix and the backboning results and outputs a genre dendrogram.

import numpy as np
import pandas as pd
import networkx as nx
import seaborn as sns
from lib import torch_nvd as nvd
from scipy.cluster import hierarchy
from matplotlib import pyplot as plt

nodes = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep = "\t").set_index("id")
# Normalization not to let this being dominated by prolific bands
nodes = (nodes.T / nodes.sum(axis = 1)).T.fillna(0.0)
# Normalization not to let this being dominated by popular genres
nodes = nodes / nodes.sum(axis = 0)

edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep = "\t")
edges = nx.from_pandas_edgelist(edges, source = "src", target = "trg", edge_attr = ["nij", "score"])

# Remove genres without enough bands (more than 1% of the network)
genres = (nodes > 0).sum()
genres = genres[genres > np.ceil(nodes.shape[0] / 100)]
nodes = nodes[genres.index].reset_index()

nodelist = list(nodes["id"].sort_values())
nodemap = {nodelist[i]: i for i in range(len(nodelist))}
nodes["id"] = nodes["id"].map(nodemap)
nodes = nodes.sort_values(by = "id").set_index("id")
nodes = nodes.reindex(sorted(nodes.columns), axis = 1)
genremap = {i: nodes.columns[i] for i in range(len(nodes.columns))}
edges = nx.relabel_nodes(edges, nodemap)

"""This fixes the issue of nodes with super high ID numbers. 
If a nodes has an ID greater than len(nodes) then remove it """
for i in list(edges.nodes):  
    if i > len(nodes):  
        edges.remove_node(i)

tensor = nvd.make_tensor(edges, nodes)
Linv = nvd._Linv(tensor)

genre_dist_matrix = nvd._pairwise_distances(tensor, Linv)
genre_dist_matrix = genre_dist_matrix.cpu().numpy()
genre_dist_matrix = genre_dist_matrix + genre_dist_matrix.T
genre_dist_matrix = pd.DataFrame(data = genre_dist_matrix, index = [genremap[i] for i in range(len(genremap))], columns = [genremap[i] for i in range(len(genremap))])

sim_matrix = 1 / np.exp(genre_dist_matrix)

row_linkage = hierarchy.linkage(genre_dist_matrix.values[np.triu_indices(genre_dist_matrix.shape[0], k = 1)], optimal_ordering = True, method = "ward")
col_linkage = hierarchy.linkage(genre_dist_matrix.values[np.triu_indices(genre_dist_matrix.shape[0], k = 1)], optimal_ordering = True, method = "ward")

sns_plot = sns.clustermap(sim_matrix, row_linkage = row_linkage, col_linkage = col_linkage, cmap = "Reds_r", yticklabels = True, xticklabels = False, vmin = 0.5, vmax = 1)
#plt.savefig("outputs/figures/fig13.png")
plt.show()