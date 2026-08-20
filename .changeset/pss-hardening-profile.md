---
"@jyje/hermes-agent-helm": minor
---

Feature(values): Ship a CI-verified Pod Security Standards `restricted` profile

Add `charts/hermes-agent/values-hardened.yaml`, a `Pod Security Standards
restricted`-compatible profile verified against a live PSS `restricted`
namespace (not just rendered): non-root uid/gid, a read-only root filesystem,
all capabilities dropped, and `S6_READ_ONLY_ROOT=1` with tmpfs-backed
`/run`/`/tmp` for the image's s6-overlay entrypoint. Expose per-init-container
`securityContext` overrides for `auth.deviceFlow` and
`team.sharedVolume.permissions` (both default to their prior hardcoded
behaviour, so existing installs are unaffected). CI gains a fourth `hardened`
scenario alongside `message`/`existing-claim`/`team`.
