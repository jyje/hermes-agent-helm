"""Tests for .github/scripts/doctor-memory.py.

`measure` runs in a Hermes pod and `check` on the CI runner (see the script's
docstring). A temporary file stands in for the container's cgroup
`memory.stat`, and a short Python child stands in for `hermes doctor`.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / ".github/scripts/doctor-memory.py"
spec = importlib.util.spec_from_file_location("doctor_memory", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MIB = 1024 * 1024
# Grows the fake cgroup's anonymous memory, holds it long enough to be
# sampled, then exits like a doctor that reported findings.
GROW = (
    "import pathlib, sys, time;"
    "pathlib.Path(sys.argv[1]).write_text('anon 700\\nfile 9000\\n');"
    "time.sleep(0.5); sys.exit(1)"
)


class MeasureTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(module, "SETTLE_SECONDS", 0)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_reports_growth_over_the_baseline_and_keeps_the_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            stat = Path(tmp) / "memory.stat"
            stat.write_text("anon 200\nfile 5000\nshmem 100\n", encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                status = module.measure([sys.executable, "-c", GROW, str(stat)], stat)
        self.assertEqual(status, 1)
        # 700 anonymous bytes at the peak, minus the 300 that were there before.
        self.assertRegex(out.getvalue(), r"^DOCTOR_MEMORY peak_bytes=400 largest_process_bytes=\d+ settled=1$")

    def test_baseline_waits_for_a_container_that_is_still_growing(self):
        growing = iter([100 * MIB, 180 * MIB, 260 * MIB, 300 * MIB, 301 * MIB, 302 * MIB, 303 * MIB, 304 * MIB])
        self.assertEqual(module.settled_baseline(lambda: next(growing)), (304 * MIB, True))

    def test_a_container_that_never_settles_is_flagged(self):
        growing = iter(range(0, 10**12, 64 * MIB))
        with mock.patch.object(module, "SETTLE_TRIES", 8):
            baseline, settled = module.settled_baseline(lambda: next(growing))
        self.assertEqual((baseline, settled), (7 * 64 * MIB, False))

    def test_without_cgroup_v2_counters_only_the_largest_process_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            stat = Path(tmp) / "memory.stat"
            stat.write_text("rss 200\ncache 5000\n", encoding="utf-8")  # cgroup v1 names
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                status = module.measure([sys.executable, "-c", "pass"], stat)
        self.assertEqual(status, 0)
        self.assertRegex(out.getvalue(), r"^DOCTOR_MEMORY largest_process_bytes=\d+$")

    def test_page_cache_is_not_counted(self):
        self.assertEqual(module.unreclaimable("anon 10\nfile 999\nshmem 5\nsock 1\n"), 16)


class QuantityTests(unittest.TestCase):
    def test_binary_decimal_and_plain_quantities(self):
        self.assertEqual(module.parse_quantity("1Gi"), 1024 * MIB)
        self.assertEqual(module.parse_quantity("512Mi"), 512 * MIB)
        self.assertEqual(module.parse_quantity("1G"), 1000**3)
        self.assertEqual(module.parse_quantity(1048576), MIB)

    def test_unknown_quantities_are_not_guessed(self):
        for value in ("", "lots", "1Xi", None, {"memory": "1Gi"}):
            with self.subTest(value=value):
                self.assertIsNone(module.parse_quantity(value))


class CheckTests(unittest.TestCase):
    VALUES = {"tests": {"resources": {"limits": {"cpu": "1", "memory": "1Gi"}}}}

    def output(self, peak_mib: int, settled: int = 1) -> str:
        return f"DOCTOR_MEMORY peak_bytes={peak_mib * MIB} largest_process_bytes={400 * MIB} settled={settled}"

    def test_enough_headroom_is_reported_without_a_warning(self):
        lines = module.check(self.output(500), self.VALUES)
        self.assertEqual(
            lines,
            ["doctor memory: peak 500 MiB (largest process 400 MiB); test Job limit 1024 MiB; headroom 2.05x"],
        )

    def test_short_headroom_warns_with_the_limit_to_set(self):
        lines = module.check(self.output(800), self.VALUES)
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].startswith("::warning::"), lines[1])
        self.assertIn("(1.28x)", lines[1])
        self.assertIn("at least 1200Mi", lines[1])

    def test_a_pod_that_was_still_growing_is_reported_but_not_compared(self):
        lines = module.check(self.output(800, settled=0), self.VALUES)
        self.assertEqual(len(lines), 1)
        self.assertIn("peak 800 MiB", lines[0])
        self.assertIn("not compared with the limit", lines[0])

    def test_missing_marker_is_reported_as_not_measured(self):
        for marker in ("", "Hermes Doctor", "DOCTOR_MEMORY"):
            with self.subTest(marker=marker):
                self.assertEqual(module.check(marker, self.VALUES), ["doctor memory: not measured"])

    def test_largest_process_stands_in_when_the_cgroup_was_unreadable(self):
        lines = module.check(f"DOCTOR_MEMORY largest_process_bytes={800 * MIB}", self.VALUES)
        self.assertIn("from the largest process only", lines[0])
        self.assertTrue(lines[1].startswith("::warning::"), lines[1])

    def test_a_release_without_a_limit_gets_no_warning(self):
        for values in ({}, {"tests": {"resources": {}}}, {"tests": {"resources": {"limits": {"memory": "lots"}}}}):
            with self.subTest(values=values):
                lines = module.check(self.output(800), values)
                self.assertEqual(len(lines), 1)
                self.assertIn("no readable memory limit", lines[0])


if __name__ == "__main__":
    unittest.main()
