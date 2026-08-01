---
sidebar:
  label: Examples
  order: 20
  attrs:
    data-sidebar-order: '20'
title: Choose a values example
description: Start from a runnable overlay, then replace only its dummy credentials and environment-specific identifiers.
---

Every example is an overlay for `charts/hermes-agent/values.yaml`. It is deliberately partial: Hermes adds its version-specific defaults and your environment injects secrets separately.

## Pick by outcome

- **Connect a model:** provider pages cover public APIs and the GitHub device-login flow.
- **Connect a proxy or bot:** integration pages cover LiteLLM, Discord, Telegram, and the protected dashboard.
- **Coordinate agents:** advanced pages cover secrets managers, shared storage, collaboration, and teams.

Never commit real keys into an overlay. Each example documents the required Secret and an install command with placeholder values.