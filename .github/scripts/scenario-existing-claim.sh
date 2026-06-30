#!/usr/bin/env bash
# existingClaim scenario: install against a pre-created PVC
# (persistence.existingClaim) and verify it's mounted/writable. Runs against
# its own ephemeral kind cluster (separate from the message scenario).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

kubectl create namespace "$NS" 2>/dev/null || true
echo "[$NS] creating shared PVC ci-shared-pvc"
printf '%s\n' \
  'apiVersion: v1' \
  'kind: PersistentVolumeClaim' \
  'metadata:' \
  '  name: ci-shared-pvc' \
  'spec:' \
  '  accessModes: [ReadWriteOnce]' \
  '  resources:' \
  '    requests:' \
  '      storage: 1Gi' \
  | kubectl apply -n "$NS" -f -
# local-path (kind default) is WaitForFirstConsumer, so the PVC binds only
# once the pod mounts it — `helm --wait` below covers that.
echo "[$NS] installing with persistence.existingClaim=ci-shared-pvc"
install_release --set persistence.existingClaim=ci-shared-pvc
run_hook_test
pod="$(pod_name)"; echo "[$NS] pod: $pod"
echo "[$NS] verifying the pre-created PVC is mounted and writable"
# shellcheck disable=SC2016  # $HERMES_HOME expands in the pod's shell, not the runner
kubectl exec -n "$NS" "$pod" -- sh -c '
  echo "ci-existingClaim-ok" > "${HERMES_HOME:-/opt/data}/ci-claim-probe.txt"
  cat "${HERMES_HOME:-/opt/data}/ci-claim-probe.txt"
'
echo "[$NS] hermes doctor on the existingClaim release"
kubectl exec -n "$NS" "$pod" -- hermes doctor
