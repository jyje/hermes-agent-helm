---
title: Anthropic
description: Configure Claude as Hermes Agent’s default model provider.
---

| Required secret | Overlay |
| --- | --- |
| `ANTHROPIC_API_KEY` | `values-anthropic.yaml` |

## When to use it

An Anthropic API key and access to a Claude model are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic.yaml \
  --set-string env.ANTHROPIC_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Keep the provider set to `anthropic` and inject the Anthropic key through a Secret.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-anthropic.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-anthropic.yaml"
--8<-- "charts/hermes-agent/values-anthropic.yaml"
```