# Changesets

Each user-visible chart change gets one Markdown file in this directory.
Use `pnpm changeset` and choose `@jyje/hermes-agent-helm`; select `patch`,
`minor`, or `major` based on Helm chart compatibility. Changes that only affect
CI, internal tooling, or unreleased documentation do not need a changeset.

When a maintainer manually runs the release proposal workflow, it consumes
pending entries, updates the private release manifest and
`charts/hermes-agent/Chart.yaml` together, refreshes chart docs, and opens or
updates the release PR. This repository never publishes the private npm
manifest.
