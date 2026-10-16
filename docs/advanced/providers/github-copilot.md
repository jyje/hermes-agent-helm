---
title: GitHub Copilot
description: Complete GitHub Copilot device login through Discord.
---

| Required secret | Overlay |
| --- | --- |
| `DISCORD_BOT_TOKEN` | `values-github-copilot.yaml` |

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

## Later starts

The token is stored in `HERMES_HOME/.env` on the persistent volume. On a later
start the init container checks it against `https://api.github.com/user` and
skips the login when it still works. Only a revoked token (HTTP 401) starts a new
device login. The check does not depend on your Copilot plan. Chart versions
up to 1.18.0 checked `copilot_internal/v2/token` instead, which answered 403 for
a valid token on a Copilot Free account and asked for a new code on every
restart ([#349](https://github.com/jyje/hermes-agent-helm/issues/349)). If you
override `validateUrl`, keep it to an endpoint that answers 401 for a revoked
token and 200 otherwise.

## Telegram instead of Discord

Set `auth.deviceFlow.notify: telegram` and give the release the Telegram bot
token and home channel (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_HOME_CHANNEL`, and
`TELEGRAM_ALLOWED_USERS`) in place of the Discord ones. The code then arrives in
the Telegram chat, and `readyNotify.enabled: true` posts a line there when the
agent is up. A live check on a Copilot Free account completed the login, posted
the ready message, and answered with `gpt-4o`. Which models work follows your
GitHub plan.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-github-copilot.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
--8<-- "charts/hermes-agent/values-github-copilot.yaml"
```