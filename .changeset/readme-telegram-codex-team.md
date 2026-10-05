---
"@jyje/hermes-agent-helm": patch
---

Documentation(team): Codex Telegram team example in the README

Add a README example for a Telegram team where every bot signs in to OpenAI Codex on its own, with the overlay, the install loop, and the notes that matter (home channel on every release, wait for the ready message, one account per bot). The README also states what the live Telegram run did and did not cover. The Telegram member values file now sets `TELEGRAM_HOME_CHANNEL`, which stops Hermes' "no home channel" notice and gives the login and ready messages somewhere to go.
