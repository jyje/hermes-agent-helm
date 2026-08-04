---
title: OpenAI
description: A minimal provider configuration for getting started quickly with the OpenAI API.
---

<div class="example-meta">
  <div><strong>Required secret</strong>OPENAI_API_KEY</div>
  <div><strong>Overlay</strong>values-openai.yaml</div>
</div>

## When to use it

An OpenAI account and API key are required. Choose this for a first installation or a broadly compatible baseline.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openai.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Replace the model ID and API key with the values for your environment.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-openai.yaml"
--8<-- "charts/hermes-agent/values-openai.yaml"
```