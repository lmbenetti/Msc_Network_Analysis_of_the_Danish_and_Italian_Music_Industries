#This code takes the two bipartite networks, the two artists projections and the two 
# backboning results and outputs 16 csv files  that are used in the Gnuplot script file called 
# "03_figure6_figure7.gp" and "04_figure8.gp"

import pandas as pd
import networkx as nx
from collections import Counter

danish_bipartite = pd.read_csv("danish_network/danish_bipartite.tsv", sep= "\t")
italian_bipartite = pd.read_csv("italian_network/italian_bipartite.tsv", sep= "\t")

danish_artist_projection = pd.read_csv("danish_network/danish_artist_projection.tsv", sep="\t")
danish_bb_results = pd.read_csv("danish_network/danish_backboning_result.tsv", sep="\t")

italian_artist_projection = pd.read_csv("italian_network/italian_artist_projection.tsv", sep="\t")
italian_bb_results = pd.read_csv("italian_network/italian_backboning_results.tsv", sep="\t")

def fig6_fig7_output_generator(df, name):    
    band_ccdf = df.groupby(by = "band").size().sort_values(ascending = False).value_counts(sort = False).reset_index()
    band_ccdf["cumsum"] = band_ccdf["count"].cumsum()
    band_ccdf["cumsum"] /= band_ccdf["cumsum"].max()
    band_ccdf.to_csv(f"outputs/plots/{name}_7b.csv", sep = ",", index = False)

    artist_ccdf = df.groupby(by = "artist").size().sort_values(ascending = False).value_counts(sort = False).reset_index()
    artist_ccdf["cumsum"] = artist_ccdf["count"].cumsum()
    artist_ccdf["cumsum"] /= artist_ccdf["cumsum"].max()
    artist_ccdf.to_csv(f"outputs/plots/{name}_7a.csv", sep = ",", index = False)

    df[["band", "year"]].drop_duplicates().groupby(by = "year").size().reset_index().to_csv(f"outputs/plots/{name}_6a_bands.csv", sep = ",", index = False)
    df[["artist", "year"]].drop_duplicates().groupby(by = "year").size().reset_index().to_csv(f"outputs/plots/{name}_6a_artists.csv", sep = ",", index = False)

    df[["band", "year"]].drop_duplicates().groupby(by = "band").size().sort_values().value_counts(sort = False).reset_index().to_csv(f"outputs/plots/{name}_6b_bands.csv", sep = ",", index = False)
    df[["artist", "year"]].drop_duplicates().groupby(by = "artist").size().sort_values().value_counts(sort = False).reset_index().to_csv(f"outputs/plots/{name}_6b_artists.csv", sep = ",", index = False)

def fig8_output_generator(artist_projection,bb_results,name):
    #Fig8a
    G = nx.from_pandas_edgelist(artist_projection, source = "src", target = "trg", edge_attr = True)
    ccdf = Counter(dict(nx.degree(G)).values())
    ccdf = pd.DataFrame(data = [(x, ccdf[x]) for x in ccdf], columns = ("k", "count")).sort_values(by = "k", ascending = False)
    ccdf["cumsum"] = ccdf["count"].cumsum()
    ccdf["cumsum"] /= ccdf["cumsum"].max()
    ccdf.to_csv(f"outputs/plots/{name}_figs8a.csv", sep = ",", index = False)
    
    #Fig8b
    G = nx.from_pandas_edgelist(bb_results, source = "src", target = "trg", edge_attr = True)
    ccdf = Counter(dict(nx.degree(G)).values())
    ccdf = pd.DataFrame(data = [(x, ccdf[x]) for x in ccdf], columns = ("k", "count")).sort_values(by = "k", ascending = False)
    ccdf["cumsum"] = ccdf["count"].cumsum()
    ccdf["cumsum"] /= ccdf["cumsum"].max()
    ccdf.to_csv(f"outputs/plots/{name}_figs8b.csv", sep = ",", index = False)


fig6_fig7_output_generator(danish_bipartite, "danish")
fig6_fig7_output_generator(italian_bipartite, "italian")
fig8_output_generator(danish_artist_projection,danish_bb_results, "danish")
fig8_output_generator(italian_artist_projection,italian_bb_results, "italian")