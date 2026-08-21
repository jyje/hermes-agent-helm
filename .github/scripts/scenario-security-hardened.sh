#!/usr/bin/env bash
# security-hardened scenario: install values-hardened.yaml into a namespace
# enforcing Pod Security Standards `restricted` and verify the workload is
# actually admitted and runs - not just that the rendered YAML looks
# compliant. Runs against its own ephemeral kind cluster (separate from the
# other scenarios).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

kubectl create namespace "$NS" 2>/dev/null || true
kubectl label namespace "$NS" --overwrite \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest

echo "[$NS] installing values-hardened.yaml under a restricted namespace"
install_release -f charts/hermes-agent/values-hardened.yaml
run_hook_test

pod="$(pod_name)"; echo "[$NS] pod: $pod"

echo "[$NS] verifying pod-level securityContext"
kubectl get pod -n "$NS" "$pod" -o jsonpath='{.spec.securityContext}' \
  | jq -e '.runAsNonRoot == true and .runAsUser == 10000'

echo "[$NS] verifying container-level securityContext (readOnlyRootFilesystem)"
kubectl get pod -n "$NS" "$pod" \
  -o jsonpath='{.spec.containers[?(@.name=="hermes-agent")].securityContext}' \
  | jq -e '.readOnlyRootFilesystem == true and .allowPrivilegeEscalation == false'

echo "[$NS] verifying the read-only rootfs pod is actually usable, not just admitted"
kubectl exec -n "$NS" "$pod" -- hermes doctor

# The two other init-container securityContexts (auth-device-login,
# init-team-shared) aren't exercised live here: device login needs a real
# human OAuth approval, and the shared-volume chown init is deliberately
# left disabled under restricted (root-only, see values-hardened.yaml).
# Assert their rendering instead, each with its feature enabled.
echo "[$NS] asserting auth.deviceFlow.securityContext renders when set"
helm template security-hardened-check charts/hermes-agent \
  --set-string env.OPENAI_API_KEY=sk-test \
  --set auth.deviceFlow.enabled=true \
  --set auth.deviceFlow.provider=github-copilot \
  --set-json 'auth.deviceFlow.securityContext={"runAsUser":10000,"runAsGroup":10000}' \
  | yq -e 'select(.kind == "Deployment" or .kind == "StatefulSet") | .spec.template.spec.initContainers[] | select(.name == "auth-device-login") | .securityContext.runAsUser == 10000' \
  | grep -q true

echo "[$NS] asserting team.sharedVolume.permissions.securityContext renders when the init is enabled"
helm template security-hardened-check charts/hermes-agent \
  --set-string env.OPENAI_API_KEY=sk-test \
  --set-string env.DISCORD_BOT_TOKEN=x --set-string env.DISCORD_HOME_CHANNEL=1 \
  --set team.enabled=true --set team.name=t --set team.identity=lead --set team.role=leader \
  --set team.leader.name=lead --set team.leader.mentionEnv=M \
  --set 'team.members[0].name=m1' --set 'team.members[0].mentionEnv=M1' --set 'team.members[0].role=r' \
  --set team.sharedVolume.permissions.enabled=true \
  | yq -e 'select(.kind == "Deployment" or .kind == "StatefulSet") | .spec.template.spec.initContainers[] | select(.name == "init-team-shared") | .securityContext.runAsUser == 0' \
  | grep -q true

echo "[$NS] security-hardened scenario passed"
