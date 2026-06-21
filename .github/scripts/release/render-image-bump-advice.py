#!/usr/bin/env python3
"""Render advise-image-bump.py's JSON output as a markdown block for the
image-bump PR body.

Usage: render-image-bump-advice.py <advice_json>
"""
from __future__ import annotations

import json
import sys

PRIORITY_LABEL = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "advice.json"
    with open(path, encoding="utf-8") as f:
        advice = json.load(f)

    items = advice.get("items") or []
    source = advice.get("source")
    model = advice.get("model")

    if source == "nim":
        heading = f"### 🤖 AI-assisted upstream review (`{model}`)"
    else:
        note = advice.get("note", "Review the upstream release notes manually.")
        print(f"### 🤖 AI-assisted upstream review\n\n> {note}")
        return 0

    print(heading)
    print()
    if not items:
        print("No chart-relevant changes found in this upstream range.")
        return 0

    print("| Priority | Item | Why | Upstream ref |")
    print("|---|---|---|---|")
    for item in items:
        label = PRIORITY_LABEL.get(item["priority"], item["priority"])
        ref = item.get("upstream_ref") or "—"
        print(f"| {label} | {item['title']} | {item['detail']} | {ref} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
