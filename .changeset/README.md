# Changesets

Each user-visible chart change gets one Markdown file in this directory.
Use `pnpm changeset` and choose `@jyje/hermes-agent-helm`; select `patch`,
`minor`, or `major` based on Helm chart compatibility. Changes that only affect
CI, internal tooling, or unreleased documentation do not need a changeset.

## Writing a release item

Changesets natively own only two fields: the package's SemVer bump in the YAML
frontmatter and the free-form Markdown summary below it. Keep the frontmatter
to package names and `major`, `minor`, or `patch`; do not add custom YAML keys
such as `type`, `scope`, or `author` there.

Use this repository convention for the first line of every summary. It records
the release-note category in the free-form Markdown that Changesets preserves:

```md
Category(scope): Title — concise user-facing detail
```

- **Category** is one of `Feature`, `Fix`, `Security`, `Dependency`,
  `Documentation`, `Deprecated`, or `Removed`.
- **scope** is a short affected area such as `chart`, `values`, `docs`,
  `image`, `persistence`, or `dashboard`.
- **Title** is the short bold label shown in a release note; the detail starts
  with an imperative, user-facing description.
- Use singular `Feature` and `Dependency` in a Changeset. A release-note
  renderer can group them under the plural headings **Features** and
  **Dependencies**. The category does not change the SemVer level.

For example:

```md
---
"@jyje/hermes-agent-helm": minor
---

Feature(docs): Documentation portal — Add chart-scoped install, values overlay,
example, and reference pages.
```

```md
---
"@jyje/hermes-agent-helm": patch
---

Fix(persistence): Bootstrap preservation — Preserve an existing Hermes
configuration during bootstrap.
```

Use `major` only for an incompatible upgrade path, `minor` for a backwards-
compatible user-visible capability or default-image update, and `patch` for a
backwards-compatible correction. Do not add a Changeset only to refresh CI,
release automation, or internal tooling.

Do not write a GitHub username into the summary. Attribution is not native
Changesets data; a custom release-note renderer may resolve the GitHub identity
from the commit or pull request that added the item. Keep that information out
of the summary so it has one source of truth.

When a maintainer manually runs the release proposal workflow, it consumes
pending entries, updates the private release manifest and
`charts/hermes-agent/Chart.yaml` together, refreshes chart docs, and opens or
updates the release PR. This repository never publishes the private npm
manifest.
