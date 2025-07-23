set terminal pdfcairo enhanced size 3,2.25 crop color solid rounded linewidth 1
set datafile separator ","
set xlabel "Degree"
set log xy
set format xy "10^{%L}"

set ylabel "CCDF Artists"
set xrange [1:100]
set output "../outputs/figures/figs8a.pdf"
plot "../outputs/plots/danish_figs8a.csv" using 1:3 w lines lc rgb "#e08282" lw 4 t "Denmark",\
"../outputs/plots/italian_figs8a.csv" using 1:3 w lines lc rgb "#92c5de" lw 4 t "Italy"

set ylabel "CCDF Bands"
set xrange [1:50]
set yrange [0.0004:]
set output "../outputs/figures/figs8b.pdf"
plot "../outputs/plots/danish_figs8b.csv" using 1:3 w lines lc rgb "#e41a1c" lw 4 t "Denmark",\
"../outputs/plots/italian_figs8b.csv" using 1:3 w lines lc rgb "#377eb8" lw 4 t "Italy"

