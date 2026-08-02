---
title: Install
description: Install Hermes Agent from this Helm repository.
sidebar:
  order: 10
---

## Install from the Helm repository

```bash
helm repo add <repository-name> https://jyje.github.io/hermes-agent-helm
helm repo update
helm upgrade --install <release-name> <repository-name>/hermes-agent \
  --namespace <namespace> --create-namespace
```

Use the chart’s [base values reference](/hermes-agent-helm/charts/hermes-agent/reference/values/) and choose a [values overlay](/hermes-agent-helm/charts/hermes-agent/overlays/) before deploying.
