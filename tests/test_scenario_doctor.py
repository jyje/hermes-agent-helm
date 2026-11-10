"""Tests for the scenario `run_doctor` helper in .github/scripts/lib.sh.

The helper mirrors the chart's `tests.doctorStrict` contract: `hermes doctor`
findings are printed but only fail a scenario when DOCTOR_STRICT=true, while a
doctor that never ran fails regardless. Stub `kubectl` and `helm` commands on
PATH stand in for the cluster so these run without kind.
"""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "lib.sh"

DOCTOR_OUTPUT = textwrap.dedent(
    """\
    ┌─────────────────────────────────────────────────────────┐
    │                 🩺 Hermes Doctor                        │
    └─────────────────────────────────────────────────────────┘
      Found 1 issue(s) to address:
      1. Missing ~/.local/bin/hermes symlink
    """
)


class RunDoctorTest(unittest.TestCase):
    def run_helper(self, *, stub_output: str, stub_rc: int, strict: str | None, values: str = "{}"):
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp) / "kubectl"
            payload = Path(tmp) / "out.txt"
            payload.write_text(stub_output, encoding="utf-8")
            stub.write_text(f'#!/bin/sh\ncat "{payload}"\nexit {stub_rc}\n', encoding="utf-8")
            stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
            # `helm get values --all -o json` for the memory headroom report.
            helm = Path(tmp) / "helm"
            helm.write_text(f"#!/bin/sh\ncat <<'JSON'\n{values}\nJSON\n", encoding="utf-8")
            helm.chmod(helm.stat().st_mode | stat.S_IEXEC)
            env = {"PATH": f"{tmp}:{os.environ['PATH']}", "NS": "t", "HOME": os.environ.get("HOME", tmp)}
            if strict is not None:
                env["DOCTOR_STRICT"] = strict
            return subprocess.run(
                ["bash", "-c", f'source "{LIB}"; run_doctor pod-0'],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_findings_are_non_fatal_by_default(self):
        result = self.run_helper(stub_output=DOCTOR_OUTPUT, stub_rc=1, strict=None)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hermes Doctor", result.stdout)
        self.assertIn("non-fatal", result.stdout)

    def test_findings_fail_in_strict_mode(self):
        result = self.run_helper(stub_output=DOCTOR_OUTPUT, stub_rc=1, strict="true")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("DOCTOR_STRICT=true", result.stdout)

    def test_clean_doctor_passes_in_strict_mode(self):
        result = self.run_helper(stub_output=DOCTOR_OUTPUT, stub_rc=0, strict="true")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_doctor_that_never_ran_fails_even_when_non_strict(self):
        result = self.run_helper(
            stub_output='error: unable to upgrade connection: container not found ("hermes-agent")\n',
            stub_rc=1,
            strict=None,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("did not run", result.stdout)

    def test_short_memory_headroom_warns_without_failing(self):
        result = self.run_helper(
            stub_output=DOCTOR_OUTPUT + f"DOCTOR_MEMORY peak_bytes={800 * 1024 * 1024} largest_process_bytes=0\n",
            stub_rc=0,
            strict="true",
            values='{"tests": {"resources": {"limits": {"memory": "1Gi"}}}}',
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("headroom 1.28x", result.stdout)
        self.assertIn("::warning::hermes doctor needed 800 MiB", result.stdout)

    def test_unmeasured_doctor_keeps_its_result(self):
        result = self.run_helper(stub_output=DOCTOR_OUTPUT, stub_rc=0, strict="true")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("doctor memory: not measured", result.stdout)


if __name__ == "__main__":
    unittest.main()
