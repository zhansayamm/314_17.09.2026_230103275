# --- Python 3: Lab 4 - False Sharing Scaling Benchmark (Unpadded / Padded / Thread-Local) ---
import numpy as np
import time
import matplotlib.pyplot as plt
from numba import njit, prange, set_num_threads

ITERATIONS = 50_000_000  # reduced slightly from 100M to keep the P-sweep fast; bump up if you have time
THREAD_COUNTS = [1, 2, 4, 8, 16]
MAX_HW_THREADS = 8  # this machine's logical core count (from earlier labs)


# ---------------- Variant 1: Unpadded (False Sharing) ----------------
@njit(parallel=True)
def false_sharing_test(num_threads: int, iters: int):
    counters = np.zeros(num_threads, dtype=np.int64)
    for tid in prange(num_threads):
        for _ in range(iters):
            counters[tid] += 1
    return counters


# ---------------- Variant 2: Padded (Cache-Line Isolated) ----------------
@njit(parallel=True)
def padded_sharing_test(num_threads: int, iters: int):
    stride = 8  # 8 int64 elements = 64 bytes = exactly one cache line per thread counter
    counters = np.zeros(num_threads * stride, dtype=np.int64)
    for tid in prange(num_threads):
        idx = tid * stride
        for _ in range(iters):
            counters[idx] += 1
    return counters


# ---------------- Task 4.3: Thread-Local Register Accumulator ----------------
@njit(parallel=True)
def thread_local_test(num_threads: int, iters: int):
    counters = np.zeros(num_threads, dtype=np.int64)
    for tid in prange(num_threads):
        local_count = 0  # lives in a CPU register / private stack slot, not shared memory
        for _ in range(iters):
            local_count += 1
        counters[tid] = local_count  # single write to shared array at the very end
    return counters


if __name__ == "__main__":
    # Warm-up JIT compilation
    _ = false_sharing_test(2, 1000)
    _ = padded_sharing_test(2, 1000)
    _ = thread_local_test(2, 1000)

    results_unpadded, results_padded, results_local = {}, {}, {}

    print("===== Task 4.1 / 4.2 / 4.3: Scaling Profile Across P =====")
    print(f"{'P':>4} | {'Unpadded (s)':>13} | {'Padded (s)':>11} | {'Thread-Local (s)':>17}")
    print("-" * 55)

    for P in THREAD_COUNTS:
        effective_p = min(P, MAX_HW_THREADS)
        set_num_threads(effective_p)

        # Re-warm-up for this thread count
        _ = false_sharing_test(effective_p, 1000)
        _ = padded_sharing_test(effective_p, 1000)
        _ = thread_local_test(effective_p, 1000)

        t0 = time.perf_counter()
        result_unpadded = false_sharing_test(effective_p, ITERATIONS)
        t1 = time.perf_counter()
        time_unpadded = t1 - t0

        t2 = time.perf_counter()
        result_padded = padded_sharing_test(effective_p, ITERATIONS)
        t3 = time.perf_counter()
        time_padded = t3 - t2

        t4 = time.perf_counter()
        result_local = thread_local_test(effective_p, ITERATIONS)
        t5 = time.perf_counter()
        time_local = t5 - t4

        # Force the compiler/interpreter to actually use the results, preventing
        # dead-code elimination of the entire loop (which was silently happening before).
        checksum = int(result_unpadded.sum()) + int(result_padded.sum()) + int(result_local.sum())
        assert checksum == 3 * effective_p * ITERATIONS, f"Checksum mismatch at P={P}: {checksum}"

        results_unpadded[P] = time_unpadded
        results_padded[P] = time_padded
        results_local[P] = time_local

        note = f" (capped at {MAX_HW_THREADS})" if P > MAX_HW_THREADS else ""
        print(f"{P:>4} | {time_unpadded:>13.4f} | {time_padded:>11.4f} | {time_local:>17.4f}{note}")

    # ---------------- Plot: Execution Time vs Thread Count ----------------
    plt.figure(figsize=(9, 6))
    plt.plot(THREAD_COUNTS, [results_unpadded[p] for p in THREAD_COUNTS],
             marker='o', label='Unpadded (False Sharing)', color='crimson')
    plt.plot(THREAD_COUNTS, [results_padded[p] for p in THREAD_COUNTS],
             marker='s', label='Padded (Cache Isolated)', color='seagreen')
    plt.plot(THREAD_COUNTS, [results_local[p] for p in THREAD_COUNTS],
             marker='^', label='Thread-Local Accumulator', color='royalblue')

    plt.xlabel("Thread Count (P)")
    plt.ylabel("Execution Time (s)")
    plt.title("False Sharing Impact: Execution Time vs Thread Count")
    plt.xticks(THREAD_COUNTS)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("false_sharing_scaling_plot.png", dpi=150)
    print("\nPlot saved to false_sharing_scaling_plot.png")

    # ---------------- Summary: Speedup from mitigation ----------------
    print("\n===== Mitigation Speedup Summary =====")
    print(f"{'P':>4} | {'Padded Speedup':>15} | {'Thread-Local Speedup':>20}")
    print("-" * 45)
    for P in THREAD_COUNTS:
        speedup_padded = results_unpadded[P] / results_padded[P]
        speedup_local = results_unpadded[P] / results_local[P]
        print(f"{P:>4} | {speedup_padded:>15.2f}x | {speedup_local:>20.2f}x")