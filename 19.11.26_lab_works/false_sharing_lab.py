import os
import re
import sys
import json
import time
import hashlib
import platform
import threading
import subprocess
import numpy as np
import numba
from numba import njit

try:
    import resource
except ImportError:          # Windows
    resource = None

# Replace with your exact Git handle before executing
GIT_USERNAME = "zhansayamm"
NUM_THREADS = 4
ITERATIONS_PER_THREAD = 60_000_000
STRIDES = (1, 4, 8, 16)
REPEATS = 3                  # each configuration is timed this many times (median is reported)
MANIFEST_PATH = "cache_lab_manifest.json"


def detect_cache_line_size() -> int:
    """Query L1 data cache coherency line size in bytes from OS sysfs/sysctl."""
    linux_path = "/sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size"
    if os.path.exists(linux_path):
        with open(linux_path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    if sys.platform == "darwin":
        out = subprocess.check_output(["sysctl", "-n", "hw.cachelinesize"], encoding="utf-8")
        return int(out.strip())
    return 64


def detect_cpu_model() -> str:
    """Human-readable CPU model string (Linux /proc/cpuinfo, macOS sysctl, else platform)."""
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith(("model name", "hardware", "cpu model")):
                        return line.split(":", 1)[1].strip()
        if sys.platform == "darwin":
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], encoding="utf-8").strip()
    except Exception:
        pass
    return platform.processor() or platform.machine()


def _sibling_key(cpu: int) -> str:
    """Identifies the physical core a logical CPU belongs to (SMT siblings share a key)."""
    path = f"/sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return str(cpu)


def choose_cores(n: int):
    """Pick n logical CPUs, preferring distinct physical cores (SMT siblings share L1,
    so pinning two threads to siblings would hide the coherence traffic we want to measure)."""
    if not hasattr(os, "sched_getaffinity"):
        return None
    avail = sorted(os.sched_getaffinity(0))
    chosen, used = [], set()
    for c in avail:
        key = _sibling_key(c)
        if key not in used:
            chosen.append(c)
            used.add(key)
        if len(chosen) == n:
            return chosen
    for c in avail:
        if len(chosen) == n:
            break
        if c not in chosen:
            chosen.append(c)
    return chosen


def pin_current_thread(core: int) -> bool:
    """Pin the *calling* thread (Linux: pid 0 == calling thread) to one logical CPU."""
    if not hasattr(os, "sched_setaffinity"):
        return False
    os.sched_setaffinity(0, {core})
    return True


# ==============================================================================
# TASK 1: Hardware Topology & Student Identity Context
# ==============================================================================
def init_system_context(git_user: str) -> dict:
    assert git_user != "REPLACE_WITH_YOUR_GIT_USERNAME" and len(git_user.strip()) > 0, (
        "Set GIT_USERNAME to your real Git handle before running."
    )
    logical_cores = os.cpu_count() or 1
    if logical_cores < NUM_THREADS:
        raise RuntimeError(f"Requires at least {NUM_THREADS} logical cores; detected {logical_cores}.")
    line_size = detect_cache_line_size()
    cpu_sig = f"{platform.machine()}::{platform.processor()}::{logical_cores}"

    # Deterministic 64-bit INSTANCE_SEED: first 16 hex digits of SHA-256(git_user::cpu_sig)
    digest = hashlib.sha256(f"{git_user}::{cpu_sig}".encode("utf-8")).hexdigest()
    instance_seed = int(digest[:16], 16)

    # Core affinity masks (one distinct logical CPU per worker thread), if the OS supports it
    affinity_supported = hasattr(os, "sched_setaffinity")
    cores = choose_cores(NUM_THREADS) if affinity_supported else None

    return {
        "git_user": git_user,
        "logical_cores": logical_cores,
        "cache_line_size": line_size,
        "elements_per_line": line_size // 8,
        "cpu_model": detect_cpu_model(),
        "cpu_sig": cpu_sig,
        "instance_seed": instance_seed,
        "affinity_supported": affinity_supported,
        "affinity_cores": cores,
    }


