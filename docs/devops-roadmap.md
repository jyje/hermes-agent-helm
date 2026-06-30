# DevOps Roadmap

This document tracks CI/CD pipeline improvements for `hermes-agent-helm`.
Items are derived from a source-control and DevOps review of the current
`.github/workflows/` configuration.

Grouped by area and ordered by priority within each group.

---

## Source Control

### 🔴 High priority

- [ ] **Enable branch protection on `main`**
  - Require at least one PR before merging (no direct push to `main`)
  - Add `validate-chart` as a required status check
  - **Risk today:** a broken commit can hit `main` and immediately trigger
    `release-chart.yaml` without any CI gate

- [ ] **Include workflow file changes in `validate-chart` trigger**
  - Current path filter watches `charts/hermes-agent/**` and
    `.github/workflows/validate-chart.yaml` only
  - Changes to `cron-fetch-image.yaml`, `release-chart.yaml`,
    `propose-release.yaml`, etc. land on `main` unvalidated
  - Add `.github/workflows/**` to the `paths:` trigger (or at minimum lint
    YAML with `actionlint`)

### 🟡 Medium priority

- [ ] **Resolve the unused `dev` branch strategy**
  - `validate-chart` triggers on `[dev, main]` but all work goes directly to
    `main`; the `dev` branch has never been used in practice
  - Either adopt a `dev → main` merge flow, or remove `dev` from trigger
    lists and clean up `CONTRIBUTING.md` so the documented strategy matches
    reality

---

## Pipeline Design

### 🟡 Medium priority

- [ ] **Split `release-chart` into independent OCI and gh-pages jobs**
  - Currently a single job runs OCI push → gh-pages deploy in sequence
  - If OCI push succeeds but gh-pages fails, re-running skips everything
    (tag-existence guard) — partial deployment with no automatic recovery
  - Splitting into two jobs (with a shared `needs:` on a tagging step) allows
    each to be re-run independently

- [ ] **Close the "release commit is not tested" gap**
  - `release/next` PRs touch only `Chart.yaml` + `README.md` +
    `CHANGELOG.md`, so `functional=false` → kind cluster test is skipped
  - The last merged commit before shipping is never integration-tested
  - Options: (a) add a lightweight smoke test that always runs on
    `release/next`, or (b) document the gap and accept it as a known trade-off
    given that the preceding feature commit was tested

### 🟢 Low priority

- [ ] **Abstract the runner label into a repository variable**
  - All workflows hard-code `ubuntu-26.04-arm`; if that image is deprecated
    or has an outage, every workflow fails simultaneously
  - Use `runs-on: ${{ vars.RUNNER_LABEL || 'ubuntu-latest' }}` so the
    fallback can be changed without a code edit
  - See [fallback design note](#runner-fallback-note) below

---

## Security

### 🟢 Low priority

- [ ] **Add Helm template security scanning**
  - No `kubesec`, `trivy`, `checkov`, or `kube-score` scan on rendered
    templates today
  - Suggested insertion point: new step in `validate-chart / lint` job,
    running `helm template | trivy config -` or `kubesec scan -`
  - Cosign signing proves provenance but does not validate what was signed

- [ ] **Generate and attach SBOM to each release**
  - `release-chart.yaml` signs the OCI artifact but produces no
    Software Bill of Materials
  - `syft` or `cosign attest --predicate` (CycloneDX/SPDX) can be added as
    a post-push step

---

## Operations

### 🟢 Low priority

- [ ] **Prune old chart packages from gh-pages**
  - `release-chart.yaml` uses `keep_files: true`; every release accumulates
    a new `.tgz` on the `gh-pages` branch indefinitely
  - Add a cleanup step that retains the last N versions (e.g., 10) and
    removes older `.tgz` files before regenerating `index.yaml`

- [ ] **Harden the AI advisor fallback in `upstream-review`**
  - If the NVIDIA NIM endpoint is down or quota is exhausted, the
    `upstream-review` job silently fails or produces no GitHub issue
  - Add explicit `continue-on-error: true` with a step that posts a
    fallback comment/issue when the AI call fails, so the failure is visible

---

## Notes

### Runner fallback note

GitHub Actions does not natively support "try runner A, fall back to runner B."
The `runs-on: [label-a, label-b]` array syntax means *all labels must match*,
not *first available*. The repository-variable approach is the lowest-overhead
workaround: a single settings change propagates to all workflows instantly.

### Functional diff filter design

The `changes` job in `validate-chart` deliberately skips the kind cluster
test for release-only commits (version bump + docs). This is an intentional
cost/speed trade-off; the item above ("release commit is not tested") captures
the known gap for future review, not necessarily for immediate fixing.

---

*Last reviewed: 2026-06-29*
