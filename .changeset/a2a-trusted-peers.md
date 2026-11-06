---
"@jyje/hermes-agent-helm": patch
---

Fix(a2a): Authorize named peers in the A2A example

Pair per-peer tokens from an external Secret with matching trusted peer names so authenticated clients can send work through the example Service.
When switching from the shared-token example, update the existing Secret and clients before applying the new overlay.
