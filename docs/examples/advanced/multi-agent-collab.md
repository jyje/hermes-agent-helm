---
title: Collaborating pair
description: Run the planner half of a collaborating pair in the same Discord channel.
---

| Required secret | Overlay |
| --- | --- |
| `NVIDIA_API_KEY, DISCORD_BOT_TOKEN` | `values-multi-agent-collab.yaml` |

## When to use it

Two bot identities, a shared channel, each bot’s Discord user ID, and provider credentials are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-multi-agent-collab.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Deploy the separate builder release and loop-brake settings together with this planner.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-multi-agent-collab.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-multi-agent-collab.yaml"
--8<-- "charts/hermes-agent/values-multi-agent-collab.yaml"
```