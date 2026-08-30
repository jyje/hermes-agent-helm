---
"@jyje/hermes-agent-helm": minor
---

Feature(secrets): Render an ExternalSecret for External Secrets Operator users

Add `externalSecret.*` values. Setting `externalSecret.enabled: true` renders
an ExternalSecret as the sole replacement for the chart's own env Secret,
not an addition beside it: `secret.yaml` stops rendering, `env` is ignored,
and every chart-owned `envFrom` (main container, auth device-login init
container, helm test Job) automatically follows the ExternalSecret's target
name via a new `hermes-agent.envSecretName` helper - no `extraEnvFrom`
needed. An empty `externalSecret.target.name` falls back to the chart's own
`<fullname>-env` name; a set one is used everywhere instead. The pod
template's `checksum/secret` annotation hashes the rendered ExternalSecret
in this mode, so changing `target`/`data`/`dataFrom` still triggers a
rollout. Automatic Pod restart on provider-side secret rotation is out of
scope - pair with a reloader controller (Reloader, Stakater) for that.
Defaults are unchanged; existing installs are unaffected.
