# Contributing

## Branch model

| Branch | Purpose | CI |
|---|---|---|
| `dev` | Maintainer experimental / integration. | lint + docs-drift + template + kind `helm test` |
| `main` | Default branch & PR target; stable. Releases cut from here. | same as dev |
| _tags_ `vX.Y.Z` | The release itself — created by CI when the chart version changes. | publishes to GitHub Packages (OCI) |

No long-lived `rc`/`release` branches — a release is a tag/event.

## How to cut a release

The chart **`version` in `charts/hermes-agent/Chart.yaml` is the source of truth**.
A release is just a reviewed PR that bumps that version; **merging it to `main`
is what ships**. There are three ways to produce that bump — pick one:

### 1. AI-assisted proposal (recommended)

Run [propose-release.yaml](.github/workflows/propose-release.yaml) via
`workflow_dispatch` (Actions tab → "📋 propose-release" → "Run workflow"). It:

- diffs `main` against the last release tag and builds the changelog
  **deterministically** (git / git-cliff) — no AI in this part;
- asks **NVIDIA NIM** to recommend a semver bump and write a summary (falls
  back to a transparent heuristic when no `NVIDIA_API_KEY` secret is present);
- bumps `Chart.yaml` + refreshes `CHANGELOG.md`, and opens/updates a single
  **release PR** (branch `release/next`, idempotent) that credits every commit
  and PR author and includes step-by-step ship instructions.

Review it, adjust the version if you disagree with the recommendation (edit
`Chart.yaml` on the branch, or comment `/version vX.Y.Z`), then merge.

> The AI only **advises**. The changelog, diff, contributors, and the version
> arithmetic are all deterministic; you make the final call by merging.

Dry-run the same proposal locally (no PR, no push) with `make propose`.

If more commits land on `main` while the proposal PR is open, comment
`/rescan` on it. [command-rescan-changes.yaml](.github/workflows/command-rescan-changes.yaml)
re-runs `propose-release.yaml`, refreshing the changelog, AI advice, and
version recommendation in place.

### 2. `/version vX.Y.Z` PR comment

A maintainer (OWNER/MEMBER/COLLABORATOR) comments `/version vX.Y.Z` on the
release proposal PR. [command-version-change.yaml](.github/workflows/command-version-change.yaml)
re-runs `propose-release.yaml` with that exact version, which regenerates the
whole proposal in place — `Chart.yaml`, `CHANGELOG.md`, chart docs, and the PR
body (showing the override and the AI's original suggestion for comparison).

### 3. Manual bump

Bump `version` in `Chart.yaml`, run `make changelog`, commit both, and open a
PR yourself.

### What merging does

Once any of the above merges to `main`,
[release-chart.yaml](.github/workflows/release-chart.yaml) sees the new version, and if no
`vX.Y.Z` tag exists yet it creates the tag + GitHub Release (git-cliff notes)
and publishes the chart to **both**:

- `oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent` (OCI artifact), and
- the classic Helm repository at `https://<owner>.github.io/hermes-agent-helm`
  (published to the `gh-pages` branch, `index.yaml` merged with prior releases).

Commits that touch `Chart.yaml` for other reasons (e.g. `appVersion`,
description) are safe — the tag-existence guard makes them no-ops.

> `appVersion` tracks the upstream Hermes image (date-based, e.g. `v2026.6.5`)
> and is bumped manually; only the chart `version` drives releases.

## Conventional Commits (recommended)

Not enforced, but [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `ci:`, `refactor:`, …) make the git-cliff changelog
clean and grouped. `chore(release):` commits are skipped in the changelog.

## CI validation

PRs and pushes run lint + an isolated **kind** install/test, and every release
is re-verified against the published, cosign-signed artifact.

See **[docs/ci.md](docs/ci.md)** for the full pipeline — the parallel
default / existingClaim test scenarios, the failover model pool, fork-PR
behavior, and the post-release verification.

## Local development environment

See **[docs/local-dev.md](docs/local-dev.md)** for:

- Setting up a local Kubernetes cluster (kind recommended; minikube and MicroK8s also covered)
- Port-forwarding a remote cluster agent for dev testing
- Configuring a Discord bot with the NVIDIA NIM provider and `hermes gateway`

## Local checks (run before pushing)

```bash
make lint        # helm lint
make template    # render manifests
make docs        # regenerate the chart README (helm-docs) — commit the result
make test        # install + helm test (needs a cluster/kind)
make changelog   # regenerate CHANGELOG.md (when bumping version)
```

CI fails if the chart README is out of date, so always `make docs` after editing
`values.yaml`.

See [AGENTS.md](AGENTS.md) for chart design principles.
