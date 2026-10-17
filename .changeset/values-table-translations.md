---
"@jyje/hermes-agent-helm": patch
---

Documentation(locales): The Values table in the translated chart READMEs is current again

The Korean, Japanese and Simplified Chinese chart READMEs carried a hand-copied Values table that had drifted: it lacked the `dashboard.*`, `readyNotify.*` and other newer rows and still showed the old Copilot `validateUrl` default. `make docs` now copies the generated English table into them, and CI fails if a copy differs, so they stay in step with `values.yaml`.
