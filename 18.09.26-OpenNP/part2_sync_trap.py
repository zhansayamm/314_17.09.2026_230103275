import random
import threading
import time

total_hits_locked = 0
hits_lock = threading.Lock()

def monte_carlo_locked(iterations):
    global total_hits_locked
    local_random = random.Random()
    for _ in range(iterations):
        x = local_random.random()
        y = local_random.random()
        if x * x + y * y <= 1.0:
            with hits_lock:
                total_hits_locked += 1  # correct, but lock per iteration

def run_single_threaded_baseline(total_points=50_000_000):
    local_random = random.Random()
    hits = 0
    start = time.perf_counter()
    for _ in range(total_points):
        x = local_random.random()
        y = local_random.random()
        if x * x + y * y <= 1.0:
            hits += 1
    elapsed = time.perf_counter() - start
    pi_estimate = 4 * hits / total_points
    return pi_estimate, elapsed

def run_part2(total_points=50_000_000, num_threads=4):
    global total_hits_locked
    print("=== PART 2: The Synchronization Trap (Locked) ===")

    total_hits_locked = 0
    per_thread = total_points // num_threads
    threads = [threading.Thread(target=monte_carlo_locked, args=(per_thread,))
               for _ in range(num_threads)]
    start = time.perf_counter()
    for t in threads: t.start()
    for t in threads: t.join()
    locked_time = time.perf_counter() - start
    pi_locked = 4 * total_hits_locked / total_points
    print(f"Locked (4 threads): pi≈{pi_locked:.4f} | time={locked_time:.4f}s "
          f"| hits={total_hits_locked:,}/{total_points:,}")

    print("Running single-threaded baseline for comparison...")
    pi_single, single_time = run_single_threaded_baseline(total_points)
    print(f"Single-threaded:    pi≈{pi_single:.4f} | time={single_time:.4f}s")

    print(f"\nSlowdown Factor (locked vs single-threaded): "
          f"{locked_time / single_time:.2f}x "
          f"{'SLOWER' if locked_time > single_time else 'faster'}")

if __name__ == "__main__":
    run_part2(total_points=50_000_000, num_threads=4)
