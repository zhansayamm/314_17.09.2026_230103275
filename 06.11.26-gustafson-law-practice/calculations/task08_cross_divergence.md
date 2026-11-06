With s = α = 0.08 and P = 128:
Amdahl: S = 1 / (0.08 + 0.92/128) = 1 / 0.0872 ≈ 11.47
Gustafson: S = 128 − 0.08 · 127 = 117.84
Discrepancy: Gustafson is ≈ 10.3× larger, so Amdahl is ≈ 90% lower: (117.84 − 11.47) / 117.84 ≈ 90.3%.
Why they diverge: Amdahl is capped at 1/s = 12.5 because the problem size is fixed. Gustafson has no cap because the parallel work grows with P. The gap widens as P increases.
