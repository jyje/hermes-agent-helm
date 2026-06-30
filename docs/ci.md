# CI / continuous validation

This repo has three GitHub Actions workflows that together validate a change
from pull request to published, signed artifact.

| Workflow | Trigger | Role |
|---|---|---|
| [validate-chart.yaml](../.github/workflows/validate-chart.yaml) | PRs and pushes to `dev`/`main` touching `charts/hermes-agent/**` | Lint + an isolated **kind** install/test before anything merges. |
| [release-chart.yaml](../.github/workflows/release-chart.yaml) | Push to `main` that changes `charts/hermes-agent/Chart.yaml` | Tags `vX.Y.Z`, publishes the OCI artifact + Helm repo, and cosign-signs it. See [CONTRIBUTING.md](../CONTRIBUTING.md#how-to-cut-a-release). |
| [verify-release.yaml](../.github/workflows/verify-release.yaml) | After a successful `release-chart` run | Re-verifies the **published, signed** artifact end to end. |

## validate-chart

Two jobs run on every functional change:

### `lint`

`helm lint`, `helm template`, and a **helm-docs drift check** — if
`charts/hermes-agent/README.md` is out of date relative to `README.md.gotmpl`,
the job fails. Always run `make docs` after editing `values.yaml` and commit the
result.

### `test`

Two scenarios run as a **matrix**, each on its **own ephemeral kind cluster**
(a separate runner) — fully isolated, with native per-job status, timeout, and
failure diagnostics instead of one bundled log. The PR checks list shows them
separately: `test (message)` and `test (existing-claim)`. Scenario logic lives
in [.github/scripts](../.github/scripts) (`lib.sh` + one script per scenario)
rather than inline in the workflow.

A `changes` job skips `test` entirely for version-bump-only commits (where the
chart behavior is unchanged).

#### message scenario — [scenario-message.sh](../.github/scripts/scenario-message.sh)

1. Install with chart-managed storage.
2. Run the chart's `hermes doctor` test hook (the same Job as `helm test`, but
   invoked directly so it can't stall on the hook watch).
3. **Only on trusted runs** (an `NVIDIA_API_KEY` secret is present): inject a
   skill onto the PVC, then do one `hermes chat` round-trip through NVIDIA NIM.

The `CI_MODELS` pool is **failover only** — the round-trip passes on the first
model that answers, not every model. The chat invocation mirrors the chart's own
test hook: `hermes chat -m <model> --provider nvidia -q <prompt> --max-turns N`.

The live Discord notification step (workflow-level, after the scenario script)
only runs for this scenario, since it's the only one with Discord enabled.

#### existingClaim scenario — [scenario-existing-claim.sh](../.github/scripts/scenario-existing-claim.sh)

Exercises `persistence.existingClaim` (the ability to mount a pre-existing PVC
instead of one the chart creates — [PR #37](https://github.com/jyje/hermes-agent-helm/pull/37)):

1. Create a `ci-shared-pvc` PVC **outside** the chart.
2. Install with `--set persistence.existingClaim=ci-shared-pvc`.
3. Confirm the `hermes doctor` test hook passes.
4. Exec into the pod and write then read `${HERMES_HOME}/ci-claim-probe.txt`.
5. Re-run `hermes doctor`.

This is a **smoke test**: it proves the chart binds to a pre-created PVC and
starts cleanly. It does **not** yet verify multi-instance sharing (RWX) or data
persistence across restarts/upgrades — the original motivation for the feature
(a shared knowledge base across several agents). Widening it to a cross-read /
restart-persistence check is a known follow-up.

### Fork PRs

Fork PRs don't receive repository secrets, so the chat round-trip (and any live
Discord check) is skipped and the run falls back to **doctor-only**, which is
safe and still meaningful.

## verify-release

After a release is published, this workflow proves the whole supply chain
against the artifact users actually pull (namespace `verify-hermes-chart`):

1. **cosign verify** the OCI artifact against this repo's Actions OIDC identity.
2. `helm install` **from the OCI registry** (not local source).
3. Run the same `hermes doctor` + chat round-trip as `validate-chart`.

A failure here means the published artifact or its signature is broken.

## Running the equivalents locally

```bash
make lint        # helm lint
make template    # render manifests
make docs        # regenerate the chart README (helm-docs) — commit the result
make test        # install + helm test (needs a cluster/kind)
```

See [docs/local-dev.md](local-dev.md) for setting up a local kind cluster and a
Discord + NVIDIA dev loop.
