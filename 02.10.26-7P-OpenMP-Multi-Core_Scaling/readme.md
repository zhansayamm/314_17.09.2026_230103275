# Challenge 1: The Core Speedometer & Amdahl's Law

OUTPUT :
Hardware Threads Detected: 8
Threads | Time (s) | Speedup | Efficiency (%)

---

1 | 1.1479 | 1.00 x | 100.0  
2 | 0.5934 | 1.93 x | 96.7  
4 | 0.3183 | 3.61 x | 90.2  
8 | 0.2609 | 4.40 x | 55.0

Deliverables & Technical Questions for Challenge 1:
A. Record your baseline T_1 (1 thread) and your maximum multi-thread runtime T_max in
Table 1 below:
T_1 - 1 - 1.1479
T_max - 8 - 0.2609

B.Why is the warm-up call = monte_carlo_pi(10_000) strictly required before recording
benchmark timings?
Numba compiles function when it first time called not when it defined.

C. Did your parallel efficiency stay at 100% when scaling from 1 to max threads? What
architectural factors (e.g. memory bus contention, hyperthreading/SMT core vs physical
core limits) explain the degradation?
No, it doesn't stay at 100% efficiency.Because of the hyperthreading.Most likely the machine has 4 physical cores with 2 hardware threads each.

D. Why does inside_circle += 1 inside prange not corrupt the count? What implicit
OpenMP reduction construct does Numba generate here?
Numba recognizes inside_circle += 1 inside a prange as a reduction, not as a shared-variable update. A normal shared increment is a read-modify-write, which is a classic data race. Numba avoids it by never letting threads touch one shared copy.

# Challenge 2: Load Imbalance & Dynamic Scheduling

OUTPUT:
Row-Parallel Render Time: 1.792 s
Column-Parallel Render Time: 1.804 s
Saved image: mandelbrot_output.png

Deliverables & Technical Questions for Challenge 2:
A. Compare t_rows vs t_cols . Which axis decomposition completed faster on your
machine and why?
In my machine t_rows faster-1.792s.Arrays are stored row by row in memory. In the row version each thread writes neighboring memory, which is cache-friendly. The column version jumps across memory with each write.

B. Explain how NumPy's C-contiguous (row-major) memory layout interacts with CPU
cache lines when threads write to img[r, c] vs img[c, r] .
NumPy stores img row by row. Element [r, c] sits at r × W + c, so the last index is the one that's contiguous in memory. A cache line is 64 bytes, which holds 16 int32 values.

C. Load imbalance analysis: If thread 0 receives the top 20% of rows and thread 2 receives
the center 20% of rows, why does one thread idle while the other struggles? How does
OpenMP dynamic scheduling resolve this?
Instead of fixed blocks, the work is split into small chunks (for example, a few rows each) placed in a shared queue. A thread that finishes a chunk takes the next available one.

D. Attach your exported mandelbrot_output.png file alongside your completed task sheet.
done.

# Challenge 3: Stencil Computation & Memory Bandwidth

OUTPUT:
Heat Diffusion Complete: 0.228 s
Throughput: 2962.01 Megacells/sec

Deliverables & Technical Questions for Challenge 3:
A. Record your benchmark runtime and Megacells/sec throughput in Table 1.
done.

B. Change the array precision from np.float64 to np.float32 . Re-run the test. By what
factor did runtime decrease? Why does halving memory footprint improve stencil
throughput far more than compute capability?
the runtime scales with bytes moved, not with flops, so halving the data type size gives close to a 2x speedup.

C. Memory Roofline Model: Explain why adding twice as many CPU cores does not produce
a 2x speedup on stencil codes once memory bandwidth is saturated.
All cores share the same memory channels, which have a fixed bandwidth. A few cores already saturate it. Extra cores add compute power, but the data can't arrive any faster, so they just wait.
