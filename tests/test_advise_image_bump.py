import importlib.util
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / ".github/scripts/release/advise-image-bump.py"
FILER = Path(__file__).parents[1] / ".github/scripts/release/file-image-bump-issues.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_script():
    spec = importlib.util.spec_from_file_location("advise_image_bump_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AdviseImageBumpTests(unittest.TestCase):
    def test_condensing_keeps_reverted_changes_that_did_not_ship(self):
        module = load_script()
        notes = ("## v0.23.0\n\nOfficial release.\n\n"
                 "## Reverted\n\nExperimental gateway change did not ship.\n\n"
                 "## Contributors\n\n" + "contributor " * 2000)
        text, stats = module.condense_notes(notes, 3000)
        self.assertIn("Experimental gateway change did not ship", text)
        self.assertNotIn("Reverted", stats["omitted"]["v0.23.0"])

    def test_manual_filing_has_explicit_non_nim_attribution(self):
        filer = load_module(FILER, "manual_issue_attribution")
        item = {"priority": "medium", "detail": "Verified evidence."}
        body = filer.issue_body("v0.22.2", item, {"source": "manual"})
        self.assertIn("review-upstream agent skill", body)
        self.assertIn("not a NVIDIA NIM workflow run", body)
        self.assertNotIn("Auto-filed", body)
        self.assertIn("Verified evidence.", body)

    def test_nim_and_legacy_filing_keep_existing_attribution(self):
        filer = load_module(FILER, "nim_issue_attribution")
        item = {"priority": "medium", "detail": "Verified evidence."}
        for advice in (None, {"source": "nim"}):
            with self.subTest(advice=advice):
                body = filer.issue_body("v0.22.2", item, advice)
                self.assertIn("Auto-filed by cron-fetch-image.yaml", body)
                self.assertNotIn("manual original-release-note review", body)

    def setUp(self):
        self.module = load_script()

    def test_system_prompt_preserves_passthrough_awareness(self):
        prompt = self.module.SYSTEM_PROMPT

        self.assertIn("FREE-FORM PASSTHROUGHS", prompt)
        self.assertIn("`config:`", prompt)
        self.assertIn("`extraEnv`/`extraEnvFrom`", prompt)
        self.assertIn("ALREADY usable today", prompt)
        self.assertIn("NEVER a reason to file an item", prompt)

    def test_sanitize_items_drops_invalid_items_truncates_titles_and_sorts(self):
        long_title = "T" * 81
        long_detail = "D" * 241
        items = self.module.sanitize_items(
            [
                {"priority": "low", "title": "Low", "detail": "kept last"},
                {"priority": "medium", "title": "Missing detail"},
                {"priority": "unknown", "title": "Unknown", "detail": "dropped"},
                "not an object",
                {
                    "priority": "HIGH",
                    "title": long_title,
                    "detail": long_detail,
                    "upstream_ref": 123,
                },
                {"priority": "medium", "title": "Medium", "detail": "kept second"},
            ]
        )

        self.assertEqual([item["priority"] for item in items], ["high", "medium", "low"])
        self.assertEqual(items[0]["title"], "T" * 77 + "...")
        # A detail past the old 240-char budget is kept whole (#299).
        self.assertEqual(items[0]["detail"], long_detail)
        self.assertEqual(items[0]["upstream_ref"], "123")

    def test_prompt_no_longer_asks_for_a_240_char_detail(self):
        prompt = self.module.SYSTEM_PROMPT

        self.assertNotIn("<=240", prompt)
        self.assertIn("never end mid-sentence", prompt)

    def test_long_detail_reaches_the_issue_body_intact(self):
        filer = load_module(FILER, "file_image_bump_issues_under_test")
        detail = (
            "Upstream now refuses SQLite WAL mode on some cross-VM filesystems. "
            + "The chart's persistence section assumes any PVC works for HERMES_HOME. " * 5
            + "Add a warning to values.yaml and the EN/KO storage docs, and link "
            "https://github.com/NousResearch/hermes-agent/blob/v2026.9.14/tests/"
            "hermes_state/test_cross_vm_fs_wal_refusal.py as the source."
        )
        self.assertGreater(len(detail), 240)

        [item] = self.module.sanitize_items(
            [{"priority": "high", "title": "Document WAL refusal", "detail": detail}]
        )
        body = filer.issue_body("v2026.9.14", item)

        self.assertIn(detail, body)
        self.assertIn("test_cross_vm_fs_wal_refusal.py as the source.", body)
        self.assertNotIn("Truncated", body)

    def test_runaway_detail_is_bounded_and_marked(self):
        limit = self.module.MAX_DETAIL_CHARS
        [item] = self.module.sanitize_items(
            [{"priority": "low", "title": "Runaway", "detail": "x" * (limit + 500)}]
        )

        self.assertTrue(item["detail"].startswith("x" * limit))
        self.assertIn("500 more characters were omitted", item["detail"])
        self.assertLess(len(item["detail"]), limit + 300)

    def test_extract_json_accepts_a_markdown_fence(self):
        result = self.module.extract_json('```json\n{"items": [{"title": "Fence"}]}\n```')

        self.assertEqual(result, {"items": [{"title": "Fence"}]})

    def test_extract_json_recovers_json_from_reasoning_prose(self):
        result = self.module.extract_json(
            'I considered the release notes carefully.\n{"items": [{"title": "Prose"}]}\nDone.'
        )

        self.assertEqual(result, {"items": [{"title": "Prose"}]})


def release(version, sections):
    body = f"# Hermes Agent {version}\n\nIntro for {version}.\n\n"
    body += "".join(f"## {title}\n\n{text}\n\n" for title, text in sections)
    return f"## {version}\n\n{body}"


class CondenseNotesTests(unittest.TestCase):
    def setUp(self):
        self.module = load_script()

    def test_small_notes_are_sent_whole(self):
        notes = release("v0.1.0", [("Highlights", "small")])
        text, stats = self.module.condense_notes(notes, 10_000)

        self.assertEqual(text, notes)
        self.assertEqual(stats["omitted"], {})

    def test_large_notes_keep_every_release_key_sections_and_name_omissions(self):
        notes = release("v0.22.0", [
            ("✨ Highlights", "H" * 40_000),
            ("⚠️ Upgrade notes", "session_reset retired"),
            ("🖥️ Desktop App", "D" * 20_000),
            ("👥 Contributors", "@someone"),
        ]) + release("v0.22.2", [
            ("Highlights", "newest highlight"),
            ("🐛 Bug Fixes", "B" * 30_000),
        ])
        text, stats = self.module.condense_notes(notes, 20_000)

        self.assertLessEqual(len(text), 20_000)
        self.assertIn("session_reset retired", text)
        self.assertIn("newest highlight", text)
        self.assertIn("Intro for v0.22.2", text)
        self.assertNotIn("@someone", text)
        self.assertIn("Section truncated by the advisor", text)
        self.assertIn("releases/tag/v0.22.0", text)
        self.assertIn("👥 Contributors", stats["omitted"]["v0.22.0"])
        self.assertIn("✨ Highlights (truncated)", stats["omitted"]["v0.22.0"])
        self.assertIn("🐛 Bug Fixes", stats["omitted"]["v0.22.2"])


class FakeNim(BaseHTTPRequestHandler):
    status = 200
    body = b""
    content_type = "application/json"

    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        self.send_response(self.status)
        self.send_header("Content-Type", self.content_type)
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *args):
        pass


