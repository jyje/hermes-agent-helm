---
name: release-flow
description: Run the AI-assisted release proposal flow for this chart end-to-end via gh CLI — trigger propose-release, review the PR, adjust the version, watch CI, and merge. Use when the user asks to cut/propose/ship a release, check on a release PR, or change its version.
---

# Release flow (propose-release via gh CLI)

This repo's release model: the chart `version` in `charts/hermes-agent/Chart.yaml`
is the source of truth, and **merging a PR that bumps it is what ships**. This
skill drives the whole loop with `gh`, without using the GitHub web UI.

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for the full conceptual
background; this skill is the CLI operationalization of "1. AI-assisted
proposal".

## Steps

1. **Trigger `propose-release.yaml`** (workflow_dispatch only — maintainer
   action, never runs on fork PRs):

   ```bash
   # let AI/heuristic recommend the version
   gh workflow run propose-release.yaml

   # or pin an exact version up front
   gh workflow run propose-release.yaml -f version=0.0.4

   # or force a bump level (ignored if version is set)
   gh workflow run propose-release.yaml -f bump=minor
   ```

2. **Watch the run**:

   ```bash
   gh run list --workflow=propose-release.yaml --limit 1
   gh run watch <run-id>
   ```

3. **Review the release PR** (branch `release/next`, idempotent — re-running
   step 1 updates the same PR):

   ```bash
   gh pr list --head release/next
   gh pr view <PR-number>     # recommended version, changelog, AI summary
   gh pr diff <PR-number>     # actual Chart.yaml / CHANGELOG.md diff
   ```

4. **Adjust the version if needed** (maintainer override — retitles the PR
   and regenerates chart docs):

   ```bash
   gh pr comment <PR-number> --body "/version v0.0.5"
   ```

   Re-run step 1 afterwards only if you also want the AI summary/changelog
   regenerated against new commits on `main`.

5. **Check CI** (`validate-chart.yaml` runs automatically on PR push):

   ```bash
   gh pr checks <PR-number> --watch
   ```

6. **Merge** — this triggers `release-chart.yaml`, which tags `vX.Y.Z`, writes
   the GitHub Release, and publishes the chart to both the OCI registry
   (`oci://ghcr.io/<owner>/hermes-agent`) and the GitHub Pages Helm repo
   (`https://<owner>.github.io/hermes-agent-helm`):

   ```bash
   gh pr merge <PR-number> --merge
   ```

7. **Watch the release run**:

   ```bash
   gh run list --workflow=release-chart.yaml --limit 1
   gh run watch <run-id>
   ```

## Notes

- `main` currently has no branch protection — merging is immediate, no
  required reviews/checks are enforced by GitHub itself. Still wait for
  `gh pr checks` to go green before merging.
- `release-chart.yaml` is a no-op (tag-existence guard) if the `vX.Y.Z` tag
  already exists, so re-running things after a merge is safe.
- `release/next` is deleted automatically by `release-chart.yaml` after a
  successful release.
