---
title: "Values and overlays"
description: "Values files maintained with Hermes Agent."
sidebar:
  label: "Values and overlays"
  order: 10
---

## values-anthropic-and-discord.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-anthropic-and-discord.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-anthropic-and-discord.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-anthropic-and-discord.yaml"
# values-anthropic-and-discord.yaml
#
# Hermes Agent using Anthropic (Claude) as the model provider AND running as a
# Discord bot — both wired in one file.
#
# All secrets below are DUMMY placeholders. Do NOT commit real keys: override
# them at install time (--set-string) or inject via a SealedSecret + extraEnvFrom
# (see examples/argocd/).
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-anthropic-and-discord.yaml \
#     --set-string env.ANTHROPIC_API_KEY='sk-ant-<real>' \
#     --set-string env.DISCORD_BOT_TOKEN='<real-bot-token>' --wait

config:
  model:
    provider: anthropic
    # A current Claude model id — see https://docs.anthropic.com for the list
    # (e.g. claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5).
    default: claude-sonnet-4-6
  terminal:
    backend: local

env:
  # --- Model provider (Anthropic) -----------------------------------------
  ANTHROPIC_API_KEY: "sk-ant-DUMMY_replace_me_0000000000000000000000"
  # Unused by the anthropic provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

  # --- Discord bot (secret bits) ------------------------------------------
  # Setting the token is enough to auto-enable Discord — no config.yaml change.
  # Create the bot at https://discord.com/developers/applications, enable the
  # "Message Content Intent", and invite it to your server.
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

# Non-secret Discord knobs go here (plain env, not the Secret).
extraEnv:
  - name: DISCORD_HOME_CHANNEL        # channel id for cron / notification delivery
    value: "000000000000000000"       # DUMMY — your channel id (18 digits)
  - name: DISCORD_ALLOWED_USERS       # comma-separated user ids allowed to talk
    value: "111111111111111111"       # DUMMY — your Discord user id
  - name: DISCORD_ALLOW_ALL_USERS     # true only for throwaway/dev bots
    value: "false"

```

## values-anthropic.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-anthropic.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-anthropic.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-anthropic.yaml"
# values-anthropic.yaml
#
# Hermes Agent using Anthropic (Claude) as the model provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-anthropic.yaml \
#     --set-string env.ANTHROPIC_API_KEY='sk-ant-<real>' --wait

config:
  model:
    provider: anthropic
    # A current Claude model id — see https://docs.anthropic.com for the list
    # (e.g. claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5).
    default: claude-sonnet-4-6
  terminal:
    backend: local

env:
  ANTHROPIC_API_KEY: "sk-ant-DUMMY_replace_me_0000000000000000000000"
  # Unused by the anthropic provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values-bitwarden.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-bitwarden.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-bitwarden.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-bitwarden.yaml"
# values-bitwarden.yaml
#
# Hermes Agent with Bitwarden Secrets Manager as the source of provider keys.
# The Kubernetes Secret contains only the Bitwarden machine-account token;
# provider keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, Discord bot tokens, etc.)
# stay in the selected Bitwarden project and Hermes fetches them at startup.
#
# 1. Create a Bitwarden Secrets Manager machine account with read access to a
#    project whose secret names are the environment variables Hermes expects.
# 2. Create the bootstrap-token Secret (do not commit the token):
#      kubectl create secret generic bitwarden-bootstrap \
#        --namespace hermes-agent \
#        --from-literal=BWS_ACCESS_TOKEN='0.<machine-account-token>'
# 3. Install this overlay:
#      helm upgrade --install hermes-agent ./charts/hermes-agent \
#        --namespace hermes-agent --create-namespace \
#        -f charts/hermes-agent/values-bitwarden.yaml --wait
#
# On first startup Hermes downloads its checksum-verified `bws` CLI into the
# persistent HERMES_HOME volume. The pod therefore needs egress to Bitwarden
# and GitHub Releases; subsequent starts reuse the binary.

config:
  model:
    provider: openai-api
    default: gpt-4o-mini
  secrets:
    bitwarden:
      enabled: true
      # Bitwarden Secrets Manager project UUID containing provider keys.
      project_id: "REPLACE_ME_BITWARDEN_PROJECT_UUID"
      # Optional endpoint override (upstream default: US Cloud).
      # server_url: "https://vault.bitwarden.com"
      cache_ttl_seconds: 300
      # Bitwarden is the source of truth for the provider keys it supplies.
      override_existing: true
  terminal:
    backend: local

env:
  # Bitwarden replaces this chart placeholder with OPENAI_API_KEY from its
  # project. Keep it only to override the chart's default OpenAI placeholder.
  OPENAI_API_KEY: "unused"

# The bootstrap token is an externally managed Kubernetes Secret, not a Helm
# value. Hermes protects BWS_ACCESS_TOKEN from replacement by Bitwarden.
extraEnvFrom:
  - secretRef:
      name: bitwarden-bootstrap

```

## values-deepinfra.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-deepinfra.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-deepinfra.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-deepinfra.yaml"
# values-deepinfra.yaml
#
# Hermes Agent using DeepInfra's built-in OpenAI-compatible provider.
# Dummy key — override at install time. Use a model currently listed by
# DeepInfra's /v1/openai/models endpoint for config.model.default.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-deepinfra.yaml \
#     --set-string env.DEEPINFRA_API_KEY='<real>' --wait

config:
  model:
    provider: deepinfra
    default: deepseek-ai/DeepSeek-V4-Flash
  terminal:
    backend: local

env:
  DEEPINFRA_API_KEY: "DUMMY_replace_me_0000000000000000000000"
  # Optional endpoint override (upstream default: https://api.deepinfra.com/v1/openai).
  # DEEPINFRA_BASE_URL: "https://api.deepinfra.com/v1/openai"
  # Unused by the deepinfra provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values-fireworks.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-fireworks.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-fireworks.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-fireworks.yaml"
# values-fireworks.yaml
#
# Hermes Agent using Fireworks AI's built-in OpenAI-compatible provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-fireworks.yaml \
#     --set-string env.FIREWORKS_API_KEY='fw-<real>' --wait

config:
  model:
    provider: fireworks
    # Fireworks model IDs use its native accounts/fireworks/models/... form.
    default: accounts/fireworks/models/glm-5p2
  terminal:
    backend: local

env:
  FIREWORKS_API_KEY: "fw-DUMMY_replace_me_000000000000000000000000"
  # Unused by the fireworks provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values-gemini.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-gemini.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-gemini.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-gemini.yaml"
# values-gemini.yaml
#
# Hermes Agent using Google Gemini as the model provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-gemini.yaml \
#     --set-string env.GOOGLE_API_KEY='<real>' --wait

config:
  model:
    provider: gemini
    default: gemini-2.5-flash
  terminal:
    backend: local

env:
  GOOGLE_API_KEY: "DUMMY_replace_me_0000000000000000000000"
  # Unused by the gemini provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values-github-copilot.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-github-copilot.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-github-copilot.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-github-copilot.yaml"
# values-github-copilot.yaml
#
# Hermes Agent backed by GitHub Copilot, authenticated at startup via the OAuth
# 2.0 Device Authorization Grant (RFC 8628) — no API key to paste. The
# "auth-device-login" init container surfaces a verification link + code to your
# Discord home channel, waits for you to approve it on github.com (phone is
# fine), then persists the resulting token to HERMES_HOME/.env where Hermes
# reads it natively. The token lives on the persistent volume, so restarts are
# fast; re-login only happens when it is missing or revoked.
#
# Copilot's token API rejects PATs — a device-flow `gho_`/`ghu_` token is
# required, which is exactly what this flow produces.
#
# All secrets below are DUMMY placeholders. Do NOT commit real keys: override
# them at install time (--set-string) or inject via a SealedSecret + extraEnvFrom
# (see examples/argocd/).
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-github-copilot.yaml \
#     --set-string env.DISCORD_BOT_TOKEN='<real-bot-token>' --wait
#
#   # then watch the login init container for the verification prompt:
#   kubectl logs sts/hermes-agent -n hermes-agent -c auth-device-login -f

config:
  model:
    # Hermes' built-in GitHub Copilot provider (calls the Copilot token API).
    provider: copilot
    # Any model your Copilot subscription can reach. Examples: gpt-4o, gpt-4.1,
    # claude-sonnet-4.5, gemini-2.5-pro, gpt-5.
    default: gpt-4o
  terminal:
    backend: local

