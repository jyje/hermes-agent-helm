# AGENTS.md

Guidance for agents working in this repo (`hermes-agent-helm`).

## What this is

A Helm chart (`charts/hermes-agent`) that runs **Hermes Agent**
(`nousresearch/hermes-agent`) on Kubernetes as a **Deployment or StatefulSet**
(`controller.type`), with `config.yaml` managed as a **ConfigMap** and `.env`
as a **Secret**.

## Design principles

- **Community-powered & publishable.** This is a community-maintained chart (not
  an official Nous Research release) targeting public distribution (Artifact
  Hub). Do **not** hard-code any single environment, provider, or endpoint into
  the chart defaults, README, or templates.
- **Lightweight by default.** Defaults assume small clusters (homelab /
  single-node / edge): modest `resources`, `replicaCount: 1`, small
  `persistence.size`. Users scale up via values; never raise defaults to fit a
  big environment.
- **Provider-agnostic.** Hermes supports many providers (openai, anthropic,
  google, openrouter, and any OpenAI-compatible endpoint). Chart defaults use a
  provider's **public** endpoint (e.g. `https://api.openai.com/v1`,
  `https://api.anthropic.com/v1`) - never a specific in-cluster proxy.
- **Connecting to LiteLLM (or any proxy) is a usage choice, not a chart fact.**
  Configure it via values overrides; don't bake it into the chart or docs.
- **Don't frame docs by what the chart is *not*.** State what it does; omit the
  rest (e.g. don't advertise "CRD-free").
- **No Namespace resource.** The chart never renders a `Namespace`; the target
  namespace is selected only via the CLI (`kubectl`, `helm --namespace` /
  `--create-namespace`). Don't reintroduce a `namespace.*` value.
- **local terminal backend only.** `config.terminal.backend: local` - the agent
  runs commands inside the pod (pod = sandbox). Never default to / wire up the
  `docker` backend in-cluster (needs a Docker daemon/socket; absent on
  containerd, security risk). Document it as unsupported, don't add socket mounts.
- **Image tags are semver** (`vX.Y.Z`, e.g. `v0.22.2`) since October 2026.
  Up to `v2026.9.24`, upstream published date-based tags (`vYYYY.M.D`); those
  remain on Docker Hub but no new ones appear. Track only plain `vX.Y.Z` tags,
  never `rc.N-vX.Y.Z`, `-desktop`, `-amd64`/`-arm64`, `stable` or `latest`.
  `sort -V` ranks a date tag above any semver tag, so treat date tags as older
  when comparing (see `cron-fetch-image.yaml`). Image is multi-arch
  (amd64 + arm64). Always use the `v` prefix (`v0.22.2`, not `0.22.2`).
- **The login init container's Python follows Hermes.** `auth.deviceFlow.image.tag`
  (`python:<minor>-slim`) is set by `cron-fetch-image.yaml` from the Python pin in
  the tagged upstream `pm/lock.json` (3.14 today), so the login interpreter
  matches the one Hermes runs. Never bump it by hand or merge a Dependabot
  python bump: `.github/dependabot.yaml` ignores `python` 3.15 and above, and the
  image-bump PR moves the tag itself when Hermes does.
- **No inbound API.** `hermes gateway run` is outbound (messaging platforms) and
  the image is s6-supervised - so don't set `command`/`args` (use the image
  entrypoint), don't add liveness/readiness tied to a listening port by default,
  and don't create an access Service by default. The only HTTP surface is the
  optional management `dashboard` (port 9119, sensitive - exposes API keys).
- **Ship a Helm test.** `templates/tests/` Job with `helm.sh/hook: test`,
  gated by `tests.enabled` (default true), runs a `hermes doctor` style check
  (hermes CLI + docker availability). Run via `helm test`.
