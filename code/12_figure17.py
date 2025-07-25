# This script takes the labels and genres matrices, the label-genres releases and outputs a
# nestedness graph.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Getting labels
labels = pd.read_csv("danish_network/danish_labels_matrix.tsv", sep= "\t")
labels_copy = labels.copy().drop(columns=["id"])
column_sums = labels_copy.sum(axis=0).sort_values(ascending=False)
result_df = column_sums.reset_index()
result_df.columns = ["label", "releases"]
labels = result_df
labels = labels[~labels["label"].str.contains("Not on label", case=False, na=False)] #We delete not on label
labels = labels[labels["releases"] >= 5] #treshold

#Getting genres
genre = pd.read_csv("danish_network/danish_genre_matrix.tsv", sep="\t")
column_sums = genre.drop(columns=["id"]).sum(axis=0).sort_values(ascending=False)
result_df = column_sums.reset_index()
result_df.columns = ["genre", "releases"]
genre = result_df
#genre = genre[genre["releases"] >= 0] #treshold


releases = pd.read_csv("danish_network/labels_genres_danish.tsv", sep="\t")


nestedness_matrix = pd.DataFrame(0, index=labels['label'], columns=genre['genre'])
#print(nestedness_matrix)

for release in releases.values:
    if release[3] in labels.values:
        for i in range(4,(len(release)-1)):
            if pd.isna(release[i]):
                continue
            else:
                nestedness_matrix.loc[release[3], release[i]] = 1

nestedness_matrix = nestedness_matrix.fillna(0)
# print(nestedness_matrix.shape)
# print(nestedness_matrix.values.sum())

plt.figure(figsize=(30, 30)) 
sns.heatmap(nestedness_matrix, cmap='Reds', linewidths=0.5)
plt.xticks(rotation=45, ha='right')  
plt.yticks(rotation=0)  
plt.title('Genre Label Matrix')
plt.xlabel('Genre')
plt.ylabel('Label')
plt.tight_layout()
plt.show()

def compute_nodf(matrix):
    """Compute the NODF nestedness metric"""
    matrix = matrix.values  # Convert DataFrame to NumPy array
    n_rows, n_cols = matrix.shape
    nodf = 0
    count = 0

    # Row-wise nestedness
    for i in range(n_rows):
        for j in range(i + 1, n_rows):
            if matrix[i].sum() > matrix[j].sum():  # Check if i has more than j
                overlap = np.sum(matrix[j] * matrix[i]) / matrix[j].sum() if matrix[j].sum() > 0 else 0
                nodf += overlap
                count += 1

    # Column-wise nestedness
    for i in range(n_cols):
        for j in range(i + 1, n_cols):
            if matrix[:, i].sum() > matrix[:, j].sum():
                overlap = np.sum(matrix[:, j] * matrix[:, i]) / matrix[:, j].sum() if matrix[:, j].sum() > 0 else 0
                nodf += overlap
                count += 1

    return nodf / count if count > 0 else 0

# Compute and print the nestedness score
nestedness_score = compute_nodf(nestedness_matrix)
print(f"Nestedness (NODF) Score: {nestedness_score:.4f}")

