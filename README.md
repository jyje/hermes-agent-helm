<div align="center">

# jyje/hermes-agent-helm

<img height="96" src="https://raw.githubusercontent.com/cncf/artwork/main/projects/kubernetes/icon/color/kubernetes-icon-color.png" alt="Kubernetes" align="middle"/>&nbsp;<font size="6"><b>×&nbsp;</b></font>&nbsp;<img height="96" src="https://hermes-agent.nousresearch.com/docs/img/logo.png" alt="Hermes Agent" align="middle"/>

👩🏻‍💻 A Helm chart to run **Hermes Agent** on Kubernetes, community-powered, lightweight

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3%2B-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/hermes-agent)](https://artifacthub.io/packages/search?repo=hermes-agent)

[English](README.md) · [한국어](README-ko.md) · [Chart docs](charts/hermes-agent/README.md) · [CONTRIBUTING](CONTRIBUTING.md) · [AGENTS](AGENTS.md)

---

**Found this useful? Please give it a ⭐ — it helps others find it.**

</div>

## Summary

Run [Hermes Agent](https://github.com/NousResearch/hermes-agent) on Kubernetes
with one `helm install` — works with any LLM provider Hermes supports, scales
down to a single small node, and is verified to actually run, not just render.
A **community-powered** chart, not an official Nous Research release.

## Getting started

Add the Helm repository (published to GitHub Pages) and install:

```bash
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update
helm install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' \
  --wait
```

Each release is also published as an OCI artifact, so you can install
directly from the registry without `helm repo add`:

```bash
helm install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' \
  --wait
```

Optionally pin `--version` to a specific [released chart version](https://github.com/jyje/hermes-agent-helm/releases) instead of latest.

To install from this repo's source instead (e.g. to try an unreleased
change), see [Quick start](#quick-start) below.

## Why this chart

- **All of Hermes's provider support, via `values.yaml`.** Hermes itself
  already supports `openai-api`, `anthropic`, `gemini`, `openrouter`, `nvidia`,
  `deepseek`, and any OpenAI-compatible endpoint (e.g.
  [LiteLLM](https://github.com/BerriAI/litellm)) through environment
  variables — this chart just exposes that config through `values.yaml` and
  ships ready-to-adapt examples per provider, with no provider baked into the
  templates.
- **Lightweight → production.** Sized for homelab / single-node / edge clusters
  out of the box (one replica, modest requests, a small PVC), and ready for
  production by scaling *up* — not *out*. Hermes is a single-instance personal
  agent (one `HERMES_HOME`, one gateway, one memory), so you don't replicate a
  pod; you run several well-managed instances and group them into a **team**
  that shares context over a common gateway channel. See
  [Hermes teams](docs/teams.md).
- **Verified end-to-end.** CI installs the chart on an ephemeral **kind**
  cluster and runs the bundled test Job (`hermes doctor`), plus a **live
  `hermes chat` round-trip** against a real NVIDIA NIM account — not a mock.
  🔜 Telegram/Discord round-trip verification is still a placeholder.

For the full resource breakdown, configuration model, and provider-by-provider
install examples (including messenger integrations), see
[charts/hermes-agent/README.md](charts/hermes-agent/README.md).

## Repository layout

```
charts/hermes-agent/                     # the Helm chart (see its README for the full values table)
charts/hermes-agent/values-*.yaml        # ready-to-adapt examples: providers, Discord/Telegram, LiteLLM (see chart README "More examples")
examples/helm/                           # install from Git and from OCI (ghcr.io) + publish guide
examples/argocd/                         # ArgoCD Application examples (one per values-*.yaml) + GitOps/SealedSecret pattern
charts/hermes-operator/                  # ⏸️ long-term, not started: possible install chart for an Agent/AgentTeam-CRD operator — placeholder, TBA (see Roadmap)
docs/                                    # deeper guides: teams.md (group instances into a team), collaboration.md (make them hand off by @mention), roadmap.md
.github/workflows/                       # ci (lint + docs-drift + real round-trip on kind) and release (version bump -> tag -> ghcr OCI)
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

# or start from a ready-made example (provider, Discord/Telegram, LiteLLM, ...)
helm upgrade --install hermes-agent ./charts/hermes-agent \
  --namespace hermes-agent --create-namespace \
  -f charts/hermes-agent/values-anthropic-and-discord.yaml \
  --set-string env.ANTHROPIC_API_KEY='sk-ant-...' \
  --set-string env.DISCORD_BOT_TOKEN='...' --wait
```

See [charts/hermes-agent/README.md](charts/hermes-agent/README.md) for the full
values table, the "More examples" table (`values-*.yaml` for every supported
provider plus Discord/Telegram and LiteLLM), and an
[ArgoCD example](examples/argocd/).

## Development

Branch model, release process, and local checks (`make lint` / `make docs` /
`make test`) are covered in [CONTRIBUTING.md](CONTRIBUTING.md); chart design
principles are in [AGENTS.md](AGENTS.md).

## CI/CD

- **Every PR and every push to `dev`/`main`** runs [validate-chart.yaml](.github/workflows/validate-chart.yaml):
  `helm lint`, `helm template`, a chart-docs drift check, and a full install +
  test on an ephemeral **kind** cluster (real `hermes chat` round-trip when an
  `NVIDIA_API_KEY` secret is available).
- **Releases are version-bump-driven, not tag-push-driven.** Run
  [propose-release.yaml](.github/workflows/propose-release.yaml) (Actions →
  "📋 propose-release"): it diffs `main` against the last release tag, builds the
  changelog **deterministically** (git-cliff), asks **NVIDIA NIM** to recommend
  a semver bump + summary (graceful heuristic fallback when no key), and
  opens/updates a single **release PR** crediting every commit & PR author.
  Adjust the version if you disagree, then merge. (Or skip the proposal and bump
  `Chart.yaml` yourself / comment `/version vX.Y.Z`.) Once that PR merges to
  `main`, [release-chart.yaml](.github/workflows/release-chart.yaml) tags `vX.Y.Z`, writes the
  GitHub Release, and publishes the chart to `oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent`.

So: lint + test gate every change; the *release* itself is just a normal
reviewed PR (the version bump) — the AI only advises, merging is what ships. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full release playbook.

## Roadmap

This chart deploys and manages **one** agent well; teams via an ArgoCD
ApplicationSet are how you scale today, and a CRD-based operator is a
long-term, not-started candidate. See [docs/roadmap.md](docs/roadmap.md).

---

> Banner © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
