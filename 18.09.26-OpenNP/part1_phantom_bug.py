import random
import threading
import time

total_hits_unsafe = 0

def monte_carlo_unsafe(iterations):
    global total_hits_unsafe
    local_random = random.Random()
    for _ in range(iterations):
        x = local_random.random()
        y = local_random.random()
        if x * x + y * y <= 1.0:
            total_hits_unsafe += 1  # RACE: read-modify-write, not atomic

def run_part1(total_points=50_000_000, num_threads=4):
    global total_hits_unsafe
    print("=== PART 1: The Phantom Bug (Unsynchronized) ===")
    per_thread = total_points // num_threads

    for run in range(1, 6):
        total_hits_unsafe = 0
        threads = [threading.Thread(target=monte_carlo_unsafe, args=(per_thread,))
                   for _ in range(num_threads)]
        start = time.perf_counter()
        for t in threads: t.start()
        for t in threads: t.join()
        elapsed = time.perf_counter() - start

        pi_estimate = 4 * total_hits_unsafe / total_points
        print(f"Run {run}: hits={total_hits_unsafe:,}/{total_points:,} "
              f"| pi≈{pi_estimate:.4f} | time={elapsed:.4f}s")

if __name__ == "__main__":
    run_part1(total_points=50_000_000, num_threads=4)
