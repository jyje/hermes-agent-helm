#!/usr/bin/env bash
# bootstrap-overwrite scenario: prove that bootstrap.overwrite=false preserves
# a runtime config.yaml edit across a rollout. This needs a real pod restart:
# a Helm upgrade with no rendered pod-template change would not rerun the init
# container and would make the assertion vacuous.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=.github/scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

kubectl create namespace "$NS" 2>/dev/null || true
echo "[$NS] installing with bootstrap.overwrite=false"
install_release --set bootstrap.overwrite=false

pod="$(pod_name)"
old_uid="$(kubectl get pod -n "$NS" "$pod" -o jsonpath='{.metadata.uid}')"
echo "[$NS] writing a runtime edit into config.yaml on $pod"
# shellcheck disable=SC2016  # $HERMES_HOME expands in the pod's shell, not the runner
kubectl exec -n "$NS" "$pod" -- sh -c '
  printf "\\n# %s\\n" "ci-bootstrap-overwrite-preserved" >> "${HERMES_HOME:-/opt/data}/config.yaml"
  grep -Fx "# ci-bootstrap-overwrite-preserved" "${HERMES_HOME:-/opt/data}/config.yaml"
'

# Change only a Pod annotation to force a new pod and therefore rerun the seed
# init container. The chart configuration itself remains identical.
rollout_id="${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}"
echo "[$NS] upgrading with a Pod annotation to force the seed init container"
install_release \
  --set bootstrap.overwrite=false \
  --set-string "podAnnotations.ci-bootstrap-overwrite=${rollout_id}"

new_pod="$(pod_name)"
new_uid="$(kubectl get pod -n "$NS" "$new_pod" -o jsonpath='{.metadata.uid}')"
if [ "$old_uid" = "$new_uid" ]; then
  echo "::error::Helm upgrade did not replace the pod; bootstrap preservation was not exercised"
  exit 1
fi

echo "[$NS] asserting the runtime edit survived on $new_pod"
# shellcheck disable=SC2016  # $HERMES_HOME expands in the pod's shell, not the runner
kubectl exec -n "$NS" "$new_pod" -- sh -c '
  grep -Fx "# ci-bootstrap-overwrite-preserved" "${HERMES_HOME:-/opt/data}/config.yaml"
'

echo "[$NS] verifying the upgraded workload remains healthy"
kubectl exec -n "$NS" "$new_pod" -- hermes doctor
echo "[$NS] bootstrap-overwrite scenario passed"
