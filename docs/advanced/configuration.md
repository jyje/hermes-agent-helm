---
title: Configuration model
description: Understand how config.yaml, environment variables, Secrets, and the persistent Hermes home work together.
---

## Precedence

Hermes merges partial chart configuration with its built-in version-specific defaults. The effective precedence is **CLI > config.yaml > environment > built-in defaults**. The chart therefore does not attempt to reproduce the complete upstream configuration.

## Why configuration is seeded

The chart seeds `config.yaml` into `$HERMES_HOME` with an init container. It is not mounted read-only: Hermes writes runtime state in its home directory. The default `bootstrap.overwrite: false` seeds only when the file is absent, preserving runtime edits across upgrades. Set it to `true` to replace the file with chart values on every rollout. After seeding or preserving the file, the init container runs Hermes' non-interactive config migration and backs up `config.yaml` and `.env` before changing them. Configs with no explicit version are migrated; configs that explicitly declare a version below Hermes' support floor are left untouched and require the operator recovery documented in the [chart README](../../charts/hermes-agent/README.md#recovering-a-config-older-than-the-migration-floor).

## Controller choice

Use a Deployment for the normal single-agent case. Use a StatefulSet when stable pod identity matters to your workload. Neither mode creates a Namespace; choose it through Helm's `--namespace` flag.
