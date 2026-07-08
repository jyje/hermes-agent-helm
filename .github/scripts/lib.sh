#!/usr/bin/env bash
# Shared helpers for the validate-chart test scenarios. Sourced by
# scenario-message.sh / scenario-existing-claim.sh — each scenario now runs
# in its OWN ephemeral kind cluster (separate matrix job), so unlike the
# previous single-cluster setup, these helpers don't need to juggle multiple
# namespaces or be exported into background subshells.
set -euo pipefail

NS="${NS:-test-hermes-chart}"

# install_release [extra helm --set flags...]
# Installs with NVIDIA NIM when a key is available, else a doctor-only
# placeholder.
install_release() {
  if [ -n "${NVIDIA_API_KEY:-}" ]; then
    echo "[$NS] installing with NVIDIA NIM (model pool: $CI_MODELS)"
    helm upgrade --install hermes-agent charts/hermes-agent \
      --namespace "$NS" --create-namespace \
      --set config.model.provider=nvidia \
      --set-string config.model.default="${CI_MODELS%%,*}" \
      --set-string env.NVIDIA_API_KEY="$NVIDIA_API_KEY" \
      --set-string env.OPENAI_API_KEY=unused \
      --set tests.chat.enabled=true \
      --set tests.chat.failOnError=true \
      --set "tests.chat.models={$CI_MODELS}" \
      "$@" \
      --wait --timeout 5m
  else
    echo "[$NS] no NVIDIA_API_KEY — installing placeholder (doctor-only)"
    helm upgrade --install hermes-agent charts/hermes-agent \
      --namespace "$NS" --create-namespace \
      --set-string env.OPENAI_API_KEY=sk-test \
      "$@" \
      --wait --timeout 5m
  fi
}

# run_hook_test
# Renders the chart's Helm-hook test Job from the installed release and runs
# it directly (NOT `helm test`, whose hook watch can stall many minutes on a
# CI runner). Polls until Complete (pass) or Failed.
run_hook_test() {
  job=hermes-agent-test
  helm get hooks hermes-agent -n "$NS" > "/tmp/hooks-$NS.yaml"
  kubectl delete job "$job" -n "$NS" --ignore-not-found
  kubectl create -n "$NS" -f "/tmp/hooks-$NS.yaml"
  for _ in $(seq 1 150); do
    conds=$(kubectl get job "$job" -n "$NS" \
      -o jsonpath='{.status.conditions[?(@.status=="True")].type}' 2>/dev/null || true)
    case "$conds" in
      *Complete*) echo "[$NS] hook test: Complete"; return 0 ;;
      *Failed*)   echo "[$NS] hook test: Failed";   return 1 ;;
    esac
    sleep 2
  done
  echo "[$NS] hook test: timed out"; return 1
}

pod_name() {
  kubectl get pod -n "$NS" -l app.kubernetes.io/name=hermes-agent \
    -o jsonpath='{.items[0].metadata.name}'
}

# chat_round_trip <pod> — passes on the first model that answers; the
# free-tier pool tolerates per-model flakiness (it's a FAILOVER pool, not
# exhaustive per-model testing).
chat_round_trip() {
  pod="$1"; ok=false
  chat_timeout_secs="${CHAT_TIMEOUT_SECS:-180}"
  for model in $(echo "$CI_MODELS" | tr ',' ' '); do
    echo "[$NS] --- model: $model ---"
    # Prompt goes via -q (not positional) and --max-turns bounds the
    # round-trip — same invocation the chart's own test hook uses. Bound each
    # model attempt with timeout so one stalled model doesn't consume the
    # entire workflow step budget.
    if timeout -k 15 "${chat_timeout_secs}" \
      kubectl exec -n "$NS" "$pod" -- \
        hermes chat -m "$model" --provider nvidia \
          -q "ci-ping" --max-turns 2; then
      ok=true; break
    fi
    echo "[$NS] model $model failed or timed out after ${chat_timeout_secs}s, trying next"
  done
  [ "$ok" = true ]
}
