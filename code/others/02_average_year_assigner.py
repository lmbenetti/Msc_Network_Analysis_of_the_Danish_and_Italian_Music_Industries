# This script takes the year matrix and outputs a df with the average year of activity per band


import pandas as pd

df = pd.read_csv("danish_network/danish_years_matrix.tsv", sep= "\t")

years = df.columns[1:].astype(int)
weighted_sums = (df.iloc[:, 1:] * years).sum(axis=1)
total_releases = df.iloc[:, 1:].sum(axis=1)
df["average_year"] = weighted_sums / total_releases
df["average_year"] = df["average_year"].fillna(0)  # Set NaN to 0 if no releases
df = df[["id", "average_year"]]
df["average_year"] = df["average_year"].round().astype(int)

df.to_csv("outputs/danish_average_year.tsv", sep="\t", index=False)