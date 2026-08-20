---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Ship a CI-verified Pod Security Standards hardening profile

Add `auth.deviceFlow.securityContext` and `team.sharedVolume.permissions.securityContext`
so both non-default init containers can be overridden for a non-root or
read-only-rootfs deployment, alongside the existing `podSecurityContext`/
`securityContext`. Add `values-hardened.yaml`, a Pod Security Standards
`restricted`-compliant overlay verified end-to-end in a CI kind cluster that
enforces `restricted` admission: non-root and a read-only rootfs both work
against the pinned image once `/run` and `/tmp` are writable+executable tmpfs
mounts. Defaults are unchanged; existing installs are unaffected.