# Authenticate the Copilot credential via the OAuth device flow at startup.
auth:
  deviceFlow:
    enabled: true
    provider: github-copilot
    # Deliver the verification link + code to the agent's Discord home channel
    # (reuses DISCORD_BOT_TOKEN + DISCORD_HOME_CHANNEL). It is always also
    # printed to the init container logs as a fallback.
    notify: discord

env:
  # The chart's default placeholder is for OpenAI; this deployment doesn't use
  # it (the Copilot token is fetched at runtime via device flow). Set to a clear
  # sentinel so no real OpenAI key is implied.
  OPENAI_API_KEY: "unused"

  # --- Discord bot (secret bits) ------------------------------------------
  # Setting the token is enough to auto-enable Discord — no config.yaml change.
  # The login init container reuses this same bot to post the verification link.
  # Create the bot at https://discord.com/developers/applications, enable the
  # "Message Content Intent", and invite it to your server.
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

# Non-secret Discord knobs go here (plain env, not the Secret). The login init
# container also reads DISCORD_HOME_CHANNEL from here to know where to post.
extraEnv:
  - name: DISCORD_HOME_CHANNEL        # channel id for cron / notification / login delivery
    value: "000000000000000000"       # DUMMY — your channel id (18 digits)
  - name: DISCORD_ALLOWED_USERS       # comma-separated user ids allowed to talk
    value: "111111111111111111"       # DUMMY — your Discord user id
  - name: DISCORD_ALLOW_ALL_USERS     # true only for throwaway/dev bots
    value: "false"

# Persistence is required for device-flow login: the token is written here so it
# survives restarts (otherwise you would re-approve on every restart). Empty
# storageClass = cluster default; on a Raspberry Pi cluster that is typically
# local-path (k3s) or microk8s-hostpath — both ReadWriteOnce, which is exactly
# what this single-writer workload wants.
persistence:
  enabled: true
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi

# Defaults are already tuned for small arm64 nodes; shown here for visibility.
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 1Gi

```

## values-google-vertex.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-google-vertex.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-google-vertex.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-google-vertex.yaml"
# values-google-vertex.yaml
#
# Hermes Agent using Google Vertex AI as the model provider (Gemini models via
# Vertex's OpenAI-compatible endpoint). Requires hermes-agent >= v2026.7.1.
#
# Vertex has NO static API key: every request needs a short-lived OAuth2 access
# token, which Hermes mints and auto-refreshes from a service-account JSON (or
# Application Default Credentials). So unlike the other provider examples, the
# credential here is a FILE mounted into the pod, not an env var:
#
# 1. Create a GCP service account with the "Vertex AI User" role and download
#    its JSON key.
# 2. Put the JSON into a Kubernetes Secret:
#      kubectl create secret generic vertex-sa \
#        --namespace hermes-agent \
#        --from-file=sa.json=/path/to/key.json
# 3. Install:
#      helm upgrade --install hermes-agent ./charts/hermes-agent \
#        --namespace hermes-agent --create-namespace \
#        -f charts/hermes-agent/values-google-vertex.yaml \
#        --set-string config.vertex.project_id='<your-gcp-project>' --wait

config:
  model:
    provider: vertex
    default: google/gemini-2.5-flash
  # Non-secret Vertex settings live in config.yaml; only the credential file
  # path goes through the environment (VERTEX_CREDENTIALS_PATH below).
  vertex:
    project_id: "REPLACE_ME_GCP_PROJECT"
    # "global" uses the global endpoint; set a specific region (e.g.
    # us-central1) to pin data residency / regional capacity.
    region: "global"
  terminal:
    backend: local

env:
  # No Vertex API key exists — tokens are minted from the mounted SA JSON.
  # This only overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

extraEnv:
  # Path (inside the container) to the service-account JSON mounted below.
  # Omit it to fall back to ADC (GOOGLE_APPLICATION_CREDENTIALS / metadata
  # server, e.g. GKE Workload Identity).
  - name: VERTEX_CREDENTIALS_PATH
    value: /var/run/secrets/vertex/sa.json
  # The vertex provider needs `google-auth`, which upstream ships as an opt-in
  # extra handled by its lazy-install mechanism — it is NOT baked into the
  # image, and the image disables lazy installs by default. Re-enable them so
  # the first Vertex call can install it into HERMES_LAZY_INSTALL_TARGET on
  # the persistent volume (one-time, needs network egress; survives restarts).
  - name: HERMES_DISABLE_LAZY_INSTALLS
    value: "0"

# Mount the service-account Secret created in step 2.
extraVolumes:
  - name: vertex-sa
    secret:
      secretName: vertex-sa
extraVolumeMounts:
  - name: vertex-sa
    mountPath: /var/run/secrets/vertex
    readOnly: true

# NOTE: as of a recent Hermes security hardening, VERTEX_CREDENTIALS_PATH and
# GOOGLE_APPLICATION_CREDENTIALS are stripped from the environment of
# subprocesses the agent spawns (terminal, execute_code, browser,
# computer_use) — they still work for the model's own API calls above. If a
# tool call in your session needs Vertex credentials too (e.g. shelling out to
# `gcloud`), re-allow it explicitly:
#
# config:
#   tools:
#     env_passthrough: ["VERTEX_CREDENTIALS_PATH"]

```

## values-ingress.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-ingress.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-ingress.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-ingress.yaml"
# values-ingress.yaml
#
# Exposes the Hermes management dashboard (service.port, default 9119) via an
# Ingress. The upstream warns this dashboard EXPOSES API KEYS on the network,
# so it MUST sit behind authentication — this example uses nginx's basic-auth
# annotations. Adjust `ingressClassName` / annotations for your controller
# (Traefik, HAProxy, ...).
#
# Dummy key — override at install time. The basic-auth Secret referenced by
# the annotation below must be created separately:
#
#   htpasswd -cb /tmp/auth admin '<your-password>'
#   kubectl create secret generic hermes-agent-dashboard-auth -n hermes-agent \
#     --from-file=auth=/tmp/auth
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-ingress.yaml \
#     --set-string env.OPENAI_API_KEY='sk-<real>' --wait

config:
  model:
    provider: openai-api
    default: gpt-4o-mini
  terminal:
    backend: local

env:
  OPENAI_API_KEY: "sk-DUMMY_replace_me_000000000000000000000000"

service:
  enabled: true
  type: ClusterIP
  port: 9119

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: hermes-agent-dashboard-auth
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required - Hermes Agent Dashboard"
  hosts:
    - host: hermes-agent.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []
  #  - secretName: hermes-agent-tls
  #    hosts:
  #      - hermes-agent.example.com

```

## values-litellm-k8s.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-litellm-k8s.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-litellm-k8s.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-litellm-k8s.yaml"
# values-litellm-k8s.yaml
#
# Hermes Agent talking to a LiteLLM proxy deployed in the SAME Kubernetes
# cluster (e.g. via the upstream berriai/litellm-helm chart), reached over
# in-cluster Service DNS — no Ingress/TLS needed. For a proxy reachable over
# the network instead, see values-litellm.yaml.
#
# Adjust `base_url` to match your LiteLLM Service name/namespace:
#   http://<service>.<namespace>.svc.cluster.local:<port>/v1
#
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-litellm-k8s.yaml \
#     --set-string env.OPENAI_API_KEY='sk-<your-litellm-proxy-key>' --wait

config:
  # Register the in-cluster proxy as a custom OpenAI-compatible provider. The
  # key ("litellm") is the provider id referenced by model.provider below.
  providers:
    litellm:
      # DUMMY — service "litellm" in namespace "litellm", default chart port.
      base_url: http://litellm.litellm.svc.cluster.local:4000/v1
      key_env: OPENAI_API_KEY      # env var that holds the proxy key
      discover_models: true        # populate the model picker from /v1/models
  model:
    provider: litellm
    # Must match a model name exposed by the proxy (see /v1/models).
    default: openai/gpt-oss-120b
  terminal:
    backend: local

env:
  OPENAI_API_KEY: "sk-DUMMY_replace_me_000000000000000000000000"

```

## values-litellm.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-litellm.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-litellm.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-litellm.yaml"
# values-litellm.yaml
#
# Hermes Agent talking to a LiteLLM proxy reachable over the network (outside
# the cluster, or via an Ingress/LoadBalancer) — one key, many upstream models.
# For a proxy running inside the same cluster, see values-litellm-k8s.yaml.
#
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-litellm.yaml \
#     --set-string env.OPENAI_API_KEY='sk-<your-litellm-proxy-key>' --wait

