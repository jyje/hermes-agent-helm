#!/usr/bin/env python3
"""Measure the memory `hermes doctor` needs and compare it with the Helm test limit.

The chart's test Job runs `hermes doctor` under `tests.resources.limits.memory`.
That Job was once OOMKilled at a limit it had passed under before, and the kill
was the first sign. lib.sh's `run_doctor` uses the two modes below so that
shrinking headroom shows up as a CI warning while the Job still passes.

`measure` runs inside a Hermes pod (lib.sh feeds this file to `python3 -` on
stdin). It waits for the container to stop growing, runs the doctor unchanged,
samples the container's cgroup while it runs, prints one marker line and exits
with the doctor's own status.

`check` runs on the CI runner. It takes that marker line and reads the release's
computed values on stdin (they hold secrets, so they never touch argv or disk),
and warns when the test Job's limit is less than HEADROOM times the measured
peak. It never fails: the limit holding is the Helm test's own job.
"""

from __future__ import annotations

import argparse
import json
import re
import resource
import subprocess
import sys
import time
from pathlib import Path

CGROUP_STAT = Path("/sys/fs/cgroup/memory.stat")
# cgroup v2 counters the kernel cannot reclaim under pressure (a pod has no
# swap). Page cache is left out on purpose: it grows to fill any limit and is
# dropped on demand, so it says nothing about what the doctor needs.
UNRECLAIMABLE = ("anon", "shmem", "kernel_stack", "pagetables", "percpu", "sock", "slab_unreclaimable")
SAMPLE_SECONDS = 0.1
# The baseline counts as settled once this many samples, one per interval, stay
# within the spread. A pod that never settles is reported but not compared.
SETTLE_SAMPLES = 5
SETTLE_SECONDS = 1.0
SETTLE_SPREAD = 16 * 1024 * 1024
SETTLE_TRIES = 60
MARKER = "DOCTOR_MEMORY"
HEADROOM = 1.5
MIB = 1024 * 1024
UNITS = {
    "": 1,
    "k": 1000, "M": 1000**2, "G": 1000**3, "T": 1000**4,
    "Ki": 1024, "Mi": 1024**2, "Gi": 1024**3, "Ti": 1024**4,
}


def unreclaimable(stat_text: str) -> int | None:
    """Bytes the container cannot give back, or None without cgroup v2 counters."""
    stat = dict(line.split()[:2] for line in stat_text.splitlines() if len(line.split()) >= 2)
    if "anon" not in stat:
        return None
    return sum(int(stat.get(key, 0)) for key in UNRECLAIMABLE)


def settled_baseline(sample) -> tuple[int | None, bool]:
    """The container's memory once it stops growing, and whether it did.

    The growth over this baseline is credited to the doctor, so a gateway that
    is still starting (a pod that was just restarted) must finish first.
    """
    recent: list[int] = []
    for _ in range(SETTLE_TRIES):
        current = sample()
        if current is None:
            return None, False
        recent = [*recent, current][-SETTLE_SAMPLES:]
        if len(recent) == SETTLE_SAMPLES and max(recent) - min(recent) < SETTLE_SPREAD:
            return current, True
        time.sleep(SETTLE_SECONDS)
    return recent[-1], False


def measure(command: list[str], stat_path: Path = CGROUP_STAT) -> int:
    def sample() -> int | None:
        try:
            return unreclaimable(stat_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    # The pod's other processes (the gateway) are already in the baseline, so
    # the growth over it is what the doctor itself adds.
    baseline, settled = settled_baseline(sample)
    peak = baseline
    proc = subprocess.Popen(command, stdin=subprocess.DEVNULL)
    while proc.poll() is None:
        current = sample()
        if current is not None and (peak is None or current > peak):
            peak = current
        time.sleep(SAMPLE_SECONDS)
    # ru_maxrss is the largest single child process, in KiB on Linux.
    largest = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024
    fields = f"largest_process_bytes={largest}"
    if baseline is not None and peak is not None:
        fields = f"peak_bytes={peak - baseline} {fields} settled={int(settled)}"
    sys.stdout.flush()
    print(f"{MARKER} {fields}", flush=True)
    return proc.returncode if proc.returncode >= 0 else 128 - proc.returncode


def parse_quantity(value: object) -> int | None:
    """Bytes for a Kubernetes memory quantity such as 1Gi, 512Mi, 1G or 1048576."""
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([A-Za-z]*)", str(value).strip())
    if match is None or match[2] not in UNITS:
        return None
    return int(float(match[1]) * UNITS[match[2]])


def job_memory_limit(values: object) -> int | None:
    try:
        return parse_quantity(values["tests"]["resources"]["limits"]["memory"])
    except (KeyError, TypeError):
        return None


def check(marker: str, values: object) -> list[str]:
    """Lines to print on the runner; a `::warning::` line when headroom is short."""
    measured = dict(re.findall(r"(\w+)=(\d+)", marker)) if marker.startswith(MARKER) else {}
    largest = int(measured.get("largest_process_bytes", 0))
    # Without cgroup v2 counters the largest process is the best lower bound.
    peak = int(measured.get("peak_bytes", 0)) or largest
    if peak <= 0:
        return ["doctor memory: not measured"]
    summary = f"doctor memory: peak {peak // MIB} MiB (largest process {largest // MIB} MiB)"
    if not int(measured.get("peak_bytes", 0)):
        summary += ", from the largest process only"
    if measured.get("settled") == "0":
        return [f"{summary}; the pod was still growing when the doctor started, so it is not compared with the limit"]
    limit = job_memory_limit(values)
    if limit is None:
        return [f"{summary}; the test Job has no readable memory limit"]
    ratio = limit / peak
    lines = [f"{summary}; test Job limit {limit // MIB} MiB; headroom {ratio:.2f}x"]
    if ratio < HEADROOM:
        needed = -(-int(peak * HEADROOM) // MIB)
        lines.append(
            f"::warning::hermes doctor needed {peak // MIB} MiB and tests.resources.limits.memory"
            f" allows {limit // MIB} MiB ({ratio:.2f}x). Raise the limit to at least {needed}Mi"
            f" to keep {HEADROOM}x headroom before the Helm test is OOMKilled."
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    modes = parser.add_subparsers(dest="mode", required=True)
    modes.add_parser("measure", help="run hermes doctor in this container and report its peak memory")
    checker = modes.add_parser(
        "check", help="compare a measured marker line with the test limit in `helm get values --all -o json` (stdin)"
    )
    checker.add_argument("--measured", required=True, help=f"the `{MARKER} ...` line that `measure` printed")
    args = parser.parse_args()
    if args.mode == "measure":
        return measure(["hermes", "doctor"])
    try:
        values = json.loads(sys.stdin.read())
    except ValueError:
        values = {}
    print("\n".join(check(args.measured, values)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
