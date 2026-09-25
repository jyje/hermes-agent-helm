---
"@jyje/hermes-agent-helm": minor
---

Fix(persistence): Migrate persisted Hermes config

Run Hermes' non-interactive config migration after chart seeding, with backups and a documented recovery path for configs below the upstream migration floor.
