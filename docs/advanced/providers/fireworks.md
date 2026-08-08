---
title: Fireworks AI
description: Use Fireworks AI through its OpenAI-compatible provider endpoint.
---

| Required secret | Overlay |
| --- | --- |
| `FIREWORKS_API_KEY` | `values-fireworks.yaml` |

## When to use it

A Fireworks API key and a supported model are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-fireworks.yaml \
  --set-string env.FIREWORKS_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Check the available model catalog before changing `config.model.default`.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-fireworks.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-fireworks.yaml"
--8<-- "charts/hermes-agent/values-fireworks.yaml"
```