Amdahl’s frame: s is measured on one processor as a fraction of a fixed T₁. It does not change with P, hence the ceiling 1/s.
Gustafson’s frame: α is measured on the parallel machine as a fraction of the parallel runtime. The growing problem enlarges only the parallel work, while the absolute serial time stays roughly constant.
Relation between the two fractions: the serial fraction of the scaled problem on one processor is s′ = α / (α + (1 − α)P), which decreases as P grows.
Check: with s′ in Amdahl’s formula, T₁ = α + (1 − α)P and T_P = 1, so S = P − α(P − 1). Both laws give the same result and differ only in the frame of reference.
Conclusion: there is no contradiction. The laws answer different questions (fixed-size vs fixed-time) and measure the serial fraction at different points.
