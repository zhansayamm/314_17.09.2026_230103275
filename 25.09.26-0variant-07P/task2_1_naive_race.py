# --- Python 3: Task 2.1 - Naive Race Condition (Guaranteed Manifestation) ---
import threading
import numpy as np
import time

N_STEPS = 200_000  # меньше итераций, т.к. каждая теперь дороже из-за sleep

total_sum = 0.0


def worker_naive_race(start: int, end: int, step: float):
    global total_sum
    for i in range(start, end):
        x = (i + 0.5) * step
        value = 4.0 / (1.0 + x * x)

        current = total_sum        # STEP 1: READ
        time.sleep(0)              # forces a GIL check/yield point right here
        current = current + value  # STEP 2: MODIFY (using stale 'current')
        total_sum = current        # STEP 3: WRITE (may overwrite another thread's update)


def calc_pi_naive_race(num_steps: int, num_threads: int) -> float:
    global total_sum
    total_sum = 0.0
    step = 1.0 / num_steps
    chunk = num_steps // num_threads

    threads = []
    for t in range(num_threads):
        start = t * chunk
        end = num_steps if t == num_threads - 1 else (t + 1) * chunk
        thread = threading.Thread(target=worker_naive_race, args=(start, end, step))
        threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return total_sum * step


if __name__ == "__main__":
    thread_counts = [1, 2, 4, 8]

    print("===== Task 2.1: Race Condition Quantification (Forced Manifestation) =====")
    print(f"{'P':>4} | {'Time (s)':>10} | {'Pi (calculated)':>18} | {'Absolute Error':>16}")
    print("-" * 60)

    for p in thread_counts:
        t0 = time.perf_counter()
        pi_naive = calc_pi_naive_race(N_STEPS, p)
        t1 = time.perf_counter()
        elapsed = t1 - t0
        error = abs(pi_naive - np.pi)

        print(f"{p:>4} | {elapsed:>10.4f} | {pi_naive:>18.12f} | {error:>16.2e}")