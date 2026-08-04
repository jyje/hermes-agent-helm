---
title: DeepInfra
description: Connect to the DeepInfra OpenAI-compatible endpoint.
---

| Required secret | Overlay |
| --- | --- |
| `DEEPINFRA_API_KEY` | `values-deepinfra.yaml` |

## When to use it

A DeepInfra API key and a model available from the endpoint are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-deepinfra.yaml \
  --set-string env.DEEPINFRA_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Choose a model from the DeepInfra `/v1/openai/models` list.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-deepinfra.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-deepinfra.yaml"
--8<-- "charts/hermes-agent/values-deepinfra.yaml"
```