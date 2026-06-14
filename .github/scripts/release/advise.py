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

Respond with ONLY a JSON object, no prose, no markdown fence:
{"bump":"major|minor|patch","summary":"<=80 words, what changed for users",\
"reasoning":"1-3 sentences citing the concrete change that drives the bump"}"""


def read(out: str, name: str) -> str:
    p = os.path.join(out, name)
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


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
    return {
        "bump": bump,
        "summary": "Automated heuristic summary (AI advisor unavailable). "
        "See the changelog below for the full list of changes.",
        "reasoning": f"Heuristic bump: {why}",
        "source": "heuristic",
        "model": None,
    }


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
        "max_tokens": 1024,
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
    content = body["choices"][0]["message"]["content"]
    data = extract_json(content)
    bump = str(data.get("bump", "")).lower().strip()
    if bump not in ("major", "minor", "patch"):
        raise ValueError(f"model returned invalid bump: {bump!r}")
    return {
        "bump": bump,
        "summary": str(data.get("summary", "")).strip()
        or "(model returned no summary)",
        "reasoning": str(data.get("reasoning", "")).strip()
        or "(model returned no reasoning)",
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
        try:
            advice = call_nim(ctx, changelog, diff)
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError,
                KeyError, json.JSONDecodeError, TimeoutError) as e:
            advice = heuristic(ctx, changelog, f"NIM call failed: {type(e).__name__}: {e}")

    with open(os.path.join(out, "advice.json"), "w", encoding="utf-8") as f:
        json.dump(advice, f, indent=2)
    print(json.dumps(advice, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
