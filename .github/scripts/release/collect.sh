#!/usr/bin/env bash
# Static, deterministic release-context collector. NO AI here — just git and
# git-cliff. Produces everything the AI advisor and the PR body are built on:
#
#   - CHANGELOG_FRAGMENT.md  : git-cliff changelog for the unreleased range
#   - DIFF.txt               : the chart diff since the last release (truncated)
#   - commit_authors.txt     : unique commit authors in the range
#   - context.json           : versions, change signals, contributors, PR refs
#
# Usage: collect.sh [OUT_DIR]   (default: dist/release)
set -euo pipefail

CHART_DIR="charts/hermes-agent"
CHART_YAML="$CHART_DIR/Chart.yaml"
OUT="${1:-dist/release}"
DIFF_MAX_BYTES="${DIFF_MAX_BYTES:-60000}"   # cap what we feed the advisor
mkdir -p "$OUT"

# --- versions ---------------------------------------------------------------
current_version="$(grep -E '^version:' "$CHART_YAML" | awk '{print $2}' | tr -d '"')"

# Baseline = highest semver tag reachable from HEAD (the "last release"). If the
# repo has no release tag yet, diff from the root commit.
last_release="$(git tag --merged HEAD 'v[0-9]*' 2>/dev/null | sort -V | tail -1 || true)"
if [ -n "$last_release" ]; then
  base_ref="$last_release"
else
  base_ref="$(git rev-list --max-parents=0 HEAD | tail -1)"
fi

# Never propose a version <= an existing release: bump from max(current, last tag).
last_release_ver="${last_release#v}"
bump_from="$current_version"
if [ -n "$last_release_ver" ]; then
  highest="$(printf '%s\n%s\n' "$current_version" "$last_release_ver" | sort -V | tail -1)"
  bump_from="$highest"
fi

# --- changelog fragment (git-cliff, unreleased range) -----------------------
# The target version isn't resolved yet at this point in the workflow (that
# happens later, then CHANGELOG.md itself is regenerated with --tag), so
# git-cliff has no version to attach here and renders a "## [unreleased]"
# heading. The PR body already shows the target version in its own table, so
# that heading is redundant noise there — drop it from the embedded fragment.
git cliff "${base_ref}..HEAD" --strip all > "$OUT/CHANGELOG_FRAGMENT.md" 2>/dev/null \
  || git cliff --unreleased --strip all > "$OUT/CHANGELOG_FRAGMENT.md"
grep -v '^## \[' "$OUT/CHANGELOG_FRAGMENT.md" > "$OUT/CHANGELOG_FRAGMENT.md.tmp" \
  && mv "$OUT/CHANGELOG_FRAGMENT.md.tmp" "$OUT/CHANGELOG_FRAGMENT.md"

# --- chart diff (truncated for the advisor) ---------------------------------
git diff "${base_ref}..HEAD" -- "$CHART_DIR" > "$OUT/DIFF.full.txt" || true
head -c "$DIFF_MAX_BYTES" "$OUT/DIFF.full.txt" > "$OUT/DIFF.txt"
diffstat="$(git diff --stat "${base_ref}..HEAD" -- "$CHART_DIR" | tail -1 | sed 's/^ *//' || true)"

# --- change signals (chart-version semver hints) ----------------------------
# These distinguish a real chart change (templates/values) from an
# appVersion-only bump (new upstream image), which usually warrants only a patch.
templates_changed=false; values_changed=false; chart_yaml_changed=false
appversion_changed=false; appversion_only=false
git diff --quiet "${base_ref}..HEAD" -- "$CHART_DIR/templates" || templates_changed=true
git diff --quiet "${base_ref}..HEAD" -- "$CHART_DIR/values.yaml" || values_changed=true
git diff --quiet "${base_ref}..HEAD" -- "$CHART_YAML" || chart_yaml_changed=true
if [ "$chart_yaml_changed" = true ] && git diff "${base_ref}..HEAD" -- "$CHART_YAML" | grep -qE '^\+appVersion:'; then
  appversion_changed=true
fi
if [ "$appversion_changed" = true ] && [ "$templates_changed" = false ] && [ "$values_changed" = false ]; then
  appversion_only=true
fi

commit_count="$(git rev-list --count "${base_ref}..HEAD")"

# --- contributors -----------------------------------------------------------
git log "${base_ref}..HEAD" --format='%an' | sort -u > "$OUT/commit_authors.txt"

# PR references: only trust actual GitHub linkage, not any bare "#NN" that
# happens to appear in explanatory prose (e.g. a commit body narrating a PAST
# bug by mentioning its PR number — that isn't evidence #NN shipped in THIS
# range). Two sources:
#   1. Squash-merge commit subjects, which GitHub auto-suffixes "(#NN)".
#   2. Explicit closing keywords (Closes/Fixes/Resolves/Refs #NN) anywhere.
subject_refs="$(git log "${base_ref}..HEAD" --format='%s' | grep -oE '\(#[0-9]+\)$' || true)"
body_refs="$(git log "${base_ref}..HEAD" --format='%b' | grep -ioE '\b(close[sd]?|fix(e[sd])?|resolve[sd]?|refs?)[: ]*#[0-9]+' || true)"
pr_refs="$(printf '%s\n%s\n' "$subject_refs" "$body_refs" | grep -oE '#[0-9]+' | tr -d '#' | sort -un | paste -sd, - || true)"

# --- context.json (python for safe escaping; stdlib only) -------------------
BASE_REF="$base_ref" LAST_RELEASE="$last_release" CURRENT_VERSION="$current_version" \
BUMP_FROM="$bump_from" DIFFSTAT="$diffstat" COMMIT_COUNT="$commit_count" \
TEMPLATES_CHANGED="$templates_changed" VALUES_CHANGED="$values_changed" \
CHART_YAML_CHANGED="$chart_yaml_changed" APPVERSION_CHANGED="$appversion_changed" \
APPVERSION_ONLY="$appversion_only" PR_REFS="$pr_refs" OUT_DIR="$OUT" \
python3 - <<'PY'
import json, os
out = os.environ["OUT_DIR"]
def b(v): return v == "true"
authors = []
with open(os.path.join(out, "commit_authors.txt")) as f:
    authors = [l.strip() for l in f if l.strip()]
pr_refs = [int(x) for x in os.environ["PR_REFS"].split(",") if x.strip()]
ctx = {
    "base_ref": os.environ["BASE_REF"],
    "last_release": os.environ["LAST_RELEASE"],
    "current_version": os.environ["CURRENT_VERSION"],
    "bump_from": os.environ["BUMP_FROM"],
    "commit_count": int(os.environ["COMMIT_COUNT"] or 0),
    "diffstat": os.environ["DIFFSTAT"],
    "signals": {
        "templates_changed": b(os.environ["TEMPLATES_CHANGED"]),
        "values_changed": b(os.environ["VALUES_CHANGED"]),
        "chart_yaml_changed": b(os.environ["CHART_YAML_CHANGED"]),
        "appversion_changed": b(os.environ["APPVERSION_CHANGED"]),
        "appversion_only": b(os.environ["APPVERSION_ONLY"]),
    },
    "commit_contributors": authors,
    "pr_refs": pr_refs,
}
with open(os.path.join(out, "context.json"), "w") as f:
    json.dump(ctx, f, indent=2)
print(json.dumps(ctx, indent=2))
PY

echo "collect: wrote context to $OUT (base=$base_ref, bump_from=$bump_from)" >&2
