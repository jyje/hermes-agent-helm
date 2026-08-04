---
title: Dashboard Ingress
description: Expose the sensitive management dashboard behind an authenticated Ingress.
---

<div class="example-meta">
  <div><strong>Required secret</strong>OPENAI_API_KEY, basic-auth Secret</div>
  <div><strong>Overlay</strong>values-ingress.yaml</div>
</div>

## When to use it

An OpenAI API key, a basic-auth Secret, and an Ingress controller are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-ingress.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

The dashboard can expose API keys, so enforce authentication and a private network boundary.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-ingress.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-ingress.yaml"
--8<-- "charts/hermes-agent/values-ingress.yaml"
```