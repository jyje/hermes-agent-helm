import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / ".github/scripts/release/detect-upstream-python.py"
spec = importlib.util.spec_from_file_location("detect_upstream_python", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DetectUpstreamPythonTests(unittest.TestCase):
    def test_managed_pin_wins_over_obsolete_dockerfile_comment(self):
        lock = {
            "historical_dockerfile_comment": "uv:0.11.6-python3.13-trixie",
            "packages": {
                "uv": {"version": "0.11.6"},
                "python": {"version": "3.14.7+20260901"},
            },
        }
        self.assertEqual(module.python_minor(lock), "3.14")

    def test_plain_release_pin(self):
        self.assertEqual(module.python_minor({"packages": {"python": {"version": "3.15.1"}}}), "3.15")

    def test_missing_or_malformed_pin_does_not_guess(self):
        for lock in ({}, [], {"packages": {}}, {"packages": {"python": None}},
                     {"packages": {"python": {"version": 3.14}}},
                     {"packages": {"python": {"version": "python3.13"}}},
                     {"packages": {"python": {"version": "3.14"}}}):
            with self.subTest(lock=lock), self.assertRaises(ValueError):
                module.python_minor(lock)

    def test_cli_reports_invalid_input_without_a_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock.json"
            for contents in ("not-json", json.dumps({"packages": {}})):
                path.write_text(contents)
                result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("Cannot detect upstream Python", result.stderr)


if __name__ == "__main__":
    unittest.main()
