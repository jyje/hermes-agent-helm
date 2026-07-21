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

## v1.0 readiness

The chart has been pre-1.0 (`0.x`) since its first release; the gate for
`1.0.0` is that the multi-agent team story — not just the single-agent
path — is proven, not merely documented.

| Item | Status |
| --- | --- |
| Single agent, production-proven | ✅ done — real deployments with 15+ / 26+ day uptime |
| Pair collaboration (`@mention` handoff) | ✅ recipe shipped and proven live; 🔜 field-demo evidence not yet attached to [collaboration.md](collaboration.md) |
| Leader-orchestrated team (star topology, shared workspace) | ✅ recipe shipped, field-tested on an ephemeral kind cluster; 🔜 not yet proven on a persistent cluster |
| Chart extension points for team patterns (`extraVolumes`, `extraVolumeMounts`, `extraInitContainers`) | ✅ done — cover file-based credentials and one-time volume prep |
| CI coverage (per-scenario kind matrix, functional-change detection incl. appVersion bumps, docs-drift gate, signed releases) | ✅ done |
| EN/KO documentation parity | ✅ maintained as an ongoing discipline |
| Messaging platform coverage | Discord and Telegram are the v1.0 baseline; Slack and other platforms are explicitly **post-v1.0** (the same star topology applies once platform env vars are swapped) |
| Git-backed wiki vault (team knowledge curation) | ⏸️ design only ([teams.md](teams.md) § Team + wiki vault), not required for v1.0 |

## See also

- [Hermes teams](teams.md) — the ApplicationSet-based team pattern in detail.
- [Chart README](../charts/hermes-agent/README.md) — full values table and the
  `replicaCount` single-writer rationale.
