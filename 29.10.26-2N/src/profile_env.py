#!/usr/bin/env python3
"""
profile_env.py  --  Task 0.1: Machine Telemetry Extraction

Inspects the host OS and writes a structured JSON file describing:
  * CPU model name, microarchitecture, base frequency
  * Physical cores vs logical threads (SMT / Hyper-Threading detection)
  * L1 data / L2 / L3 cache sizes and cache-line size
  * OS kernel version and Python implementation details

Sources, by platform:
  Linux   : /proc/cpuinfo, /sys/devices/system/cpu/*, lscpu, getconf
  macOS   : sysctl (+ platform / psutil fallbacks)
  Windows : PowerShell Get-CimInstance (best effort; L1 / line size not exposed)

Standard library only; psutil is used opportunistically if installed.
Usage (from the repo root):
    python3 src/profile_env.py                      # -> results/host_profile.json
    python3 src/profile_env.py -o results/hw.json
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys

SCHEMA_VERSION = "1.0"


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def run(cmd, timeout=15):
    """Run a command, return stripped stdout or None on any failure."""
    try:
        env = dict(os.environ, LC_ALL="C", LANG="C")
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, env=env)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def read(path):
    try:
        with open(path, "r", errors="replace") as f:
            return f.read().strip()
    except OSError:
        return None


def to_int(x):
    try:
        return int(str(x).strip(), 0)
    except (TypeError, ValueError):
        return None


def parse_size(s):
    """'32K' | '1M' | '32 KiB (8 instances)' | '8192' -> bytes."""
    if s is None:
        return None
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([KMGkmg]?)", str(s))
    if not m:
        return None
    mult = {"": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}[m.group(2).lower()]
    return int(float(m.group(1)) * mult)


def parse_cpu_list(s):
    """'0-3,8,10-11' -> [0,1,2,3,8,10,11]."""
    out = []
    for part in (s or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def human(n):
    if n is None:
        return None
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unit == "GiB":
            return f"{n:g} {unit}" if n == int(n) else f"{n:.1f} {unit}"
        n /= 1024


# --------------------------------------------------------------------------
# Microarchitecture inference (best-effort lookup tables)
# --------------------------------------------------------------------------
INTEL_FAM6 = {
    0x1A: "Nehalem", 0x1E: "Nehalem", 0x1F: "Nehalem", 0x2E: "Nehalem",
    0x25: "Westmere", 0x2C: "Westmere", 0x2F: "Westmere",
    0x2A: "Sandy Bridge", 0x2D: "Sandy Bridge",
    0x3A: "Ivy Bridge", 0x3E: "Ivy Bridge",
    0x3C: "Haswell", 0x3F: "Haswell", 0x45: "Haswell", 0x46: "Haswell",
    0x3D: "Broadwell", 0x47: "Broadwell", 0x4F: "Broadwell", 0x56: "Broadwell",
    0x4E: "Skylake", 0x5E: "Skylake",
    0x8E: "Kaby Lake / Coffee Lake / Whiskey Lake", 0x9E: "Kaby Lake / Coffee Lake",
    0xA5: "Comet Lake", 0xA6: "Comet Lake", 0x66: "Cannon Lake",
    0x7D: "Ice Lake", 0x7E: "Ice Lake", 0x6A: "Ice Lake (Server)", 0x6C: "Ice Lake (Server)",
    0xA7: "Rocket Lake", 0x8C: "Tiger Lake", 0x8D: "Tiger Lake",
    0x97: "Alder Lake", 0x9A: "Alder Lake", 0xB7: "Raptor Lake", 0xBA: "Raptor Lake",
    0xBF: "Raptor Lake", 0xAA: "Meteor Lake", 0xAC: "Meteor Lake",
    0xC5: "Arrow Lake", 0xC6: "Arrow Lake", 0xBD: "Lunar Lake",
    0x8F: "Sapphire Rapids", 0xCF: "Emerald Rapids",
    0xAD: "Granite Rapids", 0xAE: "Granite Rapids",
    0x37: "Silvermont", 0x4D: "Silvermont", 0x5C: "Goldmont", 0x86: "Tremont",
}


def _in(m, *ranges):
    return any(lo <= m <= hi for lo, hi in ranges)


def amd_microarch(family, model):
    if family == 0x17:
        if model in (0x08, 0x18):
            return "Zen+"
        if _in(model, (0x30, 0x3F), (0x47, 0x47), (0x60, 0x7F), (0x90, 0xAF)):
            return "Zen 2"
        return "Zen"
    if family == 0x19:
        if _in(model, (0x10, 0x1F), (0x60, 0x7F), (0xA0, 0xAF)):
            return "Zen 4"
        return "Zen 3"
    if family == 0x1A:
        return "Zen 5"
    if family == 0x15:
        return "Bulldozer-family"
    return None


ARM_PARTS = {  # implementer 0x41 (Arm Ltd.)
    0xD03: "Cortex-A53", 0xD04: "Cortex-A35", 0xD05: "Cortex-A55", 0xD07: "Cortex-A57",
    0xD08: "Cortex-A72", 0xD09: "Cortex-A73", 0xD0A: "Cortex-A75", 0xD0B: "Cortex-A76",
    0xD0C: "Neoverse-N1", 0xD0D: "Cortex-A77", 0xD40: "Neoverse-V1", 0xD41: "Cortex-A78",
    0xD44: "Cortex-X1", 0xD46: "Cortex-A510", 0xD47: "Cortex-A710", 0xD48: "Cortex-X2",
    0xD49: "Neoverse-N2", 0xD4F: "Neoverse-V2", 0xD80: "Cortex-A520",
    0xD81: "Cortex-A720", 0xD82: "Cortex-X4",
}
APPLE_GEN = {
    "M1": "Firestorm (P) / Icestorm (E)",
    "M2": "Avalanche (P) / Blizzard (E)",
}


def infer_microarch(vendor, family, model, stepping, implementer, part, brand):
    """Returns (name, source) -- name may be None."""
    v = (vendor or "").lower()
    if "intel" in v and family == 6 and model in INTEL_FAM6:
        name = INTEL_FAM6[model]
        if model == 0x55:  # handled below, kept for clarity
            pass
        return name, "intel family6 model table"
    if "intel" in v and family == 6 and model == 0x55:
        name = {4: "Skylake-SP", 5: "Cascade Lake", 6: "Cascade Lake",
                7: "Cascade Lake"}.get(stepping, "Cooper Lake" if stepping == 11 else "Skylake-SP")
        return name, "intel family6 model 0x55 + stepping"
    if "amd" in v and family:
        name = amd_microarch(family, model or 0)
        if name:
            return name, "amd family/model table"
    if implementer == 0x41 and part in ARM_PARTS:
        return ARM_PARTS[part], "arm implementer/part table"
    if brand and brand.startswith("Apple"):
        m = re.search(r"\bM(\d+)\b", brand)
        if m:
            key = f"M{m.group(1)}"
            return APPLE_GEN.get(key, f"Apple Silicon ({key} generation)"), "apple brand string"
    return None, None


def gcc_march():
    """Ask the compiler what -march=native resolves to (x86). Optional."""
    gcc = shutil.which("gcc") or shutil.which("cc")
    if not gcc:
        return None
    out = run([gcc, "-march=native", "-Q", "--help=target"])
    if out:
        m = re.search(r"^\s*-march=\s+(\S+)", out, re.M)
        if m and m.group(1) not in ("native", "x86-64", "generic"):
            return m.group(1)
    return None


# --------------------------------------------------------------------------
# LINUX
# --------------------------------------------------------------------------
def parse_cpuinfo():
    raw = read("/proc/cpuinfo") or ""
    blocks = []
    for blk in raw.split("\n\n"):
        d = {}
        for line in blk.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
        if d:
            blocks.append(d)
    return blocks


def lscpu_dict():
    out = run(["lscpu"]) or ""
    d = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def linux_cpu_ids():
    online = read("/sys/devices/system/cpu/online")
    if online:
        try:
            return parse_cpu_list(online)
        except ValueError:
            pass
    ids = [int(re.search(r"cpu(\d+)$", p).group(1))
           for p in glob.glob("/sys/devices/system/cpu/cpu[0-9]*")]
    return sorted(ids)


NOTABLE_FLAGS = ["sse4_2", "avx", "avx2", "fma", "avx512f", "avx512bw", "avx512vl",
                 "avx512_vnni", "amx_tile", "amx_bf16", "bmi2", "aes", "sha_ni",
                 "popcnt", "hypervisor"]


def linux_collect():
    notes = []
    ci = parse_cpuinfo()
    first = ci[0] if ci else {}
    ls = lscpu_dict()

    brand = first.get("model name") or ls.get("Model name") or first.get("Hardware")
    vendor = first.get("vendor_id") or ls.get("Vendor ID")
    family, model, stepping = (to_int(first.get("cpu family")), to_int(first.get("model")),
                               to_int(first.get("stepping")))
    implementer, part = to_int(first.get("CPU implementer")), to_int(first.get("CPU part"))

    ua, ua_src = infer_microarch(vendor, family, model, stepping, implementer, part, brand)
    if ua is None:
        g = gcc_march()
        if g:
            ua, ua_src = g, "gcc -march=native"
    if ua is None:
        notes.append("Microarchitecture could not be inferred; see family/model/stepping.")

    flags = set((first.get("flags") or first.get("Features") or "").split())

    # ---- frequency -------------------------------------------------------
    base = base_src = None
    v = to_int(read("/sys/devices/system/cpu/cpu0/cpufreq/base_frequency"))
    if v:
        base, base_src = v / 1000.0, "sysfs cpufreq/base_frequency"
    if base is None and brand:
        m = re.search(r"@\s*([\d.]+)\s*GHz", brand, re.I)
        if m:
            base, base_src = float(m.group(1)) * 1000, "nominal clock in brand string"
    maxf = to_int(read("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"))
    maxf = maxf / 1000.0 if maxf else None
    if maxf is None and ls.get("CPU max MHz"):
        maxf = float(ls["CPU max MHz"])
    cur = None
    try:
        cur = float(first["cpu MHz"]) if "cpu MHz" in first else None
    except ValueError:
        pass
    if base is None:
        notes.append("Base frequency not exposed by this system "
                     "(VM/container or non-Intel cpufreq); see max/current MHz.")

    freq = {"base_mhz": base, "base_source": base_src,
            "max_mhz": maxf, "current_mhz_snapshot": cur}

    # ---- topology --------------------------------------------------------
    cpus = linux_cpu_ids()
    pairs, pkgs, thread_counts = set(), set(), {}
    for c in cpus:
        base_dir = f"/sys/devices/system/cpu/cpu{c}/topology"
        core = read(f"{base_dir}/core_id")
        pkg = read(f"{base_dir}/physical_package_id")
        die = read(f"{base_dir}/die_id") or "0"
        if core is not None and pkg is not None:
            pairs.add((pkg, die, core))
            pkgs.add(pkg)
            thread_counts[(pkg, die, core)] = thread_counts.get((pkg, die, core), 0) + 1
    topo_src = "sysfs topology"
    if not pairs:
        out = run(["lscpu", "-p=CPU,CORE,SOCKET"])
        if out:
            for line in out.splitlines():
                if line and not line.startswith("#"):
                    cpu, core, sock = line.split(",")[:3]
                    pairs.add((sock, "0", core))
                    pkgs.add(sock)
                    thread_counts[(sock, "0", core)] = thread_counts.get((sock, "0", core), 0) + 1
            topo_src = "lscpu -p"
    logical = len(cpus) or os.cpu_count()
    physical = len(pairs) or None
    if physical is None:
        phys_ids = {(b.get("physical id"), b.get("core id")) for b in ci if "core id" in b}
        physical = len(phys_ids) or None
        topo_src = "/proc/cpuinfo"
    tpc = max(thread_counts.values()) if thread_counts else (
        (logical // physical) if physical else None)

    smt_ctl = read("/sys/devices/system/cpu/smt/control")
    smt_act = read("/sys/devices/system/cpu/smt/active")
    smt_enabled = (tpc or 1) > 1
    topology = {
        "sockets": len(pkgs) or to_int(ls.get("Socket(s)")),
        "physical_cores": physical,
        "logical_threads": logical,
        "threads_per_core": tpc,
        "smt_enabled": smt_enabled,
        "smt_detection": {
            "method": topo_src,
            "kernel_smt_active": smt_act,
            "kernel_smt_control": smt_ctl,
        },
        "usable_logical_cpus_for_this_process": (
            len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None),
    }
    if smt_ctl in ("off", "forceoff", "notsupported") and tpc and tpc > 1:
        notes.append("SMT reported by topology but kernel control says off; verify.")

    # ---- caches ----------------------------------------------------------
    cache = linux_caches(cpus, notes)

    return {
        "cpu": {
            "model_name": brand, "vendor": vendor, "architecture": platform.machine(),
            "microarchitecture": ua, "microarchitecture_source": ua_src,
            "family": family, "model": model, "stepping": stepping,
            "arm_implementer": implementer, "arm_part": part,
            "frequency": freq,
            "isa_extensions_present": sorted(f for f in NOTABLE_FLAGS if f in flags),
            "running_under_hypervisor": "hypervisor" in flags,
        },
        "topology": topology, "cache": cache, "notes": notes,
    }


def linux_caches(cpus, notes):
    root = "/sys/devices/system/cpu"
    per_cpu_sig = {}
    levels = {}   # (level, type) -> info from first CPU that reports it
    instances = {}  # (level, type) -> set of shared_cpu_list strings

    for c in cpus or [0]:
        sig = []
        for idx in sorted(glob.glob(f"{root}/cpu{c}/cache/index[0-9]*")):
            lvl, typ = to_int(read(f"{idx}/level")), read(f"{idx}/type")
            size = parse_size(read(f"{idx}/size"))
            shared = read(f"{idx}/shared_cpu_list")
            if lvl is None or typ is None:
                continue
            sig.append((lvl, typ, size))
            instances.setdefault((lvl, typ), set()).add(shared)
            if (lvl, typ) not in levels:
                levels[(lvl, typ)] = {
                    "level": lvl, "type": typ, "size_bytes": size,
                    "size_human": human(size),
                    "line_size_bytes": to_int(read(f"{idx}/coherency_line_size")),
                    "ways_of_associativity": to_int(read(f"{idx}/ways_of_associativity")),
                    "sets": to_int(read(f"{idx}/number_of_sets")),
                    "shared_by_logical_cpus": len(parse_cpu_list(shared)) if shared else None,
                }
        per_cpu_sig[c] = tuple(sig)

    details = []
    for key, info in sorted(levels.items()):
        info["instances_in_system"] = len(instances[key])
        if info["size_bytes"]:
            info["total_bytes_all_instances"] = info["size_bytes"] * len(instances[key])
        details.append(info)

    def pick(level, types):
        for t in types:
            if (level, t) in levels:
                return levels[(level, t)]
        return None

    l1d, l1i = pick(1, ["Data"]), pick(1, ["Instruction"])
    l2, l3 = pick(2, ["Unified", "Data"]), pick(3, ["Unified", "Data"])
    src = "sysfs cache/index*"

    # fallback: getconf / lscpu
    if not l1d and not l2 and not l3:
        src = "getconf / lscpu fallback"
        gc = lambda n: to_int(run(["getconf", n]))
        l1d = {"size_bytes": gc("LEVEL1_DCACHE_SIZE"), "line_size_bytes": gc("LEVEL1_DCACHE_LINESIZE")}
        l2 = {"size_bytes": gc("LEVEL2_CACHE_SIZE"), "line_size_bytes": gc("LEVEL2_CACHE_LINESIZE")}
        l3 = {"size_bytes": gc("LEVEL3_CACHE_SIZE"), "line_size_bytes": gc("LEVEL3_CACHE_LINESIZE")}
        ls = lscpu_dict()
        for name, tgt in (("L1d cache", "l1d"), ("L2 cache", "l2"), ("L3 cache", "l3")):
            s = parse_size(ls.get(name))
            cur = {"l1d": l1d, "l2": l2, "l3": l3}[tgt]
            if s and not cur.get("size_bytes"):
                cur["size_bytes"] = s
        if not any(x.get("size_bytes") for x in (l1d, l2, l3)):
            notes.append("No cache information exposed by this environment.")

    line = None
    for x in (l1d, l2, l3):
        if x and x.get("line_size_bytes"):
            line = x["line_size_bytes"]
            break
    if line is None:
        try:
            line = os.sysconf("SC_LEVEL1_DCACHE_LINESIZE") or None
        except (ValueError, OSError, AttributeError):
            line = None

    sigs = set(per_cpu_sig.values())
    hybrid = len(sigs) > 1
    if hybrid:
        notes.append("Heterogeneous cache layout detected (e.g. P/E cores); "
                     "top-level sizes are from the first CPU reporting each cache.")

    return {
        "source": src,
        "l1d_size_bytes": (l1d or {}).get("size_bytes"),
        "l1i_size_bytes": (l1i or {}).get("size_bytes"),
        "l2_size_bytes": (l2 or {}).get("size_bytes"),
        "l3_size_bytes": (l3 or {}).get("size_bytes"),
        "l3_shared_by_logical_cpus": (l3 or {}).get("shared_by_logical_cpus"),
        "cache_line_size_bytes": line,
        "sizes_are": "per cache instance (L1/L2 typically per core, L3 shared)",
        "heterogeneous_caches": hybrid,
        "details": details,
    }


# --------------------------------------------------------------------------
# macOS
# --------------------------------------------------------------------------
def sysctl(name):
    v = run(["sysctl", "-n", name])
    if v is None:
        return None
    return to_int(v) if re.fullmatch(r"-?\d+", v) else v


def darwin_collect():
    notes = []
    brand = sysctl("machdep.cpu.brand_string")
    vendor = sysctl("machdep.cpu.vendor")
    family, model, stepping = (sysctl("machdep.cpu.family"), sysctl("machdep.cpu.model"),
                               sysctl("machdep.cpu.stepping"))
    ua, ua_src = infer_microarch(vendor, family, model, stepping, None, None, brand)
    if ua is None:
        notes.append("Microarchitecture could not be inferred.")

    hz = sysctl("hw.cpufrequency")
    hzmax = sysctl("hw.cpufrequency_max")
    base = hz / 1e6 if isinstance(hz, int) else None
    if base is None:
        notes.append("macOS does not expose CPU frequency on Apple Silicon.")
    freq = {"base_mhz": base, "base_source": "sysctl hw.cpufrequency" if base else None,
            "max_mhz": hzmax / 1e6 if isinstance(hzmax, int) else None,
            "current_mhz_snapshot": None}

    physical, logical = sysctl("hw.physicalcpu"), sysctl("hw.logicalcpu")
    topology = {
        "sockets": sysctl("hw.packages"),
        "physical_cores": physical, "logical_threads": logical,
        "threads_per_core": (logical // physical) if physical and logical else None,
        "smt_enabled": bool(physical and logical and logical > physical),
        "smt_detection": {"method": "sysctl hw.physicalcpu vs hw.logicalcpu"},
        "usable_logical_cpus_for_this_process": os.cpu_count(),
    }

    levels = sysctl("hw.nperflevels")
    details = []
    if isinstance(levels, int) and levels >= 1:  # Apple Silicon P/E clusters
        for i in range(levels):
            details.append({
                "perf_level": i, "name": sysctl(f"hw.perflevel{i}.name"),
                "physical_cores": sysctl(f"hw.perflevel{i}.physicalcpu"),
                "l1d_size_bytes": sysctl(f"hw.perflevel{i}.l1dcachesize"),
                "l1i_size_bytes": sysctl(f"hw.perflevel{i}.l1icachesize"),
                "l2_size_bytes": sysctl(f"hw.perflevel{i}.l2cachesize"),
            })
    top = details[0] if details else {}
    cache = {
        "source": "sysctl",
        "l1d_size_bytes": top.get("l1d_size_bytes") or sysctl("hw.l1dcachesize"),
        "l1i_size_bytes": top.get("l1i_size_bytes") or sysctl("hw.l1icachesize"),
        "l2_size_bytes": top.get("l2_size_bytes") or sysctl("hw.l2cachesize"),
        "l3_size_bytes": sysctl("hw.l3cachesize"),
        "l3_shared_by_logical_cpus": None,
        "cache_line_size_bytes": sysctl("hw.cachelinesize"),
        "sizes_are": "per core class (perflevel0 = performance cores) where available",
        "heterogeneous_caches": len(details) > 1,
        "details": details,
    }
    return {
        "cpu": {"model_name": brand, "vendor": vendor, "architecture": platform.machine(),
                "microarchitecture": ua, "microarchitecture_source": ua_src,
                "family": family, "model": model, "stepping": stepping,
                "frequency": freq, "isa_extensions_present": [],
                "running_under_hypervisor": bool(sysctl("kern.hv_vmm_present"))},
        "topology": topology, "cache": cache, "notes": notes,
    }


# --------------------------------------------------------------------------
# Windows (best effort)
# --------------------------------------------------------------------------
def windows_collect():
    notes = ["Windows: L1 cache and cache-line size are not exposed via WMI; "
             "line size is assumed to be 64 B."]
    ps = ("Get-CimInstance Win32_Processor | Select-Object Name,Manufacturer,NumberOfCores,"
          "NumberOfLogicalProcessors,MaxClockSpeed,L2CacheSize,L3CacheSize,Caption | ConvertTo-Json")
    out = run(["powershell", "-NoProfile", "-Command", ps], timeout=30)
    procs = []
    if out:
        try:
            j = json.loads(out)
            procs = j if isinstance(j, list) else [j]
        except json.JSONDecodeError:
            pass
    p = procs[0] if procs else {}
    physical = sum(x.get("NumberOfCores") or 0 for x in procs) or None
    logical = sum(x.get("NumberOfLogicalProcessors") or 0 for x in procs) or os.cpu_count()
    brand = p.get("Name") or platform.processor()
    ua, ua_src = None, None
    m = re.search(r"Family (\d+) Model (\d+) Stepping (\d+)", p.get("Caption") or platform.processor() or "")
    fam = mod = step = None
    if m:
        fam, mod, step = map(int, m.groups())
        ua, ua_src = infer_microarch("intel" if "Intel" in (brand or "") else "amd",
                                     fam, mod, step, None, None, brand)
    mhz = p.get("MaxClockSpeed")
    kb = lambda v: v * 1024 if v else None
    return {
        "cpu": {"model_name": brand, "vendor": (p.get("Manufacturer") or "").strip(),
                "architecture": platform.machine(), "microarchitecture": ua,
                "microarchitecture_source": ua_src, "family": fam, "model": mod, "stepping": step,
                "frequency": {"base_mhz": mhz, "base_source": "Win32_Processor.MaxClockSpeed (nominal)",
                              "max_mhz": None, "current_mhz_snapshot": None},
                "isa_extensions_present": [], "running_under_hypervisor": None},
        "topology": {"sockets": len(procs) or None, "physical_cores": physical,
                     "logical_threads": logical,
                     "threads_per_core": (logical // physical) if physical and logical else None,
                     "smt_enabled": bool(physical and logical and logical > physical),
                     "smt_detection": {"method": "Win32_Processor core vs logical counts"},
                     "usable_logical_cpus_for_this_process": os.cpu_count()},
        "cache": {"source": "Win32_Processor", "l1d_size_bytes": None, "l1i_size_bytes": None,
                  "l2_size_bytes": kb(p.get("L2CacheSize")), "l3_size_bytes": kb(p.get("L3CacheSize")),
                  "l3_shared_by_logical_cpus": None, "cache_line_size_bytes": 64,
                  "cache_line_size_is_assumed": True,
                  "sizes_are": "L2/L3 as reported per processor package (L2 may be a total)",
                  "heterogeneous_caches": None, "details": []},
        "notes": notes,
    }


# --------------------------------------------------------------------------
# OS + Python
# --------------------------------------------------------------------------
def os_info():
    u = platform.uname()
    info = {
        "system": u.system, "node": u.node, "kernel_release": u.release,
        "kernel_version": u.version, "machine": u.machine,
        "platform_string": platform.platform(),
    }
    if u.system == "Linux":
        info["proc_version"] = read("/proc/version")
        try:
            rel = platform.freedesktop_os_release()
            info["distribution"] = rel.get("PRETTY_NAME")
        except (AttributeError, OSError):
            pass
    elif u.system == "Darwin":
        info["macos_version"] = platform.mac_ver()[0]
    elif u.system == "Windows":
        info["windows_edition"] = platform.win32_edition() if hasattr(platform, "win32_edition") else None
    return info


def python_info():
    gil = None
    if hasattr(sys, "_is_gil_enabled"):  # 3.13+
        gil = sys._is_gil_enabled()
    return {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
        "version_info": list(sys.version_info[:3]) + [sys.version_info.releaselevel],
        "compiler": platform.python_compiler(),
        "build": list(platform.python_build()),
        "executable": sys.executable,
        "pointer_bits": 64 if sys.maxsize > 2 ** 32 else 32,
        "byte_order": sys.byteorder,
        "gil_enabled": gil,
        "sys_implementation": sys.implementation.name,
    }


# --------------------------------------------------------------------------
def psutil_fallback(data):
    """Fill gaps (core counts, frequency) from psutil if it is installed."""
    try:
        import psutil
    except ImportError:
        return
    t, f = data.get("topology", {}), data.get("cpu", {}).setdefault("frequency", {})
    try:
        if not t.get("physical_cores"):
            t["physical_cores"] = psutil.cpu_count(logical=False)
            t.setdefault("smt_detection", {})["method"] = "psutil.cpu_count(logical=False)"
        if not t.get("logical_threads"):
            t["logical_threads"] = psutil.cpu_count(logical=True)
        pc, lt = t.get("physical_cores"), t.get("logical_threads")
        if pc and lt:
            t["threads_per_core"] = lt // pc
            t["smt_enabled"] = lt > pc
        fr = psutil.cpu_freq()
        if fr:
            if not f.get("base_mhz") and fr.max:
                f["base_mhz"], f["base_source"] = fr.max, "psutil.cpu_freq().max (nominal max, not true base)"
            if not f.get("current_mhz_snapshot"):
                f["current_mhz_snapshot"] = fr.current
    except Exception:
        pass


def collect():
    system = platform.system()
    if system == "Linux":
        data = linux_collect()
    elif system == "Darwin":
        data = darwin_collect()
    elif system == "Windows":
        data = windows_collect()
    else:
        data = {"cpu": {"model_name": platform.processor()}, "topology": {
            "logical_threads": os.cpu_count()}, "cache": {},
            "notes": [f"Unsupported OS '{system}'; only basic data collected."]}
    psutil_fallback(data)
    return {
        "schema_version": SCHEMA_VERSION,
        "collected_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        **data,
        "os": os_info(),
        "python": python_info(),
    }


def main():
    ap = argparse.ArgumentParser(description="Extract machine telemetry to JSON.")
    ap.add_argument("-o", "--output", default=os.path.join("results", "host_profile.json"),
                    help="output JSON path (default: results/host_profile.json)")
    ap.add_argument("--stdout", action="store_true", help="also print the JSON")
    args = ap.parse_args()

    data = collect()
    args.output = os.path.normpath(args.output)
    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    c, t, k = data["cpu"], data["topology"], data["cache"]
    print(f"[ok] wrote {args.output}")
    print(f"  CPU        : {c.get('model_name')}  ({c.get('microarchitecture') or 'uarch unknown'})")
    print(f"  Base freq  : {(c.get('frequency') or {}).get('base_mhz')} MHz")
    print(f"  Cores/Thr  : {t.get('physical_cores')} physical / {t.get('logical_threads')} logical "
          f"(SMT {'on' if t.get('smt_enabled') else 'off'})")
    print(f"  L1d/L2/L3  : {human(k.get('l1d_size_bytes'))} / {human(k.get('l2_size_bytes'))} / "
          f"{human(k.get('l3_size_bytes'))}   line={k.get('cache_line_size_bytes')} B")
    print(f"  Kernel     : {data['os'].get('system')} {data['os'].get('kernel_release')}")
    print(f"  Python     : {data['python']['implementation']} {data['python']['version']}")
    for n in data.get("notes", []):
        print(f"  note: {n}")
    if args.stdout:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()