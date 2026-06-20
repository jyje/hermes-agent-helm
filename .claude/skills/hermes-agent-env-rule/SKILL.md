---
name: hermes-agent-env-rule
description: Keep the chart's "Environment variables" README section (charts/hermes-agent/README.md.gotmpl) in sync with upstream Hermes Agent's supported env vars at the currently pinned appVersion. Use after an image version bump (cron-fetch-image PR), periodically, or when asked to check/update/audit Hermes env vars.
---

# Hermes Agent env var rule

`charts/hermes-agent/README.md.gotmpl` has an **Environment variables**
section that links to upstream's official reference and lists a curated
"commonly-used" subset, current as of the pinned image
(`{{ template "chart.appVersion" . }}`, i.e. `charts/hermes-agent/Chart.yaml`
→ `appVersion`). Upstream adds/renames/removes env vars between releases —
this skill re-checks the curated subset against the exact pinned version and
refreshes it.

Source of truth: [NousResearch/hermes-agent — Environment Variables](https://hermes-agent.nousresearch.com/docs/reference/environment-variables)
(rendered docs site; the underlying source is
`website/docs/reference/environment-variables.md` in the upstream repo).

## Steps

1. **Find the pinned version**:

   ```bash
   grep '^appVersion:' charts/hermes-agent/Chart.yaml
   ```

2. **Fetch the upstream doc at that exact tag** (not `main` — the pinned
   image may lag behind upstream's latest commits):

   ```bash
   APPVERSION=$(yq '.appVersion' charts/hermes-agent/Chart.yaml)
   gh api "repos/NousResearch/hermes-agent/contents/website/docs/reference/environment-variables.md?ref=${APPVERSION}" \
     --jq '.content' | base64 -d > /tmp/hermes-env-vars-upstream.md
   ```

   If the tag doesn't exist upstream (chart's appVersion fell out of sync),
   fall back to the nearest tag at or before it from
   `gh api repos/NousResearch/hermes-agent/tags --jq '.[].name'`.

3. **Diff against the curated table** in the chart's "Environment variables"
   section (`charts/hermes-agent/README.md.gotmpl`) — look specifically for:
   - new provider env vars (new LLM providers added upstream)
   - new messenger/platform integrations
   - renamed or removed vars that are still listed in our curated table
   - changed defaults for the runtime knobs we list (`HERMES_MAX_ITERATIONS`,
     `HERMES_AGENT_TIMEOUT`, `SESSION_IDLE_MINUTES`, etc.)

4. **Update the curated table** in `README.md.gotmpl` — keep it short (10-15
   rows max; it's a teaser, not a copy of the full reference). Prioritize:
   providers not already covered in that file's "Install options: LLM
   provider" section, messenger platforms not already covered in its
   "Messenger integrations" section, and any runtime knob likely to matter
   for a Kubernetes deployment (timeouts, session/idle behavior, dashboard
   auth). Don't touch the link to the official reference or the
   `{{ template "chart.appVersion" . }}` line — both stay accurate
   automatically.

5. **Regenerate the README**:

   ```bash
   helm-docs --chart-search-root=charts --template-files=README.md.gotmpl
   ```

6. **Review the diff** (`git diff charts/hermes-agent/README.md.gotmpl charts/hermes-agent/README.md`)
   and hand off to the `git-commit-helper` skill for the commit — this is a
   `📄 docs(chart)` change, not `style`.

## Notes

- This is about the *curated subset* only. The full reference link in the
  README is permanent and never goes stale on its own.
- Don't run this as part of every `cron-fetch-image` bump automatically —
  most version bumps don't add/remove env vars. Run it when asked, or
  periodically (e.g. once a month, or when a bump's upstream changelog
  mentions new providers/integrations).
