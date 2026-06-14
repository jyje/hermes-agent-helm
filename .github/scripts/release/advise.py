#!/usr/bin/env python3
"""AI release advisor (NVIDIA NIM, OpenAI-compatible).

This is the ONLY AI step in the release pipeline. It reads the deterministic
context produced by collect.sh and returns a *recommendation* — a semver bump
level, a human summary, and the reasoning. It never computes the version string
(semver.sh does that) and never ships anything.

Hard requirement: degrade gracefully. If NVIDIA_API_KEY is missing or the call
fails for any reason, fall back to a transparent heuristic and mark the source
so the PR makes clear no model was consulted.

Inputs  (in OUT dir, default dist/release):
    context.json, CHANGELOG_FRAGMENT.md, DIFF.txt
Output:
    advice.json -> {bump, reasoning, summary, source, model}
Stdlib only (urllib) so it needs no pip install in CI.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

NIM_URL = os.environ.get("NIM_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
NIM_MODEL = os.environ.get("NIM_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
API_KEY = os.environ.get("NVIDIA_API_KEY", "").strip()
TIMEOUT = int(os.environ.get("NIM_TIMEOUT", "60"))
MAX_RETRIES = int(os.environ.get("NIM_MAX_RETRIES", "2"))

# Reasoning models spend a large share of `max_tokens` on hidden "thinking"
# tokens before emitting the JSON answer, so they need a much bigger budget
# than plain instruct models or the answer gets cut off mid-string (and the
# JSON parse fails). Per-model defaults; NIM_MAX_TOKENS overrides for any model.
MODEL_MAX_TOKENS = {
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning": 8192,
}
DEFAULT_MAX_TOKENS = 8192
MAX_TOKENS = int(os.environ.get("NIM_MAX_TOKENS", MODEL_MAX_TOKENS.get(NIM_MODEL, DEFAULT_MAX_TOKENS)))

ARTIFACTHUB_KINDS = ("added", "changed", "deprecated", "removed", "fixed", "security")

SYSTEM_PROMPT = """\
You are a release manager for a Helm chart (chart name: hermes-agent) that \
packages the Hermes Agent for Kubernetes. You recommend the next CHART version \
using strict semantic versioning, based on a deterministic changelog and diff.

Rules you MUST follow:
- You are versioning the CHART (the `version:` field), NOT the application. An \
appVersion-only change (a new upstream image tag, no template/values change) is \
normally a PATCH for the chart.
- MAJOR: backwards-incompatible chart changes — a renamed/removed value, a \
changed default that breaks existing installs, a resource rename.
- MINOR: backwards-compatible new functionality — a new value/feature/template, \
new opt-in capability.
- PATCH: bug fixes, docs, CI, refactors, dependency/appVersion bumps that don't \
change the chart's interface.
- Pre-1.0.0 (0.y.z) is still a real interface; do not invent breaking changes \
that the diff doesn't show. Prefer the smallest correct bump.
- Also propose 1-3 entries for the chart's `annotations.artifacthub.io/changes` \
list (Artifact Hub "Changes" tab for this release). Each entry has a `kind` \
(one of added, changed, deprecated, removed, fixed, security) and a short, \
user-facing `description` (<=160 chars, imperative, no commit links).

Respond with ONLY a JSON object, no prose, no markdown fence:
{"bump":"major|minor|patch","summary":"<=80 words, what changed for users",\
"reasoning":"1-3 sentences citing the concrete change that drives the bump",\
"artifacthub_changes":[{"kind":"added|changed|deprecated|removed|fixed|security",\
"description":"<=160 chars, user-facing"}]}"""


def read(out: str, name: str) -> str:
    p = os.path.join(out, name)
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def first_change_line(changelog: str) -> str:
    """First changelog bullet, stripped of its trailing (commit link) — author suffix."""
    for line in changelog.splitlines():
        line = line.strip()
        if line.startswith("- "):
            return re.sub(r"\s*\(\[.*$", "", line[2:]).strip()
    return "See CHANGELOG.md for details."


def heuristic(ctx: dict, changelog: str, why: str) -> dict:
    """Transparent fallback when the model isn't consulted."""
    sig = ctx.get("signals", {})
    text = changelog.lower()
    if "breaking" in text or re.search(r"!:", changelog):
        bump = "major"
    elif sig.get("appversion_only"):
        bump = "patch"
    elif "### features" in text or re.search(r"\bfeat\b", text):
        bump = "minor"
    else:
        bump = "patch"
    kind_for_bump = {"major": "changed", "minor": "added", "patch": "fixed"}
    return {
        "bump": bump,
        "summary": "Automated heuristic summary (AI advisor unavailable). "
        "See the changelog below for the full list of changes.",
        "reasoning": f"Heuristic bump: {why}",
        "artifacthub_changes": [
            {"kind": kind_for_bump[bump], "description": first_change_line(changelog)}
        ],
        "source": "heuristic",
        "model": None,
    }


