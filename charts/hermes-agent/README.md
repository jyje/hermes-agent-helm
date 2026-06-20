<div align="center">

# hermes-agent-helm/hermes-agent

<p>
  <img height="96" src="https://helm.sh/img/boat.svg" alt="Helm"/>
  &nbsp;&nbsp;<sup><b> ➕ </b></sup>&nbsp;&nbsp;
  <img height="96" src="https://hermes-agent.nousresearch.com/docs/img/logo.png" alt="Hermes Agent"/>
</p>

</div>

👩🏻‍💻 A Helm chart to run Hermes Agent on Kubernetes, community-powered, lightweight

Run Hermes Agent — a multi-provider LLM agent framework — on Kubernetes. Configure any provider Hermes supports (OpenAI, Anthropic, Gemini, OpenRouter, NVIDIA, or any OpenAI-compatible proxy such as LiteLLM/vLLM) entirely via values.yaml, with a built-in helm test health check.

![Version: 0.3.0](https://img.shields.io/badge/Version-0.3.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v2026.6.19](https://img.shields.io/badge/AppVersion-v2026.6.19-informational?style=flat-square)

## Overview

Run [Hermes Agent](https://github.com/NousResearch/hermes-agent) on Kubernetes.
It deploys:

- a **Deployment** (default) or **StatefulSet** (`controller.type`), single
  replica with persistent `HERMES_HOME`, running the image's s6-supervised
  gateway
- a **ConfigMap** holding the partial `config.yaml`
- a **Secret** holding the `.env` (injected via `envFrom`)
- for `controller.type=statefulset`: a headless Service for DNS/governance
  (no inbound port — the gateway is outbound); for `deployment`: a standalone
  PVC instead. Either way, an **optional** ClusterIP Service for the dashboard,
  and an **optional** Ingress in front of it (`ingress.enabled`)
- a **Helm test** Job (`helm test`) that runs a `hermes doctor` style check

Hermes supports many LLM providers via **built-in provider keys**
(`openai-api`, `anthropic`, `gemini`, `openrouter`, `nvidia`, `deepseek`,
`lmstudio`, …). For an **OpenAI-compatible proxy** (LiteLLM, vLLM, LM Studio),
register it under `config.providers` and reference it by key. The chart is fully
driven by `values.yaml` — point it at a hosted API or an in-cluster proxy.

> The provider key `openai` is **not** valid in Hermes (it aliases to
> OpenRouter). Use `openai-api` for api.openai.com, or a custom provider for a
> proxy — see `values-litellm.yaml` / `values-litellm-k8s.yaml` in
> ["More examples"](#more-examples).

The agent's command execution uses the **`local` backend** (commands run inside
the pod; the pod is the sandbox). The `docker` backend is intentionally **not
supported in-cluster** — it requires a Docker daemon/socket, absent on
containerd clusters (MicroK8s / Raspberry Pi) and a security risk to mount.

> Image tags are **date-based** (e.g. `v2026.6.5` == Hermes v0.16.0); the image
> is multi-arch (amd64 + arm64), so it runs on Raspberry Pi clusters.

> **Scaling note.** Hermes is a single-instance personal agent, so this chart
> pins `replicaCount: 1` and there is no multi-replica mode (see the
> `replicaCount` note in the [values table](#values)). To grow, scale *up* (more
> `resources`, larger `persistence.size`) — and when one agent isn't enough, run
> several instances and group them into a **team** that shares one gateway
> channel. See [Hermes teams](../../docs/teams.md).

## Install

```bash
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

The chart ships a placeholder `OPENAI_API_KEY`; override it (and `config.model`)
for your provider at install/upgrade time, or supply a values file.

> Tip: using a release name equal to the chart name (`hermes-agent`) keeps
> resource names clean (`hermes-agent-0`) instead of doubling the prefix
> (`hermes-agent-hermes-agent-0`). Or set `fullnameOverride`.

### Install options: LLM provider

This is the main thing you configure at install time — *which* LLM backend
Hermes talks to. (For chat platforms, see
[Messenger integrations](#messenger-integrations-telegram--discord) below.)

- **Built-in provider** — set `config.model.provider` to one of Hermes'
  built-in keys (`openai-api`, `anthropic`, `gemini`, `openrouter`, `nvidia`,
  `deepseek`, `lmstudio`, …) and `config.model.default` to a model id for that
  provider. Supply the matching key under `env` (`OPENAI_API_KEY`,
  `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `NVIDIA_API_KEY`, …).

  ```bash
  # OpenAI
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=openai-api \
    --set-string config.model.default=gpt-4o-mini \
    --set-string env.OPENAI_API_KEY='sk-...' --wait

  # Gemini
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=gemini \
    --set-string config.model.default=gemini-2.5-flash \
    --set-string env.GOOGLE_API_KEY='<your-key>' \
    --set-string env.OPENAI_API_KEY=unused --wait

  # NVIDIA NIM (this is the provider CI exercises end-to-end)
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=nvidia \
    --set-string config.model.default=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning \
    --set-string env.NVIDIA_API_KEY='nvapi-...' \
    --set-string env.OPENAI_API_KEY=unused --wait
  ```

- **Custom OpenAI-compatible provider** (LiteLLM, vLLM, LM Studio, …) — register
  it under `config.providers.<id>` (`base_url`, `key_env`) and point
  `config.model.provider` at that `<id>`. See `values-litellm.yaml` (remote
  proxy) or `values-litellm-k8s.yaml` (in-cluster) in
  ["More examples"](#more-examples).

### Messenger integrations (Telegram / Discord)

`hermes gateway run` (the workload's command) connects whatever chat platforms
it finds **credentials** for — so wiring a messenger is just a matter of
supplying its bot token. The token is sensitive, so put it under `.Values.env`
(rendered into the Secret); the non-secret knobs (allowed users, home channel)
can go under `.Values.extraEnv` (plain env). Setting the token is enough to
**auto-enable** the platform — no `config.yaml` change required.

> **Verification status:** the chart renders the right Secret/env and the agent
> picks the platform up. On trusted CI runs where the `DISCORD_BOT_TOKEN` and
> `DISCORD_HOME_CHANNEL` secrets are configured, CI does a full live
> round-trip — `hermes send` to that channel, then reads the channel back via
> the Discord API to confirm the message arrived — and **fails if it can't be
> verified** (the bot needs *View Channel* + *Read Message History*). Fork PRs
> skip it since secrets aren't exposed. Telegram is still placeholder-only.
> Provide a real bot token to try either in your own cluster.

- **Discord** — create a bot at the
  [Discord Developer Portal](https://discord.com/developers/applications),
  enable the **Message Content Intent**, and invite it to your server.

  ```bash
  helm upgrade --install hermes-agent ./charts/hermes-agent -n hermes-agent --create-namespace \
    --set-string config.model.provider=nvidia \
    --set-string config.model.default=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning \
    --set-string env.NVIDIA_API_KEY='nvapi-...' \
    --set-string env.OPENAI_API_KEY=unused \
    --set-string env.DISCORD_BOT_TOKEN='<bot-token>' --wait
  ```

  Optional non-secret knobs (via `extraEnv`, or `--set`):

  | env var | meaning |
  | --- | --- |
  | `DISCORD_ALLOWED_USERS` | comma-separated user IDs allowed to talk to the bot |
  | `DISCORD_ALLOW_ALL_USERS` | `true` to allow anyone (dev only) |
  | `DISCORD_HOME_CHANNEL` | channel ID for cron / notification delivery |
  | `DISCORD_HOME_CHANNEL_NAME` | display name for that home channel |

- **Telegram** — create a bot via [@BotFather](https://t.me/BotFather) and set
  `env.TELEGRAM_BOT_TOKEN` (optionally `TELEGRAM_HOME_CHANNEL`,
  `TELEGRAM_ALLOWED_USERS` via `extraEnv`).

See `values-anthropic-and-discord.yaml` / `values-openai-and-telegram.yaml` in
["More examples"](#more-examples) for copy-pasteable messenger blocks.

> Want **several agents in one shared channel**? Point each instance at the same
> `DISCORD_HOME_CHANNEL` (different `DISCORD_BOT_TOKEN` each) to form a Hermes
> team — see [Hermes teams](../../docs/teams.md).

## Test

After install, run the bundled Helm test (a Job, hook `helm.sh/hook: test`):

```bash
helm test hermes-agent -n hermes-agent
# the test is a Job, so fetch its output by label (not `helm test --logs`):
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

It runs `hermes --version`, verifies the seeded `config.yaml`, checks docker
availability (informational, since the backend is `local`), and runs
`hermes doctor`. Disable with `--set tests.enabled=false`; make doctor failures
fatal with `--set tests.doctorStrict=true`.

### Verifying a provider end-to-end (`tests.chat.enabled`)

`tests.chat.enabled=true` adds a 5th check: a real `hermes chat` round-trip
using the **same `config`/`env` the release was installed with** (the test Job
mounts the same ConfigMap and Secret as the main workload — no separate
provider key needed), with the **full conversation (prompt + response) printed
to the test Job's logs**. Since `helm test` doesn't take `--set`, flip the flag
with `helm upgrade --reuse-values` and then run the test:

```bash
helm upgrade hermes-agent ./charts/hermes-agent -n hermes-agent \
  --reuse-values --set tests.chat.enabled=true --wait

helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

Sample output (NVIDIA NIM, prompt `tests.chat.prompt` default "Just say hi."):

```
[5/5] hermes chat round-trip
--- prompt ---
Just say hi.
--- model: (config default) (timeout 180s) ---
Query: Just say hi.
Initializing agent...
────────────────────────────────────────

╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
    Hi.
╰──────────────────────────────────────────────────────────────────────────────╯

--- end response ---
```

By default a failed/empty round-trip is **non-fatal** (logged only); set
`tests.chat.failOnError=true` to make it fail the test job (this is what CI
does when an `NVIDIA_API_KEY` secret is available).

For free-tier providers where a single model can be flaky/overloaded, set
`tests.chat.models` to a list of `provider/model` ids — the test Job tries
each in order via `hermes chat -m <id> --provider <config.model.provider>`
(its own `tests.chat.timeout` per attempt) and passes as soon as one succeeds.
This is what CI does (a small pool of free NVIDIA NIM models).

## Configuration model

Hermes reads `$HERMES_HOME/config.yaml` and secrets from the environment as
**partial overrides** on top of its version-specific built-in defaults
(precedence: CLI > `config.yaml` > `.env` > built-in defaults). This chart
follows that model — you only set what you want to change, and never reproduce
the full upstream config (which would drift across Hermes versions).

- **`config.yaml`** — set only override keys under `.Values.config`. It is
  rendered into a ConfigMap and **seeded into `HERMES_HOME`** (the persistent
  volume) by an init container, because Hermes also writes to its home at
  runtime (skills, `auth.json`, self-improvement). `bootstrap.overwrite=true`
  (default) re-seeds on every deploy; set `false` to seed only when absent.
- **Secrets / API keys** — set under `.Values.env`. Rendered into a Secret and
  injected via `envFrom` as environment variables (env wins over `config.yaml`).
  For GitOps, avoid committing real keys in `env` — instead deploy a
  `SealedSecret` (or similar) via `extraResources` and reference the Secret it
  produces with `extraEnvFrom` (applied after the chart's own Secret, so it
  wins). See [`examples/argocd/`](../../examples/argocd/) for a complete
  SealedSecret + `extraEnvFrom` GitOps example.
- **Dashboard Ingress** — the management dashboard (`service.port`, default
  9119) requires `--insecure` to bind beyond `127.0.0.1`, which the upstream
  warns **exposes API keys on the network**. Set `service.enabled: true` and
  `ingress.enabled: true` only behind authentication (e.g. an
  oauth2-proxy/basic-auth Ingress annotation) or on a private network — see
  `ingress.hosts` / `ingress.tls` in `values.yaml`.

## More examples

Ready-to-adapt `-f` overlays for common setups, aimed at a small/home cluster
(e.g. a Raspberry Pi / arm64 k3s cluster). All secrets in these files are
**dummy placeholders** — override them at install time with `--set-string` (see
the command in each file's header comment), or via the SealedSecret +
`extraEnvFrom` pattern above.

| File | Model provider | Extras |
| --- | --- | --- |
| [`values-nvidia-nim-and-discord.yaml`](values-nvidia-nim-and-discord.yaml) | NVIDIA NIM | **Discord bot** wired in |
| [`values-anthropic-and-discord.yaml`](values-anthropic-and-discord.yaml) | Anthropic (Claude) | **Discord bot** wired in |
| [`values-openai-and-telegram.yaml`](values-openai-and-telegram.yaml) | OpenAI (`openai-api`) | **Telegram bot** wired in |
| [`values-openai.yaml`](values-openai.yaml) | OpenAI (`openai-api`) | — |
| [`values-anthropic.yaml`](values-anthropic.yaml) | Anthropic (Claude) | — |
| [`values-gemini.yaml`](values-gemini.yaml) | Google Gemini | — |
| [`values-openrouter.yaml`](values-openrouter.yaml) | OpenRouter | — |
| [`values-litellm.yaml`](values-litellm.yaml) | LiteLLM proxy (remote/Ingress) | — |
| [`values-litellm-k8s.yaml`](values-litellm-k8s.yaml) | LiteLLM proxy (in-cluster Service DNS) | — |
| [`values-ingress.yaml`](values-ingress.yaml) | OpenAI (`openai-api`) | **Dashboard Ingress** wired in (basic-auth) |

Deploying via ArgoCD instead of plain `helm`/`-f`? See
[`examples/argocd/`](../../examples/argocd/) — it has one Application manifest
per example above, each with its `extraEnvFrom`-based secret pattern.

## Values

| Key | Type | Description | Default |
|-----|------|-------------|---------|
| affinity | object | Affinity rules for Pod scheduling. | `{}` |
| args | list | Arguments appended to `command`. | `["gateway","run"]` |
| bootstrap.enabled | bool | Seed the rendered config.yaml into HERMES_HOME via an init container. | `true` |
| bootstrap.overwrite | bool | true: overwrite HERMES_HOME/config.yaml with chart content on every    deploy (declarative). false: seed only if it does not already exist    (preserve runtime edits). | `true` |
| command | list | Container entrypoint. The image's DEFAULT CMD is the interactive `hermes` chat, which exits immediately in a pod (no TTY -> EOF -> "Goodbye"), causing a restart loop. So run the long-lived gateway explicitly; inside the s6-overlay image `gateway run` is auto-redirected to the SUPERVISED s6 service (auto-restart on crash). Append `--no-supervise` only if you want to bypass s6. | `["hermes"]` |
| config | object | ------------------------------------------------------------------------- | `{"agent":{"gateway_timeout":1800,"max_turns":90},"model":{"default":"gpt-4o-mini","provider":"openai-api"},"providers":{},"terminal":{"backend":"local"}}` |
| controller | object | ------------------------------------------------------------------------- | `{"type":"deployment"}` |
| controller.type | string | Workload kind: "deployment" or "statefulset". | `"deployment"` |
| env | object | ------------------------------------------------------------------------- | `{"OPENAI_API_KEY":"sk-REPLACE_ME"}` |
| extraEnv | list | Plain (non-secret) env vars injected directly on the container. | `[]` |
| extraEnvFrom | list | Extra envFrom sources (reference existing ConfigMaps/Secrets). | `[]` |
| extraResources | list | Extra raw manifests rendered as-is alongside this chart's resources.    Each entry is `tpl`-rendered, so `{{ .Release.Namespace }}` etc. work, and    may be either an object or a multiline string (see examples/argocd/).    Useful for things this chart doesn't model directly, e.g. a SealedSecret    that a sealed-secrets controller decrypts into a Secret referenced via    `extraEnvFrom` (see examples/argocd/). | `[]` |
| fullnameOverride | string | Fully override the generated resource name (release-name-chart). | `""` |
| image.pullPolicy | string | Image pull policy. | `"IfNotPresent"` |
| image.repository | string | Container image repository (multi-arch: amd64 + arm64). | `"nousresearch/hermes-agent"` |
| image.tag | string | Image tag. Upstream uses DATE-based tags (e.g. "v2026.6.5" == Hermes v0.16.0), plus `latest` / `main`. There is no semver tag. Empty defaults to `.Chart.AppVersion`. | `""` |
| imagePullSecrets | list | Image pull secrets for private registries. | `[]` |
| ingress.annotations | object | Annotations to add to the Ingress (e.g. auth, cert-manager, rewrite rules). | `{}` |
| ingress.className | string | IngressClass name (e.g. "nginx", "traefik"). Empty uses the cluster default. | `""` |
| ingress.enabled | bool | Create an Ingress resource. | `false` |
| ingress.hosts | list | Host/path rules, all routed to the Service port above. | `[{"host":"hermes-agent.example.com","paths":[{"path":"/","pathType":"Prefix"}]}]` |
| ingress.tls | list | TLS configuration for the Ingress. | `[]` |
| nameOverride | string | Override the chart name used in resource names. | `""` |
| nodeSelector | object | Node selector for Pod scheduling. | `{}` |
| persistence | object | ------------------------------------------------------------------------- | `{"accessModes":["ReadWriteOnce"],"enabled":true,"mountPath":"/opt/data","size":"5Gi","storageClass":""}` |
| persistence.storageClass | string | StorageClass for the volumeClaimTemplate. Empty = cluster default. | `""` |
| podAnnotations | object | Annotations to add to the Pod. | `{}` |
| podLabels | object | Labels to add to the Pod. | `{}` |
| podSecurityContext | object | Pod-level securityContext. Left empty by default to stay compatible with the image's s6-overlay init (which starts as root and drops privileges itself). Add hardening here once verified for your environment. | `{}` |
| probes | object | Health probes. Empty = none. The image's s6-overlay already supervises and auto-restarts the gateway in-container, so k8s probes are optional. Provide a full probe spec to enable, e.g. an exec check:   liveness:     exec: { command: ["hermes","gateway","status"] }     initialDelaySeconds: 30     periodSeconds: 30 | `{"liveness":{},"readiness":{}}` |
| probes.liveness | object | Liveness probe spec. Empty = no liveness probe. | `{}` |
| probes.readiness | object | Readiness probe spec. Empty = no readiness probe. | `{}` |
| replicaCount | int | DO NOT change this. Hermes Agent is a single-writer workload bound to one HERMES_HOME (ReadWriteOnce PVC). Raising replicaCount does NOT scale it out — with controller.type=deployment extra replicas just hang Pending (can't mount the same RWO volume); with statefulset they become separate, disconnected agent instances with their own PVC/identity. There is no supported multi-replica mode for this chart. | `1` |
| resources | object | Container resource requests/limits. Lightweight defaults aimed at small clusters (incl. Raspberry Pi / arm64). | `{"limits":{"cpu":"2","memory":"2Gi"},"requests":{"cpu":"100m","memory":"256Mi"}}` |
| securityContext | object | Container-level securityContext. Same caveat as `podSecurityContext` above. | `{}` |
| service | object | ------------------------------------------------------------------------- | `{"annotations":{},"enabled":false,"port":9119,"type":"ClusterIP"}` |
| service.annotations | object | Annotations to add to the Service. | `{}` |
| service.enabled | bool | Create a ClusterIP Service (only useful if you expose the dashboard). | `false` |
| service.port | int | Service port (and the dashboard's container port). | `9119` |
| service.type | string | Service type. | `"ClusterIP"` |
| serviceAccount.annotations | object | Annotations to add to the ServiceAccount. | `{}` |
| serviceAccount.create | bool | Create a ServiceAccount for the pod. | `true` |
| serviceAccount.name | string | Name to use; generated from fullname when empty. | `""` |
| tests | object | ------------------------------------------------------------------------- | `{"chat":{"enabled":false,"failOnError":false,"maxTurns":1,"models":[],"prompt":"Just say hi.","timeout":180},"doctorStrict":false,"doctorTimeout":120,"enabled":true,"image":{"pullPolicy":"","repository":"","tag":""},"resources":{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}}` |
| tests.chat | object | ------------------------------------------------------------------------- | `{"enabled":false,"failOnError":false,"maxTurns":1,"models":[],"prompt":"Just say hi.","timeout":180}` |
| tests.chat.enabled | bool | Run a `hermes chat` round-trip and log the conversation. | `false` |
| tests.chat.failOnError | bool | When true, a failed/empty round-trip fails the test job. | `false` |
| tests.chat.maxTurns | int | Max agent turns for the round-trip. | `1` |
| tests.chat.models | list | Optional pool of `provider/model` ids to try in order (via `hermes chat    -m <id> --provider config.model.provider`), each with its own `timeout`.    Passes as soon as one succeeds — useful for free-tier models that are    sometimes overloaded. Leave empty to use `config.model.default` as-is    (single attempt, no `-m`/`--provider` override). | `[]` |
| tests.chat.prompt | string | Prompt sent to the agent. | `"Just say hi."` |
| tests.chat.timeout | int | Seconds to allow each round-trip attempt to run before timing out. | `180` |
| tests.doctorStrict | bool | When true, `hermes doctor` issues fail the test. When false, doctor runs    for visibility but only hard checks (hermes --version, seeded config) fail. | `false` |
| tests.doctorTimeout | int | Seconds to allow `hermes doctor` to run before timing out. | `120` |
| tests.enabled | bool | Render the chart test Job. | `true` |
| tests.image | object | Image used by the test Job. Empty fields fall back to the main `image.*` (so the hermes CLI + doctor are available and arch matches). | `{"pullPolicy":"","repository":"","tag":""}` |
| tests.resources | object | Resource requests/limits for the test Job's container. | `{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}` |
| tolerations | list | Tolerations for Pod scheduling. | `[]` |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
