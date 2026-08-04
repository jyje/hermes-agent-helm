---
title: Mixture of Agents
description: Combine multiple reference models with an aggregator model.
---

| Required secret | Overlay |
| --- | --- |
| `OPENROUTER_API_KEY` | `values-moa.yaml` |

## When to use it

Hermes image v2026.7.1 or later and credentials for each referenced provider are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-moa.yaml \
  --set-string env.OPENROUTER_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Replace the preset reference and aggregator models for your workload.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-moa.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-moa.yaml"
--8<-- "charts/hermes-agent/values-moa.yaml"
```