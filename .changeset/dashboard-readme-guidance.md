---
"@jyje/hermes-agent-helm": patch
---

Documentation(dashboard): Expose the dashboard section

Split the dense dashboard paragraph into a step-by-step "Expose the dashboard" section: choose a sign-in method, turn it on and route it, set a trusted proxy and find its address, change settings later with `bootstrap.overwrite=true` (the seeded `config.yaml` is not updated otherwise), expect a slow first start, and a symptom table.
