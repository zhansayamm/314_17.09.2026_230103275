"""Experiment A - The Stubborn Serial Tail (Amdahl / Karp-Flatt)."""
import time
import math
from multiprocessing import Pool


def heavy_math(n):
    return sum(math.sin(i) * math.cos(i) for i in range(1, n))


def run_experiment(workers, total_chunks=16, chunk_size=2_000_000):
    t0 = time.perf_counter()
    time.sleep(0.40)  # intentional sequential bottleneck (~12% serial fraction)
    with Pool(processes=workers) as pool:
        pool.map(heavy_math, [chunk_size] * total_chunks)
    return time.perf_counter() - t0


if __name__ == "__main__":
    cores = [1, 2, 4]
    runtimes = {p: run_experiment(p) for p in cores}
    t1 = runtimes[1]

    print("\n--- Serial Tail Karp-Flatt Analysis ---")
    print(f"P= 1 | Time={t1:6.3f}s | (baseline)")
    for p in [2, 4]:
        tp = runtimes[p]
        sp = t1 / tp
        e = ((p * tp / t1) - 1.0) / (p - 1.0)
        print(f"P={p:2d} | Time={tp:6.3f}s | Speedup={sp:5.2f}x | Karp-Flatt e={e:6.3f}")
    print(f"\nSerial fraction estimate from the sleep: {0.40 / t1:.3f}")