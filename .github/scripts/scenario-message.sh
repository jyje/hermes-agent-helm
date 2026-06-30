#!/usr/bin/env bash
# message scenario: chart-managed storage, the hook test, and (on trusted
# runs with an NVIDIA_API_KEY) a skill-injection + chat round-trip through
# NVIDIA NIM. Also the only scenario that installs Discord, so the
# live-notify step in the workflow only fires from this scenario. Runs
# against its own ephemeral kind cluster.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

discord_args=()
if [ -n "${DISCORD_BOT_TOKEN:-}" ]; then
  discord_args+=(--set-string "env.DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN")
  if [ -n "${DISCORD_HOME_CHANNEL:-}" ]; then
    discord_args+=(--set "extraEnv[0].name=DISCORD_HOME_CHANNEL" \
                  --set-string "extraEnv[0].value=$DISCORD_HOME_CHANNEL")
  fi
fi

# ${arr[@]+...} guards against bash's "unbound variable" on an EMPTY array
# under `set -u` (still the default /bin/bash on macOS, 3.2 — fixed upstream
# in bash 4.4, but worth not relying on the runner's bash version).
install_release "${discord_args[@]+"${discord_args[@]}"}"
run_hook_test

if [ -n "${NVIDIA_API_KEY:-}" ]; then
  pod="$(pod_name)"; echo "[$NS] pod: $pod"
  echo "[$NS] === skill injection ==="
  # shellcheck disable=SC2016  # $HERMES_HOME/$skill_dir expand in the pod's shell, not the runner
  kubectl exec -n "$NS" "$pod" -- sh -c '
    skill_dir="${HERMES_HOME:-/opt/data}/skills"
    mkdir -p "$skill_dir"
    printf "# CI Ping\n\nWhen the user says \"ci-ping\", reply with exactly: CI_PONG\n" \
      > "$skill_dir/ci-test.md"
    echo "Skill written:"; cat "$skill_dir/ci-test.md"
  '
  echo "[$NS] === chat with injected skill ==="
  chat_round_trip "$pod" \
    || { echo "::error::[$NS] all models failed chat round-trip"; exit 1; }
else
  echo "[$NS] doctor-only (hook test already covered the health check)"
fi
