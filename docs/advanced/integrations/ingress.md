---
title: Listener routing with Ingress
description: Route selected Hermes listeners through an Ingress controller.
---

| Required secret | Overlay |
| --- | --- |
| `OPENAI_API_KEY, API_SERVER_KEY, WEBHOOK_SECRET` | `values-ingress-listeners.yaml` |

## When to use it

Use this when the cluster has an Ingress controller. An API key, listener
secrets, and a controller configuration appropriate for the selected hosts are
required. The dashboard remains sensitive: protect it with authentication if
you route it at all.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-ingress-listeners.yaml --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Set `paths[].service` only when using an external Service. When omitted, it
defaults to this release's Service and the path's `port` defaults to
`service.port`. The chart rejects an implicit chart-Service backend when
`service.enabled: false`.

For Gateway API clusters, use [HTTPRoute](httproute.md) instead. Both routing
resources are off by default; choose the API operated by the cluster instead of
enabling both for the same host and path.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-ingress-listeners.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-ingress-listeners.yaml"
--8<-- "charts/hermes-agent/values-ingress-listeners.yaml"
```
