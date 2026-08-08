---
title: Advanced
description: Configure, integrate, operate, and extend Hermes Agent deployments.
---

Advanced guidance starts with the chart's base `values.yaml` and adapts it through partial overlays. Hermes provides version-specific defaults while your environment injects secrets separately.

## Choose by outcome

- **Configure the chart:** understand the configuration model, secrets, storage, and tests.
- **Connect a model:** provider pages cover public APIs and the GitHub device-login flow.
- **Connect a proxy or bot:** integration pages cover LiteLLM, Discord, Telegram, and the protected dashboard.
- **Coordinate agents:** patterns and team guides cover secrets managers, shared storage, collaboration, and teams.

Never commit real keys into an overlay. Each example documents the required Secret and an install command with placeholder values.
