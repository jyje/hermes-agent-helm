---
"@jyje/hermes-agent-helm": patch
---

Documentation(dashboard): Prefer dashboard.enabled

Explain that setting `HERMES_DASHBOARD=1` yourself in `extraEnv` or `env` skips the readiness probe, the derived `public_url` and `trusted_proxies`, the auth-provider check, and the trusted-proxy warning, and how to add your own readiness probe if you keep the variable.
