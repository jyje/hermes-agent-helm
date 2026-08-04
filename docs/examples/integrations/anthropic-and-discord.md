---
title: Anthropic + Discord
description: Combine the Claude provider and a Discord bot in one release.
---

| Required secret | Overlay |
| --- | --- |
| `ANTHROPIC_API_KEY, DISCORD_BOT_TOKEN` | `values-anthropic-and-discord.yaml` |

## When to use it

An Anthropic API key, Discord bot token, channel ID, and allowed user IDs are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Use this to validate model and messenger settings together.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-anthropic-and-discord.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-anthropic-and-discord.yaml"
--8<-- "charts/hermes-agent/values-anthropic-and-discord.yaml"
```