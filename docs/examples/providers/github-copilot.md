---
title: GitHub Copilot
description: Complete GitHub Copilot device login through Discord.
---

<div class="example-meta">
  <div><strong>Required secret</strong>DISCORD_BOT_TOKEN</div>
  <div><strong>Overlay</strong>values-github-copilot.yaml</div>
</div>

## When to use it

A Discord bot, GitHub Copilot access, and persistent storage are required so login tokens can be reused.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-github-copilot.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Approve the device code from the initial pod logs or Discord prompt in GitHub.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-github-copilot.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
--8<-- "charts/hermes-agent/values-github-copilot.yaml"
```