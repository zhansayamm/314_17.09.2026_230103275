# --- Python 3: Numerical Integration Benchmarking ---
import numpy as np
import time
from numba import njit, prange, set_num_threads, get_num_threads

N_STEPS = 100_000_000


# 1. Serial Baseline
@njit
def calc_pi_serial(num_steps: int) -> float:
    step = 1.0 / num_steps
    total_sum = 0.0
    for i in range(num_steps):
        x = (i + 0.5) * step
        total_sum += 4.0 / (1.0 + x * x)
    return total_sum * step


# 2. Parallel Reduction (Numba compiles prange reduction into OpenMP-style tree reduction)
@njit(parallel=True)
def calc_pi_reduction(num_steps: int) -> float:
    step = 1.0 / num_steps
    total_sum = 0.0
    for i in prange(num_steps):
        x = (i + 0.5) * step
        total_sum += 4.0 / (1.0 + x * x)  # Numba automatically infers parallel reduction
    return total_sum * step


if __name__ == "__main__":
    # Warm-up JIT compilation
    _ = calc_pi_serial(1000)
    _ = calc_pi_reduction(1000)

    # Benchmark Serial (P=1 baseline)
    t0 = time.perf_counter()
    pi_serial = calc_pi_serial(N_STEPS)
    t1 = time.perf_counter()
    time_serial = t1 - t0

    print(f"Serial: Pi = {pi_serial:.12f} | Time = {time_serial:.4f}s | Error = {abs(pi_serial - np.pi):.2e}")
    print()

    # Sweep over different thread counts P
    thread_counts = [1, 2, 4, 8]
    results = {}

    print("===== Amdahl's Law Sweep: Speedup S(P) and Efficiency E(P) =====")
    print(f"{'P':>4} | {'Time (s)':>10} | {'Pi':>15} | {'Error':>10} | {'Speedup S(P)':>13} | {'Efficiency E(P)':>16}")
    print("-" * 80)

    for p in thread_counts:
        set_num_threads(p)

        # Re-warm-up to make sure JIT is compiled for this thread count
        _ = calc_pi_reduction(1000)

        t2 = time.perf_counter()
        pi_parallel = calc_pi_reduction(N_STEPS)
        t3 = time.perf_counter()
        time_parallel = t3 - t2

        speedup = time_serial / time_parallel
        efficiency = speedup / p

        results[p] = {
            "pi": pi_parallel,
            "time": time_parallel,
            "error": abs(pi_parallel - np.pi),
            "speedup": speedup,
            "efficiency": efficiency
        }

        print(f"{p:>4} | {time_parallel:>10.4f} | {pi_parallel:>15.12f} | {results[p]['error']:>10.2e} | {speedup:>13.2f} | {efficiency:>16.2%}")

    print()
    print(f"Actual number of threads available on this machine: {get_num_threads()}")