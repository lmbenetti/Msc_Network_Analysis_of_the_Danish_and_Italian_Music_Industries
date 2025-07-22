#This code takes the two bipartite networks and outputs 12 csv files 
#that are used in the Gnuplot script file called "03_figure6_figure7".

import pandas as pd

df = pd.read_csv("danish_network/danish_bipartite.tsv", sep= "\t")
df2 = pd.read_csv("italian_network/italian_bipartite.tsv", sep= "\t")

def output_generator(df, name):    
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

output_generator(df, "danish")
output_generator(df2, "italian")