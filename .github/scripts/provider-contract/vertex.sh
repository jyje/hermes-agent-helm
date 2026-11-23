#!/usr/bin/env bash
# Offline Vertex provider contract: render the example values, then check them
# against the chart-pinned Hermes image with no network and no credentials.
#
#   .github/scripts/provider-contract/vertex.sh
#
# Needs helm, yq, openssl, npm and docker. Set AIMOCK_VERSION to override the pin.
set -euo pipefail

root="$(cd "$(dirname "$0")/../../.." && pwd)"
here="$root/.github/scripts/provider-contract"
AIMOCK_VERSION="${AIMOCK_VERSION:-1.48.0}"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail() { echo "::error::[vertex-contract] $*"; exit 1; }

helm template vertex "$root/charts/hermes-agent" \
  -f "$root/charts/hermes-agent/values-google-vertex.yaml" > "$work/rendered.yaml"

image="$(yq 'select(.kind == "Deployment") | .spec.template.spec.containers[] | select(.name == "hermes-agent") | .image' "$work/rendered.yaml")"
cred_path="$(yq 'select(.kind == "Deployment") | .spec.template.spec.containers[0].env[] | select(.name == "VERTEX_CREDENTIALS_PATH") | .value' "$work/rendered.yaml")"
secret_name="$(yq 'select(.kind == "Deployment") | .spec.template.spec.volumes[] | select(.name == "vertex-sa") | .secret.secretName' "$work/rendered.yaml")"
mount_path="$(yq 'select(.kind == "Deployment") | .spec.template.spec.containers[0].volumeMounts[] | select(.name == "vertex-sa") | .mountPath' "$work/rendered.yaml")"
read_only="$(yq 'select(.kind == "Deployment") | .spec.template.spec.containers[0].volumeMounts[] | select(.name == "vertex-sa") | .readOnly' "$work/rendered.yaml")"

[ -n "$image" ] || fail "no hermes-agent image in the rendered Deployment"
[ "$secret_name" = "vertex-sa" ] || fail "credential Secret is '$secret_name', expected vertex-sa"
[ "$read_only" = "true" ] || fail "credential mount is not read-only"
case "$cred_path" in "$mount_path"/*) ;; *) fail "VERTEX_CREDENTIALS_PATH '$cred_path' is not under mount '$mount_path'" ;; esac
echo "rendered: image=$image credential=$cred_path (Secret $secret_name, read-only mount)"

mkdir -p "$work/contract" "$work/aimock"
cp -R "$here/fixtures" "$here/vertex_contract.py" "$work/contract/"
yq 'select(.kind == "ConfigMap") | .data["config.yaml"]' "$work/rendered.yaml" > "$work/contract/config.yaml"
[ -s "$work/contract/config.yaml" ] || fail "no config.yaml in the rendered ConfigMap"

# Synthetic service-account key. token_uri points at the in-container token endpoint.
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$work/key.pem" 2>/dev/null
python3 - "$work" <<'PY'
import json, sys
w = sys.argv[1]
json.dump({
    "type": "service_account", "project_id": "embedded-project-not-used",
    "private_key_id": "synthetic", "private_key": open(f"{w}/key.pem").read(),
    "client_email": "contract@embedded-project-not-used.iam.gserviceaccount.com",
    "token_uri": "http://127.0.0.1:4011/token",
}, open(f"{w}/sa.json", "w"))
PY

npm install --silent --no-audit --no-fund --prefix "$work/aimock" "@copilotkit/aimock@$AIMOCK_VERSION"

docker run --rm --network none --cap-drop ALL --tmpfs /tmp --workdir /opt/hermes \
  --entrypoint /opt/hermes/.venv/bin/python3 \
  -e HERMES_HOME=/tmp/hermes-home -e HERMES_DISABLE_LAZY_INSTALLS=1 \
  -e "VERTEX_CREDENTIALS_PATH=$cred_path" \
  -v "$work/contract:/contract:ro" \
  -v "$work/aimock/node_modules/@copilotkit/aimock:/opt/aimock:ro" \
  -v "$work/sa.json:$cred_path:ro" \
  "$image" -c '
import os, shutil
os.makedirs("/tmp/hermes-home", exist_ok=True)
shutil.copy("/contract/config.yaml", "/tmp/hermes-home/config.yaml")
exec(open("/contract/vertex_contract.py").read())
'
