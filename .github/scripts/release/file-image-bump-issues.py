#!/usr/bin/env python3
"""File one GitHub Issue per chart-relevant upstream change found by
advise-image-bump.py. The maintainer triages each issue independently:
accept (branch + implement) or reject (close with a reason).

Idempotent: skips any item whose exact issue title is already open, so
re-runs (e.g. workflow_dispatch) don't file duplicates.

Usage: file-image-bump-issues.py <advice_json> <target_version> <owner/repo>
Requires the `gh` CLI to be authenticated (GH_TOKEN env var).
"""
from __future__ import annotations

import json
import subprocess
import sys

PRIORITY_LABEL = {"high": "priority:high", "medium": "priority:medium", "low": "priority:low"}


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True)


def issue_title(target_version: str, title: str) -> str:
    return f"[{target_version}] {title}"


def already_filed(repo: str, title: str) -> bool:
    result = gh("issue", "list", "--repo", repo, "--state", "open",
                "--search", f"{title} in:title", "--json", "title")
    existing = {row["title"] for row in json.loads(result.stdout)}
    return title in existing


def issue_body(target_version: str, item: dict) -> str:
    ref_line = f"\n**Upstream ref:** {item['upstream_ref']}" if item.get("upstream_ref") else ""
    return (
        f"**Upstream version:** `{target_version}`\n"
        f"**Priority:** {item['priority']}{ref_line}\n\n"
        f"{item['detail']}\n\n"
        "---\n"
        "**Maintainer triage:**\n"
        "- ✅ Accept → create a branch and implement this, referencing this issue.\n"
        "- ❌ Reject → close this issue with a short reason.\n\n"
        "_Auto-filed by cron-fetch-image.yaml's upstream-review job "
        "(NVIDIA NIM, nemotron-3-ultra-550b-a55b)._"
    )


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 1
    advice_path, target_version, repo = sys.argv[1:4]

    with open(advice_path, encoding="utf-8") as f:
        advice = json.load(f)
    items = advice.get("items") or []
    if not items:
        print("No chart-relevant upstream changes found — nothing to file.")
        return 0

    for item in items:
        title = issue_title(target_version, item["title"])
        if already_filed(repo, title):
            print(f"Skipping (already filed): {title}")
            continue
        gh(
            "issue", "create", "--repo", repo,
            "--title", title,
            "--body", issue_body(target_version, item),
            "--label", "upstream-review",
            "--label", PRIORITY_LABEL[item["priority"]],
        )
        print(f"Filed: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
