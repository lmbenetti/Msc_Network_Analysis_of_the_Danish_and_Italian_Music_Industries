# This script takes the genre matrix and the backboning results and outputs a Tsne visualization of labels

import numpy as np
import pandas as pd
import networkx as nx
import seaborn as sns
from lib import torch_nvd as nvd
from scipy.cluster import hierarchy
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE


nodes = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep = "\t").set_index("id")
nodes = nodes.loc[:, nodes.sum(axis=0) > 5]

# Normalization not to let this being dominated by prolific bands
nodes = (nodes.T / nodes.sum(axis = 1)).T.fillna(0.0)
# Normalization not to let this being dominated by popular labels
nodes = nodes / nodes.sum(axis = 0)

edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep = "\t")
edges = nx.from_pandas_edgelist(edges, source = "src", target = "trg", edge_attr = ["nij", "score"])

# Remove labels without enough bands (more than 1% of the network)
genres = (nodes > 0).sum()
genres = genres[genres > np.ceil(nodes.shape[0] / 100)]
nodes = nodes[genres.index].reset_index()
nodelist = list(nodes["id"].sort_values())
nodemap = {nodelist[i]: i for i in range(len(nodelist))}
nodes["id"] = nodes["id"].map(nodemap)
nodes = nodes.sort_values(by = "id").set_index("id")
nodes = nodes.reindex(sorted(nodes.columns), axis = 1)
# print(nodes.__len__())
genremap = {i: nodes.columns[i] for i in range(len(nodes.columns))}
edges = nx.relabel_nodes(edges, nodemap)

"""This fixes the issue of nodes with super high ID numbers. 
If a nodes has an ID greater than len(nodes) then remove it """
for i in list(edges.nodes):  
    if i > len(nodes):  
        edges.remove_node(i)

# print(edges.nodes)
tensor = nvd.make_tensor(edges, nodes)
Linv = nvd._Linv(tensor)

genre_dist_matrix = nvd._pairwise_distances(tensor, Linv)
genre_dist_matrix = genre_dist_matrix.cpu().numpy()
genre_dist_matrix = genre_dist_matrix + genre_dist_matrix.T
genre_dist_matrix = pd.DataFrame(data = genre_dist_matrix, index = [genremap[i] for i in range(len(genremap))], columns = [genremap[i] for i in range(len(genremap))])

dist_matrix = genre_dist_matrix.values  

tsne = TSNE(n_components=2, metric="precomputed", perplexity=30, random_state=42, init="random")
tsne_results = tsne.fit_transform(dist_matrix)

tsne_df = pd.DataFrame(tsne_results, index=genre_dist_matrix.index, columns=["x", "y"])

plt.figure(figsize=(10, 7))
sns.scatterplot(x="x", y="y", data=tsne_df)
for label, x, y in zip(tsne_df.index, tsne_df["x"], tsne_df["y"]):
    plt.text(x, y, label, fontsize=9, ha="right", va="bottom")
# plt.title("t-SNE Projection of Record Labels")
plt.show()