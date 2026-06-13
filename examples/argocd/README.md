# Deploying with ArgoCD

These Application manifests deploy `hermes-agent-helm` via ArgoCD safely —
including **multiple instances in the same namespace without collisions**.

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

Keep the chart's `env.OPENAI_API_KEY` as a placeholder and inject the real key
from a Secret created out-of-band (or via sealed-secrets / external-secrets):

```bash
kubectl create namespace hermes-agent-helm
kubectl create secret generic hermes-agent-helm-litellm -n hermes-agent-helm \
  --from-literal=OPENAI_API_KEY="$(kubectl get secret litellm-creds -n ollama-system \
    -o go-template='{{ index .data "litellm.masterkey" | base64decode }}')"
```

`extraEnvFrom` references that Secret; since it is applied after the chart's own
env Secret, its `OPENAI_API_KEY` wins.

## Apply

```bash
kubectl apply -f examples/argocd/hermes-agent-helm.application.yaml
```

## Multiple instances in the same namespace

Just duplicate the Application with a different name == releaseName. Example
second instance alongside the first, both in `hermes-agent-helm`:

```yaml
metadata:
  name: hermes-agent-helm-staging      # different name
spec:
  source:
    helm:
      releaseName: hermes-agent-helm-staging   # == metadata.name
  destination:
    namespace: hermes-agent-helm       # SAME namespace is fine
```

Resources render as `hermes-agent-helm-staging-*` (pod `hermes-agent-helm-staging-0`,
`hermes-agent-helm-staging-config`, `data-hermes-agent-helm-staging-0`, …) — no
overlap with the `hermes-agent-helm-*` set. Each gets its own PVC, so the two
instances do **not** share a knowledge base.