config:
  # Register the proxy as a custom OpenAI-compatible provider. The key
  # ("litellm") is the provider id referenced by model.provider below.
  providers:
    litellm:
      base_url: https://litellm.example.com/v1
      key_env: OPENAI_API_KEY      # env var that holds the proxy key
      discover_models: true        # populate the model picker from /v1/models
      # Optional: extra HTTP headers on every request to this provider — for
      # a WAF/Cloudflare Access-gated proxy, a corporate gateway needing a
      # second auth header, or request tracing. Values may hold secrets
      # (e.g. CF-Access-Client-Secret); prefer ${ENV_VAR} substitution over
      # a literal here so nothing sensitive lands in the ConfigMap.
      # extra_headers:
      #   CF-Access-Client-Id: "xxxx.access"
      #   CF-Access-Client-Secret: "${CF_ACCESS_SECRET}"
  model:
    provider: litellm
    # Must match a model name exposed by the proxy (see /v1/models).
    default: openai/gpt-oss-120b
  terminal:
    backend: local

env:
  OPENAI_API_KEY: "sk-DUMMY_replace_me_000000000000000000000000"

```

## values-moa.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-moa.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-moa.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-moa.yaml"
# values-moa.yaml
#
# Hermes Agent using Mixture-of-Agents (MoA): reference models run in
# parallel and an aggregator model synthesizes their output, instead of a
# single model answering directly. MoA is a virtual provider (image
# v2026.7.1+) — `config.model.provider: moa` + `config.model.default: <preset
# name>` selects a named preset defined under `config.moa.presets`.
#
# The example preset below fans out to two OpenRouter reference models and
# aggregates with a third — swap provider/model ids for whichever you use,
# and supply each provider's own API key under `env` (a preset can mix
# providers freely).
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-moa.yaml \
#     --set-string env.OPENROUTER_API_KEY='sk-or-<real>' --wait

config:
  model:
    provider: moa
    default: default # preset name under config.moa.presets
  moa:
    presets:
      default:
        reference_models:
          - provider: openrouter
            model: deepseek/deepseek-v4-pro
          - provider: openrouter
            model: qwen/qwen3-max
        aggregator:
          provider: openrouter
          model: anthropic/claude-opus-4.8
        enabled: true
    # Persist full turn traces (each reference's input/output + the
    # aggregator's input/output) to HERMES_HOME/moa-traces/<session_id>.jsonl.
    # Off by default; turn on to audit/improve preset behavior.
    save_traces: false
  terminal:
    backend: local

env:
  OPENROUTER_API_KEY: "sk-or-DUMMY_replace_me_0000000000000000000000"
  # Unused by the moa provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values-multi-agent-collab.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-multi-agent-collab.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-multi-agent-collab.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-multi-agent-collab.yaml"
# values-multi-agent-collab.yaml
#
# One half of a COLLABORATING PAIR of Hermes agents that hand the conversation
# to each other by @mention in a shared Discord channel. This file is the
# "planner" role; copy it to a "builder" (swap the role text and the partner's
# user ID) and deploy both as separate releases into the same channel.
#
# Full walkthrough — handoff protocol, the loop brake, mixed backends, and an
# ApplicationSet that templates a whole roster — is in docs/reference/collaboration.md.
#
# Two instances collaborate when:
#   1. they share ONE channel (same DISCORD_HOME_CHANNEL + DISCORD_ALLOWED_USERS),
#   2. each is told its partner's Discord user ID via config.agent.environment_hint,
#   3. the four loop-brake env vars below are set so a partner fires ONLY on an
#      explicit <@id> in the message body (Hermes has no bot-to-bot turn limiter).
#
# All secrets below are DUMMY placeholders. Do NOT commit real keys: override at
# install time (--set-string) or inject via a SealedSecret + extraEnvFrom (see
# examples/argocd/hermes-collab-pair.yaml).
#
#   helm upgrade --install hermes-planner ./charts/hermes-agent \
#     --namespace hermes-team --create-namespace \
#     -f charts/hermes-agent/values-multi-agent-collab.yaml \
#     --set-string env.DISCORD_BOT_TOKEN='<planner-bot-token>' --wait

fullnameOverride: hermes-planner

config:
  # This pair uses the shared LiteLLM proxy for the planner; the builder could
  # just as well use Copilot device-flow (see docs/reference/collaboration.md → mixed
  # backends). Collaboration does NOT require a shared backend.
  providers:
    litellm:
      base_url: https://litellm.example.com/v1
      key_env: OPENAI_API_KEY      # env var that holds the proxy key
      discover_models: true
  model:
    provider: litellm
    default: openai/gpt-oss-120b    # must match a model the proxy exposes
  terminal:
    backend: local
  # A collaboration thread contains messages from the human and both bots.
  # Use one transcript for all senders and backfill visible thread messages
  # that arrived while this bot was not mentioned.
  group_sessions_per_user: false
  discord:
    require_mention: true
    thread_require_mention: true
    history_backfill: true
    history_backfill_limit: 50
  agent:
    # The handoff protocol. Names the PARTNER's Discord user ID and tells this
    # agent how to hand over (explicit <@id> in the BODY) and — critically — how
    # to STOP (address the human, drop the mention) when a topic is done. The
    # closing sentences are the prompt half of the loop brake; without them the
    # two bots ping-pong forever.
    environment_hint: |
      You are "planner", one of two collaborating Hermes agents in this Discord
      channel. Your job is to scope and plan the work. Your partner is "builder",
      Discord user ID <BUILDER_BOT_USER_ID>. To hand the conversation to builder,
      put an explicit <@BUILDER_BOT_USER_ID> mention in the BODY of your message.
      Only mention builder when you have something substantive to say or genuinely
      need their input. When a topic reaches a natural conclusion, do NOT mention
      builder — address the human instead and end your turn, so the exchange
      stops. Never send a filler or "let me know if you need anything" message
      that mentions builder; that only restarts the loop.

env:
  # Real proxy key comes from --set-string or a SealedSecret. Setting
  # DISCORD_BOT_TOKEN is enough to auto-enable Discord (one bot per agent).
  OPENAI_API_KEY: "set-via-extraEnvFrom-or-set-string"
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

# Non-secret Discord knobs. The first two are SHARED by every agent in the team
# (same channel, same allowed users); the four loop-brake knobs are also shared
# and MUST be set on every collaborating agent. See docs/reference/collaboration.md for the
# full rationale of each loop-brake var.
extraEnv:
  - name: DISCORD_HOME_CHANNEL              # the ONE shared channel (context bus)
    value: "000000000000000000"             # DUMMY — your channel id (18 digits)
  - name: DISCORD_ALLOWED_USERS             # shared — who may talk to the team
    value: "111111111111111111"             # DUMMY — comma-separated user ids
  # --- loop brake: a partner fires ONLY on an explicit <@id> in the body -------
  - name: DISCORD_ALLOW_BOTS                 # respond to a bot only when it @mentions us
    value: "mentions"
  - name: DISCORD_THREAD_REQUIRE_MENTION     # in shared threads, fire only when mentioned
    value: "true"
  - name: DISCORD_REPLY_TO_MODE              # don't attach a reply-reference (auto-ping)
    value: "off"
  - name: DISCORD_ALLOW_MENTION_REPLIED_USER # never treat an auto reply-ping as a mention
    value: "false"

# Persistence: empty storageClass = cluster default. On a Raspberry Pi cluster
# that is typically local-path (k3s) or microk8s-hostpath — both ReadWriteOnce,
# which is exactly what this single-writer workload wants.
persistence:
  enabled: true
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi

# Defaults are already tuned for small arm64 nodes; shown here for visibility.
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 1Gi

