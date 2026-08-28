# Contributing

## Repository layout

```text
.
├── charts/
│   ├── hermes-agent/          # the Helm chart (see its README)
│   │   └── values-*.yaml      # ready-to-adapt provider/messenger examples
│   └── hermes-operator/       # ⏸️ not started: Agent/AgentTeam CRD operator
├── examples/
│   ├── helm/                  # install via Git or OCI + publish guide
│   └── argocd/                # ArgoCD Application examples + GitOps pattern
├── docs/                      # deeper guides (teams, collaboration, roadmap)
├── .github/workflows/         # CI checks + tag-driven release to ghcr OCI
├── .changeset/                # entries queued for the next release version
├── CONTRIBUTING.md            # branch model + release-on-version-bump
├── AGENTS.md                  # design principles & workflow for contributors
└── Makefile                   # docs / lint / template / install / test
```

## CI/CD

- **Chart pull requests** run [validate-chart.yaml](.github/workflows/validate-chart.yaml):
  `helm lint`, `helm template`, a chart-docs drift check, and a full install +
  test on an ephemeral **kind** cluster (real `hermes chat` round-trip when an
  `NVIDIA_API_KEY` secret is available).
- **Releases are Changesets-driven, not tag-push-driven.** A user-visible chart
  change adds a `patch`, `minor`, or `major` entry under [`.changeset/`](.changeset/).
  When you are ready to release, manually run
  [propose-release.yaml](.github/workflows/propose-release.yaml) to combine pending
  entries into one reviewable release PR, write its `CHANGELOG.md` notes,
  and synchronize the private release manifest with `Chart.yaml`, Artifact Hub
  metadata, chart docs, and versioned examples. Review and merge that PR; then
  [release-chart.yaml](.github/workflows/release-chart.yaml) tags `vX.Y.Z`, writes the GitHub
  Release, and publishes the chart to `oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent`.

So: lint + test gate every change; the *release* itself is just a normal
reviewed PR (the version bump) - the pending Changesets decide its SemVer,
merging is what ships.

The two flows above are the ones you hit as a contributor. Every workflow,
including scheduled upstream image tracking and post-release verification, is
documented in [docs/contributing/ci.md](docs/contributing/ci.md) - keep that
page as the single source for workflow details rather than restating them here.

## Documentation locales

Korean (`ko`) is the full-parity locale. Every English docs page and the root
and chart READMEs have Korean twins. Keep those pairs equivalent in the same
change.

New locales are deliberately smaller. They translate only the entry path and
fall back to English elsewhere. This keeps security and operational guidance
accurate until a native-speaking maintainer can maintain a broader translation.
Do not expand a locale's scope incidentally in an unrelated docs PR.

| Entry page | Localized form |
| --- | --- |
| Root README | `README-<locale>.md`, included by `docs/<locale>/index.md` |
| Chart README | `charts/hermes-agent/README-<locale>.md`, included by `docs/<locale>/chart/index.md` |
| Getting started | `docs/<locale>/getting-started/index.md` and `install.md` |
| Chart landing | `docs/<locale>/chart/hermes-agent/index.md` |
| Section landings | `docs/<locale>/advanced/index.md` and `about/index.md` |
| Contributing | Keep the English `CONTRIBUTING.md` source |

Add this front matter to every translated page. Use the full SHA of the
English source commit used for the translation, then update it whenever the
translation is refreshed:

```yaml
translation_source:
  path: README.md
  commit: 0123456789abcdef0123456789abcdef01234567
```

Every entry-scoped locale landing page must also show this reader-facing
notice, translated into that locale:

> This locale translates the entry path. Sections not available in this
> language use English.

The generated `## Values` table in every chart README stays English. It is
generated from `values.yaml`, so translating a copy would create a second,
drifting reference.

## Branch model

