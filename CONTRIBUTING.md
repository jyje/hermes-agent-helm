# Contributing

## Branch model

| Branch | Purpose | CI |
|---|---|---|
| `dev` | Maintainer experimental / integration. | lint + docs-drift + template + kind `helm test` |
| `main` | Default branch & PR target; stable. Releases cut from here. | same as dev |
| _tags_ `vX.Y.Z` | The release itself — created by CI when the chart version changes. | publishes to GitHub Packages (OCI) |

No long-lived `rc`/`release` branches — a release is a tag/event.

## How to cut a release

The chart **`version` in `charts/hermes-agent-helm/Chart.yaml` is the source of truth**.

1. Bump `version` (e.g. `0.1.0` → `0.2.0`) following semver.
2. Refresh the changelog: `make changelog` (git-cliff) and commit `CHANGELOG.md`
   together with the version bump.
3. Merge to `main`. CI ([release.yml](.github/workflows/release.yml)) sees the
   new version, and if no `vX.Y.Z` tag exists yet it:
   - creates the tag + GitHub Release (notes from git-cliff), and
   - packages and pushes the chart to `oci://ghcr.io/<owner>/charts`.

Commits that touch `Chart.yaml` for other reasons (e.g. `appVersion`,
description) are safe — the tag-existence guard makes them no-ops.

> `appVersion` tracks the upstream Hermes image (date-based, e.g. `v2026.6.5`)
> and is bumped manually; only the chart `version` drives releases.

### Triggering a release

- **Manually**: run [release.yml](.github/workflows/release.yml) via
  `workflow_dispatch` (Actions tab → "release" → "Run workflow"). Useful for
  re-running a publish after a failed step.
- **`/version vX.Y.Z` PR comment**: a maintainer (OWNER/MEMBER/COLLABORATOR)
  can comment `/version vX.Y.Z` on a PR. [version-comment.yml](.github/workflows/version-comment.yml)
  bumps `charts/hermes-agent-helm/Chart.yaml` `version` to `X.Y.Z`, regenerates
  `CHANGELOG.md` (git-cliff), and pushes that commit to the PR branch. Merging
  the PR to `main` then triggers `release.yml` as usual.

## Conventional Commits (recommended)

Not enforced, but [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `ci:`, `refactor:`, …) make the git-cliff changelog
clean and grouped. `chore(release):` commits are skipped in the changelog.

## CI validation

PRs and pushes run an isolated **kind** install + `helm test` (the `hermes
doctor` Job). If a `GOOGLE_API_KEY` repository secret is set, CI additionally
does a real model round-trip via Google AI Studio (Gemini) — see
[ci.yml](.github/workflows/ci.yml). Fork PRs don't receive the secret, so they
fall back to doctor-only (safe).

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
