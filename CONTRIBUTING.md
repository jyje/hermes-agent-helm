# Contributing

## Branch model

| Branch | Purpose | CI |
|---|---|---|
| `dev` | Maintainer experimental / integration. | lint + docs-drift + template + kind `helm test` |
| `main` | Default branch & PR target; stable. Releases cut from here. | same as dev |
| _tags_ `vX.Y.Z` | The release itself — created by CI when the chart version changes. | publishes to GitHub Packages (OCI) |

No long-lived `rc`/`release` branches — a release is a tag/event.

## How to cut a release

Changesets is the source of the next SemVer decision. Each user-visible chart
change adds a Markdown entry under [`.changeset/`](.changeset/), naming this
private release manifest and its `patch`, `minor`, or `major` impact. The
manifest and `charts/hermes-agent/Chart.yaml` always receive the same resulting
version in the generated release PR; the manifest is never published to npm.

### Add a Changeset (recommended)

Run `pnpm changeset`, select `@jyje/hermes-agent-helm`, choose the chart's
SemVer impact, and write a concise user-facing summary. Commit that file with
the implementation PR. CI does not require a Changeset for CI-only, tooling,
or other unreleased maintenance work.

### Write an item that can become a release note

The YAML frontmatter is native Changesets data: keep it limited to package
names and `major`, `minor`, or `patch`. Categories are therefore recorded in
the Markdown summary, using this repository convention for its heading and
detail paragraph:

```md
Category(scope): Title

Concise user-facing detail.
```

Use `Feature`, `Fix`, `Security`, `Dependency`, `Documentation`, `Deprecated`,
or `Removed` for `Category`, and a short affected area such as `chart`,
`values`, `docs`, or `image` for `scope`. `Feature` and `Dependency` are
singular item categories; a release-note renderer can group them beneath
**Features** and **Dependencies**. For example:

```md
---
"@jyje/hermes-agent-helm": minor
---

Feature(docs): Documentation portal

Add chart-scoped install, values overlay, example, and reference pages.
```

Write the detail paragraph in imperative, user-facing language; do not repeat
`minor`, `major`, or `patch` in the summary. SemVer is native Changesets
frontmatter data; Category is a release-note convention and does not affect it.
GitHub attribution is not native Changesets data, so do not duplicate a
username in the summary; a custom release-note renderer can derive it from the
commit or pull request. See
[`.changeset/README.md`](.changeset/README.md) for the complete guide,
including SemVer selection and a fix example.

Rendered references stay compact: prefer the implementation PR as
`[#101](https://github.com/jyje/hermes-agent-helm/pull/101) (minor) [@jyje](https://github.com/jyje)`;
when there is no PR, use a linked short commit hash in the same position.

Pending Changesets remain on `main` until you manually run
[propose-release.yaml](.github/workflows/propose-release.yaml) from the Actions
tab. It opens or updates one release PR. Its custom version step:

- combines the pending patch/minor/major entries into one SemVer version;
- writes the corresponding `CHANGELOG.md` section;
- synchronizes `package.json`, `Chart.yaml`, Artifact Hub changes, chart docs,
  and versioned install examples.

Review the calculated version and generated notes, then merge the release PR.
If the release impact is wrong, edit or add the pending Changeset instead of
editing the generated chart version directly, then manually run the workflow
again to refresh the same release PR.

For a non-mutating local preview, run `make propose`. On a disposable release
branch, `make release-version` applies the same generated version step.

### What merging does

Once any of the above merges to `main`,
[release-chart.yaml](.github/workflows/release-chart.yaml) sees the new version, and if no
`vX.Y.Z` tag exists yet it creates the tag + GitHub Release (Changesets notes)
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
(`feat:`, `fix:`, `docs:`, `ci:`, `refactor:`, …) keep history readable.
Changeset summaries, rather than commit subjects, are the release changelog.

## CI validation

PRs and pushes run lint + an isolated **kind** install/test, and every release
is re-verified against the published, cosign-signed artifact.

See **[docs/reference/ci.md](docs/reference/ci.md)** for the full pipeline — the parallel
default / existingClaim test scenarios, the failover model pool, fork-PR
behavior, and the post-release verification.

## Local development environment

See **[docs/reference/local-development.md](docs/reference/local-development.md)** for:

- Setting up a local Kubernetes cluster (kind recommended; minikube and MicroK8s also covered)
- Port-forwarding a remote cluster agent for dev testing
- Configuring a Discord bot with the NVIDIA NIM provider and `hermes gateway`

## Local checks (run before pushing)

```bash
make lint        # helm lint
make template    # render manifests
make docs        # regenerate the chart README (helm-docs) — commit the result
make test        # install + helm test (needs a cluster/kind)
pnpm changeset   # add a release intent for a user-visible chart change
make propose     # preview the pending calculated version
```

CI fails if the chart README is out of date, so always `make docs` after editing
`values.yaml`.

See [AGENTS.md](AGENTS.md) for chart design principles.
