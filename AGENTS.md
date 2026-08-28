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
- **Image tags are date-based** (`vYYYY.M.D`, e.g. `v2026.6.5` == Hermes v0.16.0)
  - there is no semver tag. Image is multi-arch (amd64 + arm64). Don't invent
  semver tags like `0.8.0`.
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

- **Documentation locales have explicit scopes.** Korean (`ko`) has full
  parity: every English `README.md` has a `README-ko.md` twin at the repo root
  and under `charts/hermes-agent/`, and every English page under `docs/` has
  its `docs/ko/` twin. When you edit either side, apply the equivalent edit to
  its twin in the same change. Other locales are entry-path scoped, not
  full-tree mirrors: update only their translated entry pages, and do not
  require a translation for an unrelated English or Korean page. Their entry
  landing page must tell readers that the remaining sections use English.
  Record the source path and full English commit SHA in each translated page's
  front matter. See `CONTRIBUTING.md` for the entry-path list and notice
  wording. The chart README's auto-generated `## Values` table stays English
  in every locale so it cannot drift from `values.yaml`.
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
  This only updates `README.md`; if the change affects prose covered in
  `README-ko.md` (not just the values table), update that by hand too. Update
  an entry-scoped locale only when the changed page is in that locale's entry
  path.
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