def thread_seed(instance_seed: int, tid: int) -> int:
    """Per-thread 64-bit seed derived from INSTANCE_SEED."""
    h = hashlib.sha256(f"{instance_seed}:{tid}".encode("utf-8")).hexdigest()
    return int(h[:16], 16)


# ==============================================================================
# TASK 2 / TASK 4: native kernels (GIL released, explicit signatures -> pure i64 code)
# ==============================================================================
# Both kernels run the same xorshift64 stream (pure register work), so the ONLY difference
# between them is where the running sum lives: in memory (RMW every iteration) or in a register.
# A non-linear stream also prevents LLVM from folding the loop into a closed form.
@njit("void(uint64[::1], int64, int64, uint64)", nogil=True)
def worker_strided_accumulate(buffer, slot, iters, seed):
    x = seed | np.uint64(1)
    other = (slot + 1) % buffer.shape[0]
    for _ in range(iters):
        x ^= x << np.uint64(13)
        x ^= x >> np.uint64(7)
        x ^= x << np.uint64(17)
        # in-place read-modify-write on buffer[slot]
        v = buffer[slot] + (x >> np.uint64(40))
        buffer[slot] = v
        # Opaque, practically-never-taken may-alias store. It stops LLVM's loop-invariant
        # scalar promotion, which would otherwise hoist buffer[slot] into a register
        # (a plain loop gets compiled to exactly that, making false sharing disappear).
        if v == np.uint64(0xFFFFFFFFFFFFFFFF):
            buffer[other] = x


@njit("void(uint64[::1], int64, int64, uint64)", nogil=True)
def worker_private_accumulate(buffer, slot, iters, seed):
    x = seed | np.uint64(1)
    acc = np.uint64(0)                       # thread-local register accumulator
    for _ in range(iters):
        x ^= x << np.uint64(13)
        x ^= x >> np.uint64(7)
        x ^= x << np.uint64(17)
        acc += x >> np.uint64(40)
    buffer[slot] = acc                       # single shared-memory write at the end


