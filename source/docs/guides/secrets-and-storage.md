---
title: Secrets and persistence
description: Supply credentials safely and preserve Hermes state without turning the values file into a secret store.
---

## Credentials

The chart uses `envFrom` to make the chart-managed Secret available to Hermes. Environment variables win over `config.yaml`, so provider credentials belong in `env` or `extraEnvFrom`, not in a checked-in `.env` file.

For production, create a Secret outside Helm and reference it with `extraEnvFrom`; the Bitwarden example documents an alternative bootstrap pattern.

## Persistent home

The default persistent volume is intentionally modest. It stores config, login state, sessions, and agent memory. Scale its size or storage class through values. Shared agent knowledge is a separate concern: use an RWX volume only when multiple agents genuinely need the same writable directory.