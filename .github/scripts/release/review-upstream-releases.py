#!/usr/bin/env python3
"""Review formal stable releases independently of Docker image bump eligibility.

Agent contract: .claude/skills/review-upstream/SKILL.md.
Original notes/results are artifacts; the digest ledger is cached between runs.
Eviction causes a backfill, never an assumption that a release was reviewed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request

UPSTREAM = "NousResearch/hermes-agent"
SCRIPTS = Path(__file__).resolve().parent
TAG = re.compile(r"^v([0-9]{1,3})\.([0-9]+)\.([0-9]+)$")


def version(tag: str) -> tuple[int, int, int]:
    match = TAG.fullmatch(tag)
    if not match:
        raise ValueError(f"Not a plain stable SemVer tag: {tag}")
    return tuple(map(int, match.groups()))


def digest(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def plan(releases: list[dict], ledger: dict, first: str, force: bool = False) -> list[dict]:
    floor = version(first)
    selected = {}
    for release in releases:
        tag = release.get("tag_name", "")
        if not TAG.fullmatch(tag) or release.get("draft") or release.get("prerelease"):
            continue
        if version(tag) < floor:
            continue
        prior = ledger.get(tag, {})
        body = release.get("body") or ""
        if (not force and body and prior.get("status") == "reviewed"
                and prior.get("notes_sha256") == digest(body)):
            continue
        selected[tag] = release
    return sorted(selected.values(), key=lambda release: version(release["tag_name"]))


def github_json(endpoint: str, paginate: bool = False):
    args = ["gh", "api"]
    if paginate:
        args += ["--paginate", "--slurp"]
    result = subprocess.run([*args, endpoint], capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    return [item for page in payload for item in page] if paginate else payload


def command(args: list[str], log: Path) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed (exit {result.returncode}); see {log.name}")


def image_info(tag: str) -> dict:
    url = f"https://hub.docker.com/v2/repositories/nousresearch/hermes-agent/tags/{tag}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.load(response)
        return {"status": "available", "architectures": sorted({
            image["architecture"] for image in data.get("images", []) if image.get("architecture")
        }), "digest": data.get("digest")}
    except urllib.error.HTTPError as exc:
        code = exc.code
        exc.close()
        return {"status": "missing" if code == 404 else "unknown", "http_status": code}
    except (OSError, ValueError) as exc:
        return {"status": "unknown", "error": type(exc).__name__}


def chart_context(chart: Path) -> str:
    paths = [chart / "Chart.yaml", chart / "values.yaml", chart / "README.md.gotmpl",
             *sorted(chart.glob("values-*.yaml"))]
    return "\n\n".join(f"## {path}\n\n{path.read_text(encoding='utf-8')}" for path in paths)


def review_one(tag: str, chart: Path, output: Path, repo: str, context: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    result = {"tag": tag, "status": "unreviewed"}
    advice_path = output / "advice.json"
    try:
        release = github_json(f"repos/{UPSTREAM}/releases/tags/{tag}")
        body = release.get("body") or ""
        if release.get("tag_name") != tag or release.get("draft") or release.get("prerelease"):
            raise ValueError("Original release metadata does not describe the selected stable tag")
        if not body.strip():
            raise ValueError("Original official release notes are empty")
        (output / "original-release.json").write_text(json.dumps(release, indent=2), encoding="utf-8")
        notes = output / "release-notes.md"
        notes.write_text(f"## {tag}\n\n{body}", encoding="utf-8")
        result.update(notes_sha256=digest(body), release_url=release.get("html_url"),
                      image=image_info(tag))
        # An absent image is evidence, not a reason to skip formal release review.
        command(["helm", "lint", str(chart), "--set-string", f"image.tag={tag}"],
                output / "helm-lint.log")
        for controller in ("deployment", "statefulset"):
            command(["helm", "template", "review", str(chart), "--set-string", f"image.tag={tag}",
                     "--set", f"controller.type={controller}"], output / f"render-{controller}.log")
        result["checks"] = "Helm lint and both controller renders passed; static only"
        command([sys.executable, str(SCRIPTS / "advise-image-bump.py"),
                 str(notes), str(context), str(advice_path)], output / "advisor.log")
        advice = json.loads(advice_path.read_text(encoding="utf-8"))
        source = advice.get("source")
        result["source"] = source
        if source == "skipped":
            result["note"] = advice.get("note", "Advisor skipped; review remains incomplete")
            return result
        if source != "nim" or not isinstance(advice.get("items"), list):
            raise ValueError(advice.get("note") or "Advisor did not produce a complete review")
        omitted = (advice.get("input") or {}).get("omitted") or {}
        critical = ("upgrade", "breaking", "security", "migrat", "revert", "deprecat",
                    "highlight", "preamble", "gateway", "docker", "config")
        if any(any(word in title.lower() for word in critical)
               for titles in omitted.values() for title in titles):
            raise ValueError("Important release-note sections were omitted; manual review is required")
        command([sys.executable, str(SCRIPTS / "file-image-bump-issues.py"),
                 str(advice_path), tag, repo], output / "issue-filer.log")
        result.update(status="reviewed", item_count=len(advice["items"]))
        if advice.get("input"):
            result["input"] = advice["input"]  # Includes omitted-section coverage.
        return result
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        # Preserve the failure and continue reviewing other releases. The filer
        # creates an explicit manual-review issue, not an empty findings result.
        result.update(status="failed", error=str(exc))
        if advice_path.exists():
            advice_path.replace(output / "advisor-result-before-failure.json")
        advice_path.write_text(json.dumps({"source": "failed", "note": str(exc), "items": []}),
                               encoding="utf-8")
        try:
            command([sys.executable, str(SCRIPTS / "file-image-bump-issues.py"),
                     str(advice_path), tag, repo], output / "failure-issue.log")
        except (OSError, RuntimeError) as filing_error:
            result["filing_error"] = str(filing_error)
        return result


def read_ledger(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("releases"), dict):
        raise ValueError(f"Invalid review ledger: {path}")
    return data["releases"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--chart", type=Path, default=Path("charts/hermes-agent"))
    parser.add_argument("--state-dir", type=Path, default=Path(".review-state"))
    parser.add_argument("--output-dir", type=Path, default=Path(".review-results"))
    parser.add_argument("--from-tag", default="v0.21.6")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--plan-only", action="store_true", help="Inventory only; no model or issue writes")
    args = parser.parse_args()
    version(args.from_tag)
    args.state_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    ledger = read_ledger(Path(".github/upstream-review-baseline.json"))
    ledger.update(read_ledger(args.state_dir / "ledger.json"))
    releases = github_json(f"repos/{UPSTREAM}/releases?per_page=100", paginate=True)
    inventory = plan(releases, {}, args.from_tag, force=True)
    # Retain original bodies even when an unchanged digest skips a new model
    # call, including the manually reviewed migration-era baseline.
    (args.output_dir / "original-note-inventory.json").write_text(json.dumps([
        {key: release.get(key) for key in ("tag_name", "html_url", "published_at", "body",
                                          "draft", "prerelease")}
        for release in inventory
    ], indent=2) + "\n", encoding="utf-8")
    selected = plan(inventory, ledger, args.from_tag, args.force)
    if args.plan_only:
        report = {"from_tag": args.from_tag, "selected": [r["tag_name"] for r in selected],
                  "reviewed_tags": sorted(ledger, key=version)}
        (args.output_dir / "plan.json").write_text(json.dumps(report, indent=2) + "\n",
                                                   encoding="utf-8")
        print(json.dumps(report))
        return 0
    context = args.output_dir / "chart-context.md"
    context.write_text(chart_context(args.chart), encoding="utf-8")
    # Give the advisor existing tracking context to avoid filing semantic duplicates.
    issues = github_json(f"repos/{args.repo}/issues?state=all&per_page=100", paginate=True)
    with context.open("a", encoding="utf-8") as stream:
        stream.write("\n\n## Existing issues and PRs (avoid duplicate tracking)\n")
        stream.write("\n".join(f"- #{i['number']} [{i['state']}] {i['title']}" for i in issues))
    results = []
    chart_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    for release in selected:
        tag = release["tag_name"]
        result = review_one(tag, args.chart, args.output_dir / tag, args.repo, context)
        result.update(chart_sha=chart_sha, reviewed_at=datetime.now(timezone.utc).isoformat())
        results.append(result)
        print(f"{tag}: {result['status']}", flush=True)
        if result["status"] == "reviewed":
            ledger[tag] = result
    (args.state_dir / "ledger.json").write_text(
        json.dumps({"schema": 1, "releases": ledger}, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "results.json").write_text(
        json.dumps({"selected": len(selected), "results": results,
                    "review_ledger": ledger,
                    "note": "Unchanged reviewed note digests are skipped; use --force for backfill."},
                   indent=2) + "\n", encoding="utf-8")
    print(f"Formal stable releases selected: {len(selected)}")
    return int(any(result["status"] == "failed" for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
