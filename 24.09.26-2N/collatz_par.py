import sys
import time
import math

import numba
from numba import njit, prange, set_num_threads

MOD = 1_000_000_007
DEFAULT_N = 13_275_000  # 10,000,000 + 3275 * 1,000
RUNS = 3


@njit
def seq_sweep(N):
    max_steps = 0
    total = 0
    for i in range(1, N + 1):
        n = i
        s = 0
        while n > 1:
            if (n & 1) == 0:
                n >>= 1
            else:
                n = 3 * n + 1
            s += 1
        if s > max_steps:
            max_steps = s
        total += s
    return max_steps, total


@njit(parallel=True)
def par_sweep(N):
    max_steps = 0
    total = 0
    for i in prange(1, N + 1):          # like: #pragma omp parallel for reduction(...)
        n = i
        s = 0
        while n > 1:
            if (n & 1) == 0:
                n >>= 1
            else:
                n = 3 * n + 1
            s += 1
        max_steps = max(max_steps, s)   # max reduction
        total += s                      # sum reduction
    return max_steps, total


def bench(fn, N, k=None):
    """Run RUNS times; return (times, max_steps, total)."""
    if k is not None:
        set_num_threads(k)
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        m, tot = fn(N)
        times.append(time.perf_counter() - t0)
    return times, m, tot


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    max_threads = numba.config.NUMBA_NUM_THREADS

    ks = [k for k in (1, 2, 4, 8, 16) if k <= max_threads]
    if max_threads not in ks:
        ks.append(max_threads)  # "16 (or max)"
    ks.sort()

    print(f"N = {N} | Numba threads available = {max_threads} | "
          f"threading layer requested: {numba.config.THREADING_LAYER}")

    # Sequential reference (Phase 2 baseline)
    seq_sweep(1000)  # compile outside the timed region
    st, ref_max, ref_total = bench(seq_sweep, N)
    t_seq = (st[1] + st[2]) / 2.0
    ref_checksum = ref_total % MOD
    print(f"T_seq = {t_seq:.6f} s | max steps = {ref_max} | checksum = {ref_checksum}\n")

    par_sweep(1000)  # compile
    results = {}
    for k in ks:
        times, m, tot = bench(par_sweep, N, k)
        ok = (m == ref_max and tot % MOD == ref_checksum)
        results[k] = (times, (times[1] + times[2]) / 2.0)
        print(f"k={k:>2}: runs = {[round(t, 4) for t in times]}  checksum {'OK' if ok else 'MISMATCH!'}")

    # Derive p from the k = 2 speedup
    if 2 not in results:
        print("\nk = 2 not available; cannot derive p.")
        return
    s2 = t_seq / results[2][1]
    p = 2.0 * (1.0 - 1.0 / s2)
    print(f"\nS_emp(2) = {s2:.4f}  ->  p = 2*(1 - 1/S_emp(2)) = {p:.4f}")
    if p > 1:
        print("  (p > 1: superlinear/noisy at k=2; note this in your report.)")

    # Table 1
    print("\n| Threads (k) | Run 1 (Cold) | Run 2 (s) | Run 3 (s) | Avg T_k (s) | S_emp(k) | S_theo(k) | Delta(k) |")
    print("|---|---|---|---|---|---|---|---|")
    for k in ks:
        times, avg = results[k]
        s_emp = t_seq / avg
        s_theo = 1.0 / ((1.0 - p) + p / k)
        label = f"k = {k}" + (" (max)" if k == max_threads and k not in (1, 2, 4, 8, 16) else "")
        print(f"| {label} | {times[0]:.4f} | {times[1]:.4f} | {times[2]:.4f} | "
              f"{avg:.4f} | {s_emp:.3f} | {s_theo:.3f} | {s_theo - s_emp:.3f} |")


if __name__ == "__main__":
    main()