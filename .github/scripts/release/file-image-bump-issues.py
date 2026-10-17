#!/usr/bin/env python3
"""File one GitHub Issue per chart-relevant upstream change found by
advise-image-bump.py. The maintainer triages each issue independently:
accept (branch + implement) or reject (close with a reason).

Idempotent: skips any item whose exact issue title is already open, so
re-runs (e.g. workflow_dispatch) don't file duplicates.

A failed review (advice `source: failed`) is never reported as "nothing
found": it files one `upstream-review` issue asking for a manual pass, and
the workflow then fails the job. A skipped review (no NVIDIA_API_KEY, no
release notes) only prints a notice, so runs without the secret stay green.

Usage: file-image-bump-issues.py <advice_json> <target_version> <owner/repo>
Requires the `gh` CLI to be authenticated (GH_TOKEN env var).

Agent workflow: .claude/skills/review-upstream/SKILL.md.
Use advice source "manual" for an authorized agent review rather than a NIM
result. The skill owns scope and semantic deduplication; this script owns
the shared issue format, labels and exact-title duplicate guard.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

PRIORITY_LABEL = {"high": "priority:high", "medium": "priority:medium", "low": "priority:low"}


def gh(*args: str) -> subprocess.CompletedProcess:
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, file=sys.stdout, end="")
        print(result.stderr, file=sys.stderr, end="")
        result.check_returncode()
    return result


def issue_title(target_version: str, title: str) -> str:
    return f"[{target_version}] {title}"


def already_filed(repo: str, title: str) -> bool:
    result = gh("issue", "list", "--repo", repo, "--state", "open",
                "--search", f"{title} in:title", "--json", "title")
    existing = {row["title"] for row in json.loads(result.stdout)}
    return title in existing


def run_url() -> str:
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo, run_id = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID")
    return f"{server}/{repo}/actions/runs/{run_id}" if repo and run_id else ""


def coverage_note(advice: dict) -> str:
    """Say which release-note sections the model never saw, if any."""
    omitted = (advice.get("input") or {}).get("omitted") or {}
    if not omitted:
        return ""
    lines = "\n".join(f"- `{v}`: {', '.join(titles)}" for v, titles in omitted.items())
    return (
        "> [!NOTE]\n"
        "> The release notes were condensed to fit the model input. These sections "
        "were not reviewed:\n\n" + lines + "\n\n"
    )


def failure_title(target_version: str) -> str:
    return issue_title(target_version, "Automated upstream review failed - review manually")


def failure_body(target_version: str, advice: dict) -> str:
    url = run_url()
    run_line = f"\n**Workflow run:** {url}" if url else ""
    return (
        f"**Upstream version:** `{target_version}`{run_line}\n\n"
        "The AI review of upstream changes could not produce a result, so no "
        "chart follow-ups were filed for this image bump. This does not mean "
        "there are none.\n\n"
        f"**Error:** {advice.get('note') or 'unknown'}\n\n"
        "Review the upstream release notes between the previous and this "
        "`appVersion` by hand and file `upstream-review` issues for anything "
        "the chart should react to. Close this issue when that is done.\n\n"
        "_Auto-filed by cron-fetch-image.yaml's upstream-review job._"
    )


def issue_body(target_version: str, item: dict, advice: dict | None = None) -> str:
    ref_line = f"\n**Upstream ref:** {item['upstream_ref']}" if item.get("upstream_ref") else ""
    attribution = (
        "_Filed from a manual original-release-note review using the "
        "review-upstream agent skill; not a NVIDIA NIM workflow run._"
        if (advice or {}).get("source") == "manual"
        else "_Auto-filed by cron-fetch-image.yaml's upstream-review job "
        "(NVIDIA NIM, nemotron-3-ultra-550b-a55b)._"
    )
    return (
        f"**Upstream version:** `{target_version}`\n"
        f"**Priority:** {item['priority']}{ref_line}\n\n"
        f"{item['detail']}\n\n"
        f"{coverage_note(advice or {})}"
        "---\n"
        "**Maintainer triage:**\n"
        "- ✅ Accept → create a branch and implement this, referencing this issue.\n"
        "- ❌ Reject → close this issue with a short reason.\n\n"
        f"{attribution}"
    )


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 1
    advice_path, target_version, repo = sys.argv[1:4]

    with open(advice_path, encoding="utf-8") as f:
        advice = json.load(f)
    source = advice.get("source")
    if source == "failed":
        title = failure_title(target_version)
        print(f"::error::Upstream review failed: {advice.get('note')}")
        if already_filed(repo, title):
            print(f"Skipping (already filed): {title}")
        else:
            gh(
                "issue", "create", "--repo", repo,
                "--title", title,
                "--body", failure_body(target_version, advice),
                "--label", "upstream-review",
                "--label", PRIORITY_LABEL["high"],
            )
            print(f"Filed: {title}")
        return 0
    if source == "skipped":
        print(f"::notice::Upstream review skipped: {advice.get('note')}")
        return 0

    items = advice.get("items") or []
    if not items:
        print("The review found no chart-relevant upstream changes - nothing to file.")
        if coverage_note(advice):
            print("::notice::Release notes were condensed; some sections were not reviewed: "
                  + json.dumps(advice["input"]["omitted"], ensure_ascii=False))
        return 0

    for item in items:
        title = issue_title(target_version, item["title"])
        if already_filed(repo, title):
            print(f"Skipping (already filed): {title}")
            continue
        gh(
            "issue", "create", "--repo", repo,
            "--title", title,
            "--body", issue_body(target_version, item, advice),
            "--label", "upstream-review",
            "--label", PRIORITY_LABEL[item["priority"]],
        )
        print(f"Filed: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
