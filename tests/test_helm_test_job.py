import shutil
import subprocess
import unittest
from pathlib import Path


CHART = Path(__file__).parents[1] / "charts/hermes-agent"


def render_test_job(*args):
    return subprocess.run(
        ["helm", "template", "t", str(CHART), "--show-only", "templates/tests/test-hermes-doctor.yaml", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


@unittest.skipUnless(shutil.which("helm"), "helm is not installed")
class HelmTestJobCodexCheckTests(unittest.TestCase):
    def test_codex_device_flow_checks_the_native_helpers(self):
        text = render_test_job("-f", str(CHART / "values-openai-codex.yaml"))
        self.assertIn("python3 /login/device_login.py --check-native", text)
        self.assertIn("name: login-script", text)

    def test_copilot_device_flow_does_not_add_the_check(self):
        text = render_test_job("-f", str(CHART / "values-github-copilot.yaml"))
        self.assertNotIn("--check-native", text)
        self.assertNotIn("login-script", text)

    def test_no_device_flow_does_not_add_the_check(self):
        text = render_test_job()
        self.assertNotIn("--check-native", text)
        self.assertNotIn("login-script", text)


@unittest.skipUnless(shutil.which("helm"), "helm is not installed")
class HelmTestJobReadyHookTests(unittest.TestCase):
    def test_enabled_hook_is_seeded_and_loaded_by_the_real_registry(self):
        text = render_test_job("--set", "readyNotify.enabled=true", "--set", "readyNotify.notify=telegram")
        self.assertIn("from gateway.hooks import HookRegistry", text)
        self.assertIn("/hooks/ready-notify/handler.py", text)

    def test_disabled_hook_adds_nothing(self):
        text = render_test_job()
        self.assertNotIn("HookRegistry", text)
        self.assertNotIn("ready-notify", text)


if __name__ == "__main__":
    unittest.main()
