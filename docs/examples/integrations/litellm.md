---
title: LiteLLM (external)
description: Connect to a LiteLLM proxy reachable over the network.
---

| Required secret | Overlay |
| --- | --- |
| `OPENAI_API_KEY` | `values-litellm.yaml` |

## When to use it

The LiteLLM HTTPS endpoint and a proxy virtual key are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-litellm.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Use this for a proxy outside the cluster or exposed through an Ingress or LoadBalancer.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-litellm.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-litellm.yaml"
--8<-- "charts/hermes-agent/values-litellm.yaml"
```