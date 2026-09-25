#!/usr/bin/env bash
# Verify safe config migration on a fresh HERMES_HOME and a persistent claim.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

NS="${NS:-test-hermes-chart}"
IMAGE_TAG="v2026.9.21"
MIGRATION_RUN="${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}"

kubectl create namespace "$NS" 2>/dev/null || true
echo "[$NS] installing $IMAGE_TAG with a fresh persistent home"
install_release --set-string "image.tag=$IMAGE_TAG"

assert_current_schema() {
  local pod="$1"
  kubectl exec -n "$NS" "$pod" -- \
    /opt/hermes/.venv/bin/python -c \
    'from hermes_cli.config import check_config_version; current, latest = check_config_version(); print(f"config schema {current}/{latest}"); assert current == latest'
}

rollout_with() {
  local overwrite="$1"
  local marker="$2"
  install_release \
    --set-string "image.tag=$IMAGE_TAG" \
    --set "bootstrap.overwrite=$overwrite" \
    --set-string "podAnnotations.ci-config-migration=$MIGRATION_RUN-$marker"
}

pod="$(pod_name)"
assert_current_schema "$pod"
kubectl logs -n "$NS" "$pod" -c seed-config | tee "/tmp/config-migration-$NS.log"
grep -F '[chart-config-migrate] Migrating config schema' "/tmp/config-migration-$NS.log"
kubectl exec -n "$NS" "$pod" -- \
  /opt/hermes/.venv/bin/python -c \
  'from hermes_cli.config import get_config_path; from hermes_cli.config_backups import list_config_backups; backups = list_config_backups(get_config_path(), "pre-chart-migrate"); print(f"config backups: {len(backups)}"); assert backups'

echo "[$NS] testing a chart-managed replacement on an existing PVC"
# shellcheck disable=SC2016  # HERMES_HOME expands in the pod's shell
kubectl exec -n "$NS" "$pod" -- sh -eu -c \
  'printf "# ci-replaced-by-bootstrap\n" >> "${HERMES_HOME:-/opt/data}/config.yaml"'
rollout_with true overwrite-existing
pod="$(pod_name)"
assert_current_schema "$pod"
if kubectl exec -n "$NS" "$pod" -- grep -Fq '# ci-replaced-by-bootstrap' "${HERMES_HOME:-/opt/data}/config.yaml"; then
  echo "::error::bootstrap.overwrite=true did not replace the existing config"
  exit 1
fi

echo "[$NS] testing migration of an unversioned config with overwrite disabled"
# shellcheck disable=SC2016  # HERMES_HOME expands in the pod's shell
kubectl exec -n "$NS" "$pod" -- sh -eu -c \
  'sed -i "/^_config_version:/d; s/^  default: gpt-4o-mini$/  default: ci-preserved-model/" "${HERMES_HOME:-/opt/data}/config.yaml"'
rollout_with false preserve-unversioned
pod="$(pod_name)"
assert_current_schema "$pod"
kubectl exec -n "$NS" "$pod" -- grep -Fx '  default: ci-preserved-model' "${HERMES_HOME:-/opt/data}/config.yaml"
kubectl logs -n "$NS" "$pod" -c seed-config | grep -F 'Migrating config schema v0 ->'

echo "[$NS] testing safe refusal for an explicitly unsupported config version"
# shellcheck disable=SC2016  # HERMES_HOME expands in the pod's shell
kubectl exec -n "$NS" "$pod" -- sh -eu -c \
  'printf "%s\n" "_config_version: 11" "model:" "  default: preserved-test-model" > "${HERMES_HOME:-/opt/data}/config.yaml"'
rollout_with false preserve-old-version
pod="$(pod_name)"
kubectl exec -n "$NS" "$pod" -- grep -Fx '_config_version: 11' "${HERMES_HOME:-/opt/data}/config.yaml"
kubectl exec -n "$NS" "$pod" -- grep -Fx '  default: preserved-test-model' "${HERMES_HOME:-/opt/data}/config.yaml"
kubectl logs -n "$NS" "$pod" -c seed-config | grep -F 'Config left unchanged'

echo "[$NS] applying the documented, reviewed migration-floor step"
# shellcheck disable=SC2016  # HERMES_HOME expands in the pod's shell
kubectl exec -n "$NS" "$pod" -- sh -eu -c \
  'sed -i "s/^_config_version: 11$/_config_version: 12/" "${HERMES_HOME:-/opt/data}/config.yaml"'
rollout_with false migrate-reviewed-old-config
pod="$(pod_name)"
assert_current_schema "$pod"
kubectl exec -n "$NS" "$pod" -- grep -Fx '  default: preserved-test-model' "${HERMES_HOME:-/opt/data}/config.yaml"
kubectl logs -n "$NS" "$pod" -c seed-config | grep -F '[chart-config-migrate] Migrating config schema v12 ->'

echo "[$NS] running Helm doctor hook against the migrated release"
run_hook_test

echo "[$NS] config migration scenario passed"
