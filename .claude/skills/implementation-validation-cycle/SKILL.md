---
name: implementation-validation-cycle
description: Run the repository's feature-branch to orphan-test-branch validation lifecycle with a verified full SHA, remote GitHub Actions evidence, failure classification, PR reporting, and safe cleanup. Use when preparing or revalidating a feature PR, when a temporary remote validation workflow is needed, or when a validation-cycle failure must be diagnosed.
---

# Implementation validation cycle

Use this skill after the implementation has passed its required local checks and
the user has approved the implementation commit. It produces remote evidence;
it never changes the merge path from `feat/<scope>` to `main`.

## Inputs and gates

Require all of these before mutation: implementation worktree, feature branch,
issue/PR number, validation profile, and the full implementation SHA from
`git rev-parse HEAD`. Push the implementation first.

Run the preflight helper. It rejects abbreviated SHAs and a feature branch whose
remote tip is not exactly the requested commit.

```bash
scripts/validation-cycle.sh preflight \
  --repo /path/to/repo --feature-branch feat/<scope> --sha <40-char-sha>
```

For a chart change, local evidence normally includes `make docs` when
`values.yaml` changed, `make lint`, `make template`, `make package`, and an
isolated kind install plus `helm test`. Record an unavailable local dependency
honestly; do not claim the remote result was local evidence.

## Remote loop

1. Use `create` without `--apply` first. Inspect the feature SHA, test branch,
   worktree path, profile, and generated workflow path.
2. With explicit approval, rerun `create --apply`. It creates an orphan
   `test/<scope>` worktree containing only `.github/workflows/validate-implementation.yaml`, commits it, and pushes it. The workflow checks out the full pinned SHA.
3. Capture the exact run ID and wait only for that run:

   ```bash
   gh run watch <run-id> --repo <owner/repo> --exit-status
   ```

4. On failure, classify before editing:
   - **implementation**: feature checkout, assertion, or chart workload fails.
     Return to the feature worktree, rerun local checks, commit a feature fix,
     and restart with its new SHA.
   - **harness**: the orphan workflow, its pinned SHA, or its setup fails before
     testing the implementation. Change only the orphan branch and rerun.
   - **infrastructure**: runner, registry, or transient platform failure.
     Preserve state and retry only when the failure is demonstrably transient;
     otherwise ask the maintainer.
5. On success, post one PR comment with the tested SHA, run URL, inputs,
   expected and actual results, and a short secret-safe log excerpt. Use the
   helper to print the Markdown skeleton:

   ```bash
   scripts/validation-cycle.sh evidence \
     --sha <40-char-sha> --run-url <actions-url> --input '<test input>' \
     --expected '<expected result>' --actual '<actual result>'
   ```

6. Only after the comment succeeds, inspect the exact test worktree then call
   `cleanup --apply --comment-url <comment-url>`. Never open a test-to-`main`
   PR, merge the feature branch into the test branch, auto-merge a PR, or run a
   release.

## Helpers

- `scripts/validation-cycle.sh`: preflight, orphan-worktree creation, workflow
  rendering, evidence skeleton, and guarded cleanup.
- `assets/validate-implementation.yaml.tmpl`: the temporary chart-validation
  workflow. It checks out `__IMPLEMENTATION_SHA__` and is the only file copied
  to an orphan test branch.
- `scripts/test-validation-cycle.sh`: local fixture tests for the SHA mismatch,
  dry-run, workflow rendering, and evidence formatting paths.

Add a profile only when its commands and assertions are deterministic. Keep
feature-specific assertions in the temporary workflow, not the implementation
branch. See CONTRIBUTING.md's "Promoting a validation to permanent CI" for
the criteria deciding whether a proven assertion should become permanent CI.
