import sys
import time

import numpy as np
import numba
from numba import njit, prange, set_num_threads, get_thread_id

MOD = 1_000_000_007
DEFAULT_N = 13_275_000  # 10,000,000 + 3275 * 1,000
THRESHOLD = 100
RUNS = 3
MAX_THREADS = numba.config.NUMBA_NUM_THREADS
PAD = 8  # 8 x int64 = 64 bytes = one cache line


@njit(inline="always")
def steps_of(i):
    n = i
    s = 0
    while n > 1:
        if (n & 1) == 0:
            n >>= 1
        else:
            n = 3 * n + 1
        s += 1
    return s


@njit(parallel=True)
def naive(N, hit_count):
    max_steps = 0
    total = 0
    for i in prange(1, N + 1):
        s = steps_of(i)
        max_steps = max(max_steps, s)
        total += s
        if s > THRESHOLD:
            hit_count[get_thread_id()] += 1     # FALSE SHARING: int32 counters packed together
    return max_steps, total


@njit(parallel=True)
def reduction(N):
    max_steps = 0
    total = 0
    hits = 0
    for i in prange(1, N + 1):
        s = steps_of(i)
        max_steps = max(max_steps, s)
        total += s
        if s > THRESHOLD:
            hits += 1                            # reduction variable, private per thread
    return max_steps, total, hits


@njit(parallel=True)
def padded(N, hit_count):
    max_steps = 0
    total = 0
    for i in prange(1, N + 1):
        s = steps_of(i)
        max_steps = max(max_steps, s)
        total += s
        if s > THRESHOLD:
            hit_count[get_thread_id() * PAD] += 1   # each counter on its own cache line
    return max_steps, total


def timed(fn):
    times = []
    out = None
    for _ in range(RUNS):
        t0 = time.perf_counter()
        out = fn()
        times.append(time.perf_counter() - t0)
    return times, out


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    k = MAX_THREADS
    set_num_threads(k)
    print(f"N = {N} | threads = {k}\n")

    # compile outside the timed region
    naive(1000, np.zeros(MAX_THREADS, dtype=np.int32))
    reduction(1000)
    padded(1000, np.zeros(MAX_THREADS * PAD, dtype=np.int64))

    hc = np.zeros(MAX_THREADS, dtype=np.int32)

    def run_naive():
        hc[:] = 0
        m, tot = naive(N, hc)
        return m, tot, int(hc.sum())

    hp = np.zeros(MAX_THREADS * PAD, dtype=np.int64)

    def run_padded():
        hp[:] = 0
        m, tot = padded(N, hp)
        return m, tot, int(hp.sum())

    t_naive, o_naive = timed(run_naive)
    t_red, o_red = timed(lambda: reduction(N))
    t_pad, o_pad = timed(run_padded)

    ok = (o_naive == tuple(o_red) == o_pad)
    print(f"max steps = {o_red[0]} | checksum = {o_red[1] % MOD} | hits(>{THRESHOLD}) = {o_red[2]}")
    print(f"All three variants agree: {'YES' if ok else 'NO - MISMATCH!'}\n")

    def avg(t):
        return (t[1] + t[2]) / 2.0

    a_naive, a_red, a_pad = avg(t_naive), avg(t_red), avg(t_pad)

    print("| Implementation | Variant | Thread Count | Execution Time (s) | Effective Throughput (iter/sec) | Speedup vs naive | Penalty Ratio (T_naive / T_variant) |")
    print("|---|---|---|---|---|---|---|")
    rows = [
        ("Variant 1: Naive hits[tid]++ (False Sharing)", a_naive),
        ("Variant 2a: Reduction", a_red),
        ("Variant 2b: Cache-Padded (64 B)", a_pad),
    ]
    for name, t in rows:
        print(f"| {name} | Max Physical: {k} | {k} | {t:.4f} | {N / t:,.0f} | {a_naive / t:.2f}x | {a_naive / t:.2f} |")
    print("\nRaw runs (s):")
    print(f"  naive     : {[round(x, 4) for x in t_naive]}")
    print(f"  reduction : {[round(x, 4) for x in t_red]}")
    print(f"  padded    : {[round(x, 4) for x in t_pad]}")


if __name__ == "__main__":
    main()