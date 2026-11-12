import argparse
import math
import multiprocessing as mp
import statistics
import time

from harness import run_benchmark, emit_verify_tag

STUDENT_ID = 230103275    
N_STRONG = 1_600_000      # 1.6 x 10^6
N0_WEAK = 250_000         # 2.5 x 10^5 per core
SERIAL_FRACTION = 0.05    # Stage A covers the first 5% of elements
STAGE_B_ITERS = 35        # inner iterations per element in Stage B


# ------------------------------------------------------------ Stage A -------
def stage_a(n_serial: int) -> float:
    """Serial bottleneck: 12 transcendental ops (6 sin + 6 sqrt) per element."""
    sin, sqrt = math.sin, math.sqrt
    acc = 0.0
    for i in range(n_serial):
        x = 1.0 + (i % 997) * 0.001
        for _ in range(6):
            x = sqrt(sin(x) + 2.0)   # 1 sin + 1 sqrt per step, stays in [1, 1.74]
        acc += x
    return acc


# ------------------------------------------------------------ Stage B -------
def kernel_chunk(args):
    """Embarrassingly parallel kernel: no shared writes, returns a partial sum."""
    start, end, seed = args
    sin = math.sin
    acc = 0.0
    for i in range(start, end):
        x = 0.5 + (i % 1000) * 0.001 + seed * 1e-9
        for _ in range(STAGE_B_ITERS):
            x = x * 0.5 + sin(x) + 0.1   # multiply-add + trig, bounded
        acc += x
    return acc


def _noop(_):
    return 0


def make_chunks(n: int, p: int, seed: float):
    """Split [0, n) into p contiguous, near-equal chunks."""
    base, rem = divmod(n, p)
    chunks, start = [], 0
    for t in range(p):
        size = base + (1 if t < rem else 0)
        chunks.append((start, start + size, seed))
        start += size
    return chunks


# ------------------------------------------------------------ one config ----
def measure(p: int, n: int, warmup: int, timed: int):
    """Benchmark the full pipeline for (p, n). Pool is created OUTSIDE timing."""
    n_serial = int(SERIAL_FRACTION * n)
    with mp.Pool(processes=p) as pool:
        pool.map(_noop, range(p), chunksize=1)   # make sure workers are up

        a_times, sums = [], []

        def trial():
            t0 = time.perf_counter_ns()
            seed = stage_a(n_serial)                         # Stage A (serial)
            t1 = time.perf_counter_ns()
            parts = pool.map(kernel_chunk, make_chunks(n, p, seed), chunksize=1)
            a_times.append((t1 - t0) / 1e6)
            sums.append(sum(parts))                          # fixed order: deterministic

        stats = run_benchmark(trial, warmup_runs=warmup, timed_runs=timed)

    stage_a_ms = statistics.median(a_times[warmup:])
    stable = len(set(sums)) == 1
    return stats, stage_a_ms, stable, sums[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N_STRONG)
    ap.add_argument("--n0", type=int, default=N0_WEAK)
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--timed", type=int, default=7)
    args = ap.parse_args()

    p_log = mp.cpu_count()
    ps = list(range(1, p_log + 1))
    print(f"P_log = {p_log}, warmup={args.warmup}, timed={args.timed}")

    # ---------------- Experiment 2A: strong scaling -------------------------
    print(f"\n=== 2A: Strong scaling, N = {args.n:,} ===")
    print(f"{'p':>3} {'T ms':>10} {'IQR ms':>9} {'StageA ms':>10} "
          f"{'S':>7} {'E %':>7} {'Amdahl S':>9}  check")
    t1 = ref_sum = f_serial = None
    strong = {}
    for p in ps:
        st, a_ms, stable, total = measure(p, args.n, args.warmup, args.timed)
        if p == 1:
            t1, ref_sum = st.median_ms, total
            f_serial = a_ms / st.median_ms      # measured serial fraction
        s = t1 / st.median_ms
        amdahl = 1.0 / (f_serial + (1.0 - f_serial) / p)
        close = abs(total - ref_sum) <= 1e-9 * abs(ref_sum)
        strong[p] = (s, s / p)
        print(f"{p:>3} {st.median_ms:>10.1f} {st.iqr_ms:>9.1f} {a_ms:>10.1f} "
              f"{s:>7.2f} {100 * s / p:>7.1f} {amdahl:>9.2f}  "
              f"{'OK' if (stable and close) else 'MISMATCH'}")
    print(f"Measured serial fraction f = T_StageA / T_1 = {f_serial:.4f} "
          f"(Amdahl limit {1 / f_serial:.1f}x)")

    # ---------------- Experiment 2B: weak scaling ---------------------------
    print(f"\n=== 2B: Weak scaling, N0 = {args.n0:,} per worker ===")
    print(f"{'p':>3} {'N(p)':>10} {'T ms':>10} {'IQR ms':>9} {'StageA ms':>10} "
          f"{'E_weak %':>9} {'alpha':>7} {'S_Gust':>8}  check")
    tw1 = None
    weak = {}
    for p in ps:
        n = p * args.n0
        st, a_ms, stable, _ = measure(p, n, args.warmup, args.timed)
        if p == 1:
            tw1 = st.median_ms
        e_weak = tw1 / st.median_ms
        alpha = a_ms / st.median_ms
        s_g = p - alpha * (p - 1)
        weak[p] = (e_weak, s_g)
        print(f"{p:>3} {n:>10,} {st.median_ms:>10.1f} {st.iqr_ms:>9.1f} {a_ms:>10.1f} "
              f"{100 * e_weak:>9.1f} {alpha:>7.4f} {s_g:>8.2f}  "
              f"{'OK' if stable else 'MISMATCH'}")

    # ---------------- Verification tags -------------------------------------
    pm = ps[-1]
    print()
    print(emit_verify_tag("TASK2_STRONG", STUDENT_ID, strong[pm][0], strong[pm][1]))
    print(emit_verify_tag("TASK2_WEAK", STUDENT_ID, weak[pm][0], weak[pm][1]))


if __name__ == "__main__":
    main()