#!/usr/bin/env bash
# Shared helpers for the validate-chart test scenarios. Sourced by
# scenario-message.sh / scenario-existing-claim.sh: each scenario now runs
# in its OWN ephemeral kind cluster (separate matrix job), so unlike the
# previous single-cluster setup, these helpers don't need to juggle multiple
# namespaces or be exported into background subshells.
set -euo pipefail

NS="${NS:-test-hermes-chart}"

wait_for_hermes_startup() {
  local pod logs
  echo "[$NS] waiting for Hermes stage2 startup to finish"
  for _ in $(seq 1 90); do
    pod="$(pod_name 2>/dev/null || true)"
    if [ -n "$pod" ]; then
      logs="$(kubectl logs -n "$NS" "$pod" --tail=100 2>/dev/null || true)"
      if printf '%s\n' "$logs" | grep -Fq '[stage2] Setup complete; starting user services'; then
        echo "[$NS] Hermes startup complete on $pod"
        return 0
      fi
    fi
    sleep 2
  done
  echo "::error::[$NS] Hermes did not finish stage2 startup within 180 seconds"
  [ -z "${pod:-}" ] || kubectl logs -n "$NS" "$pod" --tail=100 || true
  return 1
}

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
    echo "[$NS] no NVIDIA_API_KEY - installing placeholder (doctor-only)"
    helm upgrade --install hermes-agent charts/hermes-agent \
      --namespace "$NS" --create-namespace \
      --set-string env.OPENAI_API_KEY=sk-test \
      "$@" \
      --wait --timeout 5m
  fi
  wait_for_hermes_startup
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

# run_doctor <pod>
# Runs `hermes doctor` in the pod the way the chart's Helm test does: its
# findings are always printed, but they fail the scenario only when
# DOCTOR_STRICT=true, mirroring `tests.doctorStrict` (default false). Upstream
# doctor exits 1 on any finding, including optional ones that say nothing
# about the chart (a missing ~/.local/bin/hermes symlink, unset optional
# tool/API keys), so an unconditional call made every image bump that added
# such a check fail (#303). A doctor that never ran (exec error, pod gone)
# still fails regardless of strictness: its banner must be in the output.
run_doctor() {
  local pod="$1" out rc=0
  out="$(kubectl exec -n "$NS" "$pod" -- hermes doctor 2>&1)" || rc=$?
  printf '%s\n' "$out"
  if ! printf '%s\n' "$out" | grep -Fq 'Hermes Doctor'; then
    echo "::error::[$NS] hermes doctor did not run in $pod (exit $rc)"
    return 1
  fi
  if [ "$rc" -ne 0 ]; then
    if [ "${DOCTOR_STRICT:-false}" = "true" ]; then
      echo "::error::[$NS] hermes doctor reported issues (exit $rc) and DOCTOR_STRICT=true"
      return "$rc"
    fi
    echo "::warning::[$NS] hermes doctor reported issues (exit $rc); non-fatal because DOCTOR_STRICT is not true (tests.doctorStrict default)"
  fi
  return 0
}

pod_name() {
  kubectl get pod -n "$NS" -l app.kubernetes.io/name=hermes-agent \
    -o jsonpath='{.items[0].metadata.name}'
}

# chat_round_trip <pod>: passes on the first model that answers; the
# free-tier pool tolerates per-model flakiness (it's a FAILOVER pool, not
# exhaustive per-model testing). Each model attempt is bounded by
# CHAT_ROUND_TRIP_TIMEOUT so a single hung model can't burn the whole
# step's time budget and starve the remaining failover candidates.
CHAT_ROUND_TRIP_TIMEOUT="${CHAT_ROUND_TRIP_TIMEOUT:-1800}"
chat_round_trip() {
  pod="$1"; ok=false
  chat_timeout_secs="${CHAT_TIMEOUT_SECS:-180}"
  for model in $(echo "$CI_MODELS" | tr ',' ' '); do
    echo "[$NS] --- model: $model (timeout ${CHAT_ROUND_TRIP_TIMEOUT}s) ---"
    # Prompt goes via -q (not positional) and --max-turns bounds the
    # round-trip: same invocation the chart's own test hook uses. Bound each
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
