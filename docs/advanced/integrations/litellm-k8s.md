---
title: LiteLLM (in cluster)
description: Connect to LiteLLM through a Service in the same Kubernetes cluster.
---

| Required secret | Overlay |
| --- | --- |
| `OPENAI_API_KEY` | `values-litellm-k8s.yaml` |

## When to use it

The LiteLLM Service name, namespace, port, and proxy key are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-litellm-k8s.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Set the base URL to the Service FQDN to avoid an Ingress and TLS hop.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-litellm-k8s.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-litellm-k8s.yaml"
--8<-- "charts/hermes-agent/values-litellm-k8s.yaml"
```