# Changelog

All notable changes to this chart are documented here.
## [0.4.1] - 2026-06-21

### Features

- ✨ feat(chart): add values.schema.json for upfront values validation ([`7722e44`](https://github.com/jyje/hermes-agent-helm/commit/7722e444441f5a7702ccd4cd89db0f4195b3c47f)) — @jyje

### Bug Fixes

- 🛠️ fix(release): quote artifacthub.io/changes entries to satisfy Artifact Hub ([`809e00f`](https://github.com/jyje/hermes-agent-helm/commit/809e00f2018ad3103c33090477ac0512b54c6db4)) — @jyje
- 🛠️ fix(release): keep the Korean chart README's version in sync too ([`07944be`](https://github.com/jyje/hermes-agent-helm/commit/07944be61bc658901e198b663197a1e1f3e5363d)) — @jyje

### Documentation

- 📄 docs: add Artifact Hub badge to the project README ([`fc951f0`](https://github.com/jyje/hermes-agent-helm/commit/fc951f02705ea45423566172f15f214afd90d679)) — @jyje
- 📄 docs(chart): add a TL;DR install block to the top of the chart README ([`d99e531`](https://github.com/jyje/hermes-agent-helm/commit/d99e531111ebb09f8f7b78a332918a16d9fa96e0)) — @jyje
- 📄 docs(chart): move quick-start content above, details below ([`8db8327`](https://github.com/jyje/hermes-agent-helm/commit/8db8327b95b8fd1b068bc4b81d40517d8536b9bd)) — @jyje

## [0.4.0] - 2026-06-20

### Features

- ✨ feat(skills): add hermes-agent-env-rule ([`1744dd1`](https://github.com/jyje/hermes-agent-helm/commit/1744dd1e3dcf92581d11fb28e27f1bdebd506e5e)) — @jyje
- ✨ feat(ci): tag dependabot commits with a dedicated bot prefix ([`52e9541`](https://github.com/jyje/hermes-agent-helm/commit/52e9541fdfbfc6ac1a9da48c98a11be893ff57a1)) — @jyje
- ✨ feat(ci): authenticate bot PRs via a GitHub App to skip approval gate ([`20dea61`](https://github.com/jyje/hermes-agent-helm/commit/20dea6169f8a35e5e3cb9886c2e8f1b0624aa8cc)) — @jyje

### Documentation

- 📄 docs(chart): add Environment variables section to README ([`afa9d7a`](https://github.com/jyje/hermes-agent-helm/commit/afa9d7a7f4b2dd617216bd3f0876942de4b0aab5)) — @jyje
- 📄 docs(chart): add Korean translation of the chart README ([`830ab12`](https://github.com/jyje/hermes-agent-helm/commit/830ab128a184b6590273ad044fb2b3b3438e35d3)) — @jyje

## [0.3.1] - 2026-06-20

### Features

- ✨ feat(pages): render chart cards with version, description, and icon ([`a5a4da3`](https://github.com/jyje/hermes-agent-helm/commit/a5a4da31595c6121e6209dee0829b862d17e2150)) — @jyje

### Bug Fixes

- 🛠️ fix(pages): correct YAML indentation in release-chart docs build step ([`564680c`](https://github.com/jyje/hermes-agent-helm/commit/564680cd96edaabeea57fdb033437bb1af081dc5)) — @jyje

### Miscellaneous

- 🎨 style(pages): give index and chart docs pages their own visual identity ([`c717ffe`](https://github.com/jyje/hermes-agent-helm/commit/c717ffe1e37ffbfcab73344140c8b589cf4b1691)) — @jyje
- 🎨 style(chart): move Description column before Default in values table ([`1862dd9`](https://github.com/jyje/hermes-agent-helm/commit/1862dd9d963bc8b35dc41b4dc827e2794ea0ffc7)) — @jyje
- 🔧 chore(skills): add .agents symlink for cross-agent skill discovery ([`d305285`](https://github.com/jyje/hermes-agent-helm/commit/d30528572c120bfd06ae3504beb9f4b7d38d51e1)) — @jyje

## [0.3.0] - 2026-06-20

### Features

- ✨ feat(chart): run test job automatically as ArgoCD PostSync hook ([`17097da`](https://github.com/jyje/hermes-agent-helm/commit/17097dab9a3f459c9ca3346c8801bc80633e783a)) — @jyje

### Documentation

- 📄 docs(readme): document team scaling via ArgoCD ApplicationSet and add roadmap ([`34f30bd`](https://github.com/jyje/hermes-agent-helm/commit/34f30bdcdf25495ff02ffd9a448dae3766e86e7e)) — @jyje

### Miscellaneous

- 🎨 style(chart): add centered logo header and rename chart README title ([`96a210b`](https://github.com/jyje/hermes-agent-helm/commit/96a210b2ffd77348425dfdfb6ccfef4e0e086c2b)) — @jyje
- ⬆️ dep(image): bump hermes-agent image to v2026.6.19 ([`71705be`](https://github.com/jyje/hermes-agent-helm/commit/71705be2750b6764444902161cea83d3a0d269f2)) — @github-actions[bot]

## [0.2.0] - 2026-06-15

### Features

- ✨ feat(release): prepend chart description to release notes ([`1826b0e`](https://github.com/jyje/hermes-agent-helm/commit/1826b0ec9208370479663da79096d1fda57b85f9)) — @jyje
- ✨ feat(ci): add cron-fetch-image to track upstream hermes-agent image ([`88558e6`](https://github.com/jyje/hermes-agent-helm/commit/88558e65ad3489485c99c48375fe92a3b70ad15a)) — @jyje
- ✨ feat(ci): notify Discord on healthy chart CI via hermes send (#12) ([`c204909`](https://github.com/jyje/hermes-agent-helm/commit/c2049090e9998e91d6bf29d2748194333b3024f8)) — @jyje
- ✨ feat(chart): add Ingress support and expand values/ArgoCD examples (#13) ([`38f22d8`](https://github.com/jyje/hermes-agent-helm/commit/38f22d85ecff4d6651cececbd1a862d25885d512)) — @jyje

### Documentation

- 📄 docs(chart): refresh chart description to reflect current overview ([`3d2b61d`](https://github.com/jyje/hermes-agent-helm/commit/3d2b61d573fab7b6e86032054313d5e093eae9fa)) — @jyje
- 📄 docs: update README to unify description of Hermes Agent Helm chart ([`f615749`](https://github.com/jyje/hermes-agent-helm/commit/f6157491ab83ef460f8a1de1ca63cfa4418726e1)) — @jyje
- 📄 docs(chart): prepend repo tagline to chart description ([`6f071b7`](https://github.com/jyje/hermes-agent-helm/commit/6f071b72354efce90469366d7ccfe5dc753acd76)) — @jyje

### Miscellaneous

- 🔧 chore(changelog): consolidate v0.0.1-v0.1.0 history into v0.1.1 ([`a33a14b`](https://github.com/jyje/hermes-agent-helm/commit/a33a14b5466e1b07820e56f24a3f784a8162648d)) — @jyje

## [0.1.1] - 2026-06-14

### Initial Release

- 🎉 init: setup project and ci ([`62d764b`](https://github.com/jyje/hermes-agent-helm/commit/62d764b8548ed2415474483023abe995a7cbf6d2)) — @jyje

### Features

- ✨ feat(chart): allow choosing StatefulSet or Deployment via controller.type ([`8db240b`](https://github.com/jyje/hermes-agent-helm/commit/8db240b47ec6d733ec4111eac00c467f9c2021f7)) — @jyje
- ✨ feat(chart): default to Deployment controller and add extraResources for GitOps secrets ([`7be636b`](https://github.com/jyje/hermes-agent-helm/commit/7be636b30909a313de89c8da9cc82e043b5effa2)) — @jyje
- ✨ feat(ci): add a model pool for the chat round-trip test and fix slow helm test ([`254712e`](https://github.com/jyje/hermes-agent-helm/commit/254712e4669cb59d2e19eabe3ab1e30f9f7bf98b)) — @jyje
- ✨ feat(ci): add AI-assisted release-proposal pipeline ([`486293c`](https://github.com/jyje/hermes-agent-helm/commit/486293c4d09b080fedcd0578a0f1e9f2931441c4)) — @jyje
- ✨ feat(ci): support explicit version override in release proposal ([`72f2b5f`](https://github.com/jyje/hermes-agent-helm/commit/72f2b5ffe826b3a46203e4de7d8a9f7c5c55d956)) — @jyje
- ✨ feat(ci): credit each changelog entry to its commit author ([`62ef69c`](https://github.com/jyje/hermes-agent-helm/commit/62ef69c642e4cad4f169eb06006f0427b77955d4)) — @jyje
- ✨ feat(dependabot): add configuration for automated dependency updates (gha, helm) ([`c13812f`](https://github.com/jyje/hermes-agent-helm/commit/c13812f1b00b2ea9c851d6ec356218c27f5db3c5)) — @jyje
- ✨ feat(release): publish chart to GitHub Pages as a classic Helm repo ([`1d25c80`](https://github.com/jyje/hermes-agent-helm/commit/1d25c8069948e7bc78e9074cfdfc142ca3631b16)) — @jyje
- ✨ feat(pages): generate per-chart docs pages for GitHub Pages ([`4611de2`](https://github.com/jyje/hermes-agent-helm/commit/4611de25f0bec8f0b7eddf2da3ab14464e4f2a72)) — @jyje
- ✨ feat(skills): add release-flow ([`921794a`](https://github.com/jyje/hermes-agent-helm/commit/921794a080703916a715197abef3156ef459e47e)) — @jyje
- ✨ feat(release): AI-propose artifacthub.io/changes entries ([`5ec3644`](https://github.com/jyje/hermes-agent-helm/commit/5ec3644fa3125c1ab213fb1c6a915b0b1e02dcda)) — @jyje
- ✨ feat(ci): add /rescan PR command and rename event- to command- prefix ([`f596803`](https://github.com/jyje/hermes-agent-helm/commit/f5968031ea28722c16e6087deaa4b183e04d0f05)) — @jyje
- ✨ feat(release): name GitHub Releases after the chart, not the repo ([`97c1f89`](https://github.com/jyje/hermes-agent-helm/commit/97c1f89e28aaf45f3f5dd45494532fcc0378e7ac)) — @jyje
- ✨ feat(release): add install/changelog/contributors release notes template ([`4f07f8c`](https://github.com/jyje/hermes-agent-helm/commit/4f07f8cf6d009bc7b608f28d8d1c1b68e1eb5d1a)) — @jyje
- ✨ feat(workflow): update rescan-changes name to use a lightning bolt emoji ([`2059ef2`](https://github.com/jyje/hermes-agent-helm/commit/2059ef245e5773eb5c28f387a973cb10b0f1bb5f)) — @jyje

### Bug Fixes

- 🛠️ fix(ci): force-kill hermes doctor on timeout and simplify round-trip prompt ([`cd1ebcc`](https://github.com/jyje/hermes-agent-helm/commit/cd1ebccee9da949664e72839a5e9478d8a5cc8b4)) — @jyje
- 🛠️ fix(ci): only run helm CI on chart or workflow changes ([`99220b1`](https://github.com/jyje/hermes-agent-helm/commit/99220b1ad9dbf20567cda560c5e7950189f64510)) — @jyje
- 🛠️ fix(ci): switch chat round-trip test from Gemini to NVIDIA NIM ([`048c71d`](https://github.com/jyje/hermes-agent-helm/commit/048c71dee39da1844b120a2b5d2dbdec818badd2)) — @jyje
- 🛠️ fix(ci): run the chart test Job directly instead of via helm test ([`7dc8eec`](https://github.com/jyje/hermes-agent-helm/commit/7dc8eec193ddd2ed9e815b29c4ae6776bfe49aa0)) — @jyje
- 🛠️ fix(ci): avoid duplicate auth header in propose-release PR step ([`b1674d2`](https://github.com/jyje/hermes-agent-helm/commit/b1674d25ce201b1451c2030276c4b4501c7dc84f)) — @jyje
- 🛠️ fix(ci): regenerate chart docs in the release proposal ([`d6ebf6f`](https://github.com/jyje/hermes-agent-helm/commit/d6ebf6f366984d3986f2ebb64989d61a99058549)) — @jyje
- 🛠️ fix(ci): harden NIM advisor against null content and any error ([`e40ce46`](https://github.com/jyje/hermes-agent-helm/commit/e40ce46c3e857b9731af2057bc72ec4440b2c6ae)) — @jyje
- 🛠️ fix(readme): reorder logos in README for improved visibility ([`f52fb4b`](https://github.com/jyje/hermes-agent-helm/commit/f52fb4bd580c896f543c626987f70203daf36e04)) — @jyje
- 🛠️ fix(release): add instructions for merging release proposals ([`453450b`](https://github.com/jyje/hermes-agent-helm/commit/453450bb8464259facf762ba5a0609c8a7292170)) — @jyje
- 🛠️ fix(release): remove workflow_dispatch trigger ([`d877004`](https://github.com/jyje/hermes-agent-helm/commit/d8770049e5a36a7aa39cb88759075996d6a3cbe7)) — @jyje
- 🛠️ fix(release): correct OCI artifact path to ghcr.io/jyje/hermes-agent-helm/hermes-agent ([`76cf8e4`](https://github.com/jyje/hermes-agent-helm/commit/76cf8e4925f46de2a807a62ba48fb080b146e34f)) — @jyje
- 🛠️ fix(release): increase NIM max_tokens budget for reasoning models ([`556c687`](https://github.com/jyje/hermes-agent-helm/commit/556c687ade6fb9d0d620d4cc4bbd7e27e8f71ee7)) — @jyje

### Refactor

- ♻️ refactor(chart): rename hermes-agent chart to hermes-agent-helm ([`27d01e4`](https://github.com/jyje/hermes-agent-helm/commit/27d01e4c8a7b1f71890a93590048e109f4e8d95f)) — @jyje
- ♻️ refactor(chart): rename chart to hermes-agent, reset version to 0.0.1 ([`0dd89ef`](https://github.com/jyje/hermes-agent-helm/commit/0dd89efe3e66a34f78f90fc3c023f24de2f06014)) — @jyje
- ♻️ refactor(ci): rename YAML file, fix dependabot settings ([`610046c`](https://github.com/jyje/hermes-agent-helm/commit/610046c789e21a7471069b718c797c28aff82c3f)) — @jyje
- ♻️ refactor(ci): rename workflows for clearer roles and kebab-case filenames ([`bf1c8d4`](https://github.com/jyje/hermes-agent-helm/commit/bf1c8d4c82754677a3dc4c1d7cbb8f1b21e776b6)) — @jyje
- ♻️ refactor(release): drop duplicate Contributors section from release notes ([`a1b174d`](https://github.com/jyje/hermes-agent-helm/commit/a1b174d73c0e12175e83c244c4e3c83071d8f5b3)) — @jyje
- ♻️ refactor(ci): rebuild /version as a propose-release re-dispatch with a pinned version ([`b53fbe7`](https://github.com/jyje/hermes-agent-helm/commit/b53fbe7d3add87e8fa1ffd1d6c8110816bfc4809)) — @jyje

### Documentation

- 📄 docs(chart): document upgrade path across a chart rename ([`cee164c`](https://github.com/jyje/hermes-agent-helm/commit/cee164c6ca34a8ff5996fde406d6c345f4a3d9ff)) — @jyje
- 📄 docs(readme): revamp READMEs, add brand logo and messenger/provider examples ([`0183005`](https://github.com/jyje/hermes-agent-helm/commit/01830056ce4244c0d30bb2dbaeb6bdc2b6584025)) — @jyje
- 📄 docs(readme): lead with the Helm repo install and default to latest ([`800054f`](https://github.com/jyje/hermes-agent-helm/commit/800054f3f8fdba3ea4f84c0e12cf75028c88b51c)) — @jyje

### Build

- 🔨 build(changelog): fix git-cliff parsing for gitmoji commit messages and generate CHANGELOG.md ([`1aeb9ca`](https://github.com/jyje/hermes-agent-helm/commit/1aeb9ca4dcd3d74d9be05a36b5e83df9fbd6be46)) — @jyje

### Miscellaneous

- 🔧 chore(ci): add debug output for the helm test job-discovery loop ([`da80da0`](https://github.com/jyje/hermes-agent-helm/commit/da80da0e3760b7b76c1e7fc9957e76ad3108acca)) — @jyje
- 🔧 chore(ci): bump checkout/setup-helm to node24-based versions ([`f034208`](https://github.com/jyje/hermes-agent-helm/commit/f034208568c5e6248660cecb65a9dbc27fb2d553)) — @jyje
- 🔧 chore(ci): make changelog entries title + commit link only ([`f656ada`](https://github.com/jyje/hermes-agent-helm/commit/f656ada2cc1b57a2162b3fa546527265a6028b9f)) — @jyje
- 🔧 chore(ci): move all runners to ubuntu-26.04-arm ([`95e0484`](https://github.com/jyje/hermes-agent-helm/commit/95e04849567832bbd2dcdcaca5df58919b792729)) — @jyje
- 🔧 chore(ci): add emoji to release proposal, dynamic release name, branch cleanup ([`84ca116`](https://github.com/jyje/hermes-agent-helm/commit/84ca11636f6521d1699aaa6437ece567c5ce2be4)) — @jyje
- 🎨 style(ci): add ⚡ emoji to version-comment workflow display name ([`e5573a2`](https://github.com/jyje/hermes-agent-helm/commit/e5573a222a8cdfcfd4de5e7942139ad1a9aa14f0)) — @jyje
- 🔧 chore(ci): skip the kind round-trip test on version-only changes ([`766f565`](https://github.com/jyje/hermes-agent-helm/commit/766f56519fe5b273b11abd741f04288b4b8821fc)) — @jyje
- 🎨 style(pages): unify theme between the index and chart docs pages ([`ff2a224`](https://github.com/jyje/hermes-agent-helm/commit/ff2a224c7c282f61a86093803edeb1e1e6718214)) — @jyje
- 🔧 chore(scripts): add .gitignore for Python cache ([`c8e5ae4`](https://github.com/jyje/hermes-agent-helm/commit/c8e5ae482fa9fbb2fe695f0ec0162ddbca7af75c)) — @jyje

