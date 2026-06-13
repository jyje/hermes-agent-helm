# AGENTS.md

Guidance for agents working in this repo (`hermes-helm`).

## What this is

A Helm chart (`charts/hermes-agent`) that runs **Hermes Agent**
(`nousresearch/hermes-agent`) on Kubernetes as a **StatefulSet**, with
`config.yaml` managed as a **ConfigMap** and `.env` as a **Secret**.

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
  `https://api.anthropic.com/v1`) — never a specific in-cluster proxy.
- **Connecting to LiteLLM (or any proxy) is a usage choice, not a chart fact.**
  Configure it via values overrides; don't bake it into the chart or docs.
- **Don't frame docs by what the chart is *not*.** State what it does; omit the
  rest (e.g. don't advertise "CRD-free").
- **No Namespace resource.** The chart never renders a `Namespace`; the target
  namespace is selected only via the CLI (`kubectl`, `helm --namespace` /
  `--create-namespace`). Don't reintroduce a `namespace.*` value.
- **local terminal backend only.** `config.terminal.backend: local` — the agent
  runs commands inside the pod (pod = sandbox). Never default to / wire up the
  `docker` backend in-cluster (needs a Docker daemon/socket; absent on
  containerd, security risk). Document it as unsupported, don't add socket mounts.
- **Image tags are date-based** (`vYYYY.M.D`, e.g. `v2026.6.5` == Hermes v0.16.0)
  — there is no semver tag. Image is multi-arch (amd64 + arm64). Don't invent
  semver tags like `0.8.0`.
- **No inbound API.** `hermes gateway run` is outbound (messaging platforms) and
  the image is s6-supervised — so don't set `command`/`args` (use the image
  entrypoint), don't add liveness/readiness tied to a listening port by default,
  and don't create an access Service by default. The only HTTP surface is the
  optional management `dashboard` (port 9119, sensitive — exposes API keys).
- **Ship a Helm test.** `templates/tests/` Job with `helm.sh/hook: test`,
  gated by `tests.enabled` (default true), runs a `hermes doctor` style check
  (hermes CLI + docker availability). Run via `helm test`.
- **config/.env are partial overrides, never full replacements.** Hermes reads
  `$HERMES_HOME/config.yaml` + env as overrides on top of its version-specific
  built-in defaults (precedence: CLI > config.yaml > .env > defaults). `config`
  is seeded into `HERMES_HOME` (the PVC) by an init container — NOT mounted
  read-only — because Hermes writes to its home at runtime. `bootstrap.overwrite`
  controls re-seed (true) vs seed-if-absent (false). Secrets go in via `envFrom`
  (env wins over config.yaml), not a `.env` file. Never try to reproduce the
  full upstream config in the chart.
- **Environment-specific config lives in `charts/hermes-agent/values.example.yaml`**
  (jyje's Raspberry Pi MicroK8s cluster: LiteLLM in `ollama-system`, deployed to
  the `hermes-agent` namespace,
  `subdir-usb` NFS StorageClass). Per-environment values do not belong in the
  chart defaults.

## Workflow

- Regenerate chart docs with **helm-docs** after any `values.yaml` change:
  `make docs` (uses `charts/hermes-agent/README.md.gotmpl` + `# --` annotations).
- Validate with `make lint` and `make template`.
- Package for release with `make package` (runs docs + lint, then
  `helm package`). `Chart.yaml` carries `artifacthub.io/*` annotations for the
  eventual Artifact Hub publish.

## Scope

- Resources: StatefulSet, ConfigMap, Secret, Services, ServiceAccount,
  optional Namespace. No operator / CRD mode.
