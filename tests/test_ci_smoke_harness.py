import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).parents[1]


class SmokeHarnessTests(unittest.TestCase):
    def run_harness(self, replies, discovery=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tool = root / 'kubectl'
            tool.write_text('''#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ['TRACE'], 'a') as stream:
    stream.write(json.dumps(args) + '\\n')
command = args[args.index('--') + 1:]
if command[:2] == ['sh', '-c']:
    sys.exit(subprocess.call(command))
if command[:3] == ['hermes', 'skills', 'list']:
    print('ci-ping' if os.environ['DISCOVERY'] == 'yes' else 'no registered skills')
    sys.exit(0)
model = command[command.index('-m') + 1]
reply, status = json.loads(os.environ['REPLIES'])[model]
print(reply)
sys.exit(status)
''')
            tool.chmod(0o755)
            result = subprocess.run(['bash', '-c', '''
source "$LIB"
timeout() { shift 3; "$@"; }
inject_ci_skill pod && chat_round_trip pod
'''], text=True, capture_output=True, env={**os.environ,
                'PATH': f'{root}:{os.environ["PATH"]}', 'LIB': str(ROOT / '.github/scripts/lib.sh'),
                'NS': 'fixture', 'CI_MODELS': ','.join(replies), 'REPLIES': json.dumps(replies),
                'TRACE': str(root / 'trace'), 'DISCOVERY': 'yes' if discovery else 'no',
                'HERMES_HOME': str(root / 'home')})
            calls = [json.loads(line) for line in (root / 'trace').read_text().splitlines()]
            skill = (root / 'home/skills/ci-ping/SKILL.md').read_text()
            return result, calls, skill

    def test_shared_fixture_is_discoverable_and_quiet_reply_is_checked(self):
        result, calls, skill = self.run_harness({'model-a': ('CI_PONG', 0)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(skill.startswith('---\nname: ci-ping\n'))
        self.assertIn('description:', skill)
        chat = calls[-1]
        self.assertIn('--quiet', chat)
        self.assertEqual(chat[chat.index('--skills') + 1], 'ci-ping')

    def test_zero_exit_with_wrong_answer_does_not_pass_and_can_fail_over(self):
        result, calls, _ = self.run_harness({
            'wrong': ('Skill not found', 0), 'right': ('CI_PONG', 0)})
        self.assertEqual(result.returncode, 0)
        self.assertIn('did not return CI_PONG', result.stdout)
        self.assertEqual(sum('chat' in call for call in calls), 2)
        result, _, _ = self.run_harness({'wrong': ('CI_PONG appears in my reasoning only', 0)})
        self.assertNotEqual(result.returncode, 0)
        result, _, _ = self.run_harness({'failed': ('CI_PONG', 1)})
        self.assertNotEqual(result.returncode, 0)

    def test_missing_discovery_stops_before_any_model_request(self):
        result, calls, _ = self.run_harness({'model-a': ('CI_PONG', 0)}, discovery=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any('chat' in call for call in calls))

    def test_both_live_entrypoints_use_the_shared_fixture(self):
        for path in ('.github/scripts/scenario-message.sh', '.github/workflows/verify-release.yaml'):
            source = (ROOT / path).read_text()
            self.assertIn('inject_ci_skill "$pod"', source)
            self.assertNotIn('ci-test.md', source)
