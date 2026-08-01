# Documentation site

This directory contains the Astro Starlight site published at
`https://jyje.github.io/hermes-agent-helm`.

The documentation tree under [`../docs`](../docs) is the source of truth.
Starlight reads that directory directly through `src/content/docs`; there is no
content generation step. Page URLs follow their Markdown paths, page names come
from frontmatter, and `docs/navigation.yml` owns the sidebar hierarchy and
ordering.

To document another chart, add its pages under `docs/charts/<chart-name>/`, add
the desired hierarchy to `docs/navigation.yml`, and link raw values to the
corresponding file under `charts/<chart-name>/`.

```bash
pnpm -C pages install
pnpm -C pages dev
pnpm -C pages check:docs
pnpm -C pages build
```

`src/content/docs` and the entries under `public/source` are repository-relative
links. Edit the canonical files in `docs/`, `charts/`, and `examples/` instead.
