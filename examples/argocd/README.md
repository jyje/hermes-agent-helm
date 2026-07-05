# Deploying with ArgoCD

These Application manifests deploy `hermes-agent` via ArgoCD safely —
including **multiple instances in the same namespace without collisions**.

Each file mirrors the corresponding
[`charts/hermes-agent/values-*.yaml`](../../charts/hermes-agent/README.md#more-examples)
example 1:1, with secrets wired via `extraEnvFrom` instead of plain `--set`:

| Application file | Mirrors | Required Secret |
| --- | --- | --- |
| [`hermes-agent.yaml`](hermes-agent.yaml) | chart defaults (`values.yaml`) | `hermes-agent-secrets` (`OPENAI_API_KEY`) |
| [`hermes-agent-openai.yaml`](hermes-agent-openai.yaml) | `values-openai.yaml` | `hermes-agent-openai-secrets` (`OPENAI_API_KEY`) |
| [`hermes-agent-openai-sealedsecret.yaml`](hermes-agent-openai-sealedsecret.yaml) | `values-openai.yaml` + GitOps | `hermes-agent-openai-sealedsecret-secrets` via **SealedSecret** (`extraResources`) |
| [`hermes-agent-anthropic.yaml`](hermes-agent-anthropic.yaml) | `values-anthropic.yaml` | `hermes-agent-anthropic-secrets` (`ANTHROPIC_API_KEY`) |
| [`hermes-agent-gemini.yaml`](hermes-agent-gemini.yaml) | `values-gemini.yaml` | `hermes-agent-gemini-secrets` (`GOOGLE_API_KEY`) |
| [`hermes-agent-openrouter.yaml`](hermes-agent-openrouter.yaml) | `values-openrouter.yaml` | `hermes-agent-openrouter-secrets` (`OPENROUTER_API_KEY`) |
| [`hermes-agent-litellm.yaml`](hermes-agent-litellm.yaml) | `values-litellm.yaml` | `hermes-agent-litellm-secrets` (`OPENAI_API_KEY`, proxy key) |
| [`hermes-agent-litellm-k8s.yaml`](hermes-agent-litellm-k8s.yaml) | `values-litellm-k8s.yaml` | `hermes-agent-litellm-k8s-secrets` via **SealedSecret** (`extraResources`) |
| [`hermes-agent-anthropic-and-discord.yaml`](hermes-agent-anthropic-and-discord.yaml) | `values-anthropic-and-discord.yaml` | `hermes-agent-anthropic-discord-secrets` (`ANTHROPIC_API_KEY`, `DISCORD_BOT_TOKEN`) |
| [`hermes-agent-openai-and-telegram.yaml`](hermes-agent-openai-and-telegram.yaml) | `values-openai-and-telegram.yaml` | `hermes-agent-openai-telegram-secrets` (`OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`) |
| [`hermes-agent-nvidia-nim-and-discord.yaml`](hermes-agent-nvidia-nim-and-discord.yaml) | `values-nvidia-nim-and-discord.yaml` | `hermes-agent-nim-discord-secrets` (`NVIDIA_API_KEY`, `DISCORD_BOT_TOKEN`) |
| [`hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml`](hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml) | `values-nvidia-nim-and-discord.yaml` + GitOps | `hermes-agent-nim-discord-sealedsecret-secrets` via **SealedSecret** (`extraResources`, `NVIDIA_API_KEY` + `DISCORD_BOT_TOKEN`) |
| [`hermes-agent-github-copilot.yaml`](hermes-agent-github-copilot.yaml) | `values-github-copilot.yaml` + GitOps | `hermes-agent-copilot-secrets` via **SealedSecret** (`DISCORD_BOT_TOKEN` only — Copilot token minted at runtime via **OAuth device flow**) |
| [`hermes-agent-ingress.yaml`](hermes-agent-ingress.yaml) | `values-ingress.yaml` | `hermes-agent-ingress-secrets` (`OPENAI_API_KEY`) + `hermes-agent-dashboard-auth` (nginx basic-auth) |
| [`hermes-collab-pair.yaml`](hermes-collab-pair.yaml) | `values-multi-agent-collab.yaml` (×2: planner+builder) | `hermes-planner-discord-secrets` + `hermes-builder-discord-secrets` — a **collaborating pair** that hands off by `@mention`; see [docs/collaboration.md](../../docs/collaboration.md) |
| [`hermes-team.yaml`](hermes-team.yaml) | `values-team-leader.yaml` + `values-team-member.yaml` | `hermes-august-discord-secrets` + `hermes-may-discord-secrets` + `hermes-march-discord-secrets` — a **leader-orchestrated team** (leader Application + member ApplicationSet, star topology, shared RWX workspace); see [docs/teams.md](../../docs/teams.md) |

`hermes-agent.yaml` is the bare-minimum starting point — pure chart defaults
plus the secret wiring; copy it and add a `valuesObject` to customize.

`hermes-collab-pair.yaml` is the first multi-Application example: **two** agents
(a `planner` on LiteLLM and a `builder` on Copilot device-flow) sharing one
Discord channel and handing off by `@mention`. See
[docs/collaboration.md](../../docs/collaboration.md) for the handoff protocol and
the four loop-brake env vars.

`hermes-team.yaml` scales that pattern up: one Application for the team
**leader** (`august`) plus an **ApplicationSet** whose member roster (`may`,
`march`) is a list-generator entry — adding a teammate is a one-line diff. The
agents share a Discord channel (star topology: mentions flow leader ↔ member
only) and an RWX workspace PVC created out-of-band. See
[docs/teams.md](../../docs/teams.md) → "Leader-orchestrated teams".

All examples use the **OCI registry** source form (`repoURL`/`chart`/
`targetRevision` pointing at `ghcr.io`). A Git source form
(`repoURL`/`targetRevision`/`path`) works too if you'd rather track a chart
checked into a Git repo — swap freely between the two.

`hermes-agent-litellm-k8s.yaml` is the most complete example: it demonstrates
the full GitOps pattern (SealedSecret via `extraResources` + `extraEnvFrom` +
non-default `persistence.storageClass`). The others use a plain Secret created
out-of-band (see each file's header comment for the exact `kubectl create
secret` command).

All Applications target `destination.namespace: hermes-agent` and use distinct
`releaseName`s — they can be applied together in the same namespace without
colliding (see below).

## The one rule: unique `fullname` per instance

Every chart resource is named from the Helm **fullname**
(`{fullname}`, `{fullname}-0`, `{fullname}-config`, `{fullname}-env`,
`{fullname}-headless`, `{fullname}-test`, `data-{fullname}-0`). Two Applications
collide only if they render the **same fullname** in the **same namespace**.

So give each Application a distinct `spec.source.helm.releaseName`, and:

> **Set `metadata.name` == `spec.source.helm.releaseName`.**

This does two things:
1. Makes the fullname unique per instance (no name collisions).
2. Makes the chart's `app.kubernetes.io/instance` value equal the Application —
   intuitive and consistent.

## Why there is no tracking-label clash here

ArgoCD tracks ownership with a label whose key is set by
`application.instanceLabelKey`. This cluster uses **`argocd.argoproj.io/instance`**
(the ArgoCD-specific key), while the chart uses **`app.kubernetes.io/instance`**
for its own selectors. Different keys → **no clash**, even with the default
`label` tracking method. (If a cluster instead used `app.kubernetes.io/instance`
for tracking, switch it to annotation tracking:
`application.resourceTrackingMethod: annotation` in `argocd-cm`.)

## Secrets (do not commit keys)

Keep the chart's `env.<KEY>` values as placeholders and inject the real
key(s) from a Secret created out-of-band (or via sealed-secrets /
external-secrets). Each Application's header comment has the exact command,
e.g.:

```bash
kubectl create namespace hermes-agent
kubectl create secret generic hermes-agent-openai-secrets -n hermes-agent \
  --from-literal=OPENAI_API_KEY='sk-<your-key>'
```

`extraEnvFrom` references that Secret; since it is applied after the chart's own
env Secret, its values win.

### SealedSecret walkthrough (NVIDIA NIM + Discord)

[`hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml`](hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml)
is the GitOps variant of
[`hermes-agent-nvidia-nim-and-discord.yaml`](hermes-agent-nvidia-nim-and-discord.yaml):
instead of creating a plain Secret out-of-band, it ships a
[bitnami **SealedSecret**](https://github.com/bitnami-labs/sealed-secrets) in
`extraResources`. The sealed-secrets controller decrypts it in-cluster into a
regular Secret (`hermes-agent-nim-discord-sealedsecret-secrets`), which
`extraEnvFrom` then mounts. The encrypted blob is safe to commit to Git — only
the controller's private key (held by your cluster) can decrypt it.

This walkthrough seals **two** keys at once (`NVIDIA_API_KEY` and
`DISCORD_BOT_TOKEN`). For a single key, see the simpler `kubeseal --raw
--from-file` form used in
[`hermes-agent-openai-sealedsecret.yaml`](hermes-agent-openai-sealedsecret.yaml).

**Prerequisites:**
- The [sealed-secrets controller](https://github.com/bitnami-labs/sealed-secrets)
  is installed in the target cluster (e.g. `helm install sealed-secrets
  sealed-secrets/sealed-secrets -n kube-system`).
- The `kubeseal` CLI is installed locally, matching (or able to fetch) the
  controller's public certificate.

**1. Write a plaintext Secret manifest — do not apply it:**

```bash
cat > /tmp/hermes-agent-nim-discord-secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: hermes-agent-nim-discord-sealedsecret-secrets
  namespace: hermes-agent
type: Opaque
stringData:
  NVIDIA_API_KEY: "nvapi-<your-real-key>"
  DISCORD_BOT_TOKEN: "<your-real-bot-token>"
EOF
```

**2. Seal it.** `kubeseal -o yaml` reads a Secret manifest and emits the
SealedSecret equivalent, encrypting every entry in `data`/`stringData` with the
controller's public key (fetched automatically from the cluster, or pass
`--cert <pub-cert.pem>` for an offline cert):

```bash
kubeseal --scope namespace-wide \
  -o yaml < /tmp/hermes-agent-nim-discord-secret.yaml \
  > /tmp/hermes-agent-nim-discord-sealedsecret.yaml
```

This produces a `SealedSecret` with `spec.encryptedData.NVIDIA_API_KEY` and
`spec.encryptedData.DISCORD_BOT_TOKEN`, each a long `AgB...` / `AgD...` base64
blob. `--scope namespace-wide` lets the SealedSecret be renamed/moved within
`hermes-agent` without re-sealing — matches the convention used by the other
SealedSecret examples in this directory.

**3. Splice the two `encryptedData` values** into
`hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml`'s
`extraResources[0].spec.encryptedData`, replacing the
`AgDUMMY_replace_with_kubeseal_output==` placeholders:

```yaml
extraResources:
  - apiVersion: bitnami.com/v1alpha1
    kind: SealedSecret
    metadata:
      name: hermes-agent-nim-discord-sealedsecret-secrets
    spec:
      encryptedData:
        NVIDIA_API_KEY: AgB...      # <- from step 2
        DISCORD_BOT_TOKEN: AgD...   # <- from step 2
      template:
        metadata:
          name: hermes-agent-nim-discord-sealedsecret-secrets
        type: Opaque
```

Also fill in real values for `extraEnv[].value` (`DISCORD_HOME_CHANNEL`,
`DISCORD_ALLOWED_USERS`) and pick an NVIDIA NIM model your account can reach.

**4. Apply the Application and verify:**

```bash
kubectl apply -f examples/argocd/hermes-agent-nvidia-nim-and-discord-sealedsecret.yaml

# the controller should decrypt the SealedSecret into a Secret:
kubectl get sealedsecret,secret -n hermes-agent hermes-agent-nim-discord-sealedsecret-secrets

# and the pod should pick up both keys via extraEnvFrom (fullnameOverride:
# hermes-agent keeps resource names short — see the file's valuesObject):
kubectl exec -n hermes-agent deploy/hermes-agent -- \
  env | grep -E '^(NVIDIA_API_KEY|DISCORD_BOT_TOKEN)='
```

If `kubectl get secret` shows no Secret, check the controller's logs
(`kubectl logs -n kube-system -l app.kubernetes.io/name=sealed-secrets`) — the
most common cause is sealing with the wrong cluster's certificate.

## Apply

```bash
kubectl apply -f examples/argocd/hermes-agent-openai.yaml
```

(Swap in any other file from the table above.)

## Multiple instances in the same namespace

Just duplicate the Application with a different name == releaseName. Example
second instance alongside the first, both in `hermes-agent`:

```yaml
metadata:
  name: hermes-agent-staging      # different name
spec:
  source:
    helm:
      releaseName: hermes-agent-staging   # == metadata.name
  destination:
    namespace: hermes-agent       # SAME namespace is fine
```

Resources render as `hermes-agent-staging-*` (pod `hermes-agent-staging-0`,
`hermes-agent-staging-config`, `data-hermes-agent-staging-0`, …) — no
overlap with the `hermes-agent-*` set. Each gets its own PVC, so the two
instances do **not** share a knowledge base.
