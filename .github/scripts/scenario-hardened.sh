#!/usr/bin/env bash
# hardened scenario: install values-hardened.yaml into a namespace that
# enforces Pod Security Standards `restricted`, and verify the workload
# passes admission and comes up healthy. Runs against its own ephemeral kind
# cluster (separate from the other scenarios).
#
# The two new init-container securityContext overrides
# (auth.deviceFlow.securityContext, team.sharedVolume.permissions.securityContext)
# are deliberately NOT exercised here: device login needs a human OAuth
# approval, and the shared-volume chown is documented as incompatible with
# `restricted` (see values-hardened.yaml). Those are covered by render
# assertions in the `lint` job instead.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

kubectl create namespace "$NS" 2>/dev/null || true
kubectl label namespace "$NS" --overwrite \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest

echo "[$NS] installing values-hardened.yaml under PSS restricted"
install_release -f charts/hermes-agent/values-hardened.yaml
run_hook_test

pod="$(pod_name)"; echo "[$NS] pod: $pod"
echo "[$NS] verifying the Pod actually got runAsNonRoot, not just requested it"
kubectl get pod -n "$NS" "$pod" -o jsonpath='{.spec.securityContext}' \
  | jq -e '.runAsNonRoot == true' >/dev/null
restarts="$(kubectl get pod -n "$NS" "$pod" -o jsonpath='{.status.containerStatuses[0].restartCount}')"
if [ "$restarts" != "0" ]; then
  echo "::error::[$NS] hermes-agent restarted $restarts time(s) - the s6-overlay entrypoint likely crash-looped before the hook test's install wait caught it"
  exit 1
fi
echo "[$NS] hardened scenario passed: 0 restarts, runAsNonRoot confirmed on the live Pod"
