---
title: Google Gemini
description: Use the Google AI Studio Gemini API as the model provider.
---

<div class="example-meta">
  <div><strong>Required secret</strong>GOOGLE_API_KEY</div>
  <div><strong>Overlay</strong>values-gemini.yaml</div>
</div>

## When to use it

A Google AI Studio API key is required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-gemini.yaml \
  --set-string env.GOOGLE_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Adjust the Gemini model ID and API key for your environment.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-gemini.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-gemini.yaml"
--8<-- "charts/hermes-agent/values-gemini.yaml"
```