---
title: Upstage Solar
description: Use Upstage Solar as the model provider.
---

<div class="example-meta">
  <div><strong>Required secret</strong>UPSTAGE_API_KEY</div>
  <div><strong>Overlay</strong>values-upstage.yaml</div>
</div>

## When to use it

An Upstage API key and a Solar model are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-upstage.yaml \
  --set-string env.UPSTAGE_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Set the Solar model ID and API key for your environment.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-upstage.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-upstage.yaml"
--8<-- "charts/hermes-agent/values-upstage.yaml"
```