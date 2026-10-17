import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).parents[1] / ".github/scripts/release/review-upstream-releases.py"
spec = importlib.util.spec_from_file_location("review_upstream_releases", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def release(tag="v0.21.7", body="Original official notes"):
    return {"tag_name": tag, "body": body, "draft": False, "prerelease": False,
            "html_url": f"https://github.com/NousResearch/hermes-agent/releases/tag/{tag}"}


class ReviewUpstreamReleasesTests(unittest.TestCase):
    def test_formal_release_without_image_is_selected_independent_of_app_or_pr_state(self):
        candidates = [release("v0.22.2"), release(), release("rc.1-v0.23.0"),
                      release("v2026.9.24"), {**release("v0.23.0"), "prerelease": True}]
        self.assertEqual([r["tag_name"] for r in module.plan(candidates, {}, "v0.21.6")],
                         ["v0.21.7", "v0.22.2"])
        # Planning deliberately has no current-appVersion or existing-bump-PR gate.

    def test_reruns_skip_only_matching_reviewed_original_note_digests(self):
        original = release()
        ledger = {"v0.21.7": {"status": "reviewed", "notes_sha256": module.digest(original["body"])}}
        self.assertEqual(module.plan([original], ledger, "v0.21.6"), [])
        self.assertEqual(module.plan([original], ledger, "v0.21.6", force=True), [original])
        changed = release(body="Corrected original notes")
        self.assertEqual(module.plan([changed], ledger, "v0.21.6"), [changed])
        ledger["v0.21.7"]["status"] = "unreviewed"
        self.assertEqual(module.plan([original], ledger, "v0.21.6"), [original])

    def run_one(self, original, advice, image_status="missing", fetch_error=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "tag"
        context = Path(temporary.name) / "context.md"
        context.write_text("Public chart context")
        def run(args, log):
            log.write_text("fixture command succeeded")
            if Path(args[1]).name == "advise-image-bump.py":
                Path(args[-1]).write_text(json.dumps(advice))
        with mock.patch.object(module, "github_json", return_value=original, side_effect=fetch_error), \
             mock.patch.object(module, "command", side_effect=run) as commands, \
             mock.patch.object(module, "image_info", return_value={"status": image_status}):
            result = module.review_one("v0.21.7", Path("charts/hermes-agent"),
                                       output, "jyje/hermes-agent-helm", context)
        return result, output, commands

    def test_missing_image_does_not_hide_notes_or_block_static_review(self):
        result, output, commands = self.run_one(release(), {"source": "nim", "items": []})
        self.assertEqual(result["status"], "reviewed")
        self.assertEqual(result["image"]["status"], "missing")
        self.assertEqual(json.loads((output / "original-release.json").read_text())["body"],
                         release()["body"])
        self.assertEqual(sum(call.args[0][0] == "helm" for call in commands.call_args_list), 3)

    def test_partial_api_failure_and_empty_original_notes_stay_failed(self):
        failed, output, _ = self.run_one(None, {}, fetch_error=RuntimeError("GitHub HTTP 503"))
        self.assertEqual(failed["status"], "failed")
        self.assertNotIn("notes_sha256", failed)
        self.assertEqual(json.loads((output / "advice.json").read_text())["source"], "failed")
        successful, _, _ = self.run_one(release(), {"source": "nim", "items": []})
        self.assertEqual(successful["status"], "reviewed")
        empty, _, _ = self.run_one(release(body=""), {"source": "nim", "items": []})
        self.assertEqual(empty["status"], "failed")

    def test_missing_key_and_omitted_critical_sections_are_not_clean_reviews(self):
        skipped, _, _ = self.run_one(release(), {"source": "skipped", "note": "No NVIDIA_API_KEY"})
        self.assertEqual(skipped["status"], "unreviewed")
        partial, _, _ = self.run_one(release(), {
            "source": "nim", "items": [], "input": {"omitted": {"v0.21.7": ["Security fixes"]}}
        })
        self.assertEqual(partial["status"], "failed")

    def test_workflow_keeps_formal_review_independent_of_bump_gate(self):
        import yaml
        workflow = yaml.safe_load((SCRIPT.parents[2] / "workflows/cron-fetch-image.yaml").read_text())
        job = workflow["jobs"]["upstream-review"]
        self.assertNotIn("needs", job)
        self.assertNotIn("if", job)
        self.assertEqual(workflow["jobs"]["bump-pr"]["needs"], "check")
        actions = [step.get("uses", "") for step in job["steps"]]
        self.assertTrue(any(action.startswith("actions/cache/save@") for action in actions))

    def test_partial_window_keeps_only_completed_reviews_and_does_not_stop_at_first_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state"
            output = Path(directory) / "results"
            def api(endpoint, paginate=False):
                return [release("v0.21.6"), release()] if "/releases?" in endpoint else []
            outcomes = [{"tag": "v0.21.6", "status": "failed", "error": "HTTP 503"},
                        {"tag": "v0.21.7", "status": "reviewed",
                         "notes_sha256": module.digest(release()["body"])}]
            with mock.patch.object(module, "github_json", side_effect=api), \
                 mock.patch.object(module, "read_ledger", return_value={}), \
                 mock.patch.object(module, "chart_context", return_value="Public context"), \
                 mock.patch.object(module, "review_one", side_effect=outcomes) as reviewer, \
                 mock.patch.object(module.sys, "argv", [
                     str(SCRIPT), "--repo", "jyje/hermes-agent-helm",
                     "--state-dir", str(state), "--output-dir", str(output)]):
                self.assertEqual(module.main(), 1)
            self.assertEqual(reviewer.call_count, 2)
            ledger = json.loads((state / "ledger.json").read_text())["releases"]
            self.assertNotIn("v0.21.6", ledger)
            self.assertEqual(ledger["v0.21.7"]["status"], "reviewed")


if __name__ == "__main__":
    unittest.main()
