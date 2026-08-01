# Documentation site

This directory contains the Astro Starlight site published at
`https://jyje.github.io/hermes-agent-helm`.

The repository Markdown and `charts/hermes-agent/values-*.yaml` files remain
the source of truth. `scripts/prepare-content.mjs` creates the Starlight input
and raw-source endpoints immediately before development and production builds.

```bash
pnpm -C pages install
pnpm -C pages dev
pnpm -C pages build
```

Do not edit `src/content/docs/`, `public/source/`, or `public/llms*.txt`
directly: they are generated and ignored by Git.
