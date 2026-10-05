---
"@jyje/hermes-agent-helm": minor
---

Feature(auth): Ready message when the gateway starts

Add `readyNotify.enabled` (off by default) and `readyNotify.notify` (`discord` or `telegram`, or follow `auth.deviceFlow.notify`). The chart seeds a `gateway:startup` hook that posts one line to the home channel when the gateway is up, so you know when to talk to the agent after a first start that can take minutes. Hermes itself only announces restarts. The hook reuses the bot credentials already configured, never logs the token, and does nothing unless enabled.
