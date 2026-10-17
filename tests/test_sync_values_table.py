import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / ".github/scripts/sync-values-table.py"


def load():
    spec = importlib.util.spec_from_file_location("sync_values_table_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ENGLISH = "intro\n\n## Values\n\n| Key |\n| new.row |\n\nfooter\n"


class SyncValuesTableTests(unittest.TestCase):
    def write(self, directory, name, text):
        (Path(directory) / name).write_text(text, encoding="utf-8")

    def test_replaces_only_the_values_tail_and_keeps_the_translation_above_it(self):
        module = load()
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "README.md", ENGLISH)
            self.write(tmp, "README-ko.md", "한국어 소개\n\n## Values\n\n| Key |\n| old.row |\n")
            changed = module.sync(Path(tmp), ("ko",))
            result = (Path(tmp) / "README-ko.md").read_text(encoding="utf-8")
        self.assertEqual(len(changed), 1)
        self.assertTrue(result.startswith("한국어 소개\n"))
        self.assertIn("new.row", result)
        self.assertNotIn("old.row", result)
        self.assertTrue(result.endswith("footer\n"))

    def test_is_idempotent(self):
        module = load()
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "README.md", ENGLISH)
            self.write(tmp, "README-ja.md", "日本語\n\n## Values\n\nold\n")
            module.sync(Path(tmp), ("ja",))
            self.assertEqual(module.sync(Path(tmp), ("ja",)), [])

    def test_a_translation_without_a_values_heading_is_an_error(self):
        module = load()
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, "README.md", ENGLISH)
            self.write(tmp, "README-zh.md", "没有标题\n")
            with self.assertRaises(SystemExit):
                module.sync(Path(tmp), ("zh",))

    def test_the_committed_translations_match_the_english_table(self):
        module = load()
        chart = module.CHART
        english = module.values_section((chart / "README.md").read_text(encoding="utf-8"), "README.md")
        for locale in module.LOCALES:
            text = (chart / f"README-{locale}.md").read_text(encoding="utf-8")
            self.assertEqual(
                module.values_section(text, f"README-{locale}.md"),
                english,
                f"README-{locale}.md is stale: run 'make docs' and commit",
            )


if __name__ == "__main__":
    unittest.main()
