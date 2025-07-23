# This script takes the year and the genre matrix and the backboning results. It outputs a dendrogram, a csv
# with the years clustered and the cluster each genre corresponds to. Figure 14 was build in Canvas using 
# this information.

import torch
import numpy as np
import pandas as pd
import networkx as nx
import seaborn as sns
from lib import torch_nvd as nvd
from collections import defaultdict
from matplotlib import pyplot as plt

def corr(tensor, i, j, W = None):
   src_ = tensor.node_vects[:,i] - torch.mean(tensor.node_vects[:,i])
   trg_ = tensor.node_vects[:,j] - torch.mean(tensor.node_vects[:,j])
   numerator = (W * torch.outer(src_, trg_)).sum()
   denominator_src = torch.sqrt((W * torch.outer(src_, src_)).sum())
   denominator_trg = torch.sqrt((W * torch.outer(trg_, trg_)).sum())
   return numerator / (denominator_src * denominator_trg)

nodes = pd.read_csv("danish_network/danish_years_matrix.tsv", sep = "\t")
edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep = "\t", dtype = {"src": int, "trg": int})
edges = nx.from_pandas_edgelist(edges, source = "src", target = "trg", edge_attr = ["nij", "score"])

nodelist = list(nodes["id"].sort_values())
nodemap = {nodelist[i]: i for i in range(len(nodelist))}
nodes["id"] = nodes["id"].map(nodemap)
nodes = nodes.sort_values(by = "id").set_index("id")
nodes = nodes.reindex(sorted(nodes.columns), axis = 1)
genremap = {i: nodes.columns[i] for i in range(len(nodes.columns))}
edges = nx.relabel_nodes(edges, nodemap)

nodes /= nodes.sum()

# reverse_nodemap = {v: k for k, v in nodemap.items()}
# print("Original artist_id for internal node 381:", reverse_nodemap[414])

# edges.add_edge(414, 415, nij=0, score=0.0)

"""This fixes the issue of nodes with super high ID numbers. 
If a nodes has an ID greater than len(nodes) then remove it """
# for i in list(edges.nodes):  
#     if i > len(nodes):
#         print(f"Removing node {i}")  
#         edges.remove_node(i)

tensor = nvd.make_tensor(edges, nodes)
Linv = nvd._Linv(tensor)

# print(tensor.node_vects.shape)
# print(nodes.shape)  # Should match the expected number of nodes
# print(nodes.index.max())  # Check if max index is off
# print(Linv.shape)  # Should be (415, 415)
# print(set(nodes.index) - set(edges.nodes))

merges_at_distance = {}

neighbor_distances = pd.DataFrame(
   data = [
      (
         set([i,]),
         set([i + 1,]),
         nvd.ge(tensor.node_vects[:,i], tensor.node_vects[:,i + 1], Linv).cpu().numpy()
      ) for i in range(nodes.shape[1] - 1)
   ],
   columns = ("left", "right", "distance")
)

merge_id = nodes.shape[1]

