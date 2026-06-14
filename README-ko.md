<div align="center">

# jyje/hermes-agent

<img width="640" src="https://raw.githubusercontent.com/NousResearch/hermes-agent/main/assets/banner.png" alt="Hermes Agent"/>

⚓ A community-powered, lightweight Helm chart to run **Hermes Agent** on Kubernetes

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)

[English](README.md) · [한국어](README-ko.md) · [Chart docs](charts/hermes-agent/README.md) · [CONTRIBUTING](CONTRIBUTING.md) · [AGENTS](AGENTS.md)


---

**Found this useful? Please give it a ⭐ — it helps others find it.**

</div>

## Summary

`hermes-agent` is a **community-powered** Helm chart that packages
[Hermes Agent](https://github.com/NousResearch/hermes-agent)
(`nousresearch/hermes-agent`) as a Kubernetes **Deployment or StatefulSet**
(`controller.type`), with `config.yaml` managed as a **ConfigMap** and `.env`
as a **Secret**. It is not an official Nous Research release — it's
maintained in the open by the community.

## Provider-agnostic

The whole point of this chart is that it does **not** lock you to any vendor or
endpoint. Hermes supports many LLM providers — `openai`, `anthropic`, `google`,
`openrouter`, and any OpenAI-compatible endpoint such as
[LiteLLM](https://github.com/BerriAI/litellm). Chart defaults stay neutral
(point at a provider's public endpoint); you wire it to whatever you run purely
through `values.yaml`. No provider is baked into the templates.

## Lightweight

Defaults target **small clusters** (homelab / single-node / edge). Resource
requests and limits are intentionally modest, and the workload runs a single
replica with a small persistent volume. Scale `resources`, `replicaCount`, and
`persistence.size` up via values when you need more.

## Layout

```
charts/hermes-agent/                     # the Helm chart (see its README for the full values table)
charts/hermes-agent/values.example.yaml  # example overrides (custom OpenAI-compatible provider + persistence)
examples/helm/                           # install from Git and from OCI (ghcr.io) + publish guide
examples/argocd/                         # ArgoCD Application + safe multi-instance guide
.github/workflows/                       # ci (lint + docs drift + kind test) and release (version bump -> tag -> ghcr OCI)
CONTRIBUTING.md                          # branch model (dev/main + tags) + release-on-version-bump
AGENTS.md                                # design principles & workflow for contributors
Makefile                                 # docs / lint / template / install / test / package / push
```

## Quick start

```bash
# render & lint
make template
make lint

# install with the generic defaults (set your provider key)
# release name == chart name keeps resources clean (hermes-agent-0, not hermes-agent-hermes-agent-0)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1

# or use an environment-specific values file
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values.example.yaml \
  --set-string env.OPENAI_API_KEY='sk-...' --wait
```

## Docs

Chart docs are generated with [helm-docs](https://github.com/norwoodj/helm-docs)
from `charts/hermes-agent/README.md.gotmpl` + the `# --` annotations in
`values.yaml`:

```bash
make docs   # regenerate charts/hermes-agent/README.md
```

## Releasing

The chart `version` in `Chart.yaml` is the source of truth. Bump it (+ `make
changelog`) and merge to `main`; CI tags `vX.Y.Z`, writes release notes
(git-cliff), and publishes the chart to `oci://ghcr.io/<owner>` (GitHub
Packages). The `.tgz` is built in CI, never committed. Register the OCI repo once
on [Artifact Hub](https://artifacthub.io/) — `Chart.yaml` already carries the
`artifacthub.io/*` annotations.

Branches: `dev` (experimental) → `main` (PR target, releases cut here). See
[CONTRIBUTING.md](CONTRIBUTING.md) for the flow and
[examples/helm/](examples/helm/) for install/publish details.

---

> Banner © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
