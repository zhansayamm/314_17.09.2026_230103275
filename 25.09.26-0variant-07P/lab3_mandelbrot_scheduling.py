# --- Python 3: Lab 3 - Work-Sharing & Loop Scheduling Policies (Mandelbrot) ---
import numpy as np
import time
import threading
import queue
import matplotlib.pyplot as plt
from numba import njit

# NOTE: reduced resolution keeps the 4x4x3-run x 2-scheduler sweep (96 renders) fast.
# Bump back up to 1920x1080 for a single final verification render if needed.
WIDTH, HEIGHT = 960, 540
MAX_ITER = 1000

THREAD_COUNTS = [2, 4, 8, 16]
CHUNK_SIZES = [1, 16, 64, 256]
NUM_RUNS = 3


@njit(nogil=True)
def compute_pixel(px, py, width, height, max_iter):
    x0 = (px - width / 2.0) * 4.0 / width
    y0 = (py - height / 2.0) * 4.0 / height
    x, y = 0.0, 0.0
    iteration = 0
    while x * x + y * y <= 4.0 and iteration < max_iter:
        xtemp = x * x - y * y + x0
        y = 2.0 * x * y + y0
        x = xtemp
        iteration += 1
    return iteration


@njit(nogil=True)
def process_row_range(row_start, row_end, width, height, max_iter, img):
    total_iter = 0
    for y in range(row_start, row_end):
        for x in range(width):
            it = compute_pixel(x, y, width, height, max_iter)
            img[y, x] = it
            total_iter += it
    return total_iter


# ---------------- Task 3.1: Static Scheduler ----------------
def render_static(width, height, max_iter, num_threads, chunk_size):
    """schedule(static, chunk): fixed-size chunks assigned round-robin to threads up front."""
    img = np.zeros((height, width), dtype=np.int32)
    thread_iter_counts = [0] * num_threads

    chunks = []
    row = 0
    while row < height:
        end = min(row + chunk_size, height)
        chunks.append((row, end))
        row = end

    thread_chunks = [[] for _ in range(num_threads)]
    for idx, chunk in enumerate(chunks):
        thread_chunks[idx % num_threads].append(chunk)

    def worker(tid):
        local_total = 0
        for (r_start, r_end) in thread_chunks[tid]:
            local_total += process_row_range(r_start, r_end, width, height, max_iter, img)
        thread_iter_counts[tid] = local_total

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    return img, thread_iter_counts


# ---------------- Task 3.1: Dynamic Scheduler ----------------
def render_dynamic(width, height, max_iter, num_threads, chunk_size):
    """schedule(dynamic, chunk): threads pull chunks from a shared queue whenever idle."""
    img = np.zeros((height, width), dtype=np.int32)
    thread_iter_counts = [0] * num_threads

    work_queue = queue.Queue()
    row = 0
    while row < height:
        end = min(row + chunk_size, height)
        work_queue.put((row, end))
        row = end

    def worker(tid):
        local_total = 0
        while True:
            try:
                r_start, r_end = work_queue.get_nowait()
            except queue.Empty:
                break
            local_total += process_row_range(r_start, r_end, width, height, max_iter, img)
            work_queue.task_done()
        thread_iter_counts[tid] = local_total

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    return img, thread_iter_counts


# ---------------- Task 3.4: Load Imbalance Metric ----------------
def load_imbalance(thread_iter_counts):
    counts = np.array(thread_iter_counts, dtype=np.float64)
    max_work, min_work, avg_work = counts.max(), counts.min(), counts.mean()
    if avg_work == 0:
        return 0.0
    return (max_work - min_work) / avg_work


if __name__ == "__main__":
    # Warm-up JIT compilation
    _ = render_static(100, 100, 50, 2, 16)
    _ = render_dynamic(100, 100, 50, 2, 16)

    results_static, results_dynamic = {}, {}
    imbalance_static, imbalance_dynamic = {}, {}

    # ---------------- Task 3.2: Parameter Sweep Matrix ----------------
    for label, render_fn, results, imbalances in [
        ("Static", render_static, results_static, imbalance_static),
        ("Dynamic", render_dynamic, results_dynamic, imbalance_dynamic),
    ]:
        print(f"\n===== Task 3.2: Parameter Sweep Matrix ({label} Scheduler) =====")
        print(f"{'P':>4} | {'C':>5} | {'Mean Time (s)':>14} | {'Imbalance':>10}")
        print("-" * 45)
        for P in THREAD_COUNTS:
            for C in CHUNK_SIZES:
                times = []
                last_counts = None
                for run in range(NUM_RUNS):
                    t0 = time.perf_counter()
                    _, counts = render_fn(WIDTH, HEIGHT, MAX_ITER, P, C)
                    t1 = time.perf_counter()
                    times.append(t1 - t0)
                    last_counts = counts
                mean_time = sum(times) / NUM_RUNS
                imb = load_imbalance(last_counts)
                results[(P, C)] = mean_time
                imbalances[(P, C)] = imb
                print(f"{P:>4} | {C:>5} | {mean_time:>14.4f} | {imb:>10.3f}")

    # ---------------- Task 3.3: Heatmap Visualization ----------------
    def build_matrix(results):
        matrix = np.zeros((len(THREAD_COUNTS), len(CHUNK_SIZES)))
        for i, P in enumerate(THREAD_COUNTS):
            for j, C in enumerate(CHUNK_SIZES):
                matrix[i, j] = results[(P, C)]
        return matrix

    static_matrix = build_matrix(results_static)
    dynamic_matrix = build_matrix(results_dynamic)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, matrix, title in zip(axes, [static_matrix, dynamic_matrix], ["Static", "Dynamic"]):
        im = ax.imshow(matrix, cmap="viridis", aspect="auto")
        ax.set_xticks(range(len(CHUNK_SIZES)))
        ax.set_xticklabels(CHUNK_SIZES)
        ax.set_yticks(range(len(THREAD_COUNTS)))
        ax.set_yticklabels(THREAD_COUNTS)
        ax.set_xlabel("Chunk Size (C)")
        ax.set_ylabel("Thread Count (P)")
        ax.set_title(f"{title} Scheduling: Mean Execution Time (s)")
        for i in range(len(THREAD_COUNTS)):
            for j in range(len(CHUNK_SIZES)):
                ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center", color="white", fontsize=8)
        fig.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.savefig("mandelbrot_scheduling_heatmap.png", dpi=150)
    print("\nHeatmap saved to mandelbrot_scheduling_heatmap.png")

    # ---------------- Task 3.4: Load Imbalance Summary ----------------
    print("\n===== Task 3.4: Load Imbalance Summary =====")
    print(f"{'Scheduler':>10} | {'P':>4} | {'C':>5} | {'Imbalance':>10}")
    print("-" * 40)
    for P in THREAD_COUNTS:
        for C in CHUNK_SIZES:
            print(f"{'Static':>10} | {P:>4} | {C:>5} | {imbalance_static[(P, C)]:>10.3f}")
    for P in THREAD_COUNTS:
        for C in CHUNK_SIZES:
            print(f"{'Dynamic':>10} | {P:>4} | {C:>5} | {imbalance_dynamic[(P, C)]:>10.3f}")