def sanitize_artifacthub_changes(raw) -> list[dict]:
    out = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind", "")).lower().strip()
        desc = str(item.get("description", "")).strip()
        if kind not in ARTIFACTHUB_KINDS or not desc:
            continue
        if len(desc) > 160:
            desc = desc[:157].rstrip() + "..."
        out.append({"kind": kind, "description": desc})
    return out[:3]


def extract_json(s: str) -> dict:
    """Reasoning models may wrap JSON in thinking/text — grab the last object."""
    s = s.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    # last balanced-looking object
    matches = list(re.finditer(r"\{.*\}", s, re.DOTALL))
    if matches:
        return json.loads(matches[-1].group(0))
    return json.loads(s)


def call_nim(ctx: dict, changelog: str, diff: str) -> dict:
    user = (
        f"current chart version: {ctx.get('current_version')}\n"
        f"bump from: {ctx.get('bump_from')}\n"
        f"last release tag: {ctx.get('last_release') or '(none)'}\n"
        f"commits in range: {ctx.get('commit_count')}\n"
        f"change signals: {json.dumps(ctx.get('signals', {}))}\n"
        f"diffstat: {ctx.get('diffstat')}\n\n"
        f"=== CHANGELOG (deterministic, git-cliff) ===\n{changelog}\n\n"
        f"=== CHART DIFF (truncated) ===\n{diff}\n"
    )
    payload = {
        "model": NIM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": MAX_TOKENS,
    }
    req = urllib.request.Request(
        NIM_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = json.loads(resp.read().decode())
    msg = body["choices"][0]["message"]
    # Reasoning models sometimes return content=null with the text in
    # reasoning_content; fall back to that, then to empty string.
    content = msg.get("content") or msg.get("reasoning_content") or ""
    data = extract_json(content)
    bump = str(data.get("bump", "")).lower().strip()
    if bump not in ("major", "minor", "patch"):
        raise ValueError(f"model returned invalid bump: {bump!r}")
    artifacthub_changes = sanitize_artifacthub_changes(data.get("artifacthub_changes"))
    if not artifacthub_changes:
        raise ValueError(
            f"model returned no usable artifacthub_changes: {data.get('artifacthub_changes')!r}"
        )
    return {
        "bump": bump,
        "summary": str(data.get("summary", "")).strip()
        or "(model returned no summary)",
        "reasoning": str(data.get("reasoning", "")).strip()
        or "(model returned no reasoning)",
        "artifacthub_changes": artifacthub_changes,
        "source": "nim",
        "model": NIM_MODEL,
    }


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else "dist/release"
    ctx = json.loads(read(out, "context.json") or "{}")
    changelog = read(out, "CHANGELOG_FRAGMENT.md")
    diff = read(out, "DIFF.txt")

    if not API_KEY:
        advice = heuristic(ctx, changelog, "NVIDIA_API_KEY not set")
    else:
        advice = None
        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                advice = call_nim(ctx, changelog, diff)
                break
            except Exception as e:  # malformed response — worth a retry
                last_err = e
                print(f"NIM advice attempt {attempt + 1}/{MAX_RETRIES} failed: "
                      f"{type(e).__name__}: {e}", file=sys.stderr)
        if advice is None:  # advisory step — ANY failure must degrade, not crash
            advice = heuristic(ctx, changelog, f"NIM call failed: {type(last_err).__name__}: {last_err}")

    with open(os.path.join(out, "advice.json"), "w", encoding="utf-8") as f:
        json.dump(advice, f, indent=2)
    print(json.dumps(advice, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
