import random
import threading
import time

def monte_carlo_reduction(iterations, result_slot, idx):
    local_random = random.Random()
    local_hits = 0  # thread-private accumulator, no locking, no sharing
    for _ in range(iterations):
        x = local_random.random()
        y = local_random.random()
        if x * x + y * y <= 1.0:
            local_hits += 1
    result_slot[idx] = local_hits  # single write at the very end

def run_reduction_bench(num_threads, total_points):
    per_thread = total_points // num_threads
    results = [0] * num_threads
    threads = [
        threading.Thread(target=monte_carlo_reduction, args=(per_thread, results, i))
        for i in range(num_threads)
    ]
    start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    elapsed = time.perf_counter() - start

    total_hits = sum(results)  # the single reduction step
    pi_estimate = 4 * total_hits / (per_thread * num_threads)
    return pi_estimate, elapsed, total_hits

def run_part3(total_points=100_000_000):
    print("=== PART 3: OpenMP-Style Reduction (Thread-Local Accumulators) ===")
    print(f"{'Threads':>8} | {'Time(s)':>10} | {'pi estimate':>12} | {'Hits':>14}")
    print("-" * 55)

    thread_counts = [1, 2, 4, 8, 16, 32]
    baseline_time = None
    for t in thread_counts:
        pi_estimate, elapsed, hits = run_reduction_bench(t, total_points)
        if baseline_time is None:
            baseline_time = elapsed
        speedup = baseline_time / elapsed
        print(f"{t:8d} | {elapsed:10.4f} | {pi_estimate:12.5f} | {hits:14,} "
              f"(speedup vs T=1: {speedup:.2f}x)")

if __name__ == "__main__":
    run_part3(total_points=100_000_000)
