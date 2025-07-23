# This script takes the genre matrix and the backboning results of the Danish network and outputs a Latex
# table with the genres with the five highest and lowest variance in the band projection network.
# It also outputs table5.tsv, used for figure 11.

import torch, sys, warnings
import numpy as np
import pandas as pd
import networkx as nx
from lib import torch_nvd as nvd


warnings.filterwarnings("ignore")
device = "cuda" if torch.cuda.is_available() else "cpu"

def output(genre_matrix, bb_results,country):
   #genre_matrix = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep = "\t")
   #edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep = "\t")
   edges = nx.from_pandas_edgelist(bb_results, source = "src", target = "trg", edge_attr = ["nij", "score"])

   # Remove genres without enough bands (more than 1% of the network)
   genres = (genre_matrix > 0).sum()
   genres = genres[genres > np.ceil(genre_matrix.shape[0] / 100)]
   genre_matrix = genre_matrix[genres.index]

   nodelist = list(genre_matrix["id"].sort_values())
   nodemap = {nodelist[i]: i for i in range(len(nodelist))}
   genre_matrix["id"] = genre_matrix["id"].map(nodemap)
   genre_matrix = genre_matrix.sort_values(by = "id").set_index("id")
   genre_matrix = genre_matrix.reindex(sorted(genre_matrix.columns), axis = 1)
   genremap = {i: genre_matrix.columns[i] for i in range(len(genre_matrix.columns))}
   edges = nx.relabel_nodes(edges, nodemap)

   # Normalization not to let this being dominated by prolific bands
   nodes_norm = (genre_matrix.T / genre_matrix.sum(axis = 1)).T.fillna(0.0)
   # Normalization not to let this being dominated by popular genres
   nodes_norm = nodes_norm / nodes_norm.sum(axis = 0)

   """This fixes the issue of nodes with super high ID numbers. 
   If a nodes has an ID greater than len(nodes) then remove it """
   for i in list(edges.nodes):  
      if i > len(genre_matrix):  
         edges.remove_node(i)

   tensor = nvd.make_tensor(edges, nodes_norm)
   Linv = nvd._Linv(tensor)
   ER = nvd._er(tensor, Linv)

   genre_variances = pd.DataFrame(
      data = [(genremap[i], ((torch.outer(tensor.node_vects[:,i], tensor.node_vects[:,i]) * (ER ** 2)).sum() / 2).cpu().item(), 0) for i in range(len(genremap))],
      columns = ("genre", "variance", "above_null")
   )

   ps = genre_matrix.sum(axis = 1).values
   ps = ps / ps.sum()

   for _ in range(1000):
      if _ % 10 == 0:
         sys.stderr.write(f"{100 * _ / 1000:.0f}%\r")
      nodes_rnd = np.zeros(genre_matrix.shape)
      for i in range(nodes_rnd.shape[1]):
         _ = np.unique(np.random.choice(range(genre_matrix.shape[0]), size = genre_matrix.values[:,i].sum(), p = ps), return_counts = True)
         nodes_rnd[_[0], i] = _[1]
      nodes_rnd = np.nan_to_num((nodes_rnd.T / nodes_rnd.sum(axis = 1)).T)
      nodes_rnd /= nodes_rnd.sum(axis = 0)
      tensor.node_vects = torch.tensor(nodes_rnd, dtype = torch.float).double().to(device)
      genre_variances_rnd = {genremap[i]: ((torch.outer(tensor.node_vects[:,i], tensor.node_vects[:,i]) * (ER ** 2)).sum() / 2).cpu().item() for i in range(len(genremap))}
      genre_variances["null"] = genre_variances["genre"].map(genre_variances_rnd)
      genre_variances["above_null"] += genre_variances["variance"] > genre_variances["null"]

   sys.stderr.write("\n")
   genre_variances["above_null"] /= 1000
   genre_variances["bands"] = genre_variances["genre"].map((genre_matrix > 0).sum().to_dict())
   genre_variances = genre_variances.sort_values(by = "variance", ascending = False)

   genre_variances["Country"]="Denmark"
   genre_variances.to_csv(f"outputs/plots/{country}_table5.tsv", sep = "\t", index = False)

   print(f"{country} table: \n")
   print("\\begin{table}")
   print("\\centering")
   print("\\begin{tabular}{l|r}")
   print("Genre & Variance\\\\")
   print("\\hline")

   for index, row in genre_variances.head(5).iterrows():
      if row["above_null"] > 0.999 or row["above_null"] < 0.001:
         stars = "***"
      elif row["above_null"] > 0.99 or row["above_null"] < 0.01:
         stars = "**"
      elif row["above_null"] > 0.95 or row["above_null"] < 0.05:
         stars = "*"
      else:
         stars = ""
      print(f"{row['genre']} & {row['variance']:.3f}$^{{{stars}}}$\\\\")

   print("... & ...\\\\")

   for index, row in genre_variances.tail(5).iterrows():
      if row["above_null"] > 0.999 or row["above_null"] < 0.001:
         stars = "***"
      elif row["above_null"] > 0.99 or row["above_null"] < 0.01:
         stars = "**"
      elif row["above_null"] > 0.95 or row["above_null"] < 0.05:
         stars = "*"
      else:
         stars = ""
      print(f"{row['genre']} & {row['variance']:.3f}$^{{{stars}}}$\\\\")

   print("\\end{tabular}")
   print("\\caption{The genres with the five highest and lowest variance in the band projection network. $^{***} p < 0.001$, $^{**} p < 0.01$, $^{*} p < 0.05$.}")
   print("\\label{tab:genre-variance}")
   print("\\end{table} \n")

danish_genre = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep = "\t")
danish_bb = pd.read_csv("danish_network/danish_backboning_result.tsv", sep = "\t")
italian_genre = pd.read_csv("italian_network/italian_genre_matrix.tsv", sep= "\t")
italian_bb = pd.read_csv("italian_network/italian_backboning_results.tsv", sep= "\t")

output(danish_genre, danish_bb, "danish")
output(italian_genre, italian_bb, "italian")