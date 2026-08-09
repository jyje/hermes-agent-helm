---
"@jyje/hermes-agent-helm": patch
---

Fix(runtime): Preserve the Hermes image entrypoint

Keep the pinned image's s6 startup and volume ownership preparation while passing `gateway run` through the image entrypoint.
