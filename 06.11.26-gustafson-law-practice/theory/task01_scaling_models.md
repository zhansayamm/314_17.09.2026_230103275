Amdahl (1967) Gustafson (1988)
Problem size as P→∞ Fixed: W = const Grows with P: W(P) ≈ P·W(1)
What is held constant Total workload (fixed-size) Execution time (fixed-time)
Goal Solve the same problem faster Solve a larger problem in the same time
Scaling type Strong scaling Weak scaling
Limit S ≤ 1/s No ceiling; S grows linearly in P
Why “fixed-size”: In Amdahl’s model the total workload is constant, so the serial fraction s stays the same while only the parallel part is divided by P. The serial part becomes the bottleneck.
Why “fixed-time”: In Gustafson’s model extra processors are used to enlarge the parallel part of the problem. Parallel runtime stays constant, and the serial part barely grows.
Philosophy: Amdahl asks “how much faster can I solve this problem?” Gustafson asks “how much bigger a problem can I solve in the same time?”