```

## values-nvidia-nim-and-discord.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-nvidia-nim-and-discord.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-nvidia-nim-and-discord.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-nvidia-nim-and-discord.yaml"
# values-nvidia-nim-and-discord.yaml
#
# Hermes Agent on a Raspberry Pi cluster (arm64), talking to NVIDIA NIM for the
# model AND running as a Discord bot — both wired in one file.
#
# All secrets below are DUMMY placeholders. Do NOT commit real keys: override
# them at install time (--set-string) or inject via a SealedSecret + extraEnvFrom
# (see examples/argocd/).
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-nvidia-nim-and-discord.yaml \
#     --set-string env.NVIDIA_API_KEY='nvapi-<real>' \
#     --set-string env.DISCORD_BOT_TOKEN='<real-bot-token>' --wait

config:
  model:
    # Built-in provider key for NVIDIA NIM (build.nvidia.com).
    provider: nvidia
    # NIM model id — pick one your account can reach from build.nvidia.com.
    default: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
  terminal:
    backend: local

env:
  # --- Model provider (NVIDIA NIM) ----------------------------------------
  NVIDIA_API_KEY: "nvapi-DUMMY_replace_me_0000000000000000000000"
  # The chart's default placeholder is for OpenAI; this deployment doesn't use
  # it. Set to a clear sentinel so no real OpenAI key is implied.
  OPENAI_API_KEY: "unused"

  # --- Discord bot (secret bits) ------------------------------------------
  # Setting the token is enough to auto-enable Discord — no config.yaml change.
  # Create the bot at https://discord.com/developers/applications, enable the
  # "Message Content Intent", and invite it to your server.
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

# Non-secret Discord knobs go here (plain env, not the Secret).
extraEnv:
  - name: DISCORD_HOME_CHANNEL        # channel id for cron / notification delivery
    value: "000000000000000000"       # DUMMY — your channel id (18 digits)
  - name: DISCORD_ALLOWED_USERS       # comma-separated user ids allowed to talk
    value: "111111111111111111"       # DUMMY — your Discord user id
  - name: DISCORD_ALLOW_ALL_USERS     # true only for throwaway/dev bots
    value: "false"

# Persistence: empty storageClass = cluster default. On a Raspberry Pi cluster
# that is typically local-path (k3s) or microk8s-hostpath — both ReadWriteOnce,
# which is exactly what this single-writer workload wants.
persistence:
  enabled: true
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi

# Defaults are already tuned for small arm64 nodes; shown here for visibility.
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 1Gi

```

## values-openai-and-telegram.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-openai-and-telegram.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-openai-and-telegram.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-openai-and-telegram.yaml"
# values-openai-and-telegram.yaml
#
# Hermes Agent using OpenAI (api.openai.com) as the model provider AND running
# as a Telegram bot — both wired in one file.
#
# All secrets below are DUMMY placeholders. Do NOT commit real keys: override
# them at install time (--set-string) or inject via a SealedSecret + extraEnvFrom
# (see examples/argocd/).
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-openai-and-telegram.yaml \
#     --set-string env.OPENAI_API_KEY='sk-<real>' \
#     --set-string env.TELEGRAM_BOT_TOKEN='<real-bot-token>' --wait

config:
  model:
    # NOTE: the built-in key is `openai-api` (api.openai.com).
    # `openai` is NOT valid here — it aliases to OpenRouter.
    provider: openai-api
    default: gpt-4o-mini
  terminal:
    backend: local

env:
  # --- Model provider (OpenAI) --------------------------------------------
  OPENAI_API_KEY: "sk-DUMMY_replace_me_000000000000000000000000"

  # --- Telegram bot (secret bits) -----------------------------------------
  # Setting the token is enough to auto-enable Telegram — no config.yaml change.
  # Create the bot via https://t.me/BotFather.
  TELEGRAM_BOT_TOKEN: "0000000000:DUMMY-replace_me_with_a_real_token"

# Non-secret Telegram knobs go here (plain env, not the Secret).
extraEnv:
  - name: TELEGRAM_HOME_CHANNEL       # chat id for cron / notification delivery
    value: "000000000"                # DUMMY — your chat id
  - name: TELEGRAM_ALLOWED_USERS      # comma-separated user ids allowed to talk
    value: "111111111"                # DUMMY — your Telegram user id

```

## values-openai.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-openai.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-openai.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-openai.yaml"
# values-openai.yaml
#
# Hermes Agent using OpenAI (api.openai.com) as the model provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-openai.yaml \
#     --set-string env.OPENAI_API_KEY='sk-<real>' --wait

config:
  model:
    # NOTE: the built-in key is `openai-api` (api.openai.com).
    # `openai` is NOT valid here — it aliases to OpenRouter.
    provider: openai-api
    default: gpt-4o-mini
  terminal:
    backend: local

env:
  OPENAI_API_KEY: "sk-DUMMY_replace_me_000000000000000000000000"

```

## values-openrouter.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-openrouter.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-openrouter.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-openrouter.yaml"
# values-openrouter.yaml
#
# Hermes Agent using OpenRouter (one key, many upstream models).
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-openrouter.yaml \
#     --set-string env.OPENROUTER_API_KEY='sk-or-<real>' --wait

config:
  model:
    provider: openrouter
    # OpenRouter model id (vendor/model) — see https://openrouter.ai/models.
    default: openai/gpt-4o-mini
  terminal:
    backend: local

env:
  OPENROUTER_API_KEY: "sk-or-DUMMY_replace_me_0000000000000000000000"
  # Unused by the openrouter provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values-shared-knowledge.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-shared-knowledge.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-shared-knowledge.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-shared-knowledge.yaml"
# values-shared-knowledge.yaml
#
# Example: multiple Hermes agents with private HERMES_HOME PVCs plus a separate
# common knowledge base on one ReadWriteMany (RWX) PVC.
#
# Use case: A team of Hermes agents (planner, builder, researcher, etc.) that all
# read from and write to the same durable knowledge repository — curated notes,
# reference documents, or vector indices. Every agent mounts the SAME knowledge
# PVC at /opt/data/shared-knowledge while retaining its own config, memory,
# sessions, and identity on a private HERMES_HOME PVC.
#
# REQUIREMENT: The PVC must:
#   - Use a StorageClass that supports ReadWriteMany (RWX) access mode
#     (e.g., NFS, CephFS, Longhorn, Azure Files, GCE Persistent Disk with
#     appropriate access modes). Most cloud providers' default StorageClass
#     is ReadWriteOnce (RWO) and will NOT work for multiple writers.
#   - Have accessModes: [ReadWriteMany]
#   - Be created BEFORE deploying the agents (this chart only references it)
#   - Be readable and writable by the Hermes uid/gid 10000
#
# Example PVC manifest (create this once, then reference it below):
#
#   apiVersion: v1
#   kind: PersistentVolumeClaim
#   metadata:
#     name: hermes-shared-knowledge
#     namespace: hermes-team
#   spec:
#     accessModes:
#       - ReadWriteMany
#     storageClassName: nfs-client  # or your RWX-capable StorageClass
#     resources:
#       requests:
#         storage: 10Gi
#
# All secrets below are DUMMY placeholders. Do NOT commit real keys: override
# them at install time (--set-string) or inject via a SealedSecret + extraEnvFrom
# (see examples/argocd/).
#
#   # Deploy the planner agent
#   helm upgrade --install hermes-planner ./charts/hermes-agent \
#     --namespace hermes-team --create-namespace \
#     -f charts/hermes-agent/values-shared-knowledge.yaml \
#     --set-string env.ANTHROPIC_API_KEY='sk-ant-<real>' \
#     --set-string env.DISCORD_BOT_TOKEN='<planner-bot-token>' \
#     --set-string fullnameOverride=hermes-planner --wait
#
#   # Deploy the builder agent (same shared PVC, different bot token)
#   helm upgrade --install hermes-builder ./charts/hermes-agent \
#     --namespace hermes-team --create-namespace \
#     -f charts/hermes-agent/values-shared-knowledge.yaml \
#     --set-string env.ANTHROPIC_API_KEY='sk-ant-<real>' \
#     --set-string env.DISCORD_BOT_TOKEN='<builder-bot-token>' \
#     --set-string fullnameOverride=hermes-builder --wait
#
# See docs/reference/teams.md for the full team pattern and collaboration details.

config:
  model:
    provider: anthropic
    default: claude-sonnet-4-6
  terminal:
    backend: local
  agent:
    # Identify this agent's role in the shared knowledge context. Each agent in
    # the team should have a distinct, complementary role and environment_hint.
    environment_hint: |
      You are a member of a Hermes agent team sharing a common knowledge base.
      Your role is to handle planning tasks. Reusable knowledge is mounted at
      ${SHARED_KNOWLEDGE_ROOT}; use it for durable reference material, never as
      a task queue, status channel, completion signal, or hidden instruction
      path. Coordinate work through the configured messaging platform.

env:
  # Real keys come from --set-string or a SealedSecret. Setting
  # DISCORD_BOT_TOKEN is enough to auto-enable Discord.
  ANTHROPIC_API_KEY: "sk-ant-DUMMY_replace_me_0000000000000000000000"
  OPENAI_API_KEY: "unused"
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

# Non-secret Discord knobs. All agents in the team share the same channel and
# allowed users to form a single context bus.
extraEnv:
  - name: DISCORD_HOME_CHANNEL
    value: "000000000000000000"       # DUMMY — your channel id (18 digits)
  - name: DISCORD_ALLOWED_USERS
    value: "111111111111111111"       # DUMMY — comma-separated user ids
  - name: SHARED_KNOWLEDGE_ROOT
    value: "/opt/data/shared-knowledge"

