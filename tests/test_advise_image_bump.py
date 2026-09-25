import importlib.util
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
