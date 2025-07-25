library(relaimpo);
library(stargazer);

df <- read.csv("outputs/plots/danish_table7.csv", sep = ",");
m.p <- lm(exists ~ genre_sim + label_sim + year_sim, data = df);
m.n <- lm(log(nij) ~ genre_sim + label_sim + year_sim, data = df[df$exists == 1,]);

stargazer(m.p, m.n, covariate.labels = c("Genre", "Label", "Year"), dep.var.labels = c("Exists", "Size"));

calc.relimp(m.p, type = "pmvd")
calc.relimp(m.n, type = "pmvd")


