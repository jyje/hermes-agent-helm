---
"@jyje/hermes-agent-helm": patch
---

Documentation(dashboard): Fix stale dashboard guidance

Rewrite the ArgoCD ingress example so it actually enables the dashboard with its own password provider (credentials from a Secret), and correct the security docs: the dashboard binds all interfaces inside the container, an auth provider is mandatory, and `--insecure` is a deprecated no-op.
