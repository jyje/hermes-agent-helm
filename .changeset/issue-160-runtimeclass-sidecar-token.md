---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Expose runtimeClassName, extraContainers, and stop mounting the ServiceAccount token by default

Add `runtimeClassName` for kernel-isolated runtimes (gVisor, Kata) and
`extraContainers` for sidecars. Set `serviceAccount.automountServiceAccountToken`
to `false` by default, since the agent never calls the Kubernetes API; this is a
behaviour change on upgrade, previously Kubernetes applied its own default of
`true`. Override with `serviceAccount.automountServiceAccountToken: true` if
something inside the Pod deliberately needs the API.
