import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / ".github/scripts/requires-live-chat.py"
spec = importlib.util.spec_from_file_location("requires_live_chat", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RequiresLiveChatTests(unittest.TestCase):
    def test_documentation_and_release_tooling_need_no_live_model(self):
        self.assertFalse(module.requires_live_chat([
            "README.md", "charts/hermes-agent/README-ja.md",
            "charts/hermes-agent/README.md.gotmpl", "docs/ko/contributing/ci.md",
            ".github/scripts/sync-values-table.py", "tests/test_sync_values_table.py",
            ".github/scripts/release/detect-upstream-python.py",
        ], False))

    def test_chart_inputs_and_live_harness_keep_live_coverage(self):
        for path in ("charts/hermes-agent/values.yaml", "charts/hermes-agent/values-openai.yaml",
                     "charts/hermes-agent/templates/deployment.yaml",
                     "charts/hermes-agent/files/device_login.py", ".github/scripts/lib.sh",
                     ".github/scripts/scenario-message.sh", ".github/workflows/validate-chart.yaml"):
            with self.subTest(path=path):
                self.assertTrue(module.requires_live_chat([path], False))
        self.assertTrue(module.requires_live_chat(["charts/hermes-agent/Chart.yaml"], True))
        self.assertFalse(module.requires_live_chat(["charts/hermes-agent/Chart.yaml"], False))

    def test_cli_uses_the_actual_chart_diff_and_fails_closed_on_missing_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
            git("init", "-q")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "user.name", "Fixture")
            git("config", "commit.gpgsign", "false")
            chart = root / "charts/hermes-agent/Chart.yaml"
            chart.parent.mkdir(parents=True)
            chart.write_text("version: 1.20.0\nappVersion: v0.22.2\n")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            chart.write_text("version: 1.20.1\nappVersion: v0.22.2\n")
            git("commit", "-qam", "chart release only")
            def run(base_ref):
                return subprocess.check_output(
                    [sys.executable, str(SCRIPT), "--base", base_ref, "--head", "HEAD"],
                    cwd=root, text=True).strip()
            self.assertEqual(run(base), "live_chat=false")
            chart.write_text("version: 1.20.1\nappVersion: v0.23.0\n")
            git("commit", "-qam", "new image")
            self.assertEqual(run(base), "live_chat=true")
            self.assertEqual(run("f" * 40), "live_chat=true")


if __name__ == "__main__":
    unittest.main()