while neighbor_distances.shape[0] > 1:
   merged_index = neighbor_distances["distance"].argmin()
   if merged_index < (neighbor_distances.shape[0] - 1):
      adjacent_index = neighbor_distances.index[merged_index + 1]
      neighbor_distances.loc[adjacent_index, "left"] = neighbor_distances.loc[adjacent_index, "left"].union(neighbor_distances.iloc[merged_index]["left"])
      neighbor_distances.loc[adjacent_index, "distance"] = nvd.ge(
         tensor.node_vects[:,list(neighbor_distances.loc[adjacent_index, "left"])].mean(axis = 1),
         tensor.node_vects[:,list(neighbor_distances.loc[adjacent_index, "right"])].mean(axis = 1),
         Linv
      ).cpu().numpy()
      merged_set = neighbor_distances.loc[adjacent_index, "left"]
   if merged_index > 0:
      adjacent_index = neighbor_distances.index[merged_index - 1]
      neighbor_distances.loc[adjacent_index, "right"] = neighbor_distances.loc[adjacent_index, "right"].union(neighbor_distances.iloc[merged_index]["right"])
      neighbor_distances.loc[adjacent_index, "distance"] = nvd.ge(
         tensor.node_vects[:,list(neighbor_distances.loc[adjacent_index, "left"])].mean(axis = 1),
         tensor.node_vects[:,list(neighbor_distances.loc[adjacent_index, "right"])].mean(axis = 1),
         Linv
      ).cpu().numpy()
      merged_set = neighbor_distances.loc[adjacent_index, "right"]
   merges_at_distance[frozenset(merged_set)] = [
      frozenset(neighbor_distances.iloc[merged_index]["left"]),
      frozenset(neighbor_distances.iloc[merged_index]["right"]),
      float(neighbor_distances.iloc[merged_index]["distance"]),
      merge_id,
      len(merged_set)
   ]
   merge_id += 1
   neighbor_distances = neighbor_distances.drop(index = neighbor_distances.iloc[merged_index].name)

merges_at_distance[frozenset(neighbor_distances.iloc[0]["left"] | neighbor_distances.iloc[0]["right"])] = [
   frozenset(neighbor_distances.iloc[0]["left"]),
   frozenset(neighbor_distances.iloc[0]["right"]),
   float(neighbor_distances.iloc[0]["distance"]),
   merge_id,
   nodes.shape[1]
]

columns = ("node", "child1", "child2", "y_coordinate", "node_id", "size")
ys = defaultdict(float)

hierarchy = []
for merge in merges_at_distance:
   merge_y = max(merges_at_distance[merge][2], ys[merges_at_distance[merge][0]], ys[merges_at_distance[merge][1]])
   hierarchy.append((
      merge,
      merges_at_distance[merge][0],
      merges_at_distance[merge][1],
      merge_y,
      merges_at_distance[merge][3],
      merges_at_distance[merge][4]
   ))
   ys[merge] = merge_y

hierarchy = pd.DataFrame(data = hierarchy, columns = columns)

hierarchy["node"] = hierarchy["node"].map(tuple)
hierarchy["child1"] = hierarchy["child1"].map(tuple)
hierarchy["child2"] = hierarchy["child2"].map(tuple)
hierarchy = hierarchy.set_index("node")

hierarchy["child1"] = hierarchy["child1"].map(lambda x: x[0] if len(x) == 1 else hierarchy.loc[[x], "node_id"].iloc[0])
hierarchy["child2"] = hierarchy["child2"].map(lambda x: x[0] if len(x) == 1 else hierarchy.loc[[x], "node_id"].iloc[0])

year_dist_matrix = nvd._pairwise_distances(tensor, Linv)
year_dist_matrix = year_dist_matrix.cpu().numpy()
year_dist_matrix = year_dist_matrix + year_dist_matrix.T
year_dist_matrix = pd.DataFrame(data = year_dist_matrix, index = [genremap[i] for i in range(len(genremap))], columns = [genremap[i] for i in range(len(genremap))])
sim_matrix = 1 / np.exp(year_dist_matrix)

sns_plot = sns.clustermap(sim_matrix, row_linkage = hierarchy[["child1", "child2", "y_coordinate", "size"]].values, col_linkage = hierarchy[["child1", "child2", "y_coordinate", "size"]].values, cmap = "Reds_r", yticklabels = False, xticklabels = True)
plt.savefig("outputs/figures/fig14.pdf")

hierarchy = hierarchy.reset_index()
hierarchy["years"] = hierarchy["node"].map(lambda x: tuple(nodes.columns[y] for y in x))

cluster_sizes = hierarchy.set_index("node_id")["size"].to_dict()
cluster_sizes.update({i: 1 for i in range(nodes.shape[1])})
size_threshold = 10
final_cluster_ids = set()
ignore_cluster_ids = set()