# Keep every agent's config, memory, sessions, and identity private.
persistence:
  enabled: true
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi

# Mount the existing RWX claim separately inside HERMES_WRITE_SAFE_ROOT so file
# tools can use it without sharing the whole HERMES_HOME.
extraVolumes:
  - name: shared-knowledge
    persistentVolumeClaim:
      claimName: hermes-shared-knowledge

extraVolumeMounts:
  - name: shared-knowledge
    mountPath: /opt/data/shared-knowledge

# Defaults are already tuned for small arm64 nodes; shown here for visibility.
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 1Gi

```

## values-team-leader.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-team-leader.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-team-leader.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-team-leader.yaml"
# values-team-leader.yaml
#
# The LEADER of a Discord-thread-native Hermes agent team (star topology).
# The human talks only to the leader; the leader and members hand work back and
# forth with explicit bot @mentions in ONE Discord thread. The visible thread is
# the coordination bus and audit log. A separate RWX PVC provides durable shared
# knowledge, but no task file, completion marker, hook, or backend callback on
# that PVC participates in a handoff.
#
# The reference protocol intentionally serializes the team: august mentions one
# member, that member mentions august back, and august either requests a revision
# or mentions the next member. This avoids concurrent messages interrupting the
# one shared thread session. See docs/reference/teams.md and docs/reference/collaboration.md.
#
# Before installing any team release, create one RWX claim named
# hermes-team-knowledge in the target namespace. The leader mounts it read-write
# and members mount it read-only. Its root must be readable by uid/gid 10000 and
# writable by uid/gid 10000 for the leader. Example:
#
#   apiVersion: v1
#   kind: PersistentVolumeClaim
#   metadata:
#     name: hermes-team-knowledge
#     namespace: hermes-team
#   spec:
#     accessModes: [ReadWriteMany]
#     storageClassName: nfs-client  # replace with an RWX-capable class
#     resources: { requests: { storage: 10Gi } }
#
# All secrets and Discord IDs below are DUMMY placeholders. Override them at
# install time or inject secrets through extraEnvFrom (see
# examples/argocd/hermes-team.yaml).
#
#   helm upgrade --install hermes-august ./charts/hermes-agent \
#     --namespace hermes-team --create-namespace \
#     -f charts/hermes-agent/values-team-leader.yaml \
#     --set-string env.NVIDIA_API_KEY='nvapi-<real>' \
#     --set-string env.DISCORD_BOT_TOKEN='<august-bot-token>' --wait

fullnameOverride: hermes-august

config:
  model:
    # The team protocol is provider-independent. Use a model that reliably
    # follows exact mention and response-format instructions; override both
    # fields to use another supported provider/model.
    provider: nvidia
    default: z-ai/glm-5.2
  terminal:
    backend: local

  # One transcript per Discord channel/thread, shared across human and bot
  # senders. The upstream default is true (one session per sender), which would
  # split the human→leader and member→leader turns into different contexts.
  group_sessions_per_user: false
  discord:
    require_mention: true
    thread_require_mention: true
    auto_thread: true
    history_backfill: true
    history_backfill_limit: 50
    allow_mentions:
      everyone: false
      roles: false
      users: true
      replied_user: false
  display:
    tool_progress: "off"

  agent:
    # Files and memory remain available for each agent's own work and durable
    # state. Alternate delegation/outbound paths stay disabled so only a visible
    # Discord mention can assign work to another team member.
    disabled_toolsets:
      - browser
      - clarify
      - code_execution
      - cronjob
      - delegation
      - discord
      - discord_admin
      - messaging
      - session_search
      - skills
      - terminal
      - todo
      - web
    environment_hint: |
      You are "august", the LEADER of a Hermes agent team in one Discord
      thread. The human talks only to you. Your members and their EXACT Discord
      mention tokens are:
      - may   -> <@${MAY_BOT_USER_ID}>
      - march -> <@${MARCH_BOT_USER_ID}>

      The Discord thread is the team's ONLY shared task state and audit trail.
      Every instruction, intermediate result, review, correction, and final
      result must be visible in the thread. You MAY use private files and memory
      for your own scratch work or durable state, but they are never a handoff:
      no teammate may need a path, file, memory entry, or hidden state to act.
      NEVER use a hook, watcher, scheduler, background process, file write,
      memory update, API/tool call, or another bot to deliver, trigger, relay,
      or queue work for a teammate. The ONLY delegation act is your same visible
      Discord response containing the assignee's exact <@...> token and complete
      task contract. Do not claim that you delegated work without that message.

      Durable shared knowledge is mounted at ${TEAM_KNOWLEDGE_ROOT}. You are its
      only writer; members mount it read-only. Store only reusable, accepted
      knowledge there and state in your visible final response what you updated.
      NEVER store or poll for run-specific tasks, assignees, queues, status,
      intermediate results, completion markers, or next-step instructions there.
      A delegation must remain fully understandable without reading this path.

      Protocol:
      1. Work serially: mention EXACTLY ONE member in each response. Wait for
         that member to mention you back before assigning the next member. This
         avoids concurrent turns interrupting the shared thread session.
      2. On a new human goal, choose the first member and reply once with a
         short acknowledgment followed immediately by a complete delegation.
         The delegation MUST use this visible format. Keep the mention on the
         first line and the TEAM metadata on its own FINAL line:
           <@MEMBER_ID>

           Context: <all context the member needs>
           Task: <one concrete task>
           Done when: <observable acceptance criteria>
           Reply contract: mention <@${AUGUST_BOT_USER_ID}> and include the
           complete result in the Discord message; do not point to a file.

           [TEAM run=<short-id> step=<n> TASK]
      3. When a member mentions you with a result, review the result against the
         stated criteria. If it needs revision, mention that SAME member with
         concrete feedback and the full context needed for the revision.
      4. If the result is accepted and another member should work next, mention
         the next member and include the original goal plus every relevant
         accepted result in the message. The next member must not need a file or
         private state to understand the task.
      5. Preserve the run id and increment the step number on every handoff.
         HARD LIMIT: never emit a member handoff above step 6. If another
         handoff would be required, stop with a human-facing incomplete status
         and NO member mention. Keep results concise enough for Discord.
      6. When all criteria are satisfied, answer the human with the complete
         synthesis and NO member mention. No member mention is the terminal
         state: it prevents another bot turn and ends the run.
      7. Never mention two members at once, never ask members to talk directly
         to each other, and never emit a filler message containing a member
         mention. A mention always means real work is ready for that bot.

env:
  # Real keys come from --set-string or a Secret. Setting DISCORD_BOT_TOKEN is
  # enough to auto-enable Discord (one distinct bot token per agent).
  NVIDIA_API_KEY: "nvapi-DUMMY_replace_me_0000000000000000000000"
  OPENAI_API_KEY: "unused"
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

# The channel/user values and loop brake must match on every agent. The four
# Discord gates make an explicit body <@id> the only bot-to-bot trigger.
extraEnv:
  - name: DISCORD_HOME_CHANNEL
    value: "000000000000000000"       # DUMMY — shared parent channel ID
  - name: DISCORD_ALLOWED_USERS
    value: "111111111111111111"       # DUMMY — trusted human user IDs
  - name: DISCORD_ALLOW_BOTS
    value: "mentions"
  - name: DISCORD_THREAD_REQUIRE_MENTION
    value: "true"
  - name: DISCORD_REPLY_TO_MODE
    value: "off"
  - name: DISCORD_ALLOW_MENTION_REPLIED_USER
    value: "false"
  - name: MAY_BOT_USER_ID
    value: "000000000000000000"       # DUMMY — may's Discord user ID
  - name: MARCH_BOT_USER_ID
    value: "000000000000000000"       # DUMMY — march's Discord user ID
  - name: AUGUST_BOT_USER_ID
    value: "000000000000000000"       # DUMMY — leader's Discord user ID
  - name: TEAM_KNOWLEDGE_ROOT
    value: "/opt/data/team-knowledge"

# Every agent keeps its private HERMES_HOME. The separate shared volume is only
# a durable knowledge base; it is never a task queue or coordination workspace.
extraVolumes:
  - name: team-knowledge
    persistentVolumeClaim:
      claimName: hermes-team-knowledge

extraVolumeMounts:
  - name: team-knowledge
    mountPath: /opt/data/team-knowledge

extraInitContainers:
  # Some local-path provisioners create a new PVC root as root:root 0700. The
  # gateway drops to uid/gid 10000, so make this agent's PRIVATE home traversable
  # after the chart has seeded config.yaml. This volume is never shared.
  - name: init-private-home
    image: busybox:1.37
    command: ["sh", "-c", "chown -R 10000:10000 /home"]
    volumeMounts:
      - name: data
        mountPath: /home

persistence:
  enabled: true
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 1Gi

```

