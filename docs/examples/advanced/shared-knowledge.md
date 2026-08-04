---
title: Shared knowledge PVC
description: Mount an RWX PVC as shared knowledge for multiple agents.
---

| Required secret | Overlay |
| --- | --- |
| `Provider key` | `values-shared-knowledge.yaml` |

## When to use it

An existing RWX PVC writable by uid/gid 10000 and provider credentials are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-shared-knowledge.yaml \
  --set-string env.Provider_key='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Keep each agent’s HERMES_HOME on a private PVC and share only the knowledge claim.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-shared-knowledge.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-shared-knowledge.yaml"
--8<-- "charts/hermes-agent/values-shared-knowledge.yaml"
```