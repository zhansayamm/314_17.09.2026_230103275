"""Experiment A - The Granularity Trap.

Sweeps the Pool.map chunksize to show how task granularity affects speedup.
Usage: python exp_a_granularity.py [total_items] [workers]
"""
import os
import sys
import time
from multiprocessing import Pool


def collatz_steps(n):
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers, total_items=1_000_000, chunk_size=1):
    numbers = range(1, total_items + 1)
    t0 = time.perf_counter()
    with Pool(processes=workers) as pool:
        # chunk_size=1 -> total_items individual IPC task envelopes (micro-tasks)
        results = pool.map(collatz_steps, numbers, chunksize=chunk_size)
    return time.perf_counter() - t0, sum(results)


def run_serial(total_items):
    t0 = time.perf_counter()
    total = sum(collatz_steps(n) for n in range(1, total_items + 1))
    return time.perf_counter() - t0, total


if __name__ == "__main__":  # required for spawn-based platforms (Windows/macOS)
    total_items = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    chunk_sizes = [1, 10, 100, 1_000, 10_000, 100_000]
    chunk_sizes = [c for c in chunk_sizes if c <= total_items]

    print(f"items={total_items:,}  workers={workers}\n")
    t_serial, ref = run_serial(total_items)
    per_item_us = t_serial / total_items * 1e6
    print(f"Serial baseline: {t_serial:.2f}s  (~{per_item_us:.1f} us of compute per item)\n")

    print(f"{'chunk':>8} {'tasks':>10} {'time(s)':>9} {'speedup':>8} {'eff(%)':>7} {'compute/task(ms)':>17}")
    for c in chunk_sizes:
        t, checksum = run_granularity(workers, total_items, c)
        assert checksum == ref, "checksum mismatch!"
        tasks = -(-total_items // c)  # ceil division
        speedup = t_serial / t
        eff = speedup / workers * 100
        task_ms = per_item_us * c / 1000
        print(f"{c:>8,} {tasks:>10,} {t:>9.2f} {speedup:>7.2f}x {eff:>7.1f} {task_ms:>17.3f}")