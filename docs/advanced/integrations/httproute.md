---
title: Listener routing with HTTPRoute
description: Route selected Hermes listeners through a Gateway API HTTPRoute.
---

| Required secret | Overlay |
| --- | --- |
| `OPENAI_API_KEY, API_SERVER_KEY, WEBHOOK_SECRET` | `values-httproute.yaml` |

## When to use it

Use this when the cluster already provides the Gateway API CRD and a Gateway.
Set `httpRoute.parentRefs` to that Gateway. The chart does not install Gateway
API CRDs or create the Gateway.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-httproute.yaml --wait
```

## Adapt before deploying

An empty `backendRefs[].name` targets this release's Service, so it requires
`service.enabled: true`. Name an external Service explicitly to route to it
without the chart Service. The chart fails early if an implicit backend would
target no Service.

`hostnames` apply to every rule in one HTTPRoute. Create separate HTTPRoutes
when API and webhook rules must be isolated by hostname.

For clusters operated through an Ingress controller, use [Ingress](ingress.md)
instead. Both routing resources are off by default; choose one per host and
path.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-httproute.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-httproute.yaml"
--8<-- "charts/hermes-agent/values-httproute.yaml"
```
