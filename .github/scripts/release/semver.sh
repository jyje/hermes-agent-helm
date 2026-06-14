#!/usr/bin/env bash
# Deterministic semver arithmetic. The AI advisor only picks a *level*
# (patch/minor/major); the actual version string is computed here so version
# math never depends on a model's output.
#
#   semver.sh next <from> <level>   ->  prints the bumped version
#
# Examples:
#   semver.sh next 0.0.1 patch  -> 0.0.2
#   semver.sh next 0.0.1 minor  -> 0.1.0
#   semver.sh next 0.3.4 major  -> 1.0.0
set -euo pipefail

cmd="${1:-}"
from="${2:-}"
level="${3:-}"

case "$cmd" in
  next)
    [ -n "$from" ] && [ -n "$level" ] || { echo "usage: semver.sh next <from> <level>" >&2; exit 2; }
    from="${from#v}"
    IFS='.' read -r major minor patch <<EOF
$from
EOF
    major="${major:-0}"; minor="${minor:-0}"; patch="${patch:-0}"
    case "$level" in
      major) major=$((major + 1)); minor=0; patch=0 ;;
      minor) minor=$((minor + 1)); patch=0 ;;
      patch) patch=$((patch + 1)) ;;
      *) echo "unknown bump level: $level (want major|minor|patch)" >&2; exit 2 ;;
    esac
    echo "${major}.${minor}.${patch}"
    ;;
  *)
    echo "usage: semver.sh next <from> <level>" >&2
    exit 2
    ;;
esac
