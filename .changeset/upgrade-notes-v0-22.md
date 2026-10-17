---
"@jyje/hermes-agent-helm": patch
---

Documentation(chart): Upgrade notes for Hermes v0.22

Read the new "Upgrade notes" section before moving an existing release to the `v0.22.2` image: Hermes now prunes ended sessions older than 90 days at startup (`sessions.auto_prune`), with steps to keep them on an existing volume. It also covers the retired idle/daily session resets, the single multiplexed gateway, semver image tags, and the dashboard security fixes. The stale `SESSION_IDLE_MINUTES` row is removed from the environment variable table.
