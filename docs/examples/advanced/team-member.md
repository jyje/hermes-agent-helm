---
title: Team member
description: Run an individual member release in a leader-led team.
---

<div class="example-meta">
  <div><strong>Required secret</strong>NVIDIA_API_KEY, DISCORD_BOT_TOKEN</div>
  <div><strong>Overlay</strong>values-team-member.yaml</div>
</div>

## When to use it

A unique bot token, fullnameOverride, TEAM_MEMBER_NAME, and provider credentials are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-team-member.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Deploy a separate Helm release for each member using this values file.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-team-member.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-team-member.yaml"
--8<-- "charts/hermes-agent/values-team-member.yaml"
```