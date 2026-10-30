"""Experiment C - Local Buffer Chunking (amortize synchronization)."""
import time
from multiprocessing import Process, Queue


def buffered_worker(out_queue, items_per_worker, batch_size=10_000):
    buffer = []
    for i in range(items_per_worker):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))  # flush pre-aggregated chunk every batch_size items
            buffer.clear()
    if buffer:
        out_queue.put(sum(buffer))
    out_queue.put(None)  # sentinel end-of-work token


def run_buffered(p, total_items=10_000_000):
    q = Queue()
    items_per_worker = total_items // p
    workers = [
        Process(target=buffered_worker, args=(q, items_per_worker))
        for _ in range(p)
    ]

    t0 = time.perf_counter()
    for w in workers:
        w.start()

    total_sum, active = 0, p
    while active > 0:
        val = q.get()
        if val is None:
            active -= 1
        else:
            total_sum += val

    for w in workers:
        w.join()
    return time.perf_counter() - t0, total_sum


def expected_sum(p, total_items):
    n = total_items // p
    full, rem = divmod(n, 7)
    per_worker = full * 21 + sum(range(rem))  # 0+1+...+6 = 21
    return per_worker * p


if __name__ == "__main__":
    total_items = 10_000_000
    cores = [1, 2, 4, 8]
    results = {}
    for p in cores:
        t, s = run_buffered(p, total_items)
        assert s == expected_sum(p, total_items), f"checksum mismatch at P={p}"
        results[p] = t

    t1 = results[1]
    print("\n--- Buffered Queue Karp-Flatt Analysis ---")
    print(f"P= 1 | Time={t1:6.3f}s | (baseline)")
    for p in [2, 4, 8]:
        tp = results[p]
        sp = t1 / tp
        e = ((p * tp / t1) - 1.0) / (p - 1.0)
        print(f"P={p:2d} | Time={tp:6.3f}s | Speedup={sp:5.2f}x | Karp-Flatt e={e:6.3f}")