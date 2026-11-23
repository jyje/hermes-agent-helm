---
title: Google Vertex AI
description: Connect to Vertex AI Gemini using a GCP service account.
---

| Required secret | Overlay |
| --- | --- |
| `GCP service-account Secret` | `values-google-vertex.yaml` |

## When to use it

Enable the Vertex AI API in your GCP project. The example mounts a GCP
service-account JSON file with the Vertex AI User role.

The example uses `google/gemini-3.8-flash` on the global endpoint.
It replaces Gemini 2.5 Flash, which [retired on Vertex](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions).
Check [model and location availability](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash)
before choosing a different region or model. This example does not use
the Gemini Developer API.

## Install

```bash
kubectl create namespace hermes-agent
kubectl create secret generic vertex-sa --namespace hermes-agent \
  --from-file=sa.json=/path/to/sa.json

helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-google-vertex.yaml \
  --set-string config.vertex.project_id='<your-gcp-project>' --wait
```

If the namespace or Secret already exists, reuse it. Do not put the JSON key
in Helm values or commit it. The example mounts a file, not an API key.

## Adapt before deploying

On an existing release, the default `bootstrap.overwrite: false` preserves
the PVC's `config.yaml`. Update the model through Hermes or by editing that
file; upgrading the overlay alone does not change a persisted model.

## Verification

CI checks this overlay without a cloud account. When the overlay, the Hermes
image or the harness changes, it renders the chart, runs the pinned Hermes image
with no network and no credentials against a local mock, and asserts the Vertex
project, region, `google/gemini-3.8-flash` request path and a fixed reply. A
wrong route or model fails. See [`provider-contract`](../../contributing/ci.md#provider-contract)
for the exact checks and how to run it locally.

This is a mock. It does not test IAM, quota or live Vertex inference, and the
Secret is checked as a mounted file, not exercised in a Pod. After installing,
run one chat against your own project.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-google-vertex.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
--8<-- "charts/hermes-agent/values-google-vertex.yaml"
```
