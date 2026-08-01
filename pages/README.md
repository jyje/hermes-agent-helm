# Documentation site

This directory contains the Astro Starlight site published at
`https://jyje.github.io/hermes-agent-helm`.

The repository Markdown and files under `charts/*/` remain the source of truth.
`scripts/prepare-content.mjs` discovers every `charts/*/Chart.yaml` and creates
a chart-scoped Starlight area with installation, values, overlays, and raw
source endpoints immediately before development and production builds. Rich
Hermes Agent guides continue to be generated from their maintained sources.

To add another chart, place its Helm files under `charts/<chart-name>/` with a
`Chart.yaml` and `values.yaml`. Its documentation catalog entry is generated
without adding the chart name to site code.

```bash
pnpm -C pages install
pnpm -C pages dev
pnpm -C pages build
```

Do not edit `src/content/docs/`, `public/source/`, or `public/llms*.txt`
directly: they are generated and ignored by Git.