| Branch | Purpose | CI |
|---|---|---|
| `dev` | Maintainer experimental / integration. | lint + docs-drift + template + kind `helm test` |
| `main` | Default branch & PR target; stable. Releases cut from here. | same as dev |
| `<category>/<scope>` | One scoped implementation, `category` matching its Conventional Commits type (`feat`, `fix`, `docs`, `chore`, ...). Keep validation-only workflow changes out of this branch. | local verification before review |
| `test/<scope>` | Orphan branch containing only a remote-validation workflow. Keep it while the validation loop is active. | checks out a pinned implementation SHA; delete after successful evidence is recorded |
| _tags_ `vX.Y.Z` | The release itself: created by CI when the chart version changes. | publishes to GitHub Packages (OCI) |

No long-lived `rc`/`release` branches - a release is a tag/event.

## Implementation and validation lifecycle

Keep implementation and remote-validation evidence separate:

1. Create a named worktree and a `<category>/<scope>` branch for one
   implementation, `category` matching its Conventional Commits type
   (`feat/`, `fix/`, `docs/`, ...).
2. Run local checks first: after a values change, run `make docs` to
   regenerate `charts/hermes-agent/README.md`, and update `README-ko.md`
   manually when its content is affected. Then run `make lint`,
   `make template`, packaging where relevant, an isolated kind install,
   rollout check, and the chart test Job.
3. Review the diff and local evidence. Commit only after explicit approval.
4. Run the repository's
   [`implementation-validation-cycle`](.claude/skills/implementation-validation-cycle/SKILL.md)
   skill for the orphan `test/<feat-scope>` branch, remote evidence, failure
   classification, PR comment, and cleanup. It pins the exact verified
   implementation SHA and keeps validation-only workflow YAML out of the
   implementation branch.
