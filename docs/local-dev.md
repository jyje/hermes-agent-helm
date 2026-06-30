# Local development guide

## Local Kubernetes cluster

You need a running cluster to use `make test` or iterate on the chart locally.
**kind** is recommended — it is the same runtime CI uses.

### kind (recommended)

```bash
# Install
brew install kind          # macOS
# or: https://kind.sigs.k8s.io/docs/user/quick-start/#installation

# Create a cluster
kind create cluster --name hermes-dev

# Verify
kubectl cluster-info --context kind-hermes-dev
```

To tear it down:

```bash
kind delete cluster --name hermes-dev
```

### minikube

```bash
# Install
brew install minikube      # macOS

# Start (Docker driver works without VMs)
minikube start --driver=docker

# Switch kubectl context
kubectl config use-context minikube
```

### MicroK8s (Linux)

```bash
sudo snap install microk8s --classic
microk8s enable dns storage
sudo microk8s kubectl config view --raw > ~/.kube/config
```

---

## Dev install on the local cluster

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.NVIDIA_API_KEY='nvapi-...' \
  --set-string env.DISCORD_BOT_TOKEN='...' \
  --set-string env.DISCORD_HOME_CHANNEL='...' \
  --set config.model.provider=nvidia \
  --set config.model.default='meta/llama-3.3-70b-instruct' \
  --wait
```

Run the chart's own test suite after install:

```bash
make test
```

---

## Port-forwarding a remote cluster agent

When you want to test against an agent already running in a staging or
production cluster (instead of spinning up a local kind cluster), port-forward
the management dashboard to your machine:

```bash
kubectl port-forward svc/hermes-agent 9119:9119 -n hermes-agent
```

The Hermes dashboard is then available at `http://localhost:9119`.

For `exec`-based debugging:

```bash
# Open a shell inside the running agent pod
kubectl exec -it deploy/hermes-agent -n hermes-agent -- sh

# Check gateway status
hermes gateway status
```

> The agent connects **outbound** to Discord and the AI provider — there is no
> inbound webhook to expose. Port-forwarding is only needed to reach the
> management dashboard or to run ad-hoc `hermes` CLI commands through the pod.

---

## Discord bot + NVIDIA provider + gateway

### Prerequisites

| Item | Where to get it |
|---|---|
| Discord bot token | [Discord Developer Portal](https://discord.com/developers/applications) → Bot → Token |
| Discord channel ID | Right-click channel → Copy Channel ID (Developer Mode must be on) |
| NVIDIA API key | [NVIDIA NIM](https://build.nvidia.com) → Get API Key |

### values file

Create a `values-local-dev.yaml` (keep this out of version control):

```yaml
config:
  model:
    provider: nvidia
    default: meta/llama-3.3-70b-instruct

env:
  NVIDIA_API_KEY: "nvapi-<your-key>"
  DISCORD_BOT_TOKEN: "<your-bot-token>"
  DISCORD_HOME_CHANNEL: "<channel-id>"
```

### Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f values-local-dev.yaml \
  --wait
```

### Verify

```bash
# Check the agent came up
kubectl get pods -n hermes-agent

# Tail logs to watch Discord connection
kubectl logs -f deploy/hermes-agent -n hermes-agent

# Run the built-in health check
make test
```

A successful startup logs a line like `gateway connected` and the bot appears
online in Discord. Send a message in the home channel to confirm end-to-end.

### Minimal gateway values for team testing

If you are running multiple agents on a shared Discord channel (see
[docs/teams.md](teams.md)), set the allow-bots flag so agents can reply to
each other:

```yaml
extraEnv:
  - name: DISCORD_ALLOW_BOTS
    value: "1"
  - name: DISCORD_THREAD_REQUIRE_MENTION
    value: "1"
```

See [docs/collaboration.md](collaboration.md) for the full multi-agent setup.
