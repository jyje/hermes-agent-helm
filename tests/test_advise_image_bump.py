import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / ".github/scripts/release/advise-image-bump.py"


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

    def test_sanitize_items_drops_invalid_items_truncates_and_sorts(self):
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
        self.assertEqual(items[0]["detail"], "D" * 237 + "...")
        self.assertEqual(items[0]["upstream_ref"], "123")

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
