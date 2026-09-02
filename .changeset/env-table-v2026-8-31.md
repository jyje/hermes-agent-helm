---
"@jyje/hermes-agent-helm": patch
---

Documentation(env): Refresh the curated environment-variable table for v2026.8.31

Re-check the chart README's "Environment variables" teaser table against the
upstream reference at the pinned `v2026.8.31` tag. Add the providers that
arrived since the last refresh (Meta Model API, Nebius Token Factory, Ramp
Router, Tencent TokenPlan) and the dashboard auth-gate variables; drop rows
already covered by the provider table and its `values-*.yaml` examples
(Fireworks, DeepInfra, Upstage) plus two low-signal overrides, keeping the
table at its previous size. Correct the `HERMES_MAX_ITERATIONS` row: the
upstream default is 500, not 90; 90 is the value this chart seeds as
`config.agent.max_turns`. The Korean README twin gets the same table and its
stale hard-coded image version.
