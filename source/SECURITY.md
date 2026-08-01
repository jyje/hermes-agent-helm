# Security Policy

> 🇰🇷 [한국어 문서 (Korean)](SECURITY-ko.md)

This document covers security for the **Helm chart** in this repository
(`charts/hermes-agent`) — its templates, default values, examples, and CI.
It is a community-maintained chart, not an official Nous Research release.

## Reporting a vulnerability

Report privately via
[GitHub Security Advisories](https://github.com/jyje/hermes-agent-helm/security/advisories/new).
**Do not open public issues for security vulnerabilities.**

A useful report includes:

- A concise description and severity assessment.
- The affected template, value, or example (file path and line range).
- Chart version (`Chart.yaml` `version`) and, if relevant, the image tag
  (`appVersion` or your override).
- Rendered output (`helm template`) or reproduction steps demonstrating the
  issue.

You can expect an initial response within a reasonable time frame; this is a
volunteer-maintained project without an SLA or bug bounty program.

## Scope

**In scope — report here:**

- Chart templates rendering insecure resources (e.g. secrets leaked into
  ConfigMaps, logs, or annotations; unintended privilege escalation).
- Insecure defaults in `values.yaml` (e.g. anything that would expose the
  management dashboard or credentials by default).
- Vulnerabilities in the example manifests (`values-*.yaml`,
  `examples/argocd/`) that would mislead users into an insecure deployment.
- Supply-chain issues in this repository's release pipeline (GitHub Actions
  workflows, published OCI artifacts).

**Out of scope — report upstream:**

- Vulnerabilities in Hermes Agent itself (the application inside the image).
  Follow the upstream policy:
  [NousResearch/hermes-agent SECURITY.md](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md).
- Vulnerabilities in Kubernetes, Helm, or third-party charts/controllers
  (ingress controllers, sealed-secrets, etc.).
- Issues that require the operator to have already overridden the chart's
  secure defaults (e.g. exposing the dashboard with `--insecure` and no
  authentication is a documented, deliberate choice).

## Supported versions

Only the **latest released chart version** (latest `vX.Y.Z` tag) receives
security fixes. Older versions are not patched; upgrade to the latest release.

## Security model of the chart

Facts worth knowing before deploying:

- **The pod is the sandbox.** The agent runs commands inside its own pod
  (`config.terminal.backend: local`). Kubernetes-level isolation — namespace,
  `securityContext`, resource limits, NetworkPolicy — is the security
  boundary. The `docker` terminal backend is unsupported in-cluster because it
  would require a Docker daemon/socket.
- **No inbound API by default.** The agent makes outbound connections only.
  The single HTTP surface is the optional management **dashboard** (port 9119),
  which binds to `127.0.0.1` and **exposes API keys**. The chart ships with
  `service.enabled: false` and `ingress.enabled: false`; exposing the
  dashboard requires an explicit opt-in and upstream's `--insecure` flag —
  put authentication in front of it (see `values-ingress.yaml`).
- **Secrets are injected via `envFrom`**, rendered into a Kubernetes `Secret`
  — never into the ConfigMap. For GitOps, don't commit real secrets; use the
  SealedSecret pattern in
  [`examples/argocd/`](examples/argocd/#sealedsecret-walkthrough-nvidia-nim--discord).
- **`podSecurityContext` / `securityContext` are empty by default** for image
  compatibility. Hardening them (non-root, read-only root filesystem, dropped
  capabilities) is recommended where the image permits — validate in your
  environment.

## Repository protections

This repository has GitHub secret scanning with push protection, Dependabot
security updates, and private vulnerability reporting enabled.