for index, row in hierarchy.iterrows():
   if row["child1"] in ignore_cluster_ids or row["child2"] in ignore_cluster_ids:
      if not row["child1"] in ignore_cluster_ids:
         final_cluster_ids.add(row["child1"])
      if not row["child2"] in ignore_cluster_ids:
         final_cluster_ids.add(row["child2"])
      ignore_cluster_ids.add(row["node_id"])
      continue
   # 1) Always accept adding a single year
   if cluster_sizes[row["child1"]] == 1 or cluster_sizes[row["child2"]] == 1: 
      continue
   # 2) Reject merging two non-singleton clusters if their size is > x (with x = 10)
   if cluster_sizes[row["child1"]] > size_threshold or cluster_sizes[row["child2"]] > size_threshold:
      # 3) Once a cluster is rejected, ignore all its subsequent merges
      ignore_cluster_ids.add(row["node_id"])
      # 4) Once a merge is rejected, finalize its two subclusters as final clusters
      final_cluster_ids.add(row["child1"])
      final_cluster_ids.add(row["child2"])

hierarchy_years = hierarchy.set_index("node_id")["years"].to_dict()
eras = []
for final_cluster_id in final_cluster_ids:
   if final_cluster_id < nodes.shape[1]:
      eras.append((nodes.columns[final_cluster_id], nodes.columns[final_cluster_id]))
   else:
      eras.append((min(hierarchy_years[final_cluster_id]), max(hierarchy_years[final_cluster_id])))

eras = pd.DataFrame(data = eras, columns = ("start", "end"))
eras.sort_values(by = "start").to_csv("outputs/plots/fig14_cuts.csv", sep = ",", index = False)

genres = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep = "\t")

genrelist = ["id",
   "Rock", "Pop", "Electronic", "Vocal", "Chanson", "Ballad", "Pop Rock", "Jazz", "Latin", "Disco", "House", "Synth-pop", "Classical", "Folk",
   "Prog Rock", "Alternative Rock", "Techno", "Hip Hop", "Blues", "Schlager",
   "Beat", "Funk", "Punk", "Indie Rock", "Folk Rock", "Rock & Roll", "New Wave", "Reggae", "Soul", "Samba", "Heavy Metal",
   "Fusion", "Opera","Twist","Folk, World, & Country", "Europop", "Trance", "Children's"
]

genres = genres[genrelist]
nodelist = list(genres["id"].sort_values())
nodemap = {nodelist[i]: i for i in range(len(nodelist))}
genres["id"] = genres["id"].map(nodemap)
genres = genres.sort_values(by = "id").set_index("id")
genres = genres.reindex(sorted(genres.columns), axis = 1)
genremap = {i: genres.columns[i] for i in range(len(genres.columns))}

eras_df = pd.DataFrame()
for index, row in eras.sort_values(by = "start").iterrows():
   if (int(row["end"]) - int(row["start"])) > 4:
      eras_df[f"{row['start']}-{row['end']}"] = nodes.loc[:,row["start"]:row["end"]].sum(axis = 1)

eramap = {i + len(genremap): eras_df.columns[i] for i in range(len(eras_df.columns))}
eras_df /= eras_df.sum()

tensor = nvd.make_tensor(edges, genres.join(eras_df))
Linv = nvd._Linv(tensor)

distance_matrix = torch.zeros(genres.shape[1], eras_df.shape[1], device = "cpu")
for i in range(genres.shape[1]):
   for j in range(eras_df.shape[1]):
      distance_matrix[i, j] = nvd.ge(tensor.node_vects[:,i], tensor.node_vects[:,genres.shape[1] + j], Linv)

distance_matrix = pd.DataFrame(data = distance_matrix.cpu().numpy(), index = genres.columns, columns = eras_df.columns)
distance_matrix = (distance_matrix.T / distance_matrix.mean(axis = 1)).T

print("Dominant Genres per era:")
print(distance_matrix.idxmin(axis = 1).sort_values())
