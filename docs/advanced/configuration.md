---
title: Configuration model
description: Understand how config.yaml, environment variables, Secrets, and the persistent Hermes home work together.
---

## Precedence

Hermes merges partial chart configuration with its built-in version-specific defaults. The effective precedence is **CLI > config.yaml > environment > built-in defaults**. The chart therefore does not attempt to reproduce the complete upstream configuration.

## Why configuration is seeded

The chart seeds `config.yaml` into `$HERMES_HOME` with an init container. It is not mounted read-only: Hermes writes runtime state in its home directory. Set `bootstrap.overwrite: true` to reseed on each rollout, or keep the default seed-if-absent behavior to preserve edits.

## Controller choice

Use a Deployment for the normal single-agent case. Use a StatefulSet when stable pod identity matters to your workload. Neither mode creates a Namespace; choose it through Helm's `--namespace` flag.