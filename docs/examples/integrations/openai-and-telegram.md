---
title: OpenAI + Telegram
description: Combine the OpenAI provider and a Telegram bot in one release.
---

| Required secret | Overlay |
| --- | --- |
| `OPENAI_API_KEY, TELEGRAM_BOT_TOKEN` | `values-openai-and-telegram.yaml` |

## When to use it

An OpenAI API key, Telegram bot token, and chat scope are required.

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-openai-and-telegram.yaml \
  --set-string env.OPENAI_API_KEY='<real-value>' --wait
```

When an example requires more than one credential, pass every listed value with `--set-string` or use `extraEnvFrom` to reference an existing Secret.

## Adapt before deploying

Set the Telegram target scope before talking to the bot.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai-and-telegram.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-openai-and-telegram.yaml"
--8<-- "charts/hermes-agent/values-openai-and-telegram.yaml"
```