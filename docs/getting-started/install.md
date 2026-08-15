---
title: Install Hermes Agent
description: Install the chart with a provider key, then verify the rendered workload.
---

## Install the OCI artifact (recommended)

```bash
helm upgrade --install hermes-agent \
  oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --version <chart-version> --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## Or install from the Helm Repository

```bash
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## Verify

```bash
helm test hermes-agent --namespace hermes-agent
kubectl get pods --namespace hermes-agent
```

The Helm test performs the chart's doctor-style check. Pick a provider overlay next when the generic OpenAI default is not your target.
