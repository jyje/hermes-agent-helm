<div align="center" markdown="1">

# jyje/hermes-agent-helm

<img height="240" src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/hermes-agent-helm.png" alt="Kubernetes × Hermes Agent"/>

👩🏻‍💻 A Helm chart to run **Hermes Agent** on Kubernetes, community-powered, lightweight

[![GitHub Repo stars](https://img.shields.io/github/stars/jyje/hermes-agent-helm?style=social)](https://github.com/jyje/hermes-agent-helm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Helm](https://img.shields.io/badge/Helm-3%2B-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/hermes-agent)](https://artifacthub.io/packages/search?repo=hermes-agent)

[English](README.md) · [한국어](README-ko.md) · **🚀 [Hermes Team](https://jyje.github.io/hermes-agent-helm/guides/team-setup/)** · [Chart docs](charts/hermes-agent/README.md) · [CONTRIBUTING](CONTRIBUTING.md) · [SECURITY](SECURITY.md) · [AGENTS](AGENTS.md)

---

**Found this useful? Please give it a ⭐ - it helps others find it.**

</div>

## Summary

Run [Hermes Agent](https://github.com/NousResearch/hermes-agent) on Kubernetes
with one `helm install` - works with any LLM provider Hermes supports, scales
down to a single small node, and is verified to actually run, not just render.
Just as easily, group several instances into a full [**Hermes Team**](https://jyje.github.io/hermes-agent-helm/guides/team-setup/)
on the same cluster. A **community-powered** chart, not an official Nous
Research release.

## Quick Start

1. **OCI (recommended)** — install directly from the registry, no `helm repo add` needed:

    ```bash
    helm install hermes-agent oci://ghcr.io/jyje/hermes-agent-helm/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

2. **Classic Helm repo** — a Helm repository is also published to GitHub Pages, if you'd rather add it once and install by name:

    ```bash
    helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
    helm repo update
    helm install hermes-agent hermes-agent/hermes-agent \
      --namespace hermes-agent --create-namespace \
      --set-string env.OPENAI_API_KEY='sk-...' \
      --wait
    ```

Optionally pin `--version` to a specific [released chart version](https://github.com/jyje/hermes-agent-helm/releases) instead of latest.

To install from this repo's source instead (e.g. to try an unreleased
change), see [Development](#development) below.

## Why this chart

- **All of Hermes's provider support, via `values.yaml`.** Hermes itself
  already supports `openai-api`, `anthropic`, `gemini`, `openrouter`, `nvidia`,
  `deepseek`, and any OpenAI-compatible endpoint (e.g.
  [LiteLLM](https://github.com/BerriAI/litellm)) through environment
  variables - this chart just exposes that config through `values.yaml` and
  ships ready-to-adapt examples per provider, with no provider baked into the
  templates.
- **Lightweight → production.** Sized for homelab / single-node / edge clusters
  out of the box (one replica, modest requests, a small PVC), and ready for
  production by scaling *up* - not *out*. Hermes is a single-instance personal
  agent (one `HERMES_HOME`, one gateway, one memory), so you don't replicate a
  pod; you run several well-managed instances and group them into a **team**
  that shares context over a common gateway channel. See
  [Hermes teams](docs/reference/teams.md).
- **Verified end-to-end.** CI installs the chart on an ephemeral **kind**
  cluster and runs the bundled test Job (`hermes doctor`). When the
  `NVIDIA_API_KEY` repository secret is available, it also runs a **live
  `hermes chat` round-trip** against NVIDIA NIM - not a mock.
  The Discord-thread leader team has also completed a live human → leader →
  two members → leader round-trip; Telegram team orchestration remains separate.

<div align="center">
  <img src="https://raw.githubusercontent.com/jyje/hermes-agent-helm/main/docs/images/demos/team-k9s-pods.png" alt="A leader-orchestrated Hermes team (august, may, march) running on a kind cluster, shown in k9s"/>
  <p><em>Deployment evidence: leader <code>august</code> and members
  <code>may</code>/<code>march</code> running as independent releases on kind.
  This screenshot does not by itself prove the multi-turn mention loop; see
  <a href="docs/reference/teams.md">Hermes teams</a> for the current status.</em></p>
</div>

For the full resource breakdown, configuration model, and provider-by-provider
install examples (including messenger integrations), see
[charts/hermes-agent/README.md](charts/hermes-agent/README.md).

## Repository layout

```
charts/hermes-agent/                     # the Helm chart (see its README for the full values table)
charts/hermes-agent/values-*.yaml        # ready-to-adapt examples: providers, Discord/Telegram, LiteLLM (see chart README "More examples")
examples/helm/                           # install from Git and from OCI (ghcr.io) + publish guide
examples/argocd/                         # ArgoCD Application examples (one per values-*.yaml) + GitOps/SealedSecret pattern
charts/hermes-operator/                  # ⏸️ long-term, not started: possible install chart for an Agent/AgentTeam-CRD operator - placeholder, TBA (see Roadmap)
docs/                                    # deeper guides: teams.md (group instances into a team), collaboration.md (make them hand off by @mention), roadmap.md
.github/workflows/                       # ci (lint + docs-drift + real round-trip on kind) and release (version bump -> tag -> ghcr OCI)
CONTRIBUTING.md                          # branch model (dev/main + tags) + release-on-version-bump
AGENTS.md                                # design principles & workflow for contributors
Makefile                                 # docs / lint / template / install / test / package / push
```

## Full Installation

```bash
# add the Helm repository and fetch the latest chart index
helm repo add hermes-agent https://jyje.github.io/hermes-agent-helm
helm repo update

# render the chart and check its templates before installing
helm template hermes-agent hermes-agent/hermes-agent \
  --set-string env.OPENAI_API_KEY='sk-...'

# install with the generic defaults (set your provider key)
# release name == chart name keeps resources clean (hermes-agent-0, not hermes-agent-hermes-agent-0)
helm upgrade --install hermes-agent hermes-agent/hermes-agent \
  --namespace hermes-agent --create-namespace \
  --set-string env.OPENAI_API_KEY='sk-...' --wait

# run the install test (doctor-style Job)
helm test hermes-agent -n hermes-agent
kubectl logs -n hermes-agent -l app.kubernetes.io/component=test --tail=-1
```

See [charts/hermes-agent/README.md](charts/hermes-agent/README.md) for the full
values table, the "More examples" table (`values-*.yaml` for every supported
provider plus Discord/Telegram and LiteLLM - copy the raw YAML and pass it with
`-f`), and an [ArgoCD example](examples/argocd/).

## Development

Clone the repo and install from the local chart path (a relative path, not
the published registry) to check a change before opening a PR:

```bash
git clone https://github.com/jyje/hermes-agent-helm.git
cd hermes-agent-helm

# render & lint
make template
make lint

# install from the local chart source
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

Branch model, release process, and further local checks (`make docs` /
`make test`) are covered in [CONTRIBUTING.md](CONTRIBUTING.md); chart design
principles are in [AGENTS.md](AGENTS.md).

## CI/CD

- **Every PR and every push to `dev`/`main`** runs [validate-chart.yaml](.github/workflows/validate-chart.yaml):
  `helm lint`, `helm template`, a chart-docs drift check, and a full install +
  test on an ephemeral **kind** cluster (real `hermes chat` round-trip when an
  `NVIDIA_API_KEY` secret is available).
- **Releases are Changesets-driven, not tag-push-driven.** A user-visible chart
  change adds a `patch`, `minor`, or `major` entry under [`.changeset/`](.changeset/).
  When you are ready to release, manually run
  [propose-release.yaml](.github/workflows/propose-release.yaml) to combine pending
  entries into one reviewable release PR, write its `CHANGELOG.md` notes,
  and synchronizes the private release manifest with `Chart.yaml`, Artifact Hub
  metadata, chart docs, and versioned examples. Review and merge that PR; then
  [release-chart.yaml](.github/workflows/release-chart.yaml) tags `vX.Y.Z`, writes the GitHub
  Release, and publishes the chart to `oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent`.

So: lint + test gate every change; the *release* itself is just a normal
reviewed PR (the version bump) - the pending Changesets decide its SemVer,
merging is what ships. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full release playbook.

## Roadmap

This chart deploys and manages **one** agent well; teams via an ArgoCD
ApplicationSet are how you scale today, and a CRD-based operator is a
long-term, not-started candidate. See [docs/reference/roadmap.md](docs/reference/roadmap.md).

## Contributing

Issues, PRs, and ideas are all welcome - start with
[CONTRIBUTING.md](CONTRIBUTING.md) (branch model, local checks, release flow).
Every merged contribution is credited in the changelog and release notes.

Thanks to everyone who has contributed to and starred this project ⭐

<a href="https://github.com/jyje/hermes-agent-helm/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jyje/hermes-agent-helm" alt="Contributors" />
</a>

---

> Banner © [Nous Research](https://github.com/NousResearch/hermes-agent) (MIT).
