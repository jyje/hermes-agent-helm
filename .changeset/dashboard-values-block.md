---
"@jyje/hermes-agent-helm": minor
---

Feature(dashboard): First-class dashboard values

Add a `dashboard` values block that starts the management dashboard, derives `config.dashboard.public_url` from the Ingress host, sets `trusted_proxies`, and fails at render time when the selected auth provider (`basic`, `oauth`, `oidc`) has no credentials, instead of leaving an Ingress that answers 502/503. Use `dashboard.auth.provider: external` when credentials come from `extraEnvFrom` or an ExternalSecret.
