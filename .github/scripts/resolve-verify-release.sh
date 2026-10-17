#!/usr/bin/env bash
# Resolve an immutable chart release independently of the current test harness.
set -euo pipefail

if [ "${EVENT_NAME:-}" = workflow_dispatch ]; then
  ver="${RELEASE_VERSION:-}"
  [[ "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo 'Expected a plain chart version such as 1.21.0' >&2; exit 1;
  }
else
  [[ "${TRIGGER_SHA:-}" =~ ^[0-9a-f]{40}$ ]] || {
    echo 'Missing full triggering release SHA' >&2; exit 1;
  }
  ver=$(git show "$TRIGGER_SHA:charts/hermes-agent/Chart.yaml" | awk '/^version:/ {print $2}' | tr -d '"')
  [[ "$ver" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || exit 1
fi

tag_sha=$(git rev-list -n 1 "refs/tags/v$ver" 2>/dev/null || true)
if [ "${EVENT_NAME:-}" != workflow_dispatch ] && [ "$tag_sha" != "$TRIGGER_SHA" ]; then
  echo "v$ver was not tagged at the triggering push; nothing new to verify." >&2
  echo 'should_verify=false'
  exit 0
fi
[[ "$tag_sha" =~ ^[0-9a-f]{40}$ ]] || { echo "Release tag v$ver does not exist" >&2; exit 1; }
chart=$(git show "$tag_sha:charts/hermes-agent/Chart.yaml")
actual=$(printf '%s\n' "$chart" | awk '/^version:/ {print $2}' | tr -d '"')
name=$(printf '%s\n' "$chart" | awk '/^name:/ {print $2}' | tr -d '"')
[[ "$actual" = "$ver" && "$name" =~ ^[a-z0-9][a-z0-9-]*$ ]] || {
  echo 'Release tag and chart metadata do not agree' >&2; exit 1;
}
printf 'should_verify=true\nversion=%s\nchart_name=%s\nrelease_sha=%s\n' "$ver" "$name" "$tag_sha"
echo "Verifying $name v$ver from release $tag_sha with harness $(git rev-parse HEAD)" >&2
