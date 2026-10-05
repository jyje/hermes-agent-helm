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

## Login codes expire

A code is valid for about 15 minutes. If it expires before you approve it, the
init container reports the timeout and requests a new code on its own, so enter
the newest one. A live run showed exactly this: the first code expired, a
second arrived, and approving it completed the login.

## Larger context window

The Codex route advertises 272K for most models. Hermes can use about 900K when
you opt in with a `-900k` suffix, such as `gpt-6-luna-900k`, and you should
raise `compression.threshold_tokens` with it. The suffix is a Hermes alias, not
an OpenAI model name, and a larger window uses your subscription quota faster.
The overlay below explains the details.

## Several releases on one ChatGPT account

Each release logs in on its own and keeps its credential in its own
`auth.json`. Upstream documents that two logins of the same OpenAI account
share one token family and that OpenAI revokes the older one. In a live check,
three releases logged in to one Plus account within a minute, and a
`hermes auth refresh openai-codex` in each release still succeeded, so no
immediate revocation appeared. A later refresh was not checked.

- For a team, prefer one account per release.
- If a release starts failing to refresh, run
  `hermes auth refresh openai-codex` in each release to see which login died,
  then log in again there.
- Do not copy one `auth.json` into several releases. The refresh token is
  single use, so the copies cannot all stay valid.

[Open Raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-openai-codex.yaml)

## Complete overlay

```yaml title="charts/hermes-agent/values-openai-codex.yaml"
--8<-- "charts/hermes-agent/values-openai-codex.yaml"
```
