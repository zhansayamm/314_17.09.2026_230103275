import time
import multiprocessing as mp
from harness import emit_verify_tag

STUDENT_ID = 230103275  
N = 2_000_000  


def main():
    p_log = mp.cpu_count()
    clock = time.perf_counter_ns

    # warm-up so the interpreter and caches are settled
    for _ in range(100_000):
        clock()

    t0 = clock()
    for _ in range(N):
        clock()
    t1 = clock()

    avg_ns = (t1 - t0) / N  # average latency per call (includes loop overhead)

    print(f"Logical CPUs (mp.cpu_count): {p_log}")
    print(f"Average perf_counter_ns() call latency: {avg_ns:.2f} ns over {N} reads")
    print(emit_verify_tag("PHASE0", STUDENT_ID, avg_ns, float(p_log)))


if __name__ == "__main__":
    main()