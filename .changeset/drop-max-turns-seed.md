---
"@jyje/hermes-agent-helm": minor
---

Fix(config): Stop seeding agent.max_turns, following upstream's unlimited default

The chart has seeded `config.agent.max_turns: 90` since its first commit. That
value was a mirror of the upstream default at the time (`v2026.6.5`), not a
chart decision, and upstream has since made `agent.max_turns` unlimited by
default because a hard turn cap caused silent mid-task truncation; the
`HERMES_MAX_ITERATIONS` budget (500, followed by a wrap-up grace call) and
`agent.gateway_timeout` are the runaway guards now. The seed is removed and
left as a commented example with that rationale, so new installs get upstream
behaviour. Existing installs with `bootstrap.overwrite: true` (the default)
pick up the change on their next rollout; set `config.agent.max_turns`
explicitly to keep a cap. The README env-var row is reworded to match.
