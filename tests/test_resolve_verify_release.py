import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / '.github/scripts/resolve-verify-release.sh'


class ResolveVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'tag.gpgsign', 'false')
        self.chart = self.root / 'charts/hermes-agent/Chart.yaml'
        self.chart.parent.mkdir(parents=True)
        self.chart.write_text('name: hermes-agent\nversion: 1.21.0\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'release')
        self.release = self.git('rev-parse', 'HEAD')
        self.git('tag', 'v1.21.0')
        self.chart.write_text('name: hermes-agent\nversion: 1.22.0\n')
        self.git('commit', '-qam', 'new harness')
        self.harness = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def resolve(self, event='workflow_dispatch', version='1.21.0', trigger=''):
        return subprocess.run(['bash', str(SCRIPT)], cwd=self.root,
            env={**os.environ, 'EVENT_NAME': event, 'RELEASE_VERSION': version,
                 'TRIGGER_SHA': trigger}, text=True, capture_output=True)

    def test_manual_verification_uses_immutable_release_not_current_harness_metadata(self):
        result = self.resolve()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('version=1.21.0', result.stdout)
        self.assertIn(f'release_sha={self.release}', result.stdout)
        self.assertIn(self.harness, result.stderr)

    def test_successful_release_trigger_and_noop_keep_distinct_results(self):
        result = self.resolve('workflow_run', trigger=self.release)
        self.assertEqual(result.returncode, 0)
        self.assertIn('should_verify=true', result.stdout)
        result = self.resolve('workflow_run', trigger=self.harness)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), 'should_verify=false')

    def test_bad_input_missing_tag_and_mismatched_tag_fail_closed(self):
        for version in ('v1.21.0', '1.99.0', '1.21.0; touch injected', '../main'):
            with self.subTest(version=version):
                self.assertNotEqual(self.resolve(version=version).returncode, 0)
        self.git('tag', 'v9.9.9')
        self.assertNotEqual(self.resolve(version='9.9.9').returncode, 0)
        self.assertFalse((self.root / 'injected').exists())
        self.assertNotEqual(self.resolve('workflow_run', trigger='main').returncode, 0)
