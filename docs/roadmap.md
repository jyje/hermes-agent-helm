# Roadmap

[English](roadmap.md) · [한국어](roadmap-ko.md)

The chart deploys and manages **one** agent well; teams are how you scale.

| Stage | What | Horizon | Status |
| --- | --- | --- | --- |
| **Single agent** | This chart — one well-managed Hermes instance per release | now | ✅ available |
| **Agent team (ArgoCD ApplicationSet)** | Generate a team's per-agent releases from one ApplicationSet (roster as data, the chart as the template) — one shared gateway channel, unique `fullname` per member, no hand-maintained Application files per teammate | now | ✅ recommended — [docs/teams.md](teams.md) |
| **Operator** | A Kubernetes operator (`Agent` / `AgentTeam` CRDs, in a separate repo) — would replace the ApplicationSet with team-wide status as a single object, admission-time validation of team-level invariants, or active reconciliation. This repo would host its **install chart** | long-term | ⏸️ not started — placeholder in [`charts/hermes-operator/`](../charts/hermes-operator/) (TBA) |

So the trajectory is **single instance → team via ApplicationSet (today) →
operator with `Agent` / `AgentTeam` CRDs (long-term, not started)**. The
ApplicationSet already covers what "a team" needs today — the operator is
only worth building if its templating-only model proves insufficient in
practice (the three reasons above), so it stays a long-term, unscheduled
candidate rather than a near-term plan. The
[`charts/hermes-operator/`](../charts/hermes-operator/) directory is an
intentionally empty placeholder for that possible future chart.

## See also

- [Hermes teams](teams.md) — the ApplicationSet-based team pattern in detail.
- [Chart README](../charts/hermes-agent/README.md) — full values table and the
  `replicaCount` single-writer rationale.
