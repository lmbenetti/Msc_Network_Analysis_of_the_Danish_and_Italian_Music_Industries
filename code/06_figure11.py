import pandas as pd
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

tab5_italy = pd.read_csv("outputs/plots/italian_table5.tsv", sep="\t")
tab5_denmark = pd.read_csv("outputs/plots/danish_table5.tsv", sep="\t")

tab5_italy.columns.values[0] = "genre"
tab5_denmark.columns.values[0] = "genre"

merged = pd.merge(tab5_italy[["genre", "variance"]],
                  tab5_denmark[["genre", "variance"]],
                  on="genre",
                  suffixes=("_italy", "_denmark"))

corr, p_value = spearmanr(merged["variance_italy"], merged["variance_denmark"])

print(f"Spearman correlation: {corr:.4f}")
print(f"P-value: {p_value:.4e}")

plt.figure(figsize=(8, 6))
plt.scatter(merged["variance_italy"], merged["variance_denmark"], alpha=0.7)
plt.title("Variance of Genres: Italy vs. Denmark")
plt.xlabel("Variance in Italy")
plt.ylabel("Variance in Denmark")

for i, row in merged.iterrows():
    plt.text(row["variance_italy"], row["variance_denmark"], row["genre"], fontsize=8, alpha=0.6)

plt.grid(True)
plt.tight_layout()
#plt.savefig("outputs/figures/figure11.png")
plt.show()
