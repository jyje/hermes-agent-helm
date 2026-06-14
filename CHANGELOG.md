# Changelog

All notable changes to this chart are documented here.
## [0.0.1] - 2026-06-14

### Bug Fixes

- 🛠️ fix(ci): force-kill hermes doctor on timeout and simplify round-trip prompt

Add -k 10 to the timeout wrapping hermes doctor in the test Job so a
non-responsive process is SIGKILL'd 10s after SIGTERM, instead of letting
the helm test hook run close to its 12m ceiling. Also simplify the
real-model round-trip prompt to "Just say hi." with a word-boundary check,
avoiding an overly specific instruction-following requirement.
- 🛠️ fix(ci): only run helm CI on chart or workflow changes

Add path filters so the helm lint/test workflow only runs when
charts/hermes-agent-helm/** or its own workflow file changes, avoiding
unnecessary CI runs for unrelated repo changes (e.g. docs/examples).

### Documentation

- 📄 docs(chart): document upgrade path across a chart rename

Add a guide for upgrading an existing release from the old chart name to
hermes-agent-helm, covering the fullname/PVC-name shift and the immutable
volumeClaimTemplates chart-version label, with the cascade=orphan +
nameOverride fix sequence verified end-to-end on a live cluster.

### Features

- ✨ feat(chart): allow choosing StatefulSet or Deployment via controller.type

Extract the shared Pod spec into a podTemplate helper and add
controller.type (statefulset|deployment) to values.yaml. Deployment mode
skips the headless Service, creates a standalone PVC, and forces a Recreate
strategy when persistence is enabled to avoid ReadWriteOnce volume races.
- ✨ feat(chart): default to Deployment controller and add extraResources for GitOps secrets

Switch controller.type default to "deployment" for resource flexibility on
single-replica workloads, add a strongly-worded comment that replicaCount must
not be changed, and add an extraResources mechanism (object or string
manifests, both tpl-rendered) so a SealedSecret can be injected and referenced
via extraEnvFrom — documented with a LiteLLM example in values.example.yaml.

### Refactor

- ♻️ refactor(chart): rename hermes-agent chart to hermes-agent-helm

Rename charts/hermes-agent to charts/hermes-agent-helm (Chart.yaml name,
template helper prefixes, Makefile, CI/release workflows, docs, and
examples) so the published OCI package becomes ghcr.io/jyje/hermes-agent-helm.

Also add an AppVersion fallback for image.tag via new
hermes-agent-helm.image/testImage helpers, add a Korean README, and stop
ignoring .claude/ so chart-helper skills are tracked.
- ♻️ refactor(chart): rename chart to hermes-agent, reset version to 0.0.1

Rename charts/hermes-agent-helm to charts/hermes-agent (Chart.yaml name,
template helper prefixes, Makefile, CI/release/version-comment workflows,
docs, and examples updated accordingly). Chart version resets to 0.0.1;
appVersion stays pinned to the latest upstream image tag (v2026.6.5).

Generalize provider docs and values.example.yaml away from a specific
deployment (no hardcoded FQDNs/StorageClass), presenting LiteLLM and Gemini
as example provider options. README/AGENTS/CONTRIBUTING updated to describe
the StatefulSet/Deployment (controller.type) choice.

Add an opt-in hermes chat round-trip to the Helm test Job
(tests.chat.enabled), which prints the prompt/response transcript to the
test pod's logs; CI now exercises this against Gemini when a key is
available.

## [0.1.0] - 2026-06-13

### Initial Release

- 🎉 init: setup project and ci

Add the hermes-agent Helm chart (StatefulSet, ConfigMap/Secret-based config
overrides, provider-agnostic LLM config, optional Helm test job), install/
publish examples (Git + OCI/ghcr, ArgoCD), and the dev/main release pipeline
(kind + Gemini CI, version-bump-triggered tag + OCI publish, /version PR
comment ChatOps trigger).

