---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Nous free-tier overlay

Add `values-nous.yaml`, a zero-key overlay that enables the v2026.9.11 Nous free tier (`nous/welcome` inference plus connector tools) via `HERMES_GUEST_ONBOARDING=1`, and document that env var in the README's environment variable reference.