# ==============================================================================
# TASK 3: multi-threaded stride sweep
# ==============================================================================
def make_aligned_buffer(n_elems: int, align_bytes: int):
    """uint64 buffer whose first element sits on an `align_bytes` boundary."""
    raw = np.zeros(n_elems + align_bytes // 8, dtype=np.uint64)
    off = ((-raw.ctypes.data) % align_bytes) // 8
    view = raw[off: off + n_elems]
    assert view.ctypes.data % align_bytes == 0 and view.flags["C_CONTIGUOUS"]
    return raw, view


def _worker(core, kernel, view, slot, iters, seed, barrier, pinned_flags, tid):
    pinned_flags[tid] = pin_current_thread(core) if core is not None else False
    barrier.wait()                                    # all workers released together
    kernel(view, slot, iters, np.uint64(seed))


def _rusage():
    if resource is None:
        return None
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_nvcsw, r.ru_nivcsw


def run_once(ctx, kernel, stride, iters):
    align = max(64, ctx["cache_line_size"])
    raw, view = make_aligned_buffer(NUM_THREADS * stride, align)
    slots = [t * stride for t in range(NUM_THREADS)]
    seeds = [thread_seed(ctx["instance_seed"], t) for t in range(NUM_THREADS)]
    cores = ctx["affinity_cores"]
    barrier = threading.Barrier(NUM_THREADS + 1)
    pinned = [False] * NUM_THREADS
    threads = [
        threading.Thread(
            target=_worker,
            args=(None if cores is None else cores[t % len(cores)],
                  kernel, view, slots[t], iters, seeds[t], barrier, pinned, t))
        for t in range(NUM_THREADS)
    ]
    for th in threads:
        th.start()
    ru0 = _rusage()
    barrier.wait()
    t0 = time.perf_counter_ns()
    for th in threads:
        th.join()
    t1 = time.perf_counter_ns()
    ru1 = _rusage()
    ctx_sw = None if ru0 is None else {"voluntary": ru1[0] - ru0[0], "involuntary": ru1[1] - ru0[1]}
    return {
        "elapsed_ns": t1 - t0,
        "ctx_switches": ctx_sw,
        "final_values": [int(view[s]) for s in slots],
        "threads_pinned": all(pinned),
        "buffer_address_mod_line": int(view.ctypes.data % ctx["cache_line_size"]),
    }


def _median(xs):
    return float(np.median(np.array(xs, dtype=np.float64)))


def run_stride_benchmark(ctx, iters=ITERATIONS_PER_THREAD, strides=STRIDES, repeats=REPEATS):
    """Runs strided (shared RMW) and private (register) kernels for every stride layout."""
    # warm-up: kernels are already compiled (explicit signatures); this also warms threads/caches
    for k in (worker_strided_accumulate, worker_private_accumulate):
        run_once(ctx, k, 8, 100_000)

    results = {"strided": {}, "private": {}}
    for name, kernel in (("strided", worker_strided_accumulate),
                         ("private", worker_private_accumulate)):
        for stride in strides:
            runs = [run_once(ctx, kernel, stride, iters) for _ in range(repeats)]
            times = [r["elapsed_ns"] for r in runs]
            med = _median(times)
            results[name][stride] = {
                "runs_ns": times,
                "median_ns": med,
                "ns_per_update": med / iters,
                "ctx_switches_per_run": [r["ctx_switches"] for r in runs],
                "final_values_per_run": [r["final_values"] for r in runs],
                "threads_pinned": runs[0]["threads_pinned"],
                "buffer_address_mod_line": runs[0]["buffer_address_mod_line"],
            }
            print(f"{name:>8} stride={stride:<3} median={med / 1e6:10.1f} ms   "
                  f"{med / iters:8.3f} ns/update   runs(ms)={[round(t / 1e6, 1) for t in times]}")
    return results


# ==============================================================================
# TASK 5: exact-state parity + LLVM IR verification + manifest
# ==============================================================================
def _kernel_ir_body(ir: str, name: str):
    """Optimised IR of the native function itself (excludes the cpython wrapper / cfunc)."""
    for m in re.finditer(r"^define[^\n]*\n.*?^\}", ir, re.M | re.S):
        header = m.group(0).split("\n", 1)[0]
        if name in header and "cpython" not in header and "cfunc." not in header:
            return m.group(0)
    return None


def audit_llvm_and_parity(ctx, results, iters=ITERATIONS_PER_THREAD):
    # ---- 1. bit-exact parity: every run of every layout == the private baseline
    reference = results["private"][STRIDES[0]]["final_values_per_run"][0]
    mismatches = []
    for kind in ("strided", "private"):
        for stride, rec in results[kind].items():
            for i, vals in enumerate(rec["final_values_per_run"]):
                if vals != reference:
                    mismatches.append({"kind": kind, "stride": stride, "run": i, "values": vals})
    parity_ok = not mismatches
    values_sha = hashlib.sha256(
        np.array(reference, dtype=np.uint64).tobytes()).hexdigest()

    # ---- 2. LLVM IR audit of worker_strided_accumulate
    llvm = {"available": False, "passed": False}
    try:
        irs = worker_strided_accumulate.inspect_llvm()
        ir = next(iter(irs.values())) if isinstance(irs, dict) else str(irs)
        body = _kernel_ir_body(ir, "worker_strided_accumulate")
        if body is None:
            raise RuntimeError("native function body not found in IR")
        blocks = re.split(r"\n(?=[\w.$]+:)", body)
        rmw_loop_blocks = [b for b in blocks
                           if "load i64" in b and "store i64" in b and " phi " in b]
        py_calls = re.findall(r"@\"?(?:Py[A-Za-z_]+|_Py[A-Za-z_]+)", body)
        checks = {
            "has_native_i64_store": len(re.findall(r"\bstore i64\b", body)) >= 1,
            "has_native_i64_load": len(re.findall(r"\bload i64\b", body)) >= 1,
            "rmw_load_and_store_inside_loop_body": len(rmw_loop_blocks) >= 1,
            "no_python_capi_calls_in_native_body": len(py_calls) == 0,
            "no_pyobject_type_in_native_body": "PyObject" not in body,
        }
        llvm = {
            "available": True,
            "i64_stores": len(re.findall(r"\bstore i64\b", body)),
            "i64_loads": len(re.findall(r"\bload i64\b", body)),
            "loop_rmw_blocks": len(rmw_loop_blocks),
            "python_capi_calls": py_calls,
            "ir_body_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "checks": checks,
            "passed": all(checks.values()),
        }
        with open("worker_strided_accumulate.ll", "w", encoding="utf-8") as f:
            f.write(body)
    except Exception as exc:                          # noqa: BLE001
        llvm["error"] = repr(exc)

    # ---- 3. derived analysis (stride 1 vs 8 vs private)
    s = {k: results["strided"][k]["median_ns"] for k in STRIDES}
    p_all = [results["private"][k]["median_ns"] for k in STRIDES]
    p = float(np.median(p_all))
    analysis = {
        "ns_per_update": {f"stride_{k}": v / iters for k, v in s.items()},
        "ns_per_update_private": p / iters,
        "false_sharing_slowdown_stride1_over_stride8": s[1] / s[8],
        "coherence_penalty_ns_per_update_stride1_minus_stride8": (s[1] - s[8]) / iters,
        "memory_rmw_cost_ns_per_update_stride8_minus_private": (s[8] - p) / iters,
        "privatization_speedup_over_stride1": s[1] / p,
        "first_stride_isolating_threads_on_separate_lines":
            next((k for k in STRIDES if k * 8 >= ctx["cache_line_size"]), None),
    }

    manifest = {
        "git_user": ctx["git_user"],
        "instance_seed_uint64": ctx["instance_seed"],
        "instance_seed_hex": f"0x{ctx['instance_seed']:016x}",
        "seed_derivation": "int(sha256('<git_user>::<machine>::<processor>::<logical_cores>').hexdigest()[:16], 16)",
        "thread_seeds": [thread_seed(ctx["instance_seed"], t) for t in range(NUM_THREADS)],
        "hardware": {k: ctx[k] for k in ("cpu_model", "cpu_sig", "logical_cores", "cache_line_size",
                                         "elements_per_line", "affinity_supported", "affinity_cores")},
        "config": {"threads": NUM_THREADS, "iterations_per_thread": iters,
                   "strides": list(STRIDES), "repeats": REPEATS},
        "results": {kind: {str(k): {kk: vv for kk, vv in rec.items() if kk != "final_values_per_run"}
                           for k, rec in d.items()} for kind, d in results.items()},
        "final_counter_values": reference,
        "final_counter_values_sha256": values_sha,
        "parity": {"bit_exact": parity_ok, "mismatches": mismatches},
        "llvm_audit": llvm,
        "analysis": analysis,
        "environment": {"python": platform.python_version(), "numba": numba.__version__,
                        "numpy": np.__version__, "platform": platform.platform()},
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "all_checks_passed": bool(parity_ok and llvm.get("passed", False)),
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"parity (bit-exact across 4 strides + private): {'PASS' if parity_ok else 'FAIL'}")
    if llvm.get("available"):
        print("LLVM audit:", "PASS" if llvm["passed"] else "FAIL", llvm["checks"])
    else:
        print("LLVM audit unavailable:", llvm.get("error"))
    print("analysis:", json.dumps(analysis, indent=2))
    print(f"wrote {MANIFEST_PATH}")

    assert parity_ok, f"final counter values differ between layouts: {mismatches}"
    assert llvm.get("passed", False), f"LLVM audit failed: {llvm}"
    return manifest


def main():
    ctx = init_system_context(GIT_USERNAME)
    print(f"INSTANCE_SEED = 0x{ctx['instance_seed']:016x}")
    print(f"CPU: {ctx['cpu_model']} | logical cores: {ctx['logical_cores']} | "
          f"cache line: {ctx['cache_line_size']} B | pinned cores: {ctx['affinity_cores']}")
    results = run_stride_benchmark(ctx)
    audit_llvm_and_parity(ctx, results)


if __name__ == "__main__":
    main()