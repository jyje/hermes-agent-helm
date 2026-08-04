---
title: Google Vertex AI
description: Connect to Vertex AI Gemini using a GCP service account.
---

<div class="example-meta">
  <div><strong>Required secret</strong>GCP service-account Secret</div>
  <div><strong>Overlay</strong>values-google-vertex.yaml</div>
</div>

## When to use it

A GCP service-account JSON Secret with Vertex AI User permissions and a project ID are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-vertex.yaml \
  --set-string env.GCP_service-account_Secret='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Create the credential Secret before installation because the chart mounts it instead of using a static API key.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-vertex.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
--8<-- "charts/hermes-agent/values-google-vertex.yaml"
```