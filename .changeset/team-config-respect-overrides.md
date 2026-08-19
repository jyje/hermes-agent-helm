---
"@jyje/hermes-agent-helm": minor
---

Feature(teams): Let config: override team mode's Discord defaults

Team mode's config.yaml overlay (`group_sessions_per_user`,
`discord.thread_require_mention`, `discord.history_backfill`,
`discord.allow_mentions.*`) now only fills in a key the user hasn't already
set under `config:`, matching how `discord.history_backfill_limit` already
worked. Existing installs that never touched these keys render an identical
config.yaml; anyone who wants different team-mode Discord behavior can now
set it themselves.
