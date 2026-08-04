---
title: Bitwarden Secrets Manager
description: Fetch provider credentials from Bitwarden Secrets Manager at startup.
---

| Required secret | Overlay |
| --- | --- |
| `BWS_ACCESS_TOKEN` | `values-bitwarden.yaml` |

## When to use it

A Bitwarden machine account with read access and a bootstrap Kubernetes Secret are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-bitwarden.yaml \
  --set-string env.BWS_ACCESS_TOKEN='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Keep provider credentials in the Bitwarden project rather than Git or a Kubernetes Secret.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-bitwarden.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-bitwarden.yaml"
--8<-- "charts/hermes-agent/values-bitwarden.yaml"
```