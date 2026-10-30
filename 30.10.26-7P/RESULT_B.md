# RESULTS_B.md — Variant B: Scalability Lab

Student ID: 230103275

## Summary table

| Configuration     | T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8    | e(2)   | e(8)  | Verdict                       |
| ----------------- | ------ | ------ | ------ | ------ | ----- | ------ | ----- | ----------------------------- |
| A: Micro (k=1)    | 9.53\* | n/m    | n/m    | 14.31  | 0.67x | n/m    | 1.573 | Master dispatch serialization |
| B: Queue Choke    | 2.185  | 3.891  | 3.836  | 4.383  | 0.50x | 2.561  | 2.149 | IPC lock contention explosion |
| C: Buffered Batch | 0.746  | 0.313  | 0.191  | 0.196  | 3.80x | -0.160 | 0.158 | Amortized synchronization     |

\* For A, T1 is the serial baseline (1,000,000 items, no Pool). T2 and T4 were not measured (n/m); only the 8-worker sweep was run.
Speedup S_p = T1 / Tp. Karp-Flatt e(p) = (p·Tp/T1 − 1) / (p − 1).

## Experiment A — Granularity (1,000,000 items, 8 workers, serial 9.53 s)

| chunk   | tasks     | time (s) | speedup | eff (%) | compute/task (ms) |
| ------- | --------- | -------- | ------- | ------- | ----------------- |
| 1       | 1,000,000 | 14.31    | 0.67x   | 8.3     | 0.010             |
| 10      | 100,000   | 3.39     | 2.81x   | 35.1    | 0.095             |
| 100     | 10,000    | 1.91     | 4.99x   | 62.4    | 0.953             |
| 1,000   | 1,000     | 1.84     | 5.17x   | 64.7    | 9.527             |
| 10,000  | 100       | 1.93     | 4.93x   | 61.6    | 95.269            |
| 100,000 | 10        | 2.50     | 3.81x   | 47.6    | 952.687           |

## Experiment B — Queue Choke-Point (400,000 items)

| P   | Time (s) | Speedup  | Karp-Flatt e |
| --- | -------- | -------- | ------------ |
| 1   | 2.185    | baseline | —            |
| 2   | 3.891    | 0.56x    | 2.561        |
| 4   | 3.836    | 0.57x    | 2.007        |
| 8   | 4.383    | 0.50x    | 2.149        |

## Experiment C — Local buffer chunking (10,000,000 items, batch = 10,000)

| P   | Time (s) | Speedup  | Karp-Flatt e |
| --- | -------- | -------- | ------------ |
| 1   | 0.746    | baseline | —            |
| 2   | 0.313    | 2.38x    | -0.160       |
| 4   | 0.191    | 3.90x    | 0.008        |
| 8   | 0.196    | 3.80x    | 0.158        |

**Throughput vs. unbuffered (Exp B)**

| P   | B (items/s)              | C (items/s)                 | Gain   |
| --- | ------------------------ | --------------------------- | ------ |
| 1   | 400,000 / 2.185 ≈ 1.83e5 | 10,000,000 / 0.746 ≈ 1.34e7 | ≈ 73x  |
| 8   | 400,000 / 4.383 ≈ 9.1e4  | 10,000,000 / 0.196 ≈ 5.1e7  | ≈ 560x |

## Conclusion

Communication frequency, not computation, decides scalability. Exp A shows that tasks must be coarse enough to amortize dispatch; Exp B shows that fine-grained sharing of one IPC channel yields negative scaling; Exp C shows that local aggregation restores scaling and gives a >10x throughput gain.
