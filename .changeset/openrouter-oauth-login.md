---
"@jyje/hermes-agent-helm": patch
---

Documentation(providers): Sign in to OpenRouter from a running pod

Document `hermes auth add openrouter --type oauth` (new in `v2026.9.14`) as an explicit, interactive procedure: install without a static key, sign in through `kubectl exec -it` with `SSH_TTY` set so Hermes uses OpenRouter's paste-the-code flow instead of an unreachable in-pod browser callback, and confirm with `hermes auth list`. Explain that this is an OAuth authorization-code flow rather than a device-code flow, so `auth.deviceFlow` does not automate it; that the result is a plain API key stored in `auth.json` on the persistent volume; and how priority, expiry and rotation behave. English and Korean OpenRouter guides are updated together.
