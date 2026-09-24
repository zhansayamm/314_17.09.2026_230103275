
import itertools
import sys
import threading
import time

import numba
from numba import njit

MOD = 1_000_000_007
DEFAULT_N = 13_275_000  # 10,000,000 + 3275 * 1,000
RUNS = 3


@njit(nogil=True)
def run_range(lo, hi):
    """Collatz work on i in [lo, hi). Releases the GIL so threads run in parallel."""
    mx = 0
    tot = 0
    for i in range(lo, hi):
        n = i
        s = 0
        while n > 1:
            if (n & 1) == 0:
                n >>= 1
            else:
                n = 3 * n + 1
            s += 1
        if s > mx:
            mx = s
        tot += s
    return mx, tot


# ---------- chunk plans ----------
def static_plan(N, k):
    """Per-thread list of (lo, hi): one contiguous block each."""
    base, rem = divmod(N, k)
    plan, lo = [], 1
    for t in range(k):
        size = base + (1 if t < rem else 0)
        plan.append([(lo, lo + size)])
        lo += size
    return plan


def static_chunk_plan(N, k, chunk):
    """Per-thread list of (lo, hi): chunks dealt round-robin."""
    plan = [[] for _ in range(k)]
    c = 0
    for lo in range(1, N + 1, chunk):
        plan[c % k].append((lo, min(lo + chunk, N + 1)))
        c += 1
    return plan


def fixed_queue(N, chunk):
    return [(lo, min(lo + chunk, N + 1)) for lo in range(1, N + 1, chunk)]


def guided_queue(N, k):
    q, pos, remaining = [], 1, N
    while remaining > 0:
        size = max(remaining // k, 1)
        q.append((pos, pos + size))
        pos += size
        remaining -= size
    return q


# ---------- workers ----------
def worker_static(my_chunks, res, t, t0):
    mx = tot = n = 0
    for lo, hi in my_chunks:
        m, s = run_range(lo, hi)
        mx = max(mx, m)
        tot += s
        n += 1
    res[t] = (mx, tot, n, time.perf_counter() - t0)


def worker_queue(queue, counter, res, t, t0):
    mx = tot = n = 0
    qlen = len(queue)
    while True:
        c = next(counter)            # itertools.count: atomic pop under the GIL
        if c >= qlen:
            break
        lo, hi = queue[c]
        m, s = run_range(lo, hi)
        mx = max(mx, m)
        tot += s
        n += 1
    res[t] = (mx, tot, n, time.perf_counter() - t0)


def execute(k, static_chunks=None, queue=None):
    res = [None] * k
    counter = itertools.count()
    t0 = time.perf_counter()
    if static_chunks is not None:
        threads = [threading.Thread(target=worker_static, args=(static_chunks[t], res, t, t0))
                   for t in range(k)]
    else:
        threads = [threading.Thread(target=worker_queue, args=(queue, counter, res, t, t0))
                   for t in range(k)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    wall = time.perf_counter() - t0
    return wall, res


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_N
    k = numba.config.NUMBA_NUM_THREADS   # = logical cores; used as "max thread count"
    print(f"N = {N} | threads = {k}\n")

    run_range(1, 1000)  # compile outside the timed region

    schedules = [
        ("schedule(static)", "Default (N / k)", dict(static_chunks=static_plan(N, k))),
        ("schedule(static, 1000)", "1,000", dict(static_chunks=static_chunk_plan(N, k, 1000))),
        ("schedule(dynamic, 100)", "100", dict(queue=fixed_queue(N, 100))),
        ("schedule(dynamic, 10000)", "10,000", dict(queue=fixed_queue(N, 10000))),
        ("schedule(guided)", "Exponential decay", dict(queue=guided_queue(N, k))),
    ]

    results, ref = [], None
    for name, cs, kw in schedules:
        walls = []
        for _ in range(RUNS):
            w, res = execute(k, **kw)
            walls.append(w)
        avg = (walls[1] + walls[2]) / 2.0
        mx = max(r[0] for r in res)
        tot = sum(r[1] for r in res)
        if ref is None:
            ref = (mx, tot)
        ok = (mx, tot) == ref
        steps = [r[1] for r in res]
        finish = [r[3] for r in res]
        nchunks = sum(r[2] for r in res)
        results.append((name, cs, walls, avg, steps, finish, nchunks, ok))

    print(f"max steps = {ref[0]} | checksum = {ref[1] % MOD}")
    print("All schedules agree: "
          f"{'YES' if all(r[7] for r in results) else 'NO - MISMATCH!'}\n")

    base = results[0][3]
    print("| Scheduling Clause | Chunk Size | Execution Time (s) | vs static | Chunks | Tail: slowest - fastest thread (s) | Imbalance (max/mean work) | Observed Behavior & CPU Load Distribution |")
    print("|---|---|---|---|---|---|---|---|")
    for name, cs, walls, avg, steps, finish, nchunks, ok in results:
        tot = sum(steps)
        imb = max(steps) / (tot / len(steps))
        tail = max(finish) - min(finish)
        share = ", ".join(f"{100 * s / tot:.1f}" for s in steps)
        print(f"| {name} | {cs} | {avg:.4f} | {base / avg:.2f}x | {nchunks:,} | {tail:.4f} | {imb:.3f} | work share per thread (%): {share} |")

    print("\nRaw runs (s):")
    for name, cs, walls, *_ in results:
        print(f"  {name:<26}: {[round(w, 4) for w in walls]}")


if __name__ == "__main__":
    main()