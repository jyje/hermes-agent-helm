---
"@jyje/hermes-agent-helm": minor
---

Feature(auth): Telegram delivery for device-flow login

Add `auth.deviceFlow.notify: telegram`. The `auth-device-login` init container now posts the verification URL and one-time code to the Telegram home channel, reusing `TELEGRAM_BOT_TOKEN` and `TELEGRAM_HOME_CHANNEL`, so a Telegram-only agent no longer has to read the code from the init container logs. The message is sent with `sendMessage` only and never polls, so it does not conflict with the running agent. The code is still printed to the init container logs as before. Login prompts now also name the release (the team identity, or the release name outside team mode), so several parallel logins can be told apart.
