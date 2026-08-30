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