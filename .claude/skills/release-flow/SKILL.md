---
name: release-flow
description: Run the Changesets-based release proposal flow for this chart end-to-end via gh CLI — trigger propose-release, review the PR, adjust the version, watch CI, and merge. Use when the user asks to cut/propose/ship a release, check on a release PR, or change its version.
---

# Release flow (propose-release via gh CLI)

This repo's release model: Changesets under `.changeset/*.md` are the source
of the next SemVer decision, `propose-release.yaml` consumes all pending
entries into one reviewable PR that bumps `charts/hermes-agent/Chart.yaml`,
and **merging that PR is what ships**. This skill drives the whole loop with
`gh`, without using the GitHub web UI.

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for the full conceptual
background (how to write a Changeset, SemVer selection, the release-note
category convention); this skill is the CLI operationalization of "How to cut
a release".

## Steps

1. **Trigger `propose-release.yaml`** (workflow_dispatch, no inputs —
   maintainer action, never runs on fork PRs). The version is always derived
   from the pending Changesets on `main`; there is no way to pin a version or
   force a bump level at trigger time:

   ```bash
   gh workflow run propose-release.yaml
   ```

   If there are no pending Changesets, the run exits early (`has-release:
   false`) without opening or updating a PR.

2. **Watch the run**:

   ```bash
   gh run list --workflow=propose-release.yaml --limit 1
   gh run watch <run-id>
   ```

3. **Review the release PR** (branch `changeset-release/main`, managed by the
   `changesets/action` GitHub Action — idempotent, re-running step 1 updates
   the same PR):

   ```bash
   gh pr list --head changeset-release/main
   gh pr view <PR-number>     # combined version + changelog entries
   gh pr diff <PR-number>     # actual Chart.yaml / CHANGELOG.md diff
   ```

4. **Adjust the version if needed.** There is no PR-comment command for this
   (no bot listens for one). Edit or add a `.changeset/*.md` file on `main`
   with the correct `major`/`minor`/`patch` impact instead of editing the
   generated `Chart.yaml` version directly, then re-run step 1 to refresh the
   same PR against the corrected Changesets.

5. **Check CI** (`validate-chart.yaml` runs automatically on PR push):

   ```bash
   gh pr checks <PR-number> --watch
   ```

6. **Merge** — this triggers `release-chart.yaml`, which tags `vX.Y.Z`, writes
   the GitHub Release, and publishes the chart to both the OCI registry
   (`oci://ghcr.io/<owner>/hermes-agent-helm/hermes-agent`) and the GitHub Pages Helm repo
   (`https://<owner>.github.io/hermes-agent-helm`). Use `--merge` (not
   `--squash`) so `changesets/action`'s own commit structure survives:

   ```bash
   gh pr merge <PR-number> --merge
   ```

7. **Watch the release run**, then confirm `verify-release.yaml` (triggered
   automatically afterward) also goes green — it installs the just-published
   OCI artifact into a fresh kind cluster and re-verifies it:

   ```bash
   gh run list --workflow=release-chart.yaml --limit 1
   gh run watch <run-id>
   gh run list --workflow=verify-release.yaml --limit 1
   ```

## Notes

- `main` currently has no branch protection — merging is immediate, no
  required reviews/checks are enforced by GitHub itself. Still wait for
  `gh pr checks` to go green before merging.
- `release-chart.yaml` is a no-op (tag-existence guard) if the `vX.Y.Z` tag
  already exists, so re-running things after a merge is safe.
- `changeset-release/main` is managed entirely by `changesets/action` itself;
  nothing in this repo's own workflows deletes or touches that branch.
