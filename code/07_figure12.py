# This script takes the backboning results and the year matrix and outputs a csv and .gp file
# used to make figure 12

import torch, sys
import numpy as np
import pandas as pd
import networkx as nx
from lib import torch_nvd as nvd
import os

def bootstrap(variance, tensor, i, ER = None):
   better_than_obs = 0
   for _ in range(1000):
      rnd_i = tensor.node_vects[:,i][torch.randperm(tensor.node_vects[:,i].shape[0])]
      rnd_variance = ((torch.outer(rnd_i, rnd_i) * (ER ** 2)).sum() / 2).cpu().item()
      if rnd_variance >= variance:
         better_than_obs += 1
   return better_than_obs / 1000

nodes = pd.read_csv("danish_network/danish_years_matrix.tsv", sep = "\t").set_index("id")
edges = pd.read_csv("danish_network/danish_backboning_result.tsv", sep = "\t")
edges = nx.from_pandas_edgelist(edges, source = "src", target = "trg", edge_attr = ["nij", "score"])

nodes /= nodes.sum()
nodes = nodes.reset_index()

nodelist = list(nodes["id"].sort_values())
nodemap = {nodelist[i]: i for i in range(len(nodelist))}
nodes["id"] = nodes["id"].map(nodemap)
nodes = nodes.sort_values(by = "id").set_index("id")
nodes = nodes.reindex(sorted(nodes.columns), axis = 1)
genremap = {i: nodes.columns[i] for i in range(len(nodes.columns))}
edges = nx.relabel_nodes(edges, nodemap)

tensor = nvd.make_tensor(edges, nodes)
Linv = nvd._Linv(tensor)
ER = nvd._er(tensor, Linv)

year_variances = pd.DataFrame(
   data = [(genremap[i], ((torch.outer(tensor.node_vects[:,i], tensor.node_vects[:,i]) * (ER ** 2)).sum() / 2).cpu().item()) for i in range(len(genremap))],
   columns = ("year", "variance")
)

year_variances["pvalue_color"] = ""

for i in range(tensor.node_vects.shape[1]):
   sys.stderr.write(f"{year_variances.loc[i, "year"]}\r")
   pvalue = bootstrap(year_variances.loc[i, "variance"], tensor, i, ER = ER)
   if pvalue >= 0.99:
      year_variances.loc[i, "pvalue_color"] = "#f46d43"
   elif pvalue >= 0.95:
      year_variances.loc[i, "pvalue_color"] = "#fdae61"
   elif pvalue >= 0.9:
      year_variances.loc[i, "pvalue_color"] = "#fee08b"
   elif pvalue > 0.1:
      year_variances.loc[i, "pvalue_color"] = "#ffffff"
   elif pvalue > 0.05:
      year_variances.loc[i, "pvalue_color"] = "#d9ef8b"
   elif pvalue > 0.01:
      year_variances.loc[i, "pvalue_color"] = "#a6d96a"
   else:
      year_variances.loc[i, "pvalue_color"] = "#66bd63"


with open("code/06_fig12.gp", 'w') as f:
   f.write("""
set terminal pdfcairo enhanced size 3,2.25 crop color solid rounded linewidth 1
set datafile separator ","
set xlabel "Year"
set ylabel "Network Variance"
set xrange [1905:2025]
set yrange [0:1.5]
set output "../outputs/figures/figure12.pdf"
   """)
   for index, row in year_variances.iterrows():
      f.write(f"set object rectangle from {int(row["year"]) - 0.5},0 to {int(row["year"]) + 0.5},1.5 behind fillcolor rgb '{row["pvalue_color"]}' fillstyle solid noborder\n")
   f.write("plot \"../outputs/plots/danish_12.csv\" using 1:2 w lines lc rgb 'black' lw 2 notitle")

year_variances.to_csv("outputs/plots/danish_12.csv", index = False, sep = ",")
sys.stderr.write("\n")