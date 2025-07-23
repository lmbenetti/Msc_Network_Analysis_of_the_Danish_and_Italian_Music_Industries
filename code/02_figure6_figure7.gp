set terminal pdfcairo enhanced size 3,2.25 crop color solid rounded linewidth 1
set datafile separator ","

set log y
set format y "10^{%L}"

set xlabel "# Years"
set ylabel "Count"
set output "../outputs/figures/figs6b.pdf"
plot "../outputs/plots/danish_6b_artists.csv" using 1:2 w lines lc rgb "#e08282" lw 4 t "Artists Denmark",\
"../outputs/plots/danish_6b_bands.csv" using 1:2 w lines lc rgb "#d73027" lw 4 t "Bands Denmark",\
"../outputs/plots/italian_6b_artists.csv" using 1:2 w lines lc rgb "#92c5de" lw 4 t "Artists Italy",\
"../outputs/plots/italian_6b_bands.csv" using 1:2 w lines lc rgb "#377eb8" lw 4 t "Bands Italy"

set xlabel "Year"
set ylabel "Count"
set key top left
set xrange [1901:2025]
set yrange [:2500]
set output "../outputs/figures/figs6a.pdf"
plot "../outputs/plots/danish_6a_artists.csv" using 1:2 w lines lc rgb "#e08282" lw 4 t "Artists Denmark",\
"../outputs/plots/danish_6a_bands.csv" using 1:2 w lines lc rgb "#d73027" lw 4 t "Bands Denmark",\
"../outputs/plots/italian_6a_artists.csv" using 1:2 w lines lc rgb "#92c5de" lw 4 t "Artists Italy",\
"../outputs/plots/italian_6a_bands.csv" using 1:2 w lines lc rgb "#377eb8" lw 4 t "Bands Italy"

set xlabel "Degree"
set log xy
set format xy "10^{%L}"
set key top right

set ylabel "CCDF Artists"
set xrange [1:300]
set yrange [:1]
set output "../outputs/figures/figs7a.pdf"
plot "../outputs/plots/danish_7a.csv" using 1:3 w lines lc rgb "#e08282" lw 4 t "Denmark",\
"../outputs/plots/italian_7a.csv" using 1:3 w lines lc rgb "#92c5de" lw 4 t "Italy"

set ylabel "CCDF Bands"
set xrange [1:1200]
set yrange [0.0001:]
set output "../outputs/figures/figs7b.pdf"
plot "../outputs/plots/danish_7b.csv" using 1:3 w lines lc rgb "#d73027" lw 4 t "Denmark",\
"../outputs/plots/italian_7b.csv" using 1:3 w lines lc rgb "#377eb8" lw 4 t "Italy"