## values-team-member.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-team-member.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-team-member.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-team-member.yaml"
# values-team-member.yaml
#
# One MEMBER of the Discord-thread-native leader team. Deploy one release per
# member with a unique bot token and private HERMES_HOME. Override
# fullnameOverride and TEAM_MEMBER_NAME per release. The member receives its
# entire task in a visible leader @mention and returns its entire result in a
# visible @mention to august. A separately provisioned hermes-team-knowledge RWX
# claim is mounted read-only for durable background knowledge; see the leader
# values header for the PVC manifest and permission requirements.
#
#   helm upgrade --install hermes-may ./charts/hermes-agent \
#     --namespace hermes-team --create-namespace \
#     -f charts/hermes-agent/values-team-member.yaml \
#     --set-string fullnameOverride=hermes-may \
#     --set-string 'extraEnv[6].value=may' \
#     --set-string env.NVIDIA_API_KEY='nvapi-<real>' \
#     --set-string env.DISCORD_BOT_TOKEN='<may-bot-token>' --wait

fullnameOverride: hermes-may

config:
  model:
    # Members may use a different provider/model from the leader. The Discord
    # thread protocol, not a shared model backend, is the collaboration layer.
    provider: nvidia
    default: z-ai/glm-5.2
  terminal:
    backend: local
  group_sessions_per_user: false
  discord:
    require_mention: true
    thread_require_mention: true
    auto_thread: true
    history_backfill: true
    history_backfill_limit: 50
    allow_mentions:
      everyone: false
      roles: false
      users: true
      replied_user: false
  display:
    tool_progress: "off"
  agent:
    # Files and memory remain available for the member's own work and durable
    # state. Alternate delegation/outbound paths stay disabled; task and result
    # transfer between agents must remain in Discord.
    disabled_toolsets:
      - browser
      - clarify
      - code_execution
      - cronjob
      - delegation
      - discord
      - discord_admin
      - messaging
      - session_search
      - skills
      - terminal
      - todo
      - web
    environment_hint: |
      You are "${TEAM_MEMBER_NAME}", a MEMBER of a Hermes agent team in one
      Discord thread. Your leader is "august". The leader's EXACT mention
      token is <@${AUGUST_BOT_USER_ID}>.

      The Discord thread is the team's ONLY shared task state and audit trail.
      You MAY use private files and memory for your own scratch work or durable
      state, but the leader must never need a path, file, memory entry, or hidden
      state to understand your result. NEVER use a hook, watcher, scheduler,
      background process, file write, memory update, API/tool call, or another
      bot to deliver, trigger, relay, or queue a result. The ONLY handoff is your
      same visible Discord response containing august's exact mention and the
      complete result.

      Durable shared knowledge is mounted read-only at ${TEAM_KNOWLEDGE_ROOT}.
      You MAY consult it as background, but never treat a new or changed file as
      a task signal and never wait or poll for file changes. The visible Discord
      task must contain all required context. Include any knowledge you relied on
      in your complete visible result; never answer with only a file path.

      Protocol:
      1. Act only when a message from august contains your exact bot mention and
         a [TEAM ... TASK] block. Ignore human requests, messages for another
         member, and unmentioned thread traffic.
      2. Read the visible Context, Task, Done when, and Reply contract fields.
         Perform only that task. Do not delegate it and do not ask the human.
      3. Return exactly one visible response. Put august's mention on the first
         line, then the COMPLETE result, evidence, assumptions, and any caveat.
         Put the TEAM metadata on its own FINAL line, like this:
           <@${AUGUST_BOT_USER_ID}>

           <complete result>

           [TEAM run=<same-id> step=<same-n> RESULT]
         Do not point to a local file or private state.
      4. If blocked, use the same leader mention and label the response BLOCKED;
         state one precise question plus the context needed to answer it.
      5. Mention august exactly once. Never mention another member or the human.
         Plain text such as "august", "@august", or "@hermes-august" reaches
         nobody and stalls the run; only the literal <@${AUGUST_BOT_USER_ID}>
         token triggers the leader. Never send filler. Your leader mention is
         the deterministic handoff that starts august's next turn.

env:
  NVIDIA_API_KEY: "nvapi-DUMMY_replace_me_0000000000000000000000"
  OPENAI_API_KEY: "unused"
  DISCORD_BOT_TOKEN: "MTA0DUMMYtoken000000000000.DUMMY.replace_me_with_a_real_token"

extraEnv:
  - name: DISCORD_HOME_CHANNEL
    value: "000000000000000000"       # DUMMY — same parent channel as leader
  - name: DISCORD_ALLOWED_USERS
    value: "111111111111111111"       # DUMMY — same trusted human IDs
  - name: DISCORD_ALLOW_BOTS
    value: "mentions"
  - name: DISCORD_THREAD_REQUIRE_MENTION
    value: "true"
  - name: DISCORD_REPLY_TO_MODE
    value: "off"
  - name: DISCORD_ALLOW_MENTION_REPLIED_USER
    value: "false"
  - name: TEAM_MEMBER_NAME
    value: "may"                      # per release: may or march
  - name: AUGUST_BOT_USER_ID
    value: "000000000000000000"       # DUMMY — leader's Discord user ID
  - name: TEAM_KNOWLEDGE_ROOT
    value: "/opt/data/team-knowledge"

# Private home plus the shared knowledge claim. The read-only member mount makes
# the leader the sole curator and prevents multi-writer races.
extraVolumes:
  - name: team-knowledge
    persistentVolumeClaim:
      claimName: hermes-team-knowledge

extraVolumeMounts:
  - name: team-knowledge
    mountPath: /opt/data/team-knowledge
    readOnly: true

extraInitContainers:
  - name: init-private-home
    image: busybox:1.37
    command: ["sh", "-c", "chown -R 10000:10000 /home"]
    volumeMounts:
      - name: data
        mountPath: /home

persistence:
  enabled: true
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi

resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 1Gi

```

## values-upstage.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values-upstage.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values-upstage.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values-upstage.yaml"
# values-upstage.yaml
#
# Hermes Agent using Upstage Solar's built-in OpenAI-compatible provider.
# Dummy key — override at install time.
#
#   helm upgrade --install hermes-agent ./charts/hermes-agent \
#     --namespace hermes-agent --create-namespace \
#     -f charts/hermes-agent/values-upstage.yaml \
#     --set-string env.UPSTAGE_API_KEY='<real>' --wait

config:
  model:
    provider: upstage
    # Hosted/business-tier model. For Upstage's open-weight flagship instead
    # (250B-A15B MoE, https://huggingface.co/upstage/Solar-Open2-250B),
    # use "solar-open2" — same provider, no other change needed. Verified
    # working end-to-end: https://github.com/jyje/pilot-upstage-solar-open2/tree/main/02-hermes-agent-solar-open2
    default: solar-pro3
  terminal:
    backend: local

env:
  UPSTAGE_API_KEY: "DUMMY_replace_me_0000000000000000000000"
  # Optional endpoint override (upstream default: https://api.upstage.ai/v1).
  # UPSTAGE_BASE_URL: "https://api.upstage.ai/v1"
  # Unused by the upstage provider; overrides the chart's OpenAI placeholder.
  OPENAI_API_KEY: "unused"

```

## values.yaml

<div class="raw-document-actions" data-raw-path="/hermes-agent-helm/source/charts/hermes-agent/values.yaml">
  <a href="/hermes-agent-helm/source/charts/hermes-agent/values.yaml">Open raw YAML</a>
  <button type="button" data-copy-source>Copy source</button>
</div>

