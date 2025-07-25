# This script takes the merged network with backboning results and the merged ids and outputs a tsv with the 
# cross conutry and entropy rank. This data was used to manually construct table 9.

import pandas as pd
import numpy as np

id_df = pd.read_csv('merged_network/merged_bands_ids.tsv', sep='\t')
network = pd.read_csv('merged_network/merged_backboning_result.tsv', sep='\t', dtype={'src': str, 'trg': str})

network = network.drop(columns=['nij', 'score', 'sdev_cij'], axis=1)

output = id_df[['artist_id','band', 'country']].copy()
output['italian_count'] = 0
output['danish_count'] = 0
output['rank'] = 0
output['entropy'] = 0
output['artist_id'] = output['artist_id'].astype(str)

ids_dict = dict(zip(output['artist_id'], output['country']))

def row_counter(row):
    src, trg = row[0], row[1]
    src_country = ids_dict.get(src, None)
    trg_country = ids_dict.get(trg, None)
    if trg_country is not None:
        if src_country == "Italy":
            output.loc[output["artist_id"] == trg, "italian_count"] += 1
        else:
            output.loc[output["artist_id"] == trg, "danish_count"] += 1
    if src_country is not None:
        if trg_country == "Italy":
            output.loc[output["artist_id"] == src, "italian_count"] += 1
        else:
            output.loc[output["artist_id"] == src, "danish_count"] += 1

def row_rank_calculator(row):
    connections_sum = row[3]+row[4]
    danish_rank = round(row[3]/connections_sum, 2)
    italian_rank =  round(row[4]/connections_sum, 2)
    if row[2] == 'Italy':
        output.loc[output["artist_id"] == row[0], "rank"] = italian_rank
    else:
        output.loc[output["artist_id"] == row[0], "rank"] = danish_rank

def row_entropy_calculator(row):
    connection_counts = [row[3], row[4]] #in case of more nationalities, more indexes can be added.
    total = sum(connection_counts)
    probs = [count / total for count in connection_counts if count > 0]
    entropy = round(-sum(p * np.log2(p) for p in probs), 2)
    output.loc[output["artist_id"] == row[0], "entropy"] = entropy


for row in network.values:
    row_counter(row)
for row in output.values:
    row_rank_calculator(row)
for row in output.values:
    row_entropy_calculator(row)


output = output.sort_values(by=["entropy"], ascending=False)

output.to_csv('outputs/plots/table9.tsv', sep='\t', index=False)
