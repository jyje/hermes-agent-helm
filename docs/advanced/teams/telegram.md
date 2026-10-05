---
title: Telegram teams
description: Shared Telegram assistants and multi-bot Hermes teams.
---

# Telegram teams

[English](telegram.md) · [한국어](../../../ko/advanced/teams/telegram.md)

This chart supports two different Telegram setups: one bot shared by several
authorized people, and a multi-release team where each Hermes identity has its
own bot. Start with the [shared assistant values](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-telegram-team-assistant.yaml)
for one bot, or the [leader](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-telegram-team-leader.yaml)
and [member](https://github.com/jyje/hermes-agent-helm/blob/main/charts/hermes-agent/values-telegram-team-member.yaml)
values plus the [ApplicationSet example](https://github.com/jyje/hermes-agent-helm/blob/main/examples/argocd/hermes-team-telegram.yaml)
for multiple bots.

## One bot shared by several people

The shared-assistant example uses one Telegram bot and one Helm release. Access
can be limited independently for DMs and groups:

- `TELEGRAM_ALLOWED_USERS` authorizes user IDs in DMs and groups.
- `TELEGRAM_GROUP_ALLOWED_USERS` authorizes user IDs in groups only.
- `TELEGRAM_GROUP_ALLOWED_CHATS` authorizes everyone who can post in the named
  group or forum.
- Pairing can authorize a person who first contacts the bot by DM. Approvals
  are stored in `HERMES_HOME` and survive pod restarts when persistence is on.

The example enables `telegram.require_mention` and `group_sessions_per_user`.
In a group, people must mention the bot, reply to it, or use a command addressed
to it; ordinary group chatter does not start a turn. Each person has a separate
conversation. Put the bot token in a Secret and inject it with `extraEnvFrom`
for a GitOps deployment. The values file contains placeholders only.

## Several bots in one group

Deploy one release per Hermes identity. Every release has its own bot token,
`HERMES_HOME` PVC, model credentials, and team identity. They share a Telegram
group or forum topic; the leader also owns a shared roster skill and a read-write
knowledge PVC which members mount read-only. The persistent volume is for
reviewed reusable knowledge, not live tasks or handoff state.

Before deploying, create one Telegram bot per release and:

1. Enable Bot-to-Bot Communication in BotFather for every bot.
2. Add all bots to the same group, supergroup, or forum topic.
3. Make each bot an administrator, or disable Group Privacy for it. After
   changing privacy, remove and re-add the bot so the setting takes effect.
4. Use a distinct Secret and `TELEGRAM_BOT_TOKEN` for every release. A Telegram
   token cannot be polled concurrently by multiple releases.
5. Limit human access with the user and group allowlists described above.
   Include allowed human IDs in each release's Secret or shared routing Secret.

Team mode routes work with the literal public bot usernames in its roster. It
sets `group_sessions_per_user=false`, defaults
`telegram.exclusive_bot_mentions=true`, and clears shared `mention_patterns` so
only the bot named in a message handles that turn. It also enforces these
container environment gates:

| Setting | Value | Purpose |
| --- | --- | --- |
| `TELEGRAM_ALLOW_BOTS` | `mentions` | Admit another bot only when it explicitly addresses this bot. |
| `TELEGRAM_BOTS_REQUIRE_MENTION` | `true` | Do not treat a quote-reply alone as a bot handoff. |
| `TELEGRAM_REQUIRE_MENTION` | `true` | Require a trigger for group messages. |
| `TELEGRAM_REPLY_TO_MODE` | `off` | Do not add reply references that can wake another bot. |

The roster protocol serializes work: the leader delegates to one member, waits
for its result, reviews it, and eventually answers the human without another
member mention. It limits the number of handoffs and asks agents to stop rather
than add a follow-up that restarts the exchange. Hermes' per-chat bot-loop guard
remains enabled as another safeguard. These controls reduce accidental loops;
they do not substitute for observing a real Telegram exchange before relying on
the pattern.

### Why Telegram bot messages, not `hermes peer`

The requested flow is visible in the Telegram group: a human addresses the
leader, the leader addresses a member, and the final answer returns to the
human. `hermes peer` is a valid platform-neutral alternative for gateway-to-
gateway DMs, but it requires reachable API servers and `API_SERVER_KEY`
credentials and does not publish the handoff messages into that group. It is a
different interaction model, not a drop-in replacement for this example. See
the upstream [`hermes peer` guide](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode#bot-initiated-dms-across-machines-hermes-peer)
if private gateway handoffs are a better fit for your deployment.

## Validation status

The values and ApplicationSet examples are render-checked in CI. That validates
the chart contract, not Telegram delivery. Real bot-to-bot routing, negative
cases, and screenshots still require a live deployment with operator-provided
Telegram bots and credentials; no such live proof is claimed by these examples.