5. If the branch closes a tracked issue, name it in the PR description with a
   GitHub closing keyword (`Closes #123`, `Fixes #123`, `Resolves #123`) so
   merging closes it automatically. #161 and #162 stayed open after their
   implementing PRs (#182, #183) merged because this step was skipped.
6. The only merge path remains `<category>/<scope>` to `main`, and it still
   requires a separate approval.

## How to cut a release

Changesets is the source of the next SemVer decision. Each user-visible chart
change adds a Markdown entry under [`.changeset/`](.changeset/), naming this
private release manifest and its `patch`, `minor`, or `major` impact. The
manifest and `charts/hermes-agent/Chart.yaml` always receive the same resulting
version in the generated release PR; the manifest is never published to npm.

### Add a Changeset (required for user-visible changes)

Every user-visible chart change - a new `values-*.yaml` example, a new
ArgoCD example, a `values.yaml` default change, template/behavior changes,
docs the user reads - needs a Changeset. This includes additions that look
"just" like an example or doc file: if it ships in the chart or its
documented examples, it's user-visible. Run `pnpm changeset`, select
`@jyje/hermes-agent-helm`, choose the chart's SemVer impact, and write a
concise user-facing summary. Commit that file with the implementation PR.
CI does not enforce this, so review your own diff before opening the PR.
The only exemption is CI-only, tooling, or other unreleased maintenance
work (workflow YAML, scripts, this contributing guide) that ships nothing
a chart user would see.

### Deciding whether Documentation or CI work needs a Changeset

`Documentation` and CI/tooling work are the two kinds most often
miscategorized, because both can be either **chart-facing** (a chart user
sees it) or **project-internal** (only a contributor does). This decides
Changeset eligibility only - it is not a new PR-title or commit-subject
format; those keep following
[Conventional Commits](#conventional-commits-recommended) as already
described further down, and `scope` inside an actual Changeset summary keeps
the free-form meaning defined in
[Write an item that can become a release note](#write-an-item-that-can-become-a-release-note)
below (`chart`, `values`, `docs`, `image`, ...), not this chart/project axis.

| Kind of work | Chart-facing | Project-internal |
|---|---|---|
| Documentation | README, `values-*.yaml` comments, `docs/` - **needs a Changeset** | This file, `AGENTS.md`, other contributor guides - **no Changeset** |
| CI / tooling | A workflow or script change that alters what a chart user receives (rare - e.g. the docs-generation step itself) - **needs a Changeset** | CI/tooling maintenance with no effect on the shipped chart (a new lint assertion, a workflow refactor) - **no Changeset** |

If in doubt whether something is user-visible, it almost certainly is
chart-facing and needs one.

### Promoting a validation to permanent CI

The [implementation-validation-cycle](.claude/skills/implementation-validation-cycle/SKILL.md)
skill's orphan `test/<scope>` branch exists to validate one PR, then gets
deleted - it is not a place to leave a check you want to keep running forever.
When a validation step turns out to guard a standing invariant, decide
whether to promote it into `validate-chart.yaml` using these criteria:

- **Reusable invariant** - does it assert something that should always hold
  (e.g. "an unset value falls back to X"), not just a fact about this one PR's
  diff?
- **Deterministic input** - does it run on fixed local input (`helm template`
  + `yq`/`grep`) rather than a live external call? A live call is acceptable
  only if it already degrades gracefully with no secret configured, matching
  this repo's own NVIDIA NIM pattern.
- **Secret safety** - does it avoid requiring a new secret unavailable to fork
  PRs, or fail closed (skip, not error) when one is missing?
- **Trigger** - does it belong in the `lint` job (every PR, cheap, no
  cluster) or the `test` job (kind-based, gated on
  `needs.changes.outputs.functional`)? Default to `lint` unless it genuinely
  needs a live cluster.
- **Runtime cost** - does it add seconds, not minutes, to every PR's feedback
  loop? A slow check belongs in `test`'s existing matrix, not a new always-on
  step.

If it passes all five, file a **separate CI/tooling issue and PR**
(project-internal, no Changeset) rather than folding the new assertion into
the feature PR that motivated it - the feature PR's own diff should stay
scoped to the feature.
The only exception is when the feature PR would otherwise reintroduce the
exact regression the validation guards against before the follow-up lands -
in that narrow case, add the assertion directly to the feature PR instead of
leaving a known gap open.

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
- the Helm Repository at `https://<owner>.github.io/hermes-agent-helm`
  (published to the `gh-pages` branch, `index.yaml` merged with prior releases).

Commits that touch `Chart.yaml` for other reasons (e.g. `appVersion`,
description) are safe - the tag-existence guard makes them no-ops.

> `appVersion` tracks the upstream Hermes image (date-based, e.g. `v2026.6.5`)
> and is bumped manually; only the chart `version` drives releases.

## Conventional Commits (recommended)

Not enforced, but [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `ci:`, `refactor:`, …) keep history readable.
Changeset summaries, rather than commit subjects, are the release changelog.

## CI validation

Chart pull requests run lint + an isolated **kind** install/test, and every
release is re-verified against the published, cosign-signed artifact.

See **[docs/contributing/ci.md](docs/contributing/ci.md)** for the full pipeline - the parallel
default / existingClaim test scenarios, the failover model pool, fork-PR
behavior, and the post-release verification.

## Local development environment

See **[docs/contributing/local-development.md](docs/contributing/local-development.md)** for:

- Setting up a local Kubernetes cluster (kind recommended; minikube and MicroK8s also covered)
- Port-forwarding a remote cluster agent for dev testing
- Configuring a Discord bot with the NVIDIA NIM provider and `hermes gateway`

## Local checks (run before pushing)

```bash
make lint        # helm lint
make template    # render manifests
make docs        # regenerate the English chart README (helm-docs) - commit the result
make test        # install + helm test (needs a cluster/kind)
pnpm changeset   # add a release intent for a user-visible chart change
make propose     # preview the pending calculated version
```

CI reruns helm-docs and fails if `charts/hermes-agent/README.md` is out of
date. It does not generate `README-ko.md`, so keep the Korean twin in sync
manually after editing `values.yaml`. An entry-scoped locale only needs a
manual update when the affected page belongs to its entry path.

See [AGENTS.md](AGENTS.md) for chart design principles.
