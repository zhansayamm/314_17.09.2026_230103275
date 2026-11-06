Gustafson overestimates when G(P) < P: memory or bandwidth limits how much the problem can grow, so you can’t keep all P cores busy.
Gustafson underestimates when G(P) > P. Example: dense matrix multiplication has memory O(N²) but work O(N³), so G(P) = P^1.5. This gives higher speedup than Gustafson, but runtime is no longer constant.
