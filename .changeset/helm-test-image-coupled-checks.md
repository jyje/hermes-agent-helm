---
"@jyje/hermes-agent-helm": patch
---

Feature(test): Helm test guards the two paths that depend on the Hermes image

The Helm test Job now checks, only when the feature is on, that the pinned Hermes image still provides the helpers the OpenAI Codex device login imports from `hermes_cli.auth`, and that Hermes discovers and fires the seeded `gateway:startup` ready-message hook. Both run in CI on every image bump, in the post-release verification, and in your own `helm test`. A failure names what is missing instead of breaking the login or the ready message silently.
