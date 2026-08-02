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

Use this repository convention for the first line of every summary:

```md
Type(scope): concise user-facing change
```

- **Type** is one of `Feature`, `Fix`, `Security`, `Dependency`,
  `Documentation`, `Deprecated`, or `Removed`.
- **scope** is a short affected area such as `chart`, `values`, `docs`,
  `image`, `persistence`, or `dashboard`.
- Write the summary in imperative, user-facing language. Do not repeat the
  SemVer level in the text: the release renderer places it quietly at the end
  of the item.

For example:

```md
---
"@jyje/hermes-agent-helm": minor
---

Feature(docs): Add a chart-scoped Starlight documentation portal.
```

```md
---
"@jyje/hermes-agent-helm": patch
---

Fix(persistence): Preserve an existing Hermes configuration during bootstrap.
```

Use `major` only for an incompatible upgrade path, `minor` for a backwards-
compatible user-visible capability or default-image update, and `patch` for a
backwards-compatible correction. Do not add a Changeset only to refresh CI,
release automation, or internal tooling.

Do not write a GitHub username into the summary. The release renderer should
credit the GitHub identity that committed the Changeset item, keeping
attribution tied to the repository history rather than a duplicated field.

When a maintainer manually runs the release proposal workflow, it consumes
pending entries, updates the private release manifest and
`charts/hermes-agent/Chart.yaml` together, refreshes chart docs, and opens or
updates the release PR. This repository never publishes the private npm
manifest.
