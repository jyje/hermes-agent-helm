---
"@jyje/hermes-agent-helm": patch
---

Documentation(dashboard): Sign-in is shell access, profile multiplexing is on by default

State that a signed-in dashboard user can also create shell hooks and use the Chat tab, so sign-in should be treated as shell access to the pod (dashboard page, chart README, `values-ingress.yaml`, SECURITY). Also drop the stale instruction to set `config.gateway.multiplex_profiles: true`: upstream enables profile multiplexing by default and `true` is its only valid value.
