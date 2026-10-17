#!/usr/bin/env python3
"""Copy the generated English `## Values` section into the translated chart READMEs.

helm-docs only writes charts/hermes-agent/README.md. The Korean, Japanese and
Chinese READMEs keep the same table verbatim (it stays English on purpose, see
CONTRIBUTING.md "Documentation locales"), and a hand-maintained copy drifted: it
lacked rows for new values and kept an old default. `make docs` runs this after
helm-docs, and CI fails when the result differs from what is committed, so the
copies cannot go stale.

The Values section runs from the "## Values" heading to the end of the file in
every README, so this replaces that tail and leaves everything above it alone.
"""

from __future__ import annotations

import sys
from pathlib import Path

CHART = Path(__file__).resolve().parents[2] / "charts" / "hermes-agent"
LOCALES = ("ko", "ja", "zh")
MARK = "\n## Values\n"


def values_section(text: str, name: str) -> str:
    index = text.find(MARK)
    if index < 0:
        raise SystemExit(f"error: {name} has no '## Values' heading")
    return text[index:]


def sync(chart: Path = CHART, locales: tuple[str, ...] = LOCALES) -> list[Path]:
    """Rewrite each translated README. Returns the files that changed."""
    source = values_section((chart / "README.md").read_text(encoding="utf-8"), "README.md")
    changed: list[Path] = []
    for locale in locales:
        path = chart / f"README-{locale}.md"
        text = path.read_text(encoding="utf-8")
        index = text.find(MARK)
        if index < 0:
            raise SystemExit(f"error: {path.name} has no '## Values' heading")
        updated = text[:index] + source
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
    return changed


def main() -> int:
    for path in sync():
        print(f"synced the Values table into {path.relative_to(CHART.parents[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
