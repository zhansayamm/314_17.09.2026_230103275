# Phase 1: Machine Probing & Workload Formulation

N = 10,000,000 + ( 3275 \* 1,000 ) =13,275,000

# Phase 3: Multi-Thread Scaling & Empirical Amdahl Fitting

DERIVATION OF p FROM DUAL-CORE SPEEDUP: S(2) = 1 / [ (1 - p) + (p / 2) ]
1 / S(2) = 1 - p + 0.5p = 1 - 0.5p
0.5p = 1 - (1 / S(2))
p = 2 \* [ 1 - (1 / S_emp(2)) ]

p = 2·(1 − 1/S_emp(2))

| Threads (k) | Run 1 (Cold) | Run 2 (s) | Run 3 (s) | Avg T_k (s) | S_emp(k) | S_theo(k) | Delta(k) |
| ----------- | ------------ | --------- | --------- | ----------- | -------- | --------- | -------- |
| k = 1       | 2.1770       | 2.1482    | 2.1366    | 2.1424      | 1.111    | 1.000     | -0.111   |
| k = 2       | 1.1311       | 1.1841    | 1.1272    | 1.1557      | 2.060    | 2.060     | -0.000   |
| k = 4       | 0.5909       | 0.5889    | 0.5879    | 0.5884      | 4.046    | 4.385     | 0.338    |
| k = 8       | 0.3901       | 0.3821    | 0.3950    | 0.3885      | 6.128    | 10.058    | 3.930    |

# Phase 4: Hardware Penalties & Micro-Architectural Experiments

# Experiment A: The False Sharing Penalty (Cache Invalidation):

N = 13275000 | threads = 8

max steps = 688 | checksum = 100168451 | hits(>100) = 10703270
All three variants agree: YES

| Implementation                               | Variant         | Thread Count | Execution Time (s) | Effective Throughput (iter/sec) | Speedup vs naive | Penalty Ratio (T_naive / T_variant) |
| -------------------------------------------- | --------------- | ------------ | ------------------ | ------------------------------- | ---------------- | ----------------------------------- |
| Variant 1: Naive hits[tid]++ (False Sharing) | Max Physical: 8 | 8            | 0.4553             | 29,157,200                      | 1.00x            | 1.00                                |
| Variant 2a: Reduction                        | Max Physical: 8 | 8            | 0.3851             | 34,474,986                      | 1.18x            | 1.18                                |
| Variant 2b: Cache-Padded (64 B)              | Max Physical: 8 | 8            | 0.4517             | 29,389,739                      | 1.01x            | 1.01                                |

Raw runs (s):
naive : [0.4486, 0.444, 0.4666]
reduction : [0.4075, 0.3865, 0.3836]
padded : [0.4826, 0.4483, 0.4551]

# Experiment B: Loop Scheduling & Workload Imbalance:

N = 13275000 | threads = 8

max steps = 688 | checksum = 100168451
All schedules agree: YES

| Scheduling Clause        | Chunk Size        | Execution Time (s) | vs static | Chunks  | Tail: slowest - fastest thread(s) | Imbalance (max/mean work) | Observed Behavior & CPU Load Distribution                                 |
| ------------------------ | ----------------- | ------------------ | --------- | ------- | --------------------------------- | ------------------------- | ------------------------------------------------------------------------- |
| schedule(static)         | Default (N / k)   | 0.4328             | 1.00x     | 8       | 0.0392                            | 1.064                     | work share per thread (%): 10.8, 11.9, 12.4, 12.6, 12.8, 13.0, 13.1, 13.3 |
| schedule(static, 1000)   | 1,000             | 0.4382             | 0.99x     | 13,275  | 0.0305                            | 1.002                     | work share per thread (%): 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5 |
| schedule(dynamic, 100)   | 100               | 1.0628             | 0.41x     | 132,750 | 0.0001                            | 1.013                     | work share per thread (%): 12.6, 12.6, 12.4, 12.4, 12.3, 12.7, 12.6, 12.4 |
| schedule(dynamic, 10000) | 10,000            | 0.4131             | 1.05x     | 1,328   | 0.0017                            | 1.067                     | work share per thread (%): 11.5, 12.1, 11.6, 12.6, 13.3, 12.4, 13.1, 13.3 |
| schedule(guided)         | Exponential decay | 0.4119             | 1.05x     | 119     | 0.0002                            | 1.085                     | work share per thread (%):11.9, 13.0, 12.9, 13.6, 12.1, 11.8, 12.2, 12.3  |

Raw runs (s):
schedule(static) : [0.4504, 0.4377, 0.428]
schedule(static, 1000) : [0.4342, 0.4444, 0.432]
schedule(dynamic, 100) : [1.05, 1.0433, 1.0823]
schedule(dynamic, 10000) : [0.4597, 0.4197, 0.4066]
schedule(guided) : [0.4207, 0.4146, 0.4092]

# Phase 5: Technical Analysis & Defense Questions

Q1: Micro-Architectural Root Cause of False Sharing
Explain why Variant 1 in Experiment A caused massive execution degradation. Specifically reference your CPU's L1
cache line size (in bytes), the MESI/MOESI cache protocol, and bus invalidation traffic.
A1:Variant 1 used int32 hit_count[8], so all 8 counters (32 bytes) sit in a single cache line. On the Apple M1 the line size is 128 bytes. Cache coherence works per line, not per variable, so writes to "independent" counters by different threads are treated as writes to one shared object.Under a MESI/MOESI-style protocol, a core must own a line exclusively (Modified/Exclusive) to write it. When core A increments its counter, every other core's copy is invalidated. When core B then writes its own counter, it misses, fetches the line from A, and invalidates A's copy.

Q2: Hyperthreading (SMT) Saturation & Physical Core Ceilings
Did your speedup continue to scale linearly when thread count k increased from your physical core count to your logical
thread count? Why or why not? What hardware execution resources are shared between SMT threads?
A2:My Apple M1 has no SMT/hyperthreading. It has 8 physical cores. So my max k = 8.The drop after k = 4 comes mainly from the heterogeneous cores, since threads beyond the 4 performance cores land on slower efficiency cores.

Q3: Empirical vs. Theoretical Amdahl Discrepancy
State your derived parallel fraction p (from k=2). Why did the theoretical curve S_theo(k) diverge from your empirical
S_emp(k) as k increased to 8 or 16? Identify two real physical factors omitted by Amdahl's equation.
A3:Amdahl's law predicted a speedup of about 10 at 8 threads, but I only got about 6. Part of that gap came from the too-high p.

Q4: The Scheduling Trade-Off Dilemma
Compare dynamic(100) versus dynamic(10000) and static scheduling. At what chunk size did lock-queue contention
outweigh the benefits of workload balancing on your machine?
A4:Static gave each thread one big block of numbers. It took 0.433 s. The last thread got more work than the first, because bigger numbers take more steps. So some threads finished 39 ms before others.
Dynamic(10000) hands out small pieces of work, and a thread asks for a new piece when it is free. This kept all threads busy until the end. It took 0.413 s, about 5% faster than static.
Dynamic(100) made the pieces too small. There were 132,750 pieces, and every time a thread asked for one it had to wait in line at a shared queue. The work was balanced almost perfectly, but the waiting cost more than it saved. It took 1.063 s, which is 2.5 times slower than static.
