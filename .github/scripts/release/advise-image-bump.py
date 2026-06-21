#!/usr/bin/env python3
"""AI upstream-change advisor for image-bump PRs (NVIDIA NIM, OpenAI-compatible).

Reads the upstream project's release notes for every version between the
chart's current and target appVersion, plus a snapshot of what the chart
already exposes, and asks the model which upstream changes the CHART (not
the app) should react to — a new env var worth exposing, a new messaging
platform worth an example, a breaking config rename, a security fix, etc.

Hard requirement: degrade gracefully. If NVIDIA_API_KEY is missing or the
call fails for any reason, return an empty, clearly-marked result so the PR
still gets created — this is advisory, not a release gate.

Usage: advise-image-bump.py <release_notes_file> <chart_context_file> <out_json>
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
NIM_MODEL = os.environ.get("NIM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
API_KEY = os.environ.get("NVIDIA_API_KEY", "").strip()
TIMEOUT = int(os.environ.get("NIM_TIMEOUT", "300"))
MAX_RETRIES = int(os.environ.get("NIM_MAX_RETRIES", "2"))
MAX_TOKENS = int(os.environ.get("NIM_MAX_TOKENS", "8192"))

PRIORITIES = ("high", "medium", "low")

SYSTEM_PROMPT = """\
You are the maintainer of "hermes-agent", a Helm chart that packages the \
upstream Hermes Agent application for Kubernetes. You are given:
1. The upstream project's release notes for every version between the \
chart's current and new tracked appVersion.
2. A snapshot of what the chart already exposes (values.yaml + the env vars \
documented in its README).

From the upstream changes, identify ONLY the ones that should change \
something in the CHART — e.g. a new required/optional env var worth adding \
to values.yaml or the README table, a new messaging platform worth a \
values-*.yaml example, a new config.yaml key, a breaking config/env rename, \
a security fix needing urgent action, or a constraint that invalidates a \
documented assumption (e.g. AGENTS.md/README claims). Ignore anything that \
doesn't affect how the chart is configured or deployed — most desktop-app- \
only UI work, internal refactors, and CLI-only features need no chart change.

List every relevant item you find — do not cap the count, but do not invent \
busywork either; if truly nothing applies, return an empty list.

Respond with ONLY a JSON object, no prose, no markdown fence:
{"items":[{"priority":"high|medium|low","title":"<=80 chars",\
"detail":"<=240 chars, what to change in the chart and why",\
"upstream_ref":"<PR number(s) or section title from the release notes, optional>"}]}"""


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def sanitize_items(raw) -> list[dict]:
    out = []
    for item in raw if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        priority = str(item.get("priority", "")).lower().strip()
        title = str(item.get("title", "")).strip()
        detail = str(item.get("detail", "")).strip()
        if priority not in PRIORITIES or not title or not detail:
            continue
        if len(title) > 80:
            title = title[:77].rstrip() + "..."
        if len(detail) > 240:
            detail = detail[:237].rstrip() + "..."
        out.append({
            "priority": priority,
            "title": title,
            "detail": detail,
            "upstream_ref": str(item.get("upstream_ref", "")).strip(),
        })
    order = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda x: order[x["priority"]])
    return out


def extract_json(s: str) -> dict:
    """Reasoning models may wrap JSON in thinking/text — grab the last object."""
    s = s.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    matches = list(re.finditer(r"\{.*\}", s, re.DOTALL))
    if matches:
        return json.loads(matches[-1].group(0))
    return json.loads(s)


def call_nim(release_notes: str, chart_context: str) -> dict:
    """Streamed call — a large model over a large input/output can run long
    enough that NIM's gateway resets a non-streaming connection before the
    first (and only) response chunk arrives. Streaming keeps the connection
    alive with a steady trickle of chunks instead."""
    user = (
        f"=== UPSTREAM RELEASE NOTES (current appVersion -> target) ===\n{release_notes}\n\n"
        f"=== WHAT THE CHART ALREADY EXPOSES ===\n{chart_context}\n"
    )
    payload = {
        "model": NIM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": MAX_TOKENS,
        "stream": True,
    }
    req = urllib.request.Request(
        NIM_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line or not line.startswith("data:"):
                continue
            chunk_str = line[len("data:"):].strip()
            if chunk_str == "[DONE]":
                break
            chunk = json.loads(chunk_str)
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            if delta.get("content"):
                content_parts.append(delta["content"])
            if delta.get("reasoning_content"):
                reasoning_parts.append(delta["reasoning_content"])
    content = "".join(content_parts) or "".join(reasoning_parts)
    data = extract_json(content)
    items = sanitize_items(data.get("items"))
    return {"items": items, "source": "nim", "model": NIM_MODEL}


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 1
    release_notes_path, chart_context_path, out_path = sys.argv[1:4]
    release_notes = read(release_notes_path)
    chart_context = read(chart_context_path)

    if not API_KEY:
        result = {"items": [], "source": "skipped", "model": None,
                  "note": "NVIDIA_API_KEY not set — review the upstream release notes manually."}
    elif not release_notes.strip():
        result = {"items": [], "source": "skipped", "model": None,
                  "note": "No upstream release notes found — review manually."}
    else:
        result = None
        last_err: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                result = call_nim(release_notes, chart_context)
                break
            except Exception as e:  # advisory step — ANY failure must degrade, not crash
                last_err = e
                print(f"NIM advice attempt {attempt + 1}/{MAX_RETRIES} failed: "
                      f"{type(e).__name__}: {e}", file=sys.stderr)
        if result is None:
            result = {"items": [], "source": "failed", "model": NIM_MODEL,
                      "note": f"NIM call failed ({type(last_err).__name__}: {last_err}) — review manually."}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
