---
"@jyje/hermes-agent-helm": patch
---

Documentation(dashboard): Describe the real dashboard lifecycle and make values-ingress.yaml work

The chart described the management dashboard as "binds 127.0.0.1, needs
`--insecure` beyond that, which exposes API keys". None of that matches the
pinned image: the dashboard is an s6 service that stays down until
`HERMES_DASHBOARD=1`, it binds `0.0.0.0` in-container, and on any non-loopback
bind upstream's auth gate is mandatory, so without a configured provider it
fails closed and never listens; `--insecure` / `HERMES_DASHBOARD_INSECURE`
are deprecated no-ops. `values-ingress.yaml` never enabled the dashboard at
all, leaving its Ingress pointing at nothing. The example now enables the
service, configures the bundled username/password provider through `env`, and
sets `config.dashboard.public_url` plus a bounded `trusted_proxies` entry for
the ingress controller (new upstream between v2026.8.27 and v2026.8.31) so
`X-Forwarded-Proto` from a TLS-terminating ingress is honoured. Comments in
values.yaml, `_helpers.tpl` and both READMEs are corrected to match.
