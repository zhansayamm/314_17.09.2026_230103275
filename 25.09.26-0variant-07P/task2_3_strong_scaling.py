# --- Python 3: Task 2.3 - Strong Scaling Benchmark (Parallel Reduction, Variant C) ---
import os
import numpy as np
import time
from numba import njit, prange, set_num_threads, get_num_threads

N_STEPS = 100_000_000
NUM_TRIALS = 5
MAX_HW_THREADS = os.cpu_count()  # real physical/logical core count, fixed reference


@njit
def calc_pi_serial(num_steps: int) -> float:
    step = 1.0 / num_steps
    total_sum = 0.0
    for i in range(num_steps):
        x = (i + 0.5) * step
        total_sum += 4.0 / (1.0 + x * x)
    return total_sum * step


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

    # Serial baseline (average of 5 trials too, for fair comparison)
    serial_times = []
    for trial in range(NUM_TRIALS):
        t0 = time.perf_counter()
        pi_serial = calc_pi_serial(N_STEPS)
        t1 = time.perf_counter()
        serial_times.append(t1 - t0)

    avg_time_serial = sum(serial_times) / NUM_TRIALS

    print("===== Task 2.3: Strong Scaling Benchmark (Parallel Reduction) =====")
    print(f"Serial Baseline: Pi = {pi_serial:.12f} | Avg Time (5 trials) = {avg_time_serial:.4f}s")
    print(f"Hardware logical cores detected: {MAX_HW_THREADS}")
    print()

    thread_counts = [1, 2, 4, 8, 16]
    results = {}

    print(f"{'P':>4} | {'Trial Times (s)':>45} | {'Avg Time (s)':>12} | {'Speedup S(P)':>13} | {'Efficiency E(P)':>16}")
    print("-" * 100)

    for p in thread_counts:
        requested = min(p, MAX_HW_THREADS)  # cap against fixed hardware limit, not current setting
        set_num_threads(requested)

        # Re-warm-up for this thread count
        _ = calc_pi_reduction(1000)

        trial_times = []
        for trial in range(NUM_TRIALS):
            t2 = time.perf_counter()
            pi_parallel = calc_pi_reduction(N_STEPS)
            t3 = time.perf_counter()
            trial_times.append(t3 - t2)

        avg_time = sum(trial_times) / NUM_TRIALS
        speedup = avg_time_serial / avg_time
        efficiency = speedup / p

        results[p] = {
            "trial_times": trial_times,
            "avg_time": avg_time,
            "speedup": speedup,
            "efficiency": efficiency
        }

        trial_str = ", ".join(f"{t:.4f}" for t in trial_times)
        note = f" (capped at {MAX_HW_THREADS})" if p > MAX_HW_THREADS else ""
        print(f"{p:>4} | {trial_str:>45} | {avg_time:>12.4f} | {speedup:>13.2f} | {efficiency:>16.2%}{note}")

    print()
    print(f"Note: P values above {MAX_HW_THREADS} are capped to the actual hardware thread count,")
    print(f"so speedup/efficiency for P=16 reflects running with only {MAX_HW_THREADS} real threads.")