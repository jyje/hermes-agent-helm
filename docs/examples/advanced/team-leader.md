---
title: Team leader
description: Run the leader of a Discord thread-based agent team.
---

<div class="example-meta">
  <div><strong>Required secret</strong>NVIDIA_API_KEY, DISCORD_BOT_TOKEN</div>
  <div><strong>Overlay</strong>values-team-leader.yaml</div>
</div>

## When to use it

An RWX knowledge claim, a leader bot, member bot IDs, and provider credentials are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-team-leader.yaml \
  --set-string env.NVIDIA_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Mount shared knowledge read-write for the leader and hand off work explicitly to members.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-team-leader.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-team-leader.yaml"
--8<-- "charts/hermes-agent/values-team-leader.yaml"
```