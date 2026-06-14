#!/usr/bin/env bash
# Assemble the GitHub Release body: chart description (from Chart.yaml,
# single source of truth) + install snippets (latest / this version / OCI) +
# the changelog section for this version (extracted from CHANGELOG.md, so it
# matches the release-proposal PR exactly). Contributors are not included
# here — GitHub renders a native contributors block on the release page
# already.
#
# Usage: render-release-notes.sh <owner/repo> <chart_name> <version> <changelog_section_file> <chart_yaml_path>
set -euo pipefail

REPO="${1:?owner/repo}"
CHART_NAME="${2:?chart name}"
VERSION="${3:?version}"
CHANGELOG_FILE="${4:?changelog section file}"
CHART_YAML="${5:?Chart.yaml path}"

OWNER="${REPO%%/*}"
REPO_NAME="${REPO#*/}"

DESCRIPTION="$(awk '
  /^description: \|/ { found=1; next }
  found && /^[^ ]/ { exit }
  found { sub(/^  /, ""); print }
' "$CHART_YAML")"

cat <<EOF
${DESCRIPTION}

---

## Install

### Latest (Helm repo)
\`\`\`bash
helm repo add ${CHART_NAME} https://${OWNER}.github.io/${REPO_NAME}
helm repo update
helm upgrade --install ${CHART_NAME} ${CHART_NAME}/${CHART_NAME} \\
  --namespace ${CHART_NAME} --create-namespace \\
  --set-string env.OPENAI_API_KEY='sk-...' \\
  --wait
\`\`\`

### This version (v${VERSION})
\`\`\`bash
helm upgrade --install ${CHART_NAME} ${CHART_NAME}/${CHART_NAME} \\
  --namespace ${CHART_NAME} --create-namespace \\
  --version ${VERSION} \\
  --set-string env.OPENAI_API_KEY='sk-...' \\
  --wait
\`\`\`

### OCI
\`\`\`bash
helm upgrade --install ${CHART_NAME} oci://ghcr.io/${REPO}/${CHART_NAME} \\
  --namespace ${CHART_NAME} --create-namespace \\
  --version ${VERSION} \\
  --set-string env.OPENAI_API_KEY='sk-...' \\
  --wait
\`\`\`

---

## Changelog
$(cat "$CHANGELOG_FILE")
EOF
