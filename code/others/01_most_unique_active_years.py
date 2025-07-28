# This code takes the bipartite network and outputs the mode of unique active
#  years per band and the most unique active years per band and artist

import pandas as pd
from scipy.stats import mode


df = pd.read_csv("danish_network/danish_bipartite.tsv", sep="\t")

band_activity = df.groupby('band')['year'].nunique()
mode_result = mode(band_activity, keepdims=True)
print(f"The mode of unique active years per band is: {mode_result.mode[0]}")


# Find the band with the most unique active years
most_active_band = band_activity.idxmax()
most_active_years = band_activity.max()

print(f"Band with most unique active years: {most_active_band} ({most_active_years} years)")

artist_activity = band_activity = df.groupby('artist')['year'].nunique()

most_active_artist = artist_activity.idxmax()
most_active_years = artist_activity.max()

print(f"Artist with most unique active years: {most_active_artist} ({most_active_years} years)")



