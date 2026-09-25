---
"@jyje/hermes-agent-helm": patch
---

Documentation(storage): Explain which filesystems suit HERMES_HOME's SQLite databases

Explain that a PVC access mode does not establish the file locking and shared memory that SQLite WAL needs, and how to check the filesystem actually mounted at `persistence.mountPath`. Describe what Hermes detects since `v2026.9.14` (virtiofs and 9p: fresh databases fall back to `delete` journaling, existing WAL databases are never downgraded live, WAL-required paths fail explicitly) and what it does not (NFS, CIFS), with `config.database.journal_mode: delete` for network filesystems set before the first start and an offline, scaled-to-zero conversion for existing databases. English and Korean storage guides and the `persistence` values comment are updated together.
