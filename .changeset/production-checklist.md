---
"@jyje/hermes-agent-helm": patch
---

Documentation(docs): Add a Production Checklist to the repo README

Add a "Production Checklist" table (English and Korean) covering Pod
Security Standards, egress control, kernel isolation, secret management, and
upgrade safety, each row pointing at what actually backs the claim (a CI
scenario, or "documented only" where no automated check exists yet) instead
of a bare `production-ready` label.
