---
name: review-upstream
description: Review Hermes Agent stable releases against this Helm chart using original release notes, tagged source, and small per-release checks. Use for upstream reviews, image-bump compatibility reviews, and authorized upstream-review issue filing.
---

# Review upstream

Review upstream changes that require chart action. Review-only requests do not
authorize issue creation, image bumps, workflow dispatch, PRs, or merges.

## Original evidence and per-release checks

1. Record the chart commit, appVersion, requested release window and dirty work.
   Use a clean snapshot when unrelated edits are present. If no window is given,
   use current appVersion through the requested target and state the baseline.
2. Inventory formal stable GitHub releases separately from Docker tags. Paginate
   discovery and follow AGENTS.md's tag policy. Retrieve the original body of
   **every release** using
   `gh api repos/NousResearch/hermes-agent/releases/tags/<tag>`.
   Retain bodies, URLs, dates and draft/prerelease flags. Missing originals mean
   **unreviewed**, not no findings; never silently substitute summaries.
3. Read deployment, upgrade, persistence, security and configuration changes.
   Account for cumulative notes, reverted changes and later correction notices.
   State omitted sections. Inspect relevant source at the exact tag, not moving
   main. For environment-table audits, use `hermes-agent-env-rule`.
4. Perform small checks for each tag: image availability/architectures, Helm lint
   and rendering with an explicit image override, and relevant chart-used paths,
   migration/auth interfaces or runtime pins. Exercise both controller types
   when relevant. Choose checks proportional to the changes, not a fixed large
   cluster matrix. Record pass/fail/not-run per release.
5. Separate static checks from container startup, persisted-PVC migration and
   authenticated live checks. A render does not prove the image exists; an image
   does not prove a safe release. Do not start credentialed flows without scope.
   This review window is not a historical image-support commitment.

## Chart relevance and existing work

Read the filtering contract in
[advise-image-bump.py](../../../.github/scripts/release/advise-image-bump.py),
especially `SYSTEM_PROMPT`. Freeform config/env passthrough already exposes new
keys. Flag broken existing examples, changed defaults/persistence contracts,
invalid documented assumptions, security impact or actual resource changes,
not bare new keys or desktop-only features.

Compare current templates, values, examples, English/Korean docs, open/closed
issues and active PRs. Each finding needs priority, scope, original source links,
acceptance checks and evidence limits. Reference covered work instead of filing
duplicates. Keep permanent CI follow-ups separate under AGENTS.md. Do not infer
a chart major bump solely from the upstream version label.

## Shared scripts and authorized filing

Read the relevant implementation before running its mode:

- [advise-image-bump.py](../../../.github/scripts/release/advise-image-bump.py)
  is the optional NIM advisor. Inspect its output against original notes and
  report omitted input. Manual review needs no NIM key. Skipped/failed output
  is not a clean review.
- [file-image-bump-issues.py](../../../.github/scripts/release/file-image-bump-issues.py)
  writes issues with shared titles, priority labels, triage guidance and an
  exact-open-title duplicate guard. Run only when issue filing is authorized.
- [review-upstream-releases.py](../../../.github/scripts/release/review-upstream-releases.py)
  inventories formal stable releases, retains originals and small per-tag checks,
  and records only completed reviews by original-note digest. Inspect the
  committed manual baseline and cached ledger; neither means findings are fixed.
  `--plan-only` provides a read-only inventory preview without model or issue calls.
- [cron-fetch-image.yaml](../../../.github/workflows/cron-fetch-image.yaml)
  runs formal reviews independently of image bump gates. An authorized dispatch
  with `review_only=true` cannot propose an image bump; `review_from` selects
  an inclusive baseline and `force_review=true` rechecks recorded digests.
  It can still create issues and consume NIM requests. Cache eviction causes
  backfill, and missing notes or omitted critical sections require manual review.

For an authorized manual filing, prepare and inspect this JSON contract:

```json
{
  "source": "manual",
  "items": [{
    "priority": "medium",
    "title": "Concrete chart follow-up",
    "detail": "Evidence, affected files, requested change, acceptance checks and source links.",
    "upstream_ref": "Release tag and section or upstream PR"
  }]
}
```

Check semantic duplicates first: the script only checks exact open titles.
Then run from the repository root:

```sh
python3 .github/scripts/release/file-image-bump-issues.py <review.json> <target-tag> jyje/hermes-agent-helm
```

Use `source: manual` for an agent's original-note review, not NIM attribution.
Group independent review windows by target tag. After partial failure inspect
created issues before retrying. Do not close issues or implement fixes unless
requested. Never copy the shared script into the skill directory.

Finish with per-release results, findings or verified issue URLs, and explicit
unverified areas. Agent/CI-only tooling needs no Changeset; user-facing chart
fixes follow the repository Changeset and locale rules.
