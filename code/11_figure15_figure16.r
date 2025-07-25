library(ggplot2)

# Create a dataframe with your values
df <- data.frame(
  Variable = c("Genre", "Label", "Year"),
  Importance = c(0.03167105, 0.01789875, 0.10691640)
)

residual <- 1 - sum(df$Importance)

df <- rbind(df, data.frame(Variable = "Residual", Importance = residual))
df$Variable <- factor(df$Variable, levels = c("Year", "Label", "Genre", "Residual"))  # Force order
color_map <- c("Genre" = "#E41A1C", "Label" = "#377EB8", "Year" = "#4DAF4A", "Residual" = "grey70")

print(ggplot(df, aes(y = " ", x = Importance, fill = Variable)) +
  geom_bar(stat = "identity", width = 0.3) +  
  labs(title = "Edge's Weight", x = NULL, y = NULL) +
  scale_fill_manual(values = color_map) + 
  theme_minimal(base_size = 10) + 
  theme(
    legend.position = "bottom",
    legend.title = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank(),
    plot.title = element_text(face = "bold", size = 12)
  ) 
)