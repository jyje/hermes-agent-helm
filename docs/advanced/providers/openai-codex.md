---
title: OpenAI Codex
description: Authenticate a ChatGPT/Codex account through a Discord-delivered device code.
---

| Required secret | Overlay |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-openai-codex.yaml` |

## When to use it

Use this provider for account-backed Codex access. It is separate from
`openai-api`, which requires `OPENAI_API_KEY`. Model availability follows the
ChatGPT plan and the live Codex catalog returned for the authenticated account.

Persistent storage is required because Hermes stores refreshable credentials
in `HERMES_HOME/auth.json`.

## Install

```bash
helm upgrade --install hermes-codex ./charts/hermes-agent \
  --namespace hermes-codex --create-namespace \
  -f charts/hermes-agent/values-openai-codex.yaml \
  --set-string env.DISCORD_BOT_TOKEN='<real-value>' --wait
```

Open the link posted to Discord, enter the one-time code, and complete the
OpenAI sign-in. On later Pod starts the init container asks Hermes to validate
or refresh the stored credentials and skips a new login when they remain usable.

```bash
kubectl logs deploy/hermes-codex-hermes-agent -n hermes-codex \
  -c auth-device-login -f
```

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai-codex.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-openai-codex.yaml"
--8<-- "charts/hermes-agent/values-openai-codex.yaml"
```
