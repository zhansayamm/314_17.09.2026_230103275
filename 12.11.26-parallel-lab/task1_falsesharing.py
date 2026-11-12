
import argparse
import ctypes
import multiprocessing as mp
import platform
import subprocess
from multiprocessing import shared_memory

from harness import run_benchmark, emit_verify_tag

STUDENT_ID = 230103275            # <-- replace with your Student ID (integer)
M_TOTAL = 24_000_000      # M = 2.4 x 10^7 total accumulation steps
SHM_SIZE = 4096           # bytes
N_SLOTS = SHM_SIZE // 8   # 512 uint64 slots
WARMUP, TIMED = 2, 7


# ---------------------------------------------------------------- worker ----
def fs_worker(shm_name: str, slot_idx: int, iters: int) -> None:
    shm = shared_memory.SharedMemory(name=shm_name)
    arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
    acc = arr[slot_idx]
    mask = 0xFFFFFFFFFFFFFFFF
    mult = 6364136223846793005
    for i in range(iters):
        acc = (acc * mult + (i | 1)) & mask
        arr[slot_idx] = acc  # store to the (possibly shared) cache line
    del arr  # release buffer export before closing SharedMemory
    shm.close()


# --------------------------------------------------------------- helpers ----
def detect_physical_cores() -> int:
    """Best-effort physical core count using only the standard library."""
    logical = mp.cpu_count()
    try:
        system = platform.system()
        if system == "Linux":
            pairs, phys = set(), None
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("physical id"):
                        phys = line.split(":")[1].strip()
                    elif line.startswith("core id"):
                        pairs.add((phys, line.split(":")[1].strip()))
            if pairs:
                return len(pairs)
        elif system == "Darwin":
            out = subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"])
            return int(out.strip())
        elif system == "Windows":
            out = subprocess.check_output(
                ["wmic", "cpu", "get", "NumberOfCores"], text=True)
            nums = [int(x) for x in out.split() if x.isdigit()]
            if nums:
                return sum(nums)
    except Exception:
        pass
    return logical


def scaling_list(p_log: int):
    ps, p = [], 1
    while p <= p_log:
        ps.append(p)
        p *= 2
    if ps[-1] != p_log:
        ps.append(p_log)
    return ps


def run_once(shm, p: int, stride: int, iters: int) -> None:
    shm.buf[:SHM_SIZE] = bytes(SHM_SIZE)  # identical zero start state every run
    procs = [mp.Process(target=fs_worker, args=(shm.name, t * stride, iters))
             for t in range(p)]
    for pr in procs:
        pr.start()
    for pr in procs:
        pr.join()
    if any(pr.exitcode != 0 for pr in procs):
        raise RuntimeError("a worker process failed")


def read_slots(shm, p: int, stride: int):
    mv = shm.buf.cast("Q")
    vals = [mv[t * stride] for t in range(p)]
    mv.release()
    return vals


def measure(shm, p: int, stride: int, m_total: int):
    """Benchmark one (p, stride) config and verify the result."""
    iters = m_total // p
    stats = run_benchmark(lambda: run_once(shm, p, stride, iters),
                          warmup_runs=WARMUP, timed_runs=TIMED)
    vals = read_slots(shm, p, stride)
    # Every worker starts from 0 and runs the same deterministic recurrence,
    # so all slots must be identical.
    ok = len(set(vals)) == 1
    return stats, ok, vals[0]


# ------------------------------------------------------------------ main ----
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=M_TOTAL, help="total steps M")
    ap.add_argument("--pphys", type=int, default=None, help="physical cores")
    args = ap.parse_args()

    p_log = mp.cpu_count()
    p_phys = args.pphys or detect_physical_cores()
    m_total = args.m
    print(f"P_log = {p_log}, P_phys = {p_phys}, M = {m_total:,}")

    shm = shared_memory.SharedMemory(create=True, size=SHM_SIZE)
    try:
        # ---- Sweep 1: stride sweep at p = P_phys ---------------------------
        strides = [1, 2, 4, 8, 16, 32]
        p1 = p_phys
        max_p = N_SLOTS // max(strides)  # slots must fit: p * stride <= 512
        if p1 > max_p:
            print(f"[warn] p={p1} * stride=32 exceeds {N_SLOTS} slots; "
                  f"capping stride sweep at p={max_p}")
            p1 = max_p
        if m_total % p1:
            print(f"[warn] M not divisible by p={p1}; using M//p per worker")

        print(f"\n=== Stride sweep, p = {p1} ===")
        print(f"{'stride':>6} {'bytes':>6} {'min ms':>10} {'median ms':>10} "
              f"{'IQR ms':>9} {'max ms':>10}  ok")
        stride_med = {}
        for s in strides:
            st, ok, _ = measure(shm, p1, s, m_total)
            stride_med[s] = st.median_ms
            print(f"{s:>6} {s * 8:>6} {st.min_ms:>10.1f} {st.median_ms:>10.1f} "
                  f"{st.iqr_ms:>9.1f} {st.max_ms:>10.1f}  {'OK' if ok else 'MISMATCH'}")

        # ---- Sweep 2: process scaling, stride 1 and stride 16 --------------
        ps = scaling_list(p_log)
        scale = {}
        for s in (1, 16):
            print(f"\n=== Process scaling, stride = {s} ({s * 8} B apart) ===")
            print(f"{'p':>4} {'median ms':>10} {'IQR ms':>9} {'speedup':>8} "
                  f"{'eff %':>7}  ok")
            base = None
            scale[s] = {}
            for p in ps:
                if p * s > N_SLOTS:
                    print(f"{p:>4}  skipped (p*stride exceeds {N_SLOTS} slots)")
                    continue
                st, ok, _ = measure(shm, p, s, m_total)
                if base is None:
                    base = st.median_ms  # p = 1 reference
                sp = base / st.median_ms
                scale[s][p] = sp
                print(f"{p:>4} {st.median_ms:>10.1f} {st.iqr_ms:>9.1f} "
                      f"{sp:>8.2f} {100 * sp / p:>7.1f}  {'OK' if ok else 'MISMATCH'}")

        # ---- Verification tags (metric choice: see notes) ------------------
        print()
        print(emit_verify_tag("TASK1_STRIDE", STUDENT_ID,
                              stride_med[1], stride_med[16]))
        pmax = max(scale[1])
        print(emit_verify_tag("TASK1_SCALE", STUDENT_ID,
                              scale[1][pmax], scale[16].get(pmax, 0.0)))
    finally:
        shm.close()
        shm.unlink()


if __name__ == "__main__":
    main()