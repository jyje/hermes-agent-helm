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

`hermes-agent.yaml` is the bare-minimum starting point — pure chart defaults
plus the secret wiring; copy it and add a `valuesObject` to customize.

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
