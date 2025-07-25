import pandas as pd

df = pd.read_csv("/Users/licho/Documents/ITU/Msc/Msc_Network_Analysis_of_the_Danish_and_Italian_Music_Industries/italian_network/projection_band_full.txt", sep="\t")

df.to_csv("/Users/licho/Documents/ITU/Msc/Msc_Network_Analysis_of_the_Danish_and_Italian_Music_Industries/italian_network/projection_band_full.tsv", sep='\t', index=False)