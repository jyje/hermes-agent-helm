# Vertex provider contract pilot

Requires Helm, yq v4, jq, Docker, and the two local images. From the repository root:

```sh
docker pull nousresearch/hermes-agent:$(yq -r '.appVersion' charts/hermes-agent/Chart.yaml)
docker pull ghcr.io/copilotkit/aimock:1.48.0
bash tests/vertex-contract/run.sh
```

The pilot renders the Vertex overlay, overriding the test project and model
explicitly so it does not depend on #452 merging first. It checks the rendered
Kubernetes Secret reference, read-only mount, and credential path. Docker
bind mounts reproduce those paths for the Hermes CLI, not Kubernetes mount
behavior.

The test replaces Google credential construction and intercepts the HTTP
transport. It checks the original method, URL, synthetic bearer token, and
model before forwarding to aimock. The mock runs without published ports on
an internal network. The expected output is `Actual: VERTEX_CONTRACT_OK`.
This does not verify real token minting, IAM, or model availability.