```yaml title="charts/hermes-agent/values.yaml"
# Default values for hermes-agent.
# StatefulSet + ConfigMap (config.yaml) + Secret (.env) + Helm test.

# -- Override the chart name used in resource names.
nameOverride: ""
# -- Fully override the generated resource name (release-name-chart).
fullnameOverride: ""

image:
  # -- Container image repository (multi-arch: amd64 + arm64).
  repository: nousresearch/hermes-agent
  # -- Image tag. Upstream uses DATE-based tags (e.g. "v2026.6.5" ==
  # Hermes v0.16.0), plus `latest` / `main`. There is no semver tag.
  # Empty defaults to `.Chart.AppVersion`.
  tag: ""
  # -- Image pull policy.
  pullPolicy: IfNotPresent

# -- Image pull secrets for private registries.
imagePullSecrets: []

# -- Container entrypoint. The image's DEFAULT CMD is the interactive `hermes`
# chat, which exits immediately in a pod (no TTY -> EOF -> "Goodbye"), causing
# a restart loop. So run the long-lived gateway explicitly; inside the
# s6-overlay image `gateway run` is auto-redirected to the SUPERVISED s6
# service (auto-restart on crash). Append `--no-supervise` only if you want to
# bypass s6.
command: ["hermes"]
# -- Arguments appended to `command`.
args: ["gateway", "run"]

# ---------------------------------------------------------------------------
# Workload controller.
# "deployment" (default): no headless Service; when persistence is enabled, a
#   single standalone PVC (named <fullname>) is created and the rollout
#   strategy is forced to Recreate (so the new Pod doesn't race the old one
#   for the ReadWriteOnce volume). More resource-flexible (no StatefulSet
#   ordering/identity overhead) — the right choice for a single replica.
# "statefulset": stable identity, a dedicated PVC via volumeClaimTemplates
#   (data-<fullname>-0), and a headless Service for governance/DNS. Pick this
#   if you need StatefulSet semantics (ordered rollout, stable network
#   identity).
# Both render the same Pod spec (resources, env, probes, ...).
# ---------------------------------------------------------------------------
controller:
  # -- Workload kind: "deployment" or "statefulset".
  type: deployment

# -- DO NOT change this. Hermes Agent is a single-writer workload bound to one
# HERMES_HOME (ReadWriteOnce PVC). Raising replicaCount does NOT scale it out —
# with controller.type=deployment extra replicas just hang Pending (can't mount
# the same RWO volume); with statefulset they become separate, disconnected
# agent instances with their own PVC/identity. There is no supported
# multi-replica mode for this chart.
replicaCount: 1

serviceAccount:
  # -- Create a ServiceAccount for the pod.
  create: true
  # -- Name to use; generated from fullname when empty.
  name: ""
  # -- Annotations to add to the ServiceAccount.
  annotations: {}

# ---------------------------------------------------------------------------
# config.yaml -> Hermes reads $HERMES_HOME/config.yaml as a PARTIAL OVERRIDE on
# top of its version-specific built-in defaults (precedence: CLI > config.yaml >
# .env > built-in defaults). Only set the keys you want to change here; never
# reproduce the full upstream config (it drifts across versions and Hermes fills
# the rest in). This map is rendered into a ConfigMap and seeded into HERMES_HOME
# by an init container (see `bootstrap`). Keys below use the real v2026.6.5 schema.
#
# Hermes supports many providers (openai, anthropic, google, openrouter, and any
# OpenAI-compatible endpoint). Defaults use the provider's public endpoint —
# override to point anywhere (see values-litellm.yaml / values-litellm-k8s.yaml).
# ---------------------------------------------------------------------------
config:
  model:
    # Model id for the chosen provider (no vendor prefix for built-ins).
    default: gpt-4o-mini
    # Hermes provider key. Use a BUILT-IN key — common ones:
    #   openai-api (api.openai.com) | anthropic | gemini | openrouter |
    #   nvidia | deepseek | lmstudio | ...
    # NOTE: `openai` is NOT valid (it aliases to openrouter).
    # For an OpenAI-compatible proxy (LiteLLM / vLLM / LM Studio / ...), register
    # a custom provider under `config.providers` below and set this to that key
    # (see values-litellm.yaml / values-litellm-k8s.yaml).
    provider: openai-api
  # Custom OpenAI-compatible providers, keyed by provider id. Empty by default.
  #   providers:
  #     litellm:
  #       base_url: http://litellm.my-ns.svc.cluster.local:4000/v1
  #       key_env: OPENAI_API_KEY   # env var holding the key
  #       discover_models: true     # populate model picker from /v1/models
  providers: {}
  terminal:
    # Run the agent's shell/code execution INSIDE this pod. The pod itself
    # (namespace, securityContext, resource limits, PVC) is the sandbox.
    # The `docker` backend is intentionally NOT supported in-cluster: it needs
    # a Docker daemon/socket, which is a security risk and absent on containerd
    # clusters (e.g. MicroK8s / Raspberry Pi). Keep this `local`.
    backend: local
  agent:
    max_turns: 90
    gateway_timeout: 1800

# Seeding of config.yaml into HERMES_HOME (the persistent volume). Hermes writes
# to its home at runtime (skills, auth.json, self-improvement), so config lives
# in the writable volume rather than a read-only mount.
bootstrap:
  # -- Seed the rendered config.yaml into HERMES_HOME via an init container.
  enabled: true
  # -- true: overwrite HERMES_HOME/config.yaml with chart content on every
  #    deploy (declarative). false: seed only if it does not already exist
  #    (preserve runtime edits).
  overwrite: true

# ---------------------------------------------------------------------------
# .env / secrets -> Hermes reads API keys from the environment, which take
# precedence over config.yaml. Keys are rendered into a Secret and injected via
# envFrom (not written as a .env file). Override at deploy time, e.g.
#   --set-string env.OPENAI_API_KEY=sk-...
# Provider key names: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY,
# NVIDIA_API_KEY, OPENROUTER_API_KEY, LM_API_KEY (LM Studio), ...
# ---------------------------------------------------------------------------
env:
  OPENAI_API_KEY: "sk-REPLACE_ME"

# -- Plain (non-secret) env vars injected directly on the container.
extraEnv: []
#  - name: HERMES_ACCEPT_HOOKS
#    value: "1"

# -- Extra envFrom sources (reference existing ConfigMaps/Secrets).
extraEnvFrom: []
#  - secretRef:
#      name: some-existing-secret

# -- Extra volumes on the pod, for anything the agent needs as a FILE rather
#    than an env var — e.g. a Secret holding a service-account JSON
#    (see values-google-vertex.yaml).
extraVolumes: []
#  - name: vertex-sa
#    secret:
#      secretName: vertex-sa

# -- Extra volume mounts on the hermes-agent container (pairs with extraVolumes).
extraVolumeMounts: []
#  - name: vertex-sa
#    mountPath: /var/run/secrets/vertex
#    readOnly: true

# -- Extra init containers, appended after the chart's own (seed-config,
#    device-flow login). Full container spec; combine with `extraVolumes` for
#    one-time preparation of a user-provided volume (for example, a shared
#    knowledge volume used independently of the Discord team handoff).
extraInitContainers: []
#  - name: init-workspace
#    image: busybox:1.37
#    command: ["sh", "-c", "chown 10000:10000 /work"]
#    volumeMounts:
#      - name: team-workspace
#        mountPath: /work

# -- Extra raw manifests rendered as-is alongside this chart's resources.
#    Each entry is `tpl`-rendered, so `{{ .Release.Namespace }}` etc. work, and
#    may be either an object or a multiline string (see examples/argocd/).
#    Useful for things this chart doesn't model directly, e.g. a SealedSecret
#    that a sealed-secrets controller decrypts into a Secret referenced via
#    `extraEnvFrom` (see examples/argocd/).
extraResources: []

# ---------------------------------------------------------------------------
# auth -> Interactive credential bootstrap.
#
# By default the agent authenticates with the static provider key from `env`
# (rendered into the `-env` Secret). `auth.deviceFlow` is an alternative for
# providers that issue short-lived/OAuth tokens you cannot paste ahead of time:
# it performs the **OAuth 2.0 Device Authorization Grant (RFC 8628)** at pod
# startup, surfaces the verification URL + user code to a human (e.g. via the
# agent's Discord bot, mobile-friendly), waits for approval, and persists the
# resulting token to `HERMES_HOME/.env` — exactly where Hermes natively reads
# it. The token survives restarts on the persistent volume; re-login only
# happens when it is missing or revoked.
#
# Currently supports **github-copilot** (Hermes provider id `copilot`), whose
# API rejects PATs and requires a `gho_`/`ghu_` device-flow token.
# ---------------------------------------------------------------------------
auth:
  deviceFlow:
    # -- Bootstrap a provider credential via the OAuth device flow at startup.
    #    When false, the agent uses the static key from `env`/`extraEnvFrom`.
    enabled: false
    # -- Which provider profile to authenticate. Must be a key under
    #    `providers` below. Only one device-flow login runs at a time.
    provider: github-copilot
    # -- Where to deliver the verification URL + user code for human approval.
    #    `discord` reuses the agent's bot creds (DISCORD_BOT_TOKEN +
    #    DISCORD_HOME_CHANNEL from `env`/`extraEnvFrom`). The code is always
    #    also printed to the init container logs as a fallback.
    notify: discord
    # -- Seconds to wait for the human to authorize before the init container
    #    fails (and retries). Keep below the provider's device-code validity.
    timeoutSeconds: 870
    # -- Force a fresh login even if a token already exists on the volume.
    forceRelogin: false
    # -- uid/gid that should own the written token file. The login init
    #    container runs as root so it can write to any storage class reliably,
    #    then chowns the token to this owner. Set it to the Hermes runtime uid —
    #    the upstream image's s6-overlay runs the agent as uid/gid 10000 — so the
    #    non-root agent can read the credential.
    tokenOwner:
      uid: 10000
      gid: 10000
    # -- Login image. stdlib-only Python; no extra dependencies are installed.
    image:
      repository: python
      tag: "3.13-slim"
    # -- Resources for the login init container.
    resources: {}
    # Catalog of device-flow-capable providers. The chart ships sane defaults;
    # the selected one (`provider` above) is what runs. Add an entry to support
    # another provider (each provider uses its own OAuth authorization server).
    providers:
      github-copilot:
        # -- OAuth client id for the device grant. The shared opencode/Copilot-CLI
        #    client that Hermes upstream itself uses (hermes_cli/copilot_auth.py).
        clientId: "Ov23li8tweQw6odWQebz"
        # -- OAuth scope requested in the device grant.
        scope: "read:user"
        # -- Host serving the device-code + token endpoints (GitHub-style paths).
        authHost: github.com
        # -- .env key Hermes reads this provider's token from (resolution order
        #    COPILOT_GITHUB_TOKEN > GH_TOKEN > GITHUB_TOKEN).
        tokenEnv: COPILOT_GITHUB_TOKEN
        # -- Optional endpoint to verify an existing token is still live; on
        #    401/403 the init container re-runs the login. Empty = skip the check.
        validateUrl: https://api.github.com/copilot_internal/v2/token

# ---------------------------------------------------------------------------
# Persistence: HERMES_HOME state lives here.
# ---------------------------------------------------------------------------
persistence:
  enabled: true
  # -- StorageClass for the volumeClaimTemplate. Empty = cluster default.
  storageClass: ""
  accessModes:
    - ReadWriteOnce
  size: 5Gi
  mountPath: /opt/data
  # -- Use an existing PVC instead of creating a new one.
  # When specified, the chart will use this PVC and skip creating its own.
  existingClaim: ""

# ---------------------------------------------------------------------------
# Networking. `hermes gateway run` is primarily OUTBOUND (Telegram/Discord/etc.)
# and exposes no inbound API, so no access Service is created by default. A
# headless Service is always created for StatefulSet DNS/governance.
#
# The only inbound HTTP surface is the management `dashboard` (default port
# 9119, binds to 127.0.0.1). Exposing it cluster-wide requires `--insecure`,
# which the upstream warns EXPOSES API KEYS on the network — so it is opt-in.
# ---------------------------------------------------------------------------
service:
  # -- Create a ClusterIP Service (only useful if you expose the dashboard).
  enabled: false
  # -- Service type.
  type: ClusterIP
  # -- Service port (and the dashboard's container port).
  port: 9119
  # -- Annotations to add to the Service.
  annotations: {}

# Ingress for the management dashboard. Requires `service.enabled: true` AND
# the dashboard running with --insecure (see the `service` comment above for
# the API-key exposure warning) — only enable this behind authentication
# (e.g. an ingress-level oauth2-proxy/basic-auth annotation) or on a private
# network.
ingress:
  # -- Create an Ingress resource.
  enabled: false
  # -- IngressClass name (e.g. "nginx", "traefik"). Empty uses the cluster default.
  className: ""
  # -- Annotations to add to the Ingress (e.g. auth, cert-manager, rewrite rules).
  annotations: {}
  # -- Host/path rules, all routed to the Service port above.
  hosts:
    - host: hermes-agent.example.com
      paths:
        - path: /
          pathType: Prefix
  # -- TLS configuration for the Ingress.
  tls: []
  #  - secretName: hermes-agent-tls
  #    hosts:
  #      - hermes-agent.example.com

# -- Container resource requests/limits. Lightweight defaults aimed at small
# clusters (incl. Raspberry Pi / arm64).
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "2"
    memory: "2Gi"

# -- Pod-level securityContext. Left empty by default to stay compatible with
# the image's s6-overlay init (which starts as root and drops privileges
# itself). Add hardening here once verified for your environment.
podSecurityContext: {}
#  fsGroup: 1000

# -- Container-level securityContext. Same caveat as `podSecurityContext` above.
securityContext: {}
#  allowPrivilegeEscalation: false
#  capabilities:
#    drop: [ALL]

# -- Health probes. Empty = none. The image's s6-overlay already supervises and
# auto-restarts the gateway in-container, so k8s probes are optional. Provide a
# full probe spec to enable, e.g. an exec check:
#   liveness:
#     exec: { command: ["hermes","gateway","status"] }
#     initialDelaySeconds: 30
#     periodSeconds: 30
probes:
  # -- Liveness probe spec. Empty = no liveness probe.
  liveness: {}
  # -- Readiness probe spec. Empty = no readiness probe.
  readiness: {}

# -- Pod termination grace period in seconds. Empty = Kubernetes default (30s).
# The gateway (image v2026.7.1+) defaults `agent.restart_drain_timeout` to 0:
# on stop it interrupts in-flight runs immediately, persists the transcript,
# and exits fast — the default grace period is plenty. If you opt into a drain
# window via `config.agent.restart_drain_timeout: <seconds>`, raise this WELL
# ABOVE that value or the kubelet SIGKILLs the gateway mid-drain (stale lock +
# crash loop — the same race upstream warns about with systemd's
# TimeoutStopSec). See "Gateway lifecycle" in the README.
terminationGracePeriodSeconds: ""

# ---------------------------------------------------------------------------
# Helm test (chart test). `helm test <release>` runs a doctor-style Job
# (helm.sh/hook: test) AFTER install to verify the deployment. Rendered by
# default; set tests.enabled=false to skip it entirely.
# ---------------------------------------------------------------------------
tests:
  # -- Render the chart test Job.
  enabled: true
  # -- Image used by the test Job. Empty fields fall back to the main
  # `image.*` (so the hermes CLI + doctor are available and arch matches).
  image:
    repository: ""
    tag: ""
    pullPolicy: ""
  # -- When true, `hermes doctor` issues fail the test. When false, doctor runs
  #    for visibility but only hard checks (hermes --version, seeded config) fail.
  doctorStrict: false
  # -- Seconds to allow `hermes doctor` to run before timing out.
  doctorTimeout: 120
  # ---------------------------------------------------------------------------
  # Optional real model round-trip: `hermes chat -q "<prompt>"` against the
  # configured provider. The full conversation (prompt + response) is printed
  # to the test Job's logs. Requires a working provider key in `env`/`config`
  # (e.g. config.model.provider=gemini + env.GOOGLE_API_KEY, or a LiteLLM-style
  # custom provider — see values-litellm.yaml). Off by default since the
  # placeholder key cannot reach a real provider.
  # ---------------------------------------------------------------------------
  chat:
    # -- Run a `hermes chat` round-trip and log the conversation.
    enabled: false
    # -- Prompt sent to the agent.
    prompt: "Just say hi."
    # -- Max agent turns for the round-trip.
    maxTurns: 1
    # -- Seconds to allow each round-trip attempt to run before timing out.
    timeout: 180
    # -- When true, a failed/empty round-trip fails the test job.
    failOnError: false
    # -- Optional pool of `provider/model` ids to try in order (via `hermes chat
    #    -m <id> --provider config.model.provider`), each with its own `timeout`.
    #    Passes as soon as one succeeds — useful for free-tier models that are
    #    sometimes overloaded. Leave empty to use `config.model.default` as-is
    #    (single attempt, no `-m`/`--provider` override).
    models: []
  # -- Resource requests/limits for the test Job's container.
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: "1"
      memory: 512Mi

# -- Annotations to add to the Pod.
podAnnotations: {}
# -- Labels to add to the Pod.
podLabels: {}

# -- Node selector for Pod scheduling.
nodeSelector: {}
# -- Tolerations for Pod scheduling.
tolerations: []
# -- Affinity rules for Pod scheduling.
affinity: {}

```