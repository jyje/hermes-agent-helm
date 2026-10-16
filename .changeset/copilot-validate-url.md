---
"@jyje/hermes-agent-helm": patch
---

Fix(auth): Copilot device login no longer repeats on every restart

The default `validateUrl` for `github-copilot` was `https://api.github.com/copilot_internal/v2/token`. On a GitHub Copilot Free account that endpoint answered 403 for a valid token, and the init container treats 403 as invalid, so every restart asked for a new login code. The default is now `https://api.github.com/user`, which answers 401 only for a revoked token and does not depend on the Copilot plan.