- **config/.env are partial overrides, never full replacements.** Hermes reads
  `$HERMES_HOME/config.yaml` + env as overrides on top of its version-specific
  built-in defaults (precedence: CLI > config.yaml > .env > defaults). `config`
  is seeded into `HERMES_HOME` (the PVC) by an init container - NOT mounted
  read-only - because Hermes writes to its home at runtime. `bootstrap.overwrite`
  controls re-seed (true) vs seed-if-absent (false). Secrets go in via `envFrom`
  (env wins over config.yaml), not a `.env` file. Never try to reproduce the
  full upstream config in the chart.
- **Environment-specific config lives in `charts/hermes-agent/values-*.yaml`**
  (ready-to-adapt examples: every built-in provider, Discord/Telegram combos,
  and a custom OpenAI-compatible provider such as LiteLLM in/out of cluster;
  see the chart README's "More examples" table) and in `examples/argocd/`
  (the GitOps/SealedSecret + `extraEnvFrom` + persistence pattern). Per-environment
  values do not belong in the chart defaults.

## Workflow

- **Feature documentation is a release gate.** Document new and changed
  user-facing behavior in every supported language (currently en, ko, ja, zh).
  For fast iteration, an implementation PR may explicitly defer localization,
  update only the canonical English docs, and link the remaining work. Before
  proposing or merging a release that includes the feature, merge and verify
  its docs in every supported locale. English fallback does not count as
  translation. This does not require backfilling unrelated legacy pages.
  See `CONTRIBUTING.md` for translation provenance, legacy coverage, and the
  English-only contributing guide and generated Values table exceptions.
- **Changeset release items are a contributor contract.** For every
  user-visible chart change - including a new `values-*.yaml` example, a new
  ArgoCD example, or docs a user reads, not just template/default changes -
  add one `.changeset/*.md` item before opening the PR. Its frontmatter
  contains only the package and `major`/`minor`/`patch`; its first summary line
  follows `Category(scope): Title` using the approved categories in
  `.changeset/README.md`; after a blank line, write the user-facing detail.
  The category is Markdown convention, not native Changesets frontmatter, and
  does not determine SemVer. Do not add a Changeset for CI, release automation,
  or other unreleased tooling, and do not duplicate a GitHub username in the
  summary: a custom release-note renderer resolves attribution from repository
  history.
- Regenerate chart docs with **helm-docs** after any `values.yaml` change:
  `make docs` (uses `charts/hermes-agent/README.md.gotmpl` + `# --` annotations).
  Update affected README prose in all supported locales by hand, or track
  those translations as deferred work under the release gate above. Keep the
  generated Values table in English in every locale.
- **Never delete or rename a README-referenced image under `docs/images/`.**
  READMEs load them from `main` through raw URLs, so every published chart
  version depends on them; add a new file instead. See CONTRIBUTING.md
  "README images".
- Validate with `make lint` and `make template`.
- Package for release with `make package` (runs docs + lint, then
  `helm package`). `Chart.yaml` carries `artifacthub.io/*` annotations for the
  eventual Artifact Hub publish.
- For feature-branch remote evidence, use
  [`.claude/skills/implementation-validation-cycle/SKILL.md`](.claude/skills/implementation-validation-cycle/SKILL.md).
  It verifies the full implementation SHA before creating an orphan
  `test/<scope>` branch, distinguishes implementation from harness failures,
  records safe PR evidence, and only then cleans up the test branch.
- **Promoting a temporary validation to permanent CI is a separate change.**
  If an orphan-branch check (or anything discovered during review) guards a
  reusable invariant, runs on deterministic input (or degrades gracefully
  like the NIM pattern), needs no new secret unavailable to fork PRs (or
  fails closed when one's missing), defaults to the `lint` trigger unless it
  genuinely needs a live cluster, and stays cheap, file a separate
  project-internal issue/PR for it (no Changeset) instead of folding the
  assertion into the feature PR that motivated it - see CONTRIBUTING.md
  "Promoting a validation to permanent CI" for the full criteria and their
  exceptions. Bundle it into the feature PR only when skipping it would let
  that same PR reintroduce the regression the check exists to catch.

## Scope

- Resources: Deployment or StatefulSet (`controller.type`), ConfigMap, Secret,
  Services, ServiceAccount, PVC. No operator / CRD mode.
