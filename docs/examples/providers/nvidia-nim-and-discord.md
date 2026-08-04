---
title: NVIDIA NIM + Discord
description: Connect NVIDIA NIM and a Discord bot in one release.
---

<div class="example-meta">
  <div><strong>Required secret</strong>NVIDIA_API_KEY, DISCORD_BOT_TOKEN</div>
  <div><strong>Overlay</strong>values-nvidia-nim-and-discord.yaml</div>
</div>

## When to use it

NVIDIA API credentials, a Discord bot token, a channel, and allowed user IDs are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-nvidia-nim-and-discord.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

This provider-and-messenger combination can also run on ARM64 clusters.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-nvidia-nim-and-discord.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-nvidia-nim-and-discord.yaml"
--8<-- "charts/hermes-agent/values-nvidia-nim-and-discord.yaml"
```