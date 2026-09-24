import sys
import time
import math

MOD = 1_000_000_007
DEFAULT_N = 13_275_000  # 10,000,000 + 3275 * 1,000
RUNS = 3


def collatz_steps(n):
    steps = 0
    while n > 1:
        if (n & 1) == 0:
            n >>= 1
        else:
            n = 3 * n + 1
        steps += 1
    return steps


def sweep(N):
    """Sequential pass over i = 1..N. Returns (max_steps, arg_max, total_steps)."""
    max_steps = 0
    arg_max = 1
    total = 0
    for i in range(1, N + 1):
        s = collatz_steps(i)
        if s > max_steps:
            max_steps = s
            arg_max = i
        total += s
    return max_steps, arg_max, total


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pure = "--pure" in sys.argv
    N = int(args[0]) if args else DEFAULT_N

    fn = sweep
    mode = "pure CPython"
    if not pure:
        try:
            from numba import njit
            collatz_steps_j = njit(collatz_steps)  # noqa: F841 (kept for clarity)

            @njit
            def sweep_jit(N):
                max_steps = 0
                arg_max = 1
                total = 0
                for i in range(1, N + 1):
                    n = i
                    s = 0
                    while n > 1:
                        if (n & 1) == 0:
                            n >>= 1
                        else:
                            n = 3 * n + 1
                        s += 1
                    if s > max_steps:
                        max_steps = s
                        arg_max = i
                    total += s
                return max_steps, arg_max, total

            fn = sweep_jit
            mode = "Numba JIT"
        except ImportError:
            print("Numba not installed; falling back to pure CPython (slow).")

    print(f"Mode: {mode}")
    times = []
    for r in range(RUNS):
        t0 = time.perf_counter()
        max_steps, arg_max, total = fn(N)
        t1 = time.perf_counter()
        times.append(t1 - t0)
        note = "  (warmup, discarded)" if r == 0 else ""
        print(f"Run {r + 1}: {times[-1]:.6f} s{note}")

    t_seq = (times[1] + times[2]) / 2.0
    print(f"\nN          = {N}")
    print(f"Max steps  = {max_steps} (at i = {arg_max})")
    print(f"Checksum   = {total % MOD} (sum of steps mod 1,000,000,007)")
    print(f"T_seq      = {t_seq:.6f} s  ((Run2 + Run3) / 2)")


if __name__ == "__main__":
    main()