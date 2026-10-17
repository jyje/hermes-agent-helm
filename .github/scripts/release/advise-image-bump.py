#!/usr/bin/env python3
"""AI upstream-change advisor for image-bump PRs (NVIDIA NIM, OpenAI-compatible).

Reads the upstream project's release notes for every version between the
chart's current and target appVersion, plus a snapshot of what the chart
already exposes, and asks the model which upstream changes the CHART (not
the app) should react to - a new env var worth exposing, a new messaging
platform worth an example, a breaking config rename, a security fix, etc.

Hard requirement: degrade gracefully. If NVIDIA_API_KEY is missing or the
call fails for any reason, return an empty, clearly-marked result
(`source: skipped` / `source: failed`) instead of crashing - this is
advisory, not a release gate. file-image-bump-issues.py turns a `failed`
result into a visible "review manually" issue; it is never "nothing found".

Large release windows (one upstream release note can exceed 100 KB) are
condensed to a character budget before sending: the release preambles,
highlights, upgrade/breaking/security notes and deployment-facing sections
go first, contributor lists and test changelogs are dropped, and every
omitted section is named in the prompt. A failed attempt retries with half
the budget.

Usage: advise-image-bump.py <release_notes_file> <chart_context_file> <out_json>
Stdlib only (urllib) so it needs no pip install in CI.

Agent workflow: .claude/skills/review-upstream/SKILL.md.
The skill owns original-note review and scope; this script is its optional
NIM advisor and the cron-fetch-image workflow's shared implementation.
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
# Complete details (#299) need more output room than the old 240-char ones.
MAX_TOKENS = int(os.environ.get("NIM_MAX_TOKENS", "16384"))
# Release-notes budget in characters. Past windows that reviewed fine were
# up to ~40 KB; v2026.9.24 -> v0.22.2 was ~272 KB and NIM answered every
# attempt with an unparseable body within a second.
MAX_NOTES_CHARS = int(os.environ.get("NIM_MAX_NOTES_CHARS", "60000"))
UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "NousResearch/hermes-agent")
# How much of an unexpected response body to log / record on failure.
ERROR_EXCERPT_CHARS = 500

# Section-title keywords (lower-case, matched as substrings) for condensing.
# KEY sections go in first; DROP sections never go in; LOW ones go in last.
KEY_SECTION_WORDS = (
    "highlight", "upgrade", "breaking", "migrat", "deprecat", "security",
    "updating", "about this release", "gateway", "messaging", "docker",
    "infrastructure", "config", "revert",
)
LOW_SECTION_WORDS = ("desktop", "documentation", "cli, tui", "other changes")
DROP_SECTION_WORDS = ("contributor", "tests")

PRIORITIES = ("high", "medium", "low")

# The detail becomes the whole explanation of a filed issue (see
# file-image-bump-issues.py), so it must keep its final action and source
# links. It used to be cut at 240 chars, which filed half-sentences (#299).
# The bound only guards against a runaway model; hitting it is made explicit
# in the text rather than passed off as a complete review.
MAX_DETAIL_CHARS = 4000

SYSTEM_PROMPT = """\
You are the maintainer of "hermes-agent", a Helm chart that packages the \
upstream Hermes Agent application for Kubernetes. You are given:
1. The upstream project's release notes for every version between the \
chart's current and new tracked appVersion.
2. A snapshot of what the chart already exposes (values.yaml + the env vars \
documented in its README).

Two values in this chart are FREE-FORM PASSTHROUGHS, deep-merged or appended \
verbatim with no chart-side validation: `config:` (any key you set is \
written into config.yaml as-is, on top of Hermes' own built-in defaults) and \
`extraEnv`/`extraEnvFrom` (any env var). A new config.yaml key or a new env \
var upstream adds is therefore ALREADY usable today, whether or not this \
chart names it by name - that alone is NEVER a reason to file an item. Only \
flag a config.yaml key or env var if something ELSE about it needs chart \
action: the chart should set its own default for it, an EXISTING documented \
value or example silently breaks because of it (a breaking rename), or it's \
prominent enough to deserve a discoverability example.

From the upstream changes, identify ONLY the ones that should change \
something in the CHART - e.g. a new messaging platform worth a values-*.yaml \
example, a new Service port/route or container/volume/RBAC need, a \
values.schema.json validation gap, a breaking rename of a key an EXISTING \
chart example or documented value relies on, a security fix needing urgent \
action, or a constraint that invalidates a documented assumption (e.g. \
AGENTS.md/README claims). Ignore anything that doesn't affect how the chart \
is configured or deployed - most desktop-app-only UI work, internal \
refactors, and CLI-only features need no chart change, and neither does a \
bare new config.yaml key or env var on its own (see above).

List every relevant item you find - do not cap the count, but do not invent \
busywork either; if truly nothing applies, return an empty list.

The chart context can include existing issue/PR titles. Do not file a duplicate \
of an already-tracked or resolved item; use the current chart context and later \
release corrections, including reverted changes, to judge what still applies.

Respond with ONLY a JSON object, no prose, no markdown fence:
{"items":[{"priority":"high|medium|low","title":"<=80 chars",\
"detail":"what to change in the chart and why, as complete sentences: \
the concrete action, the affected values/templates/docs, and source links. \
Under 1500 chars; never end mid-sentence",\
"upstream_ref":"<PR number(s) or section title from the release notes, optional>"}]}"""


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


class NimError(RuntimeError):
    """A NIM response we could not use, with the HTTP status and a short,
    secret-free excerpt of what came back."""

    def __init__(self, message: str, status: int | None = None, excerpt: str = ""):
        self.status = status
        self.excerpt = excerpt
        detail = f" (HTTP {status})" if status is not None else ""
        if excerpt:
            detail += f"; body starts: {excerpt!r}"
        super().__init__(message + detail)


def excerpt(text: str) -> str:
    text = " ".join(text.split())
    if API_KEY:
        text = text.replace(API_KEY, "***")
    if len(text) > ERROR_EXCERPT_CHARS:
        text = text[:ERROR_EXCERPT_CHARS] + "..."
    return text


RELEASE_HEADER = re.compile(r"^## (v\S+)[ \t]*$", re.MULTILINE)
SECTION_HEADER = re.compile(r"^## .*$", re.MULTILINE)


def section_tier(title: str) -> int | None:
    """0 = key, 1 = normal, 2 = low, None = drop."""
    t = title.lower()
    if any(w in t for w in DROP_SECTION_WORDS):
        return None
    if any(w in t for w in KEY_SECTION_WORDS):
        return 0
    if any(w in t for w in LOW_SECTION_WORDS):
        return 2
    return 1


def split_releases(notes: str) -> list[tuple[str, str]]:
    """Split the workflow's `## vX.Y.Z` blocks into (version, body) pairs."""
    headers = list(RELEASE_HEADER.finditer(notes))
    if not headers:
        return [("", notes)]
    out = []
    for i, m in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(notes)
        out.append((m.group(1), notes[m.end():end].strip("\n")))
    return out


def split_sections(body: str) -> list[tuple[str, str]]:
    """(title, text) pairs; the text before the first `## ` is the preamble."""
    heads = list(SECTION_HEADER.finditer(body))
    first = heads[0].start() if heads else len(body)
    out = [("", body[:first])] if body[:first].strip() else []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        out.append((m.group(0)[3:].strip(), body[m.start():end]))
    return out


def condense_notes(notes: str, budget: int) -> tuple[str, dict]:
    """Fit the release notes into `budget` characters, keeping the most
    chart-relevant sections and naming everything left out.

    Returns (text, stats). stats["omitted"] maps a version to the titles of
    its sections that were dropped or did not fit; it is empty when the
    notes were sent whole."""
    stats = {"original_chars": len(notes), "budget_chars": budget, "omitted": {}}
    if len(notes) <= budget:
        stats["sent_chars"] = len(notes)
        return notes, stats

    releases = []  # (version, [[title, text, tier, kept_text|None]])
    for version, body in split_releases(notes):
        releases.append((version, [[t, x, 0 if not t else section_tier(t), None]
                                   for t, x in split_sections(body)]))

    # Reserve room for each release's header and omission note.
    remaining = budget - sum(len(v) + 400 for v, _ in releases)
    # Key sections share the budget fairly (shortest first, each capped at an
    # equal share of what is left), so one huge "Highlights" cannot starve
    # the newest release's upgrade notes.
    key = sorted((s for _, secs in releases for s in secs if s[2] == 0), key=lambda s: len(s[1]))
    for i, sec in enumerate(key):
        share = remaining // (len(key) - i)
        text = sec[1]
        if len(text) <= share:
            sec[3] = text
        elif share > 500:
            cut = text[:share - 120].rstrip()
            sec[3] = cut + f"\n\n_[Section truncated by the advisor: {len(text) - len(cut)} characters omitted.]_\n"
        remaining -= len(sec[3] or "")
    # Other sections go in whole, in release order, while they fit.
    for tier in (1, 2):
        for _, sections in releases:
            for sec in sections:
                if sec[2] == tier and len(sec[1]) <= remaining:
                    sec[3] = sec[1]
                    remaining -= len(sec[1])

    parts = []
    for version, sections in releases:
        omitted = [s[0] or "(preamble)" for s in sections if s[3] is None]
        truncated = [s[0] or "(preamble)" for s in sections
                     if s[3] is not None and s[3] != s[1]]
        if version:
            parts.append(f"## {version}\n")
        parts.extend(s[3] for s in sections if s[3] is not None)
        if omitted or truncated:
            stats["omitted"][version or "(notes)"] = omitted + [f"{t} (truncated)" for t in truncated]
            url = f"https://github.com/{UPSTREAM_REPO}/releases/tag/{version}" if version else ""
            names = "; ".join(omitted + [f"{t} (truncated)" for t in truncated])
            parts.append(f"\n_[Condensed by the advisor to fit the model input. Not shown: {names}. "
                         f"Full notes: {url}]_\n")
        parts.append("\n")
    text = "".join(parts)
    stats["sent_chars"] = len(text)
    return text, stats


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
        if len(detail) > MAX_DETAIL_CHARS:
            omitted = len(detail) - MAX_DETAIL_CHARS
            detail = (
                detail[:MAX_DETAIL_CHARS].rstrip()
                + f"\n\n_[Truncated by the advisor: {omitted} more characters were omitted. "
                "Check the upstream release notes before acting on this item.]_"
            )
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
    """Reasoning models may wrap JSON in thinking/text - grab the last object."""
    s = s.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    matches = list(re.finditer(r"\{.*\}", s, re.DOTALL))
    if matches:
        return json.loads(matches[-1].group(0))
    return json.loads(s)


def call_nim(release_notes: str, chart_context: str) -> dict:
    """Streamed call - a large model over a large input/output can run long
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
    # Anything that is not an SSE `data:` chunk (e.g. a plain JSON error body
    # served with HTTP 200) is kept so a failure can say what NIM returned.
    other_lines: list[str] = []
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise NimError("NIM rejected the request", e.code, excerpt(body)) from None
    with resp:
        status = resp.status
        for raw_line in resp:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            if not line.startswith("data:"):
                other_lines.append(line)
                continue
            chunk_str = line[len("data:"):].strip()
            if chunk_str == "[DONE]":
                break
            try:
                chunk = json.loads(chunk_str)
            except json.JSONDecodeError:
                raise NimError("NIM sent a non-JSON stream chunk", status, excerpt(chunk_str)) from None
            if chunk.get("error"):
                raise NimError("NIM streamed an error", status, excerpt(json.dumps(chunk["error"])))
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            if delta.get("content"):
                content_parts.append(delta["content"])
            if delta.get("reasoning_content"):
                reasoning_parts.append(delta["reasoning_content"])
    content = "".join(content_parts) or "".join(reasoning_parts)
    if not content.strip():
        raise NimError("NIM returned no completion text", status, excerpt("\n".join(other_lines)))
    try:
        data = extract_json(content)
    except json.JSONDecodeError:
        raise NimError("NIM completion is not the requested JSON", status, excerpt(content)) from None
    items = sanitize_items(data.get("items") if isinstance(data, dict) else None)
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
                  "note": "NVIDIA_API_KEY not set - review the upstream release notes manually."}
    elif not release_notes.strip():
        result = {"items": [], "source": "skipped", "model": None,
                  "note": "No upstream release notes found - review manually."}
    else:
        result = None
        last_err: Exception | None = None
        budget = MAX_NOTES_CHARS
        stats: dict = {}
        for attempt in range(MAX_RETRIES):
            notes, stats = condense_notes(release_notes, budget)
            print(f"NIM advice attempt {attempt + 1}/{MAX_RETRIES}: sending "
                  f"{stats['sent_chars']} of {stats['original_chars']} release-note chars "
                  f"(budget {budget})", file=sys.stderr)
            try:
                result = call_nim(notes, chart_context)
                break
            except Exception as e:  # advisory step - ANY failure must degrade, not crash
                last_err = e
                print(f"NIM advice attempt {attempt + 1}/{MAX_RETRIES} failed: "
                      f"{type(e).__name__}: {e}", file=sys.stderr)
                budget //= 2  # an oversized input is the likeliest cause
        if result is None:
            result = {"items": [], "source": "failed", "model": NIM_MODEL,
                      "note": f"NIM call failed ({type(last_err).__name__}: {last_err}) - review manually."}
        result["input"] = stats

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
