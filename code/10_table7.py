# This script takes:
# - The full network
# - The genre matrix
# - The labels matrix
# - The years matrix
# of both countries and outputs a csv file used to create table 7 and figures 16 and 17 with R.

import random
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine

def output(edges, genres, labels, years, country):
    # Normalization not to let this being dominated by prolific bands
    genres = (genres.T / genres.sum(axis = 1)).T.fillna(0.0)
    # Normalization not to let this being dominated by popular genres
    genres = genres / genres.sum(axis = 0)

    genres = genres.T[(genres > 0).sum() > 10].T
    genres = genres[genres.sum(axis = 1) > 0]
    # Convert labels to a dictionary of sets (each band ID maps to a set of labels)
    labels = labels.unstack().reset_index().set_index("id")
    labels = labels.loc[labels[0] == 1, "level_0"]
    labels = labels.groupby(level=0).apply(set).to_dict()
    years = years.dot(years.T).unstack()
    years.index.names = ("src", "trg")
    years = years[years.index.get_level_values(0) != years.index.get_level_values(1)]
    years = np.log(years + 1)

    edges["score"] = 1 - edges["score"]
    edges["score"] += edges.loc[edges["score"] > 0, "score"].min()
    edges["score"] = np.log(edges["score"])
    edges["score"] *= -1
    edges["score"] /= edges["score"].max()


    edges = edges[edges["src"].isin(labels) & edges["trg"].isin(labels) & edges["src"].isin(genres.index) & edges["trg"].isin(genres.index)]
    edges = edges[edges["src"].isin(genres.index) & edges["trg"].isin(genres.index)]


    nodes = list(set(edges["src"]) | set(edges["trg"]))
    positive_sample = set(map(tuple, list(pd.concat([edges[["src", "trg"]], edges[["src", "trg"]].rename(columns = {"src": "trg", "trg": "src"})]).values)))
    negative_sample = set([tuple(sorted(random.sample(nodes, 2))) for _ in range(len(positive_sample))])
    negative_sample = list(negative_sample)[:edges.shape[0]]
    negative_sample = pd.DataFrame(data = [(x[0], x[1], 0, 0) for x in negative_sample], columns = edges.columns)
    edges = pd.concat([edges, negative_sample])

    edges["exists"] = (edges["nij"] > 0).astype(int)
    edges["genre_sim"] = edges.apply(lambda x: 1 - cosine(genres.loc[x["src"]], genres.loc[x["trg"]]), axis = 1)
    # Compute label similarity (1 if they share at least one label)
    edges["label_sim"] = edges.apply(lambda x: int(bool(labels.get(x["src"], set()) & labels.get(x["trg"], set()))), axis=1)
    edges["year_sim"] = edges.apply(lambda x: years.loc[x["src"], x["trg"]], axis = 1)

    edges.drop(["src", "trg"], axis = 1).to_csv(f"outputs/plots/{country}_table7.csv", sep = ",", index = False)



# Paths for Danish network
danish_edges = pd.read_csv("danish_network/danish_band_projection_full.tsv", sep = "\t")
danish_edges = danish_edges.drop("sdev_cij", axis = "columns")
danish_genres = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep = "\t").set_index("id")
danish_labels = pd.read_csv("danish_network/danish_labels_matrix.tsv", sep = "\t").set_index("id")
danish_years = pd.read_csv("danish_network/danish_years_matrix.tsv", sep = "\t").set_index("id")

# Paths for Italian network
italian_edges = pd.read_csv("italian_network/italian_band_projection_full.tsv", sep = "\t")
italian_genres = pd.read_csv("italian_network/italian_genre_matrix.tsv", sep = "\t").set_index("id")
italian_labels = pd.read_csv("italian_network/italian_labels_matrix.tsv", sep = "\t").set_index("id")
italian_years = pd.read_csv("italian_network/italian_years_matrix.tsv", sep = "\t").set_index("id")

output(danish_edges,danish_genres,danish_labels,danish_years,"danish")
output(italian_edges,italian_genres,italian_labels,italian_years, "italian")
