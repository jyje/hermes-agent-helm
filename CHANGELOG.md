# Changelog

All notable changes to this chart are documented here.
## [0.1.0] - 2026-06-14

### Bug Fixes

- 🛠️ fix(release): correct OCI artifact path to ghcr.io/jyje/hermes-agent-helm/hermes-agent ([`76cf8e4`](https://github.com/jyje/hermes-agent-helm/commit/76cf8e4925f46de2a807a62ba48fb080b146e34f)) — @jyje
- 🛠️ fix(release): increase NIM max_tokens budget for reasoning models ([`556c687`](https://github.com/jyje/hermes-agent-helm/commit/556c687ade6fb9d0d620d4cc4bbd7e27e8f71ee7)) — @jyje

### Documentation

- 📄 docs(readme): lead with the Helm repo install and default to latest ([`800054f`](https://github.com/jyje/hermes-agent-helm/commit/800054f3f8fdba3ea4f84c0e12cf75028c88b51c)) — @jyje

### Features

- ✨ feat(release): AI-propose artifacthub.io/changes entries ([`5ec3644`](https://github.com/jyje/hermes-agent-helm/commit/5ec3644fa3125c1ab213fb1c6a915b0b1e02dcda)) — @jyje
- ✨ feat(ci): add /rescan PR command and rename event- to command- prefix ([`f596803`](https://github.com/jyje/hermes-agent-helm/commit/f5968031ea28722c16e6087deaa4b183e04d0f05)) — @jyje

### Miscellaneous

- 🔧 chore(ci): skip the kind round-trip test on version-only changes ([`766f565`](https://github.com/jyje/hermes-agent-helm/commit/766f56519fe5b273b11abd741f04288b4b8821fc)) — @jyje
- 🎨 style(pages): unify theme between the index and chart docs pages ([`ff2a224`](https://github.com/jyje/hermes-agent-helm/commit/ff2a224c7c282f61a86093803edeb1e1e6718214)) — @jyje
- 🔧 chore(scripts): add .gitignore for Python cache ([`c8e5ae4`](https://github.com/jyje/hermes-agent-helm/commit/c8e5ae482fa9fbb2fe695f0ec0162ddbca7af75c)) — @jyje

## [0.0.4] - 2026-06-14

### Bug Fixes

- 🛠️ fix(release): remove workflow_dispatch trigger ([`d877004`](https://github.com/jyje/hermes-agent-helm/commit/d8770049e5a36a7aa39cb88759075996d6a3cbe7)) — @jyje

### Features

- ✨ feat(release): publish chart to GitHub Pages as a classic Helm repo ([`1d25c80`](https://github.com/jyje/hermes-agent-helm/commit/1d25c8069948e7bc78e9074cfdfc142ca3631b16)) — @jyje
- ✨ feat(pages): generate per-chart docs pages for GitHub Pages ([`4611de2`](https://github.com/jyje/hermes-agent-helm/commit/4611de25f0bec8f0b7eddf2da3ab14464e4f2a72)) — @jyje
- ✨ feat(skills): add release-flow ([`921794a`](https://github.com/jyje/hermes-agent-helm/commit/921794a080703916a715197abef3156ef459e47e)) — @jyje

### Miscellaneous

- 🎨 style(ci): add ⚡ emoji to version-comment workflow display name ([`e5573a2`](https://github.com/jyje/hermes-agent-helm/commit/e5573a222a8cdfcfd4de5e7942139ad1a9aa14f0)) — @jyje

### Refactor

- ♻️ refactor(ci): rename workflows for clearer roles and kebab-case filenames ([`bf1c8d4`](https://github.com/jyje/hermes-agent-helm/commit/bf1c8d4c82754677a3dc4c1d7cbb8f1b21e776b6)) — @jyje

## [0.0.3] - 2026-06-14

### Bug Fixes

- 🛠️ fix(release): add instructions for merging release proposals ([`453450b`](https://github.com/jyje/hermes-agent-helm/commit/453450bb8464259facf762ba5a0609c8a7292170)) — @jyje

### Features

- ✨ feat(dependabot): add configuration for automated dependency updates (gha, helm) ([`c13812f`](https://github.com/jyje/hermes-agent-helm/commit/c13812f1b00b2ea9c851d6ec356218c27f5db3c5)) — @jyje

### Miscellaneous

- 🔧 chore(ci): add emoji to release proposal, dynamic release name, branch cleanup ([`84ca116`](https://github.com/jyje/hermes-agent-helm/commit/84ca11636f6521d1699aaa6437ece567c5ce2be4)) — @jyje

### Refactor

- ♻️ refactor(ci): rename YAML file, fix dependabot settings ([`610046c`](https://github.com/jyje/hermes-agent-helm/commit/610046c789e21a7471069b718c797c28aff82c3f)) — @jyje

## [0.0.2] - 2026-06-14

### Bug Fixes

- 🛠️ fix(ci): run the chart test Job directly instead of via helm test ([`7dc8eec`](https://github.com/jyje/hermes-agent-helm/commit/7dc8eec193ddd2ed9e815b29c4ae6776bfe49aa0)) — @jyje
- 🛠️ fix(ci): avoid duplicate auth header in propose-release PR step ([`b1674d2`](https://github.com/jyje/hermes-agent-helm/commit/b1674d25ce201b1451c2030276c4b4501c7dc84f)) — @jyje
- 🛠️ fix(ci): regenerate chart docs in the release proposal ([`d6ebf6f`](https://github.com/jyje/hermes-agent-helm/commit/d6ebf6f366984d3986f2ebb64989d61a99058549)) — @jyje
- 🛠️ fix(ci): harden NIM advisor against null content and any error ([`e40ce46`](https://github.com/jyje/hermes-agent-helm/commit/e40ce46c3e857b9731af2057bc72ec4440b2c6ae)) — @jyje
- 🛠️ fix(readme): reorder logos in README for improved visibility ([`f52fb4b`](https://github.com/jyje/hermes-agent-helm/commit/f52fb4bd580c896f543c626987f70203daf36e04)) — @jyje

### Documentation

- 📄 docs(readme): revamp READMEs, add brand logo and messenger/provider examples ([`0183005`](https://github.com/jyje/hermes-agent-helm/commit/01830056ce4244c0d30bb2dbaeb6bdc2b6584025)) — @jyje

### Features

- ✨ feat(ci): add a model pool for the chat round-trip test and fix slow helm test ([`254712e`](https://github.com/jyje/hermes-agent-helm/commit/254712e4669cb59d2e19eabe3ab1e30f9f7bf98b)) — @jyje
- ✨ feat(ci): add AI-assisted release-proposal pipeline ([`486293c`](https://github.com/jyje/hermes-agent-helm/commit/486293c4d09b080fedcd0578a0f1e9f2931441c4)) — @jyje
- ✨ feat(ci): support explicit version override in release proposal ([`72f2b5f`](https://github.com/jyje/hermes-agent-helm/commit/72f2b5ffe826b3a46203e4de7d8a9f7c5c55d956)) — @jyje
- ✨ feat(ci): credit each changelog entry to its commit author ([`62ef69c`](https://github.com/jyje/hermes-agent-helm/commit/62ef69c642e4cad4f169eb06006f0427b77955d4)) — @jyje

### Miscellaneous

- 🔧 chore(ci): add debug output for the helm test job-discovery loop ([`da80da0`](https://github.com/jyje/hermes-agent-helm/commit/da80da0e3760b7b76c1e7fc9957e76ad3108acca)) — @jyje
- 🔧 chore(ci): bump checkout/setup-helm to node24-based versions ([`f034208`](https://github.com/jyje/hermes-agent-helm/commit/f034208568c5e6248660cecb65a9dbc27fb2d553)) — @jyje
- 🔧 chore(ci): make changelog entries title + commit link only ([`f656ada`](https://github.com/jyje/hermes-agent-helm/commit/f656ada2cc1b57a2162b3fa546527265a6028b9f)) — @jyje
- 🔧 chore(ci): move all runners to ubuntu-26.04-arm ([`95e0484`](https://github.com/jyje/hermes-agent-helm/commit/95e04849567832bbd2dcdcaca5df58919b792729)) — @jyje

## [0.0.1] - 2026-06-14

### Bug Fixes

- 🛠️ fix(ci): force-kill hermes doctor on timeout and simplify round-trip prompt ([`cd1ebcc`](https://github.com/jyje/hermes-agent-helm/commit/cd1ebccee9da949664e72839a5e9478d8a5cc8b4)) — @jyje
- 🛠️ fix(ci): only run helm CI on chart or workflow changes ([`99220b1`](https://github.com/jyje/hermes-agent-helm/commit/99220b1ad9dbf20567cda560c5e7950189f64510)) — @jyje
- 🛠️ fix(ci): switch chat round-trip test from Gemini to NVIDIA NIM ([`048c71d`](https://github.com/jyje/hermes-agent-helm/commit/048c71dee39da1844b120a2b5d2dbdec818badd2)) — @jyje

### Build

- 🔨 build(changelog): fix git-cliff parsing for gitmoji commit messages and generate CHANGELOG.md ([`1aeb9ca`](https://github.com/jyje/hermes-agent-helm/commit/1aeb9ca4dcd3d74d9be05a36b5e83df9fbd6be46)) — @jyje

### Documentation

- 📄 docs(chart): document upgrade path across a chart rename ([`cee164c`](https://github.com/jyje/hermes-agent-helm/commit/cee164c6ca34a8ff5996fde406d6c345f4a3d9ff)) — @jyje

### Features

- ✨ feat(chart): allow choosing StatefulSet or Deployment via controller.type ([`8db240b`](https://github.com/jyje/hermes-agent-helm/commit/8db240b47ec6d733ec4111eac00c467f9c2021f7)) — @jyje
- ✨ feat(chart): default to Deployment controller and add extraResources for GitOps secrets ([`7be636b`](https://github.com/jyje/hermes-agent-helm/commit/7be636b30909a313de89c8da9cc82e043b5effa2)) — @jyje

### Initial Release

- 🎉 init: setup project and ci ([`62d764b`](https://github.com/jyje/hermes-agent-helm/commit/62d764b8548ed2415474483023abe995a7cbf6d2)) — @jyje

### Refactor

- ♻️ refactor(chart): rename hermes-agent chart to hermes-agent-helm ([`27d01e4`](https://github.com/jyje/hermes-agent-helm/commit/27d01e4c8a7b1f71890a93590048e109f4e8d95f)) — @jyje
- ♻️ refactor(chart): rename chart to hermes-agent, reset version to 0.0.1 ([`0dd89ef`](https://github.com/jyje/hermes-agent-helm/commit/0dd89efe3e66a34f78f90fc3c023f24de2f06014)) — @jyje

