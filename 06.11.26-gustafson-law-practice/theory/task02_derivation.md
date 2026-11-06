Normalize the runtime on the parallel machine: s + p = 1, with s = α.
The serial part takes time s regardless of P.
The parallel part takes time p on P cores, so it represents p·P units of single-core work.
A single processor would need T₁ = s + p·P for the same problem.
Scaled speedup: S(P) = T₁ / T_P = (s + pP) / 1 = s + pP.
Substitute p = 1 − α: S = α + (1 − α)P = α + P − αP = P − α(P − 1)
