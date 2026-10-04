---
"@jyje/hermes-agent-helm": patch
---

Feature(dashboard): Trusted proxy warning

Print a warning in the release notes when the dashboard is served over HTTPS but no trusted proxy is set, because sign-in still works while the session cookies are not marked Secure.
