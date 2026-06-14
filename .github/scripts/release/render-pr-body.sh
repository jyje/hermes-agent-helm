#!/usr/bin/env bash
# Assemble the release-proposal PR body from the deterministic context, the AI
# advice, and a pre-built contributors block. All command help is in English.
#
# Usage: render-pr-body.sh <OUT_DIR> <selected_version> <contributors_md_file> [selection]
#   selection: "ai" (selected == AI recommendation) | "manual" (maintainer override)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:?out dir}"
NEW_VERSION="${2:?new version}"
CONTRIB_FILE="${3:-/dev/null}"
SELECTION="${4:-ai}"

ctx="$OUT/context.json"
advice="$OUT/advice.json"

get() { python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get(sys.argv[2],''))" "$1" "$2"; }
getsig() { python3 -c "import json,sys;print(str(json.load(open(sys.argv[1]))['signals'].get(sys.argv[2],'')).lower())" "$1" "$2"; }

bump="$(get "$advice" bump)"
source="$(get "$advice" source)"
model="$(get "$advice" model)"
summary="$(get "$advice" summary)"
reasoning="$(get "$advice" reasoning)"
bump_from="$(get "$ctx" bump_from)"
last_release="$(get "$ctx" last_release)"
commit_count="$(get "$ctx" commit_count)"
diffstat="$(get "$ctx" diffstat)"

src_label="🤖 NVIDIA NIM (\`$model\`)"
[ "$source" = "heuristic" ] && src_label="📐 heuristic fallback (no model consulted)"

# What the AI would have shipped (for transparency, even on a manual override).
ai_version="$(bash "$HERE/semver.sh" next "$bump_from" "$bump")"

if [ "$SELECTION" = "manual" ]; then
  version_rows="| **Selected version** | **v${NEW_VERSION}** — maintainer override |
| **AI suggestion** | \`${bump}\` → v${ai_version} (not taken) — ${src_label} |"
else
  version_rows="| **Recommended bump** | \`${bump}\` → **v${NEW_VERSION}** (from v${bump_from}) |
| **Recommendation by** | ${src_label} |"
fi

cat <<EOF
## 🚀 Release proposal: v${NEW_VERSION}

> Opened by the **propose-release** workflow. The changelog, diff, and
> contributor list below are produced **deterministically** by git / git-cliff.
> Only the **version recommendation and summary** are AI-assisted.

| | |
|---|---|
${version_rows}
| **Previous release** | ${last_release:-（none yet）} |
| **Commits in range** | ${commit_count} |
| **Chart diff** | ${diffstat:-（no chart changes detected）} |

### Summary
${summary}

### Why this version
${reasoning}

<details>
<summary>Change signals (chart-version hints)</summary>

| signal | value |
|---|---|
| templates changed | $(getsig "$ctx" templates_changed) |
| values.yaml changed | $(getsig "$ctx" values_changed) |
| Chart.yaml changed | $(getsig "$ctx" chart_yaml_changed) |
| appVersion changed | $(getsig "$ctx" appversion_changed) |
| appVersion-only (→ patch) | $(getsig "$ctx" appversion_only) |

</details>

### Changelog
$(cat "$OUT/CHANGELOG_FRAGMENT.md")

### Contributors
$(cat "$CONTRIB_FILE")

---

## How to ship this release

This PR already bumped \`version:\` in \`charts/hermes-agent/Chart.yaml\` to the
recommended value and refreshed \`CHANGELOG.md\`. To release:

1. **Review** the recommended version and summary above. The AI only advises —
   you decide.
2. **Adjust the version if needed** (the recommendation is a starting point):
   - edit \`version:\` in \`charts/hermes-agent/Chart.yaml\` on this branch, **or**
   - comment \`/version vX.Y.Z\` on this PR to have the bot set it for you.
3. **Merge to \`main\`.** That triggers \`release.yml\`, which tags \`v${NEW_VERSION}\`,
   writes the GitHub Release notes, and pushes the chart to
   \`oci://ghcr.io/<owner>/hermes-agent\`.
4. **Regenerate this proposal** anytime by re-running the **propose-release**
   workflow (Actions tab → "propose-release" → "Run workflow"). It updates this
   same PR in place — it won't open a duplicate.

> Nothing is published until this PR is merged. Closing it ships nothing.
EOF
