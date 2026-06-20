#!/usr/bin/env python3
"""Rewrite the `annotations.artifacthub.io/changes` block in Chart.yaml using
the AI-proposed (or heuristic) entries for this release.

Does a targeted text replacement of just that block, preserving the rest of
Chart.yaml (comments, formatting) — a full YAML round-trip would strip comments.

Usage: update-artifacthub-changes.py <Chart.yaml> <advice.json>
"""
from __future__ import annotations

import json
import re
import sys


def main() -> int:
    chart_path = sys.argv[1] if len(sys.argv) > 1 else "charts/hermes-agent/Chart.yaml"
    advice_path = sys.argv[2] if len(sys.argv) > 2 else "dist/release/advice.json"

    advice = json.load(open(advice_path, encoding="utf-8"))
    changes = advice.get("artifacthub_changes") or []
    if not changes:
        print("no artifacthub_changes in advice.json — leaving Chart.yaml untouched")
        return 0

    lines = open(chart_path, encoding="utf-8").readlines()

    key_re = re.compile(r"^(\s*)artifacthub\.io/changes:\s*\|\s*$")
    start = None
    indent = None
    for i, line in enumerate(lines):
        m = key_re.match(line.rstrip("\n"))
        if m:
            start = i
            indent = m.group(1)
            break
    if start is None:
        print("artifacthub.io/changes annotation not found — leaving Chart.yaml untouched")
        return 0

    # The block scalar's content is every following line that's blank or more
    # indented than the key itself.
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() == "" or line.startswith(indent + " "):
            end += 1
        else:
            break

    content_indent = indent + "  "
    new_block = [f"{indent}artifacthub.io/changes: |\n"]
    for c in changes:
        # Artifact Hub's annotation parser rejects unquoted strings containing
        # YAML-special characters (colons, brackets, etc.) — e.g. our own
        # conventional commit subjects ("feat(release): ...") always have a
        # colon. json.dumps (ensure_ascii=False) yields a double-quoted scalar
        # that's valid YAML and keeps emoji/unicode readable.
        new_block.append(f"{content_indent}- kind: {json.dumps(c['kind'], ensure_ascii=False)}\n")
        new_block.append(f"{content_indent}  description: {json.dumps(c['description'], ensure_ascii=False)}\n")

    lines[start:end] = new_block
    with open(chart_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"updated artifacthub.io/changes with {len(changes)} entr"
          f"{'y' if len(changes) == 1 else 'ies'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
