# This script takes the backboning results and the genre matrix from both networks.
# It calculates the average shannon entropy of the full networks, taking into account the genres
# of the bands a band is connected to.

import pandas as pd
import numpy as np
from scipy.stats import entropy

def top_genre(row):
        if row.sum() == 0:
            return "None"
        return row.idxmax()

def normalized_shannon_entropy(row):
    values = row.values
    total = values.sum()
    if total == 0:
        return 0  # No releases, define entropy as 0
    probabilities = values / total
    ent = entropy(probabilities, base=2)
    max_ent = np.log2(len(values))
    return ent / max_ent

def one_genre_assigner(genre_matrix: pd.DataFrame):
    ids = genre_matrix["id"]
    genre_data = genre_matrix.drop(columns=["id"])
    top_genres = genre_data.apply(top_genre, axis=1)
    output_df = pd.DataFrame({
        "id": ids,
        "genre": top_genres
    })
    return output_df

def count_genre_connections(nodes_df: pd.DataFrame, bb_results: pd.DataFrame, threshold: int):
    id_to_genre = nodes_df.set_index('id')['genre'].to_dict()
    genre_list = sorted(nodes_df['genre'].unique())
    id_genre_counts = {
        node_id: {genre: 0 for genre in genre_list}
        for node_id in id_to_genre
    }
    
    for _, row in bb_results.iterrows():
        src = row['src']
        trg = row['trg']
        
        if src in id_to_genre and trg in id_to_genre:
            genre_trg = id_to_genre[trg]
            genre_src = id_to_genre[src]
            id_genre_counts[src][genre_trg] += 1
            id_genre_counts[trg][genre_src] += 1

    counts_df = pd.DataFrame.from_dict(id_genre_counts, orient='index').reset_index()
    counts_df.rename(columns={'index': 'id'}, inplace=True)

    #Applying threshold 
    counts_df['total_connections'] = counts_df[genre_list].sum(axis=1)
    counts_df = counts_df[counts_df['total_connections'] >= threshold]
    counts_df = counts_df.drop(columns=['total_connections'])
    
    return counts_df


def entropy_printer(genre_connections: pd.DataFrame, nationality: str):
    genre_columns = genre_connections.columns[1:]
    genre_connections["normalized_entropy"] = genre_connections[genre_columns].apply(normalized_shannon_entropy, axis=1)
    average_entropy = genre_connections["normalized_entropy"].mean()
    print(f"Average normalized {nationality} entropy: {average_entropy:.4f}")

def output(genre_matrix: pd.DataFrame, bb_results: pd.DataFrame, nationality: str, threshold:int):
    entropy_printer(count_genre_connections(one_genre_assigner(genre_matrix),bb_results, threshold),nationality)

danish_genre = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep="\t")
danish_bb = pd.read_csv("danish_network/danish_backboning_result.tsv", sep="\t")
italian_genre = pd.read_csv("italian_network/italian_genre_matrix.tsv", sep="\t")
italian_bb = pd.read_csv("italian_network/italian_backboning_results.tsv", sep="\t")


output(danish_genre,danish_bb,"Danish",3)
output(italian_genre,italian_bb,"Italian",3)