class NimFailureTests(unittest.TestCase):
    """Run the advisor against a local stand-in for NIM."""

    def serve(self, status, body, content_type="application/json"):
        handler = type("Handler", (FakeNim,), {
            "status": status, "body": body, "content_type": content_type})
        server = HTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_port}/v1/chat/completions"

    def run_advisor(self, url, notes):
        env = {"NIM_URL": url, "NVIDIA_API_KEY": "test-key", "NIM_MAX_NOTES_CHARS": "4000"}
        with mock.patch.dict(os.environ, env), tempfile.TemporaryDirectory() as tmp:
            module = load_script()
            notes_path, ctx_path, out_path = (os.path.join(tmp, n) for n in ("n.md", "c.txt", "o.json"))
            Path(notes_path).write_text(notes, encoding="utf-8")
            Path(ctx_path).write_text("image: {}", encoding="utf-8")
            with mock.patch("sys.argv", ["advise", notes_path, ctx_path, out_path]), \
                    mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                self.assertEqual(module.main(), 0)
            return json.loads(Path(out_path).read_text(encoding="utf-8"))

    def test_plain_json_error_body_with_http_200_is_reported(self):
        # The 2026-10-17 failure: a non-SSE body made the advisor parse "".
        url = self.serve(200, b'{"detail": "input is too long for this model"}')
        advice = self.run_advisor(url, release("v0.22.0", [("Highlights", "x" * 9000)]))

        self.assertEqual(advice["source"], "failed")
        self.assertIn("HTTP 200", advice["note"])
        self.assertIn("input is too long", advice["note"])
        self.assertLessEqual(advice["input"]["budget_chars"], 2000)  # halved on retry
        self.assertNotIn("test-key", json.dumps(advice))

    def test_http_error_status_and_body_are_reported(self):
        url = self.serve(400, b'{"error": "context length exceeded"}')
        advice = self.run_advisor(url, "## v0.1.0\n\nnotes")

        self.assertEqual(advice["source"], "failed")
        self.assertIn("HTTP 400", advice["note"])
        self.assertIn("context length exceeded", advice["note"])

    def test_streamed_items_still_parse(self):
        content = json.dumps({"items": [{"priority": "low", "title": "T", "detail": "D."}]})
        chunk = json.dumps({"choices": [{"delta": {"content": content}}]})
        url = self.serve(200, f"data: {chunk}\n\ndata: [DONE]\n\n".encode(), "text/event-stream")
        advice = self.run_advisor(url, "## v0.1.0\n\nnotes")

        self.assertEqual(advice["source"], "nim")
        self.assertEqual(advice["items"][0]["title"], "T")


class FilerOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.filer = load_module(FILER, "file_image_bump_issues_outcomes")
        self.calls = []

        def fake_gh(*args):
            self.calls.append(args)
            return mock.Mock(stdout="[]")

        self.filer.gh = fake_gh

    def run_filer(self, advice):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(advice, f)
        self.addCleanup(os.unlink, f.name)
        with mock.patch("sys.argv", ["filer", f.name, "v0.22.2", "o/r"]), \
                mock.patch("builtins.print") as printed:
            self.assertEqual(self.filer.main(), 0)
        return " ".join(str(c) for c in printed.call_args_list)

    def created(self):
        return [c for c in self.calls if c[:2] == ("issue", "create")]

    def test_failed_review_files_a_manual_review_issue(self):
        output = self.run_filer({"items": [], "source": "failed",
                                 "note": "NIM call failed (NimError: boom) - review manually."})

        [create] = self.created()
        self.assertIn("[v0.22.2] Automated upstream review failed - review manually", create)
        body = create[create.index("--body") + 1]
        self.assertIn("NimError: boom", body)
        self.assertIn("This does not mean there are none", body)
        self.assertNotIn("nothing to file", output)

    def test_skipped_review_files_nothing(self):
        output = self.run_filer({"items": [], "source": "skipped", "note": "NVIDIA_API_KEY not set"})

        self.assertEqual(self.created(), [])
        self.assertIn("skipped", output)

    def test_condensed_input_is_named_in_each_issue(self):
        self.run_filer({
            "source": "nim",
            "items": [{"priority": "low", "title": "T", "detail": "D.", "upstream_ref": ""}],
            "input": {"omitted": {"v0.22.1": ["🐛 Bug Fixes"]}},
        })

        [create] = self.created()
        body = create[create.index("--body") + 1]
        self.assertIn("were not reviewed", body)
        self.assertIn("`v0.22.1`: 🐛 Bug Fixes", body)


if __name__ == "__main__":
    unittest.main()
