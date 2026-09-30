# --- Python 3: Task 2.2 - Critical Section (Variant B) ---
import threading
import numpy as np
import time

N_STEPS = 1_000_000

total_sum = 0.0
lock = threading.Lock()


def worker_serial_baseline(num_steps: int, step: float) -> float:
    local_sum = 0.0
    for i in range(num_steps):
        x = (i + 0.5) * step
        local_sum += 4.0 / (1.0 + x * x)
    return local_sum


def worker_critical_section(start: int, end: int, step: float):
    global total_sum
    for i in range(start, end):
        x = (i + 0.5) * step
        value = 4.0 / (1.0 + x * x)

        with lock:            # CRITICAL SECTION: only one thread at a time
            total_sum += value


def calc_pi_serial(num_steps: int) -> float:
    step = 1.0 / num_steps
    return worker_serial_baseline(num_steps, step) * step


def calc_pi_critical(num_steps: int, num_threads: int) -> float:
    global total_sum
    total_sum = 0.0
    step = 1.0 / num_steps
    chunk = num_steps // num_threads

    threads = []
    for t in range(num_threads):
        start = t * chunk
        end = num_steps if t == num_threads - 1 else (t + 1) * chunk
        thread = threading.Thread(target=worker_critical_section, args=(start, end, step))
        threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return total_sum * step


if __name__ == "__main__":
    # Single-threaded baseline
    t0 = time.perf_counter()
    pi_serial = calc_pi_serial(N_STEPS)
    t1 = time.perf_counter()
    time_serial = t1 - t0

    print("===== Task 2.2: Critical Section Overhead =====")
    print(f"Serial Baseline: Pi = {pi_serial:.12f} | Time = {time_serial:.4f}s | Error = {abs(pi_serial - np.pi):.2e}")
    print()

    thread_counts = [1, 2, 4, 8]
    print(f"{'P':>4} | {'Time (s)':>10} | {'Pi':>16} | {'Error':>10} | {'Ideal Time (s)':>15} | {'Lock Overhead %':>16}")
    print("-" * 90)

    for p in thread_counts:
        t2 = time.perf_counter()
        pi_critical = calc_pi_critical(N_STEPS, p)
        t3 = time.perf_counter()
        time_critical = t3 - t2

        error = abs(pi_critical - np.pi)

        # Ideal time under perfect linear speedup (no synchronization cost)
        ideal_time = time_serial / p

        # Lock contention overhead: how much slower than the ideal, as a percentage
        overhead_pct = ((time_critical - ideal_time) / ideal_time) * 100

        print(f"{p:>4} | {time_critical:>10.4f} | {pi_critical:>16.12f} | {error:>10.2e} | {ideal_time:>15.4f} | {overhead_pct:>15.1f}%")