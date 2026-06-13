# hermes-agent

Hermes Agent on Kubernetes as a StatefulSet (or Deployment), configurable for
any LLM provider Hermes supports (OpenAI, Anthropic, Gemini, OpenRouter, or
any OpenAI-compatible proxy such as LiteLLM). config.yaml is managed via
ConfigMap and the .env via Secret.

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: v2026.6.5](https://img.shields.io/badge/AppVersion-v2026.6.5-informational?style=flat-square)

## Overview

Run [Hermes Agent](https://github.com/NousResearch/hermes-agent) on Kubernetes.
It deploys:

- a **StatefulSet** (default) or **Deployment** (`controller.type`), single
  replica with persistent `HERMES_HOME`, running the image's s6-supervised
  gateway
- a **ConfigMap** holding the partial `config.yaml`
- a **Secret** holding the `.env` (injected via `envFrom`)
- for `controller.type=statefulset`: a headless Service for DNS/governance
  (no inbound port — the gateway is outbound); for `deployment`: a standalone
  PVC instead. Either way, an **optional** ClusterIP Service for the dashboard
- a **Helm test** Job (`helm test`) that runs a `hermes doctor` style check

Hermes supports many LLM providers via **built-in provider keys**
(`openai-api`, `anthropic`, `gemini`, `openrouter`, `nvidia`, `deepseek`,
`lmstudio`, …). For an **OpenAI-compatible proxy** (LiteLLM, vLLM, LM Studio),
register it under `config.providers` and reference it by key. The chart is fully
driven by `values.yaml` — point it at a hosted API or an in-cluster proxy.

> The provider key `openai` is **not** valid in Hermes (it aliases to
> OpenRouter). Use `openai-api` for api.openai.com, or a custom provider for a
> proxy — see `values.example.yaml`.

The agent's command execution uses the **`local` backend** (commands run inside
the pod; the pod is the sandbox). The `docker` backend is intentionally **not
supported in-cluster** — it requires a Docker daemon/socket, absent on
containerd clusters (MicroK8s / Raspberry Pi) and a security risk to mount.

> Image tags are **date-based** (e.g. `v2026.6.5` == Hermes v0.16.0); the image
> is multi-arch (amd64 + arm64), so it runs on Raspberry Pi clusters.

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

Set `tests.chat.enabled=true` to additionally run a real `hermes chat`
round-trip against the configured provider and print the conversation (prompt +
response) to the Job's logs — useful for verifying a LiteLLM or Gemini setup
end-to-end:

```bash
# Gemini
helm test hermes-agent -n hermes-agent \
  --set tests.chat.enabled=true \
  --set config.model.provider=gemini \
  --set-string config.model.default=gemini-2.5-flash \
  --set-string env.GOOGLE_API_KEY='<your-key>'
```

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

See `charts/hermes-agent/values.example.yaml` for a complete example (custom
OpenAI-compatible proxy + persistent storage with a non-default StorageClass).

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| args[0] | string | `"gateway"` |  |
| args[1] | string | `"run"` |  |
| bootstrap.enabled | bool | `true` | Seed the rendered config.yaml into HERMES_HOME via an init container. |
| bootstrap.overwrite | bool | `true` | true: overwrite HERMES_HOME/config.yaml with chart content on every    deploy (declarative). false: seed only if it does not already exist    (preserve runtime edits). |
| command[0] | string | `"hermes"` |  |
| config | object | `{"agent":{"gateway_timeout":1800,"max_turns":90},"model":{"default":"gpt-4o-mini","provider":"openai-api"},"providers":{},"terminal":{"backend":"local"}}` | ------------------------------------------------------------------------- |
| controller | object | `{"type":"statefulset"}` | ------------------------------------------------------------------------- |
| controller.type | string | `"statefulset"` | Workload kind: "statefulset" or "deployment". |
| env | object | `{"OPENAI_API_KEY":"sk-REPLACE_ME"}` | ------------------------------------------------------------------------- |
| extraEnv | list | `[]` | Plain (non-secret) env vars injected directly on the container. |
| extraEnvFrom | list | `[]` | Extra envFrom sources (reference existing ConfigMaps/Secrets). |
| fullnameOverride | string | `""` | Fully override the generated resource name (release-name-chart). |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"nousresearch/hermes-agent"` |  |
| image.tag | string | `""` |  |
| imagePullSecrets | list | `[]` |  |
| nameOverride | string | `""` | Override the chart name used in resource names. |
| nodeSelector | object | `{}` |  |
| persistence | object | `{"accessModes":["ReadWriteOnce"],"enabled":true,"mountPath":"/opt/data","size":"5Gi","storageClass":""}` | ------------------------------------------------------------------------- |
| persistence.storageClass | string | `""` | StorageClass for the volumeClaimTemplate. Empty = cluster default. |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| probes.liveness | object | `{}` |  |
| probes.readiness | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources.limits.cpu | string | `"1"` |  |
| resources.limits.memory | string | `"1Gi"` |  |
| resources.requests.cpu | string | `"100m"` |  |
| resources.requests.memory | string | `"256Mi"` |  |
| securityContext | object | `{}` |  |
| service | object | `{"annotations":{},"enabled":false,"port":9119,"type":"ClusterIP"}` | ------------------------------------------------------------------------- |
| service.enabled | bool | `false` | Create a ClusterIP Service (only useful if you expose the dashboard). |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` | Name to use; generated from fullname when empty. |
| tests | object | `{"chat":{"enabled":false,"failOnError":false,"maxTurns":1,"prompt":"Just say hi.","timeout":180},"doctorStrict":false,"doctorTimeout":120,"enabled":true,"image":{"pullPolicy":"","repository":"","tag":""},"resources":{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}}` | ------------------------------------------------------------------------- |
| tests.chat | object | `{"enabled":false,"failOnError":false,"maxTurns":1,"prompt":"Just say hi.","timeout":180}` | ------------------------------------------------------------------------- |
| tests.chat.enabled | bool | `false` | Run a `hermes chat` round-trip and log the conversation. |
| tests.chat.failOnError | bool | `false` | When true, a failed/empty round-trip fails the test job. |
| tests.chat.maxTurns | int | `1` | Max agent turns for the round-trip. |
| tests.chat.prompt | string | `"Just say hi."` | Prompt sent to the agent. |
| tests.chat.timeout | int | `180` | Seconds to allow the round-trip to run before timing out. |
| tests.doctorStrict | bool | `false` | When true, `hermes doctor` issues fail the test. When false, doctor runs    for visibility but only hard checks (hermes --version, seeded config) fail. |
| tests.doctorTimeout | int | `120` | Seconds to allow `hermes doctor` to run before timing out. |
| tolerations | list | `[]` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
