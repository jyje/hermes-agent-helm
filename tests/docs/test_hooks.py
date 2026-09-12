"""Regression checks for translated README includes and language links.

This directory is deliberately not a package: validate-chart.yaml's
``unittest discover -s tests`` must not pick these up, because ``hooks``
imports mkdocs, which only the deploy-docs workflow installs.

Run with the documentation environment:
    python -m unittest discover -s tests/docs
"""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import hooks


class DocsHooksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(hooks, "REPO_ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.page = SimpleNamespace(
            file=SimpleNamespace(src_uri="ja/index.md"), url="ja/"
        )

    def configure(self, entries, site_url="https://example.test/custom-prefix/"):
        files = []
        for page, source in entries:
            path = self.root / "docs" / page
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'--8<-- "{source}"\n', encoding="utf-8")
            files.append(SimpleNamespace(src_uri=page, abs_src_path=path))
        hooks.on_files(
            SimpleNamespace(documentation_pages=lambda: files),
            {"site_url": site_url},
        )

    def test_readme_links_keep_the_requested_language(self):
        entries = [("index.md", "README.md")] + [
            (f"{lang}/index.md", f"README-{lang}.md")
            for lang in ("ko", "ja", "zh")
        ]
        self.configure(entries)
        source = "[English](README.md) [日本語](README-ja.md)"
        self.assertEqual(
            hooks._fix_links(source, self.page, ""),
            "[English](/custom-prefix/) [日本語](/custom-prefix/ja/)",
        )

    def test_duplicate_includes_choose_the_landing_in_either_order(self):
        entries = [
            ("chart/index.md", "charts/hermes-agent/README.md"),
            ("chart/hermes-agent/reference/readme.md", "charts/hermes-agent/README.md"),
        ]
        for ordered in (entries, entries[::-1]):
            self.configure(ordered)
            self.assertEqual(
                hooks._fix_links("[Chart](README.md#values)", self.page, "charts/hermes-agent"),
                "[Chart](/custom-prefix/chart/#values)",
            )

    def test_untranslated_doc_link_keeps_english_and_unicode_anchor(self):
        self.configure([], site_url="https://example.test/")
        self.assertEqual(
            hooks._fix_links("[Guide](docs/advanced/index.md#guide)", self.page, ""),
            "[Guide](/advanced/#guide)",
        )
        self.assertEqual(
            hooks._fix_links("[日本語](docs/ja/index.md#概要)", self.page, ""),
            "[日本語](/ja/#概要)",
        )


if __name__ == "__main__":
    unittest.main()
