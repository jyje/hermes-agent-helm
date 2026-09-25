---
title: Secrets and persistence
description: Supply credentials safely and preserve Hermes state without turning the values file into a secret store.
---

## Credentials

The chart uses `envFrom` to make the chart-managed Secret available to Hermes. Environment variables win over `config.yaml`, so provider credentials belong in `env` or `extraEnvFrom`, not in a checked-in `.env` file.

For production, create a Secret outside Helm and reference it with `extraEnvFrom`; the Bitwarden example documents an alternative bootstrap pattern.

### External Secrets Operator

Set `externalSecret.enabled: true` to have the chart render an ExternalSecret instead of its own Secret. This is a replacement, not an addition: the chart's Secret stops rendering, `env` is ignored, and every chart-owned `envFrom` (main container, auth device-login init container, helm test Job) automatically follows the ExternalSecret's target name - no `extraEnvFrom` needed. Requires the External Secrets Operator CRDs already installed in-cluster; point `externalSecret.secretStoreRef` at an existing SecretStore/ClusterSecretStore and populate `externalSecret.data`/`dataFrom`.

The chart's pod template checksum picks up changes to the ExternalSecret's `target`/`data`/`dataFrom`, so editing those in values still triggers a rollout. It does not cover the reverse: when the *external provider* rotates a secret's contents later, ESO refreshes the target Secret on its own schedule, but nothing restarts the running Pod to pick up the new value. That's a reloader controller's job (e.g. Reloader, Stakater); this chart doesn't bundle one.

## Persistent home

The default persistent volume is intentionally modest. It stores config, login state, sessions, and agent memory. Scale its size or storage class through values. Shared agent knowledge is a separate concern: use an RWX volume only when multiple agents genuinely need the same writable directory.

### Choosing storage for HERMES_HOME

Hermes keeps its session store (`state.db`) and other SQLite databases in `HERMES_HOME`, in WAL journal mode by default. WAL relies on byte-range locks and shared memory working correctly across every process that opens the file. A PVC's access mode (`ReadWriteOnce` or `ReadWriteMany`) does not tell you whether the filesystem underneath provides that. Access modes describe who may mount the volume, not how the filesystem behaves.

Prefer block-backed storage (ext4 or xfs, which is what most `ReadWriteOnce` storage classes provide). Before relying on a storage class, check the filesystem that is actually mounted at `persistence.mountPath`:

```bash
kubectl exec deploy/hermes-agent -c hermes-agent -- sh -c 'grep " /opt/data " /proc/self/mountinfo'
```

What Hermes itself detects is narrow. Since `v2026.9.14` it recognizes cross-VM filesystems, specifically `virtiofs` and `9p`, and treats them as unsafe for WAL:

- A **fresh** database on such a mount is created with `delete` journaling instead.
- A database that is **already in WAL mode on disk** is never silently downgraded. Hermes keeps WAL and logs an error.
- Code paths that require WAL fail with an explicit error rather than continuing.

NFS and CIFS are **not** flagged by that detector. That is not a statement that WAL is safe there. If `HERMES_HOME` has to live on a network filesystem, set the journal mode explicitly before the first start:

```yaml
config:
  database:
    journal_mode: delete
```

Do not switch an existing database by flipping this value on a running agent. To convert one, scale the workload to zero (`replicaCount: 0`) so nothing has the file open, back up `HERMES_HOME`, run a one-time offline `PRAGMA journal_mode=DELETE` on the database file, then set `journal_mode: delete` and scale back up. The same stop-the-writer rule applies to backups and PVC migrations in general: copy `HERMES_HOME` only while the agent is scaled to zero.

Keep one private `HERMES_HOME` per agent. Two agents must never share one home, even on `ReadWriteMany` storage. Knowledge that several agents should see belongs on the separate `team.sharedVolume`.
