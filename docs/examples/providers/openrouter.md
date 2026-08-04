---
title: OpenRouter
description: Select models from multiple upstream providers with one OpenRouter key.
---

| Required secret | Overlay |
| --- | --- |
| `OPENROUTER_API_KEY` | `values-openrouter.yaml` |

## When to use it

An OpenRouter API key and a target model are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openrouter.yaml \
  --set-string env.OPENROUTER_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Use a provider/model name from the OpenRouter catalog.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openrouter.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-openrouter.yaml"
--8<-- "charts/hermes-agent/values-openrouter.yaml"
```