#!/usr/bin/env bash
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../.." && pwd)
chart="$repo/charts/hermes-agent"
scratch=$(mktemp -d)
network="hermes-vertex-contract-${scratch##*.}"
mock="$network-aimock"
network_id=
mock_id=
cleanup() {
  if [[ -n "$mock_id" ]]; then docker rm -f "$mock_id" >/dev/null 2>&1 || true; fi
  if [[ -n "$network_id" ]]; then docker network rm "$network_id" >/dev/null 2>&1 || true; fi
  rm -f -- "$scratch/rendered.yaml" "$scratch/config.yaml" "$scratch/workload.yaml" "$scratch/sa.json"
  rmdir -- "$scratch"
}
trap cleanup EXIT

helm template vertex-contract "$chart" -f "$chart/values-google-vertex.yaml" \
  --set-string config.vertex.project_id=vertex-contract-fixture \
  --set-string config.model.default=google/gemini-3.8-flash > "$scratch/rendered.yaml"
yq -e 'select(.kind == "ConfigMap" and .data."config.yaml") | .data."config.yaml"' \
  "$scratch/rendered.yaml" > "$scratch/config.yaml"
yq -e '.model.provider == "vertex" and .vertex.region == "global" and
  .vertex.project_id == "vertex-contract-fixture" and .model.default == "google/gemini-3.8-flash"' \
  "$scratch/config.yaml" >/dev/null
yq -e 'select(.kind == "Deployment")' "$scratch/rendered.yaml" > "$scratch/workload.yaml"
yq -e -o=json '.' "$scratch/workload.yaml" | jq -e '
  .spec.template.spec |
  ([.volumes[] | select(.name == "vertex-sa" and .secret.secretName == "vertex-sa")] | length == 1) and
  ([.containers[] | select(.name == "hermes-agent") | .volumeMounts[] |
    select(.name == "vertex-sa" and .mountPath == "/var/run/secrets/vertex" and .readOnly)] | length == 1) and
  ([.containers[] | select(.name == "hermes-agent") | .env[] |
    select(.name == "VERTEX_CREDENTIALS_PATH" and .value == "/var/run/secrets/vertex/sa.json")] | length == 1)' >/dev/null
printf '%s\n' '{"project_id":"synthetic-credential-project"}' > "$scratch/sa.json"
image=$(yq -e '.spec.template.spec.containers[] |
  select(.name == "hermes-agent").image' "$scratch/workload.yaml")
printf '%s\n' 'Helm Vertex configuration and credential mount rendered as expected'

mock_image=ghcr.io/copilotkit/aimock:1.48.0
for required_image in "$image" "$mock_image"; do
  docker image inspect "$required_image" >/dev/null || {
    printf 'Required local image: %s\n' "$required_image" >&2
    exit 1
  }
done
network_id=$(docker network create --internal "$network")
mock_id=$(docker run --pull=never -d --name "$mock" --network "$network" --network-alias aimock \
  -v "$here/fixture.json:/fixtures/vertex.json:ro" \
  "$mock_image" --host 0.0.0.0 --port 4010 --fixtures /fixtures --strict)

reply=$(docker run --pull=never --rm --network "$network" --entrypoint /opt/hermes/.venv/bin/python \
  -e HERMES_HOME=/opt/data -e HERMES_DISABLE_LAZY_INSTALLS=1 \
  -e VERTEX_CREDENTIALS_PATH=/var/run/secrets/vertex/sa.json \
  -v "$scratch/config.yaml:/opt/data/config.yaml:ro" \
  -v "$scratch/sa.json:/var/run/secrets/vertex/sa.json:ro" \
  -v "$here/run-hermes.py:/vertex/run-hermes.py:ro" "$image" /vertex/run-hermes.py)
[[ "$reply" == VERTEX_CONTRACT_OK ]] || { printf '%s\n' 'Unexpected Hermes reply' >&2; exit 1; }
printf 'Actual: %s\n' "$reply"
