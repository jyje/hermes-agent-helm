# Changelog

All notable changes to this chart are documented here.
## [0.10.0] - 2026-07-21

### Miscellaneous

- 🎨 style(pages): drop repo-level Releases badge, add shared badges to chart pages ([`137c50f`](https://github.com/jyje/hermes-agent-helm/commit/137c50f96c2b8d9c468a74e1abfd2c4d7278b0c3)) — @jyje
- 🎨 style(chart): move GitHub/License badges into the README's existing badge line ([`7758af5`](https://github.com/jyje/hermes-agent-helm/commit/7758af51e7ef55ecc9e6ad9ec4c5a716adc0d0b2)) — @jyje
- ⬆️ dep(image): bump hermes-agent image to v2026.7.20 (#64) ([`8fdaec7`](https://github.com/jyje/hermes-agent-helm/commit/8fdaec76e2c049abd5a30d01348127bc637a04b8)) — @jyje-bot[bot]

## [0.9.1] - 2026-07-08

### Features

- ✨ feat(ci): add GHCR download-count badge for repo and chart READMEs ([`b8d54d6`](https://github.com/jyje/hermes-agent-helm/commit/b8d54d62f797935a60a268ec0cf19df151d1fa36)) — @jyje

### Removed

- Chore(ci): remove temporary package-query debug workflow ([`ff1ac05`](https://github.com/jyje/hermes-agent-helm/commit/ff1ac05b6afa507b3732ab7615c6e310f232acdb)) — @jyje
- 🗑️ remove(ci): revert GHCR download-count badge (GraphQL Packages API is sunset) ([`75759d5`](https://github.com/jyje/hermes-agent-helm/commit/75759d58d7962c67ab98f27d5250e451d8e5bb82)) — @jyje

### Miscellaneous

- 🎨 style(chart): match chart README badges to the root README's flat style ([`f2f8456`](https://github.com/jyje/hermes-agent-helm/commit/f2f845689c1de286aaa54e658b55993aa1f144b9)) — @jyje

## [0.9.0] - 2026-07-08

### Features

- ✨ feat(examples): add a leader-orchestrated team deployment example ([`774e135`](https://github.com/jyje/hermes-agent-helm/commit/774e1357159f16425e4817424de44389246d17ed)) — @jyje

### Bug Fixes

- 🛠️ fix(skills/git-commit-helper): sync with latest canonical policy ([`25eaee0`](https://github.com/jyje/hermes-agent-helm/commit/25eaee0848da0328fe8d80a38004969920ef393b)) — @jyje
- 🛠️ fix(dependabot): add missing prefix-development for gitmoji convention ([`5e810d3`](https://github.com/jyje/hermes-agent-helm/commit/5e810d328517767f4951bca0a58d33b8ae56724a)) — @jyje
- 🛠️ fix(ci): drop the push trigger from validate-chart ([`1fd28dc`](https://github.com/jyje/hermes-agent-helm/commit/1fd28dc434140606d5a3ad654a0cc6ea51fc367f)) — @jyje

### Documentation

- 📄 docs(readme): add a contributing section with the contributor grid ([`34b0622`](https://github.com/jyje/hermes-agent-helm/commit/34b06226acbc69c9921cf4c9ac7cf39946347802)) — @jyje
- 📄 docs(teams): document leader-orchestrated teams and the git-backed wiki vault ([`93b4b97`](https://github.com/jyje/hermes-agent-helm/commit/93b4b972f9743e00b211f45be619369249964343)) — @jyje

### Miscellaneous

- ⬆️ dep(image): bump hermes-agent image to v2026.7.7.2 (#60) ([`a26137f`](https://github.com/jyje/hermes-agent-helm/commit/a26137f00ab320da0f4d70bc36406f5a60cffcfc)) — @jyje-bot[bot]

## [0.8.1] - 2026-07-02

### Bug Fixes

- Bug(changelog): credit only main's first-parent chain in git-cliff runs (#57) ([`2644f0d`](https://github.com/jyje/hermes-agent-helm/commit/2644f0d7fd0ac5e079edb61f9040a1d8f3b57d25)) — @jyje

### Documentation

- 📄 docs: add SECURITY.md and SECURITY-ko.md (#58) ([`656eb72`](https://github.com/jyje/hermes-agent-helm/commit/656eb728dfa95592750a8807b3a02172eb4985e2)) — @jyje

## [0.8.0] - 2026-07-02

### Features

- Feat(chart): expose terminationGracePeriodSeconds for the gateway drain window (#52) ([`5385946`](https://github.com/jyje/hermes-agent-helm/commit/5385946cee29e6bcb1434913179f478240752d0f)) — @jyje
- Feat(chart): add values-moa.yaml example for the Mixture-of-Agents provider (#53) ([`6065a2e`](https://github.com/jyje/hermes-agent-helm/commit/6065a2ead81ff5a93f5bf67ce1b01fb2a7efe861)) — @jyje

### Documentation

- Docs(chart): add ZAI_API_KEY to the curated env var table (#54) ([`7647a96`](https://github.com/jyje/hermes-agent-helm/commit/7647a96d07dd251c2cfd102c1e2f9abe2caf22dd)) — @jyje

## [0.7.0] - 2026-07-01

### Features

- ✨ feat(chart): add extraVolumes and extraVolumeMounts extension points ([`678c891`](https://github.com/jyje/hermes-agent-helm/commit/678c891ba419f73d5794c0a8eef9312f282562fd)) — @jyje
- ✨ feat(chart): add Google Vertex AI provider example ([`61d9d14`](https://github.com/jyje/hermes-agent-helm/commit/61d9d145283921ee3750cbaaeeec59ab8f03d460)) — @jyje

### Bug Fixes

- 🛠️ fix(ci): run functional tests when only appVersion changes ([`79bb307`](https://github.com/jyje/hermes-agent-helm/commit/79bb307bb69d6a8bfc4d02f9da34332178f4b9d0)) — @jyje

### Miscellaneous

- ⬆️ dep(image): bump hermes-agent image to v2026.7.1 (#40) ([`df71187`](https://github.com/jyje/hermes-agent-helm/commit/df71187484223a7601500b439d13f0606b206436)) — @jyje-bot[bot]

## [0.6.1] - 2026-07-01

### Bug Fixes

- 🐛 bug(changelog): credit plain Conventional Commits (no gitmoji) too ([`9c9d9aa`](https://github.com/jyje/hermes-agent-helm/commit/9c9d9aaf98f8c92d78adee5ca641557df0559dbb)) — @jyje
- 🐛 bug(ci): stop implying full CI passed in the Discord notice ([`6f37a2c`](https://github.com/jyje/hermes-agent-helm/commit/6f37a2c999d938d6c8c5e4eeb4f6d064be1db4ae)) — @jyje
- 🐛 bug(workflow/propose-release): drop redundant unreleased heading and stop false-crediting past PRs ([`ccb67a3`](https://github.com/jyje/hermes-agent-helm/commit/ccb67a3724dba1a2056cc927843416fd578c3f02)) — @jyje

### Documentation

- 📄 docs(ci): document the matrix test job and local script reuse ([`1127b60`](https://github.com/jyje/hermes-agent-helm/commit/1127b607dd7ba1fb7361698a6a8321c6c94b0751)) — @jyje
- 📄 docs(chart): link "Hermes Agent" to its upstream repo ([`672436d`](https://github.com/jyje/hermes-agent-helm/commit/672436da8b93dfb8cff912d2a24285a55c2c7697)) — @jyje
- 📄 docs(local-dev): note helm-docs verification after editing values.yaml ([`f9912c1`](https://github.com/jyje/hermes-agent-helm/commit/f9912c105ef89405ddb8a22df4530ca33db18cdc)) — @jyje

### Build

- 🔨 build(ci): rename the default scenario to message ([`ce41b5e`](https://github.com/jyje/hermes-agent-helm/commit/ce41b5ebe3dca648163eb304ee87e0b9d38695a9)) — @jyje

### Tests

- ✅ test(ci): run each validate-chart scenario on its own kind cluster ([`0db971a`](https://github.com/jyje/hermes-agent-helm/commit/0db971a041794c5584390a52d49db983e9f2dd41)) — @jyje

## [0.6.0] - 2026-06-30

### Features

- ✨ feat(ci): add post-release OCI signature verification workflow ([`88b8c09`](https://github.com/jyje/hermes-agent-helm/commit/88b8c09ce07bc0751eb0260a9a298fd0933d0e21)) — @jyje
- Feat: add support for existingClaim in persistence configuration (#37) ([`e376ae5`](https://github.com/jyje/hermes-agent-helm/commit/e376ae599f17bc5071bc46bdce887555dd98fad8)) — @Djiit

### Bug Fixes

- 🐛 bug(ci): pass the chat round-trip prompt via -q, not as a positional arg ([`d8e0092`](https://github.com/jyje/hermes-agent-helm/commit/d8e009202c5457cae16e4edc75a60d712247ad3d)) — @jyje

### Documentation

- 📄 docs(changelog): add v0.5.7 entry and backfill note for v0.4.2 ([`62e8809`](https://github.com/jyje/hermes-agent-helm/commit/62e88095a20173a46c38a27b9211f130d6057ae1)) — @jyje
- 📄 docs(contributing): add local development environment guide ([`9610f55`](https://github.com/jyje/hermes-agent-helm/commit/9610f55768418cad8620adb9a5187433d7155b3b)) — @jyje
- 📄 docs: add DevOps roadmap ([`94c68b3`](https://github.com/jyje/hermes-agent-helm/commit/94c68b3e45ffe77d3db6b821ba8633bfb8c174a5)) — @jyje
- 📄 docs(chart): sync README template with the two example value rows ([`ac1216f`](https://github.com/jyje/hermes-agent-helm/commit/ac1216f1d1b4250a881a200b83b8ceaea32bf6f3)) — @jyje
- 📄 docs(ci): add docs/ci.md and link it from CONTRIBUTING ([`889f7e2`](https://github.com/jyje/hermes-agent-helm/commit/889f7e2f6f8d749baf7cd3ad4a405b52c85ac531)) — @jyje

### Tests

- ✅ test(ci): run validate-chart scenarios in parallel with per-scenario timeouts ([`4145df8`](https://github.com/jyje/hermes-agent-helm/commit/4145df8247a53388e45bf44b0bef852f8c3b79cb)) — @jyje
- ✅ test(ci): add comprehensive checks to the post-release verify job ([`1d22eb3`](https://github.com/jyje/hermes-agent-helm/commit/1d22eb39e7ac1152a7d2f7bf9b59b3003e592074)) — @jyje

## [0.5.7] - 2026-06-29

### Documentation

- 📄 docs(chart): add Agent team section to chart README (EN + KO) ([`314ede4`](https://github.com/jyje/hermes-agent-helm/commit/314ede4d4b9197c3618515a73e4bff2af0720f03)) — @jyje

## [0.5.6] - 2026-06-29

### Bug Fixes

- 🐛 bug(pages): fix banner image distortion on narrow screens ([`1331318`](https://github.com/jyje/hermes-agent-helm/commit/1331318228f0f37c0968f909c8cebac99e77dbad)) — @jyje

## [0.5.5] - 2026-06-28

### Bug Fixes

- 🐛 bug(pages): rewrite relative links to absolute github urls in chart page ([`262cf80`](https://github.com/jyje/hermes-agent-helm/commit/262cf80f9fc6fc61d02cb7b70a84b745c78ae895)) — @jyje

### Miscellaneous

- 🎨 style(pages): fix light theme and set background to #f4f4f4 ([`e79a472`](https://github.com/jyje/hermes-agent-helm/commit/e79a472a28fecc6cd4001897be5b5cd38f211f0c)) — @jyje
- 🎨 style(readme): update banner image to 1000×500 optimized version ([`341885c`](https://github.com/jyje/hermes-agent-helm/commit/341885c9564440779f95596dc76e4a72e2810d35)) — @jyje
- 🎨 style(pages): switch to github-markdown-light.css to force light theme ([`c0edce8`](https://github.com/jyje/hermes-agent-helm/commit/c0edce8b8bb244762dbf40143d3364f6b8fc5b4a)) — @jyje
- 🎨 style(pages): override markdown-body background to #f4f4f4 ([`6217e73`](https://github.com/jyje/hermes-agent-helm/commit/6217e7315fe0b30569cd5b36bc999be1d8124a01)) — @jyje
- 🎨 style(pages): update page title and og:title to include product name ([`1e4b653`](https://github.com/jyje/hermes-agent-helm/commit/1e4b65311228e84a3390ca4130bf1fea6c36fde5)) — @jyje

## [0.5.4] - 2026-06-28

### Miscellaneous

- 🔧 chore(readme): use raw.githubusercontent.com absolute url for banner image ([`a284745`](https://github.com/jyje/hermes-agent-helm/commit/a284745264533f13e1306be3ba1aca194b0fc03a)) — @jyje
- 🎨 style(pages): add banner image to helm repo index page ([`36e7508`](https://github.com/jyje/hermes-agent-helm/commit/36e750829574e52fb810a4d440c77045b86bfe27)) — @jyje
- 🎨 style(readme): define banner image by height (240px) instead of width ([`362e32e`](https://github.com/jyje/hermes-agent-helm/commit/362e32e06d7c3b2caebf10944eeca1a23e606586)) — @jyje
- 🔧 chore(ci): rename app-id to client-id in create-github-app-token steps ([`c233f59`](https://github.com/jyje/hermes-agent-helm/commit/c233f597da9015f96e72956800d8318ae210ce7b)) — @jyje

## [0.5.3] - 2026-06-28

### Documentation

- 📄 docs(chart): add GitHub Copilot to the provider table ([`8e2ffe1`](https://github.com/jyje/hermes-agent-helm/commit/8e2ffe11fc00742cc666a1218e9eeaf8bea6e0c6)) — @jyje

### Miscellaneous

- 🎨 style(readme): replace Helm boat logo with Kubernetes icon ([`affe113`](https://github.com/jyje/hermes-agent-helm/commit/affe113b16b2e250f6394c28f4f08461f27867ed)) — @jyje
- 🎨 style(readme): vertically center the + sign between logos using a table ([`a2d410e`](https://github.com/jyje/hermes-agent-helm/commit/a2d410ea1eadbf6f215d536e11bbc821d0f98459)) — @jyje
- 🎨 style(readme): replace ➕ with enlarged × sign ([`cfe2e32`](https://github.com/jyje/hermes-agent-helm/commit/cfe2e325fa499462f3235f017353efa13f8e4271)) — @jyje
- 🎨 style(readme): replace kubernetes logo svg with png for github rendering ([`f262e12`](https://github.com/jyje/hermes-agent-helm/commit/f262e1233c55864282f483f75bd9dd5a5865eac7)) — @jyje
- 🎨 style(readme): remove table wrapper, use inline img align for logo row ([`609dd0c`](https://github.com/jyje/hermes-agent-helm/commit/609dd0c54aaca3dee06e887cf3206bb181b2e485)) — @jyje
- 🎨 style(readme): increase × font size to max html size (7) ([`1566a37`](https://github.com/jyje/hermes-agent-helm/commit/1566a3705667fe8fa4218693c9de34192576ef63)) — @jyje
- 🎨 style(readme): replace inline logo html with single banner image ([`9422c46`](https://github.com/jyje/hermes-agent-helm/commit/9422c4670335e80bc7f0c63fd66e4a14eecf3bc5)) — @jyje

## [0.5.2] - 2026-06-28

### Features

- ✨ feat(examples): add a collaborating-agent pair deployment example ([`1913c80`](https://github.com/jyje/hermes-agent-helm/commit/1913c801d75c8e0fdf095660eb90ec69a0b0c8c6)) — @jyje

### Documentation

- 📄 docs(collaboration): add the multi-agent collaboration guide ([`56b9249`](https://github.com/jyje/hermes-agent-helm/commit/56b92493b24a49b5913b7fe5a82876bffd8c37ba)) — @jyje
- 📄 docs(collaboration): link the guide from teams docs and READMEs ([`8917671`](https://github.com/jyje/hermes-agent-helm/commit/8917671cd788332f1683abc08a2ade96857cb131)) — @jyje
- 📄 docs(readme): add TL;DR section and surface collaboration links at the top ([`26bdabc`](https://github.com/jyje/hermes-agent-helm/commit/26bdabc6ca3627501e3d872d6efa5e775e389286)) — @jyje
- 📄 docs(chart): add agent team entry to TL;DR section ([`e8b6977`](https://github.com/jyje/hermes-agent-helm/commit/e8b6977d5e70e9814d33d321091bf472c79a2144)) — @jyje

### Miscellaneous

- ⬆️ dep(workflow): bump action deps and correct Python init-container to 3.13-slim ([`303d345`](https://github.com/jyje/hermes-agent-helm/commit/303d345b53d1aaa8c453caf84d37414ea5bc43b1)) — @jyje

## [0.5.1] - 2026-06-27

### Features

- ✨ feat(release): show AppVersion in release notes, AI-review upstream bumps ([`52d3aac`](https://github.com/jyje/hermes-agent-helm/commit/52d3aac1c1e3a3e45e445f6f23d267fa0bac4a83)) — @jyje
- ✨ feat(release): split image-bump into parallel PR + AI issue-filing jobs ([`7845a73`](https://github.com/jyje/hermes-agent-helm/commit/7845a7338e6649e00618dca5585176e21ce87651)) — @jyje
- ✨ feat(chart): add OAuth device-flow login init container (#23) ([`09f11d4`](https://github.com/jyje/hermes-agent-helm/commit/09f11d4d15a520ee85bb24987c034f68dbbf7a1c)) — @jyje

### Bug Fixes

- 🛠️ fix(release): adopt a dedicated 🚀 release type for the release PR title ([`3195301`](https://github.com/jyje/hermes-agent-helm/commit/319530142ead99cae19b9a0770cd7879e758a9b6)) — @jyje
- 🛠️ fix(release): raise the image-bump advisor's NIM timeout to 300s ([`eceb1ad`](https://github.com/jyje/hermes-agent-helm/commit/eceb1ad1038c38fe011ecae4b76c73b0b16156c4)) — @jyje
- 🛠️ fix(release): stream the image-bump advisor's NIM call ([`2cda2d0`](https://github.com/jyje/hermes-agent-helm/commit/2cda2d02e3b1c0f668b731f795dae77a2679d432)) — @jyje
- 🛠️ fix(release): authenticate cosign to ghcr before signing (#25) ([`4dec2e6`](https://github.com/jyje/hermes-agent-helm/commit/4dec2e68beb16013c0d496f665ea91a9b3bc0b1f)) — @jyje

### Build

- 🔨 build(release): add one-off test workflow for the image-bump advisor ([`e506bc5`](https://github.com/jyje/hermes-agent-helm/commit/e506bc57237bff2f9b405b6962bafac1038a2ec7)) — @jyje

### Removed

- 🗑️ remove(release): drop the one-off image-bump advisor test workflow ([`0b1d419`](https://github.com/jyje/hermes-agent-helm/commit/0b1d419ecf1cabbcde86dceff894d25cb9699fbe)) — @jyje

### Miscellaneous

- 🎨 style(workflow): add a clock emoji to cron-fetch-image's display name ([`7116965`](https://github.com/jyje/hermes-agent-helm/commit/71169657ed162b36017802429c9bc47fb5628744)) — @jyje

## [0.4.2] - 2026-06-21

### Features

- ✨ feat(release): sign published charts with cosign (keyless) ([`bd133be`](https://github.com/jyje/hermes-agent-helm/commit/bd133be6e0ebb5f6269ba63dc666f2a282fcb551)) — @jyje

### Bug Fixes

- 🛠️ fix(release): log in to ghcr before signing in the backfill workflow ([`9b893f8`](https://github.com/jyje/hermes-agent-helm/commit/9b893f8554df38202856593196f7b9cc92fe9a9d)) — @jyje

### Build

- 🔨 build(release): add one-off cosign backfill workflow ([`fb1d002`](https://github.com/jyje/hermes-agent-helm/commit/fb1d002c1ab3ab18d59af5ff0cb73e17ff27c646)) — @jyje

### Removed

- 🗑️ remove(release): drop the one-off cosign backfill workflow ([`a4240f7`](https://github.com/jyje/hermes-agent-helm/commit/a4240f703479e1a0c37f21a95e73568bc5835c95)) — @jyje

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

### Miscellaneous

- Chore(deps): bump actions/checkout from 6 to 7 ([`de41fd0`](https://github.com/jyje/hermes-agent-helm/commit/de41fd0f5a19334833a84bfeeeda5280ac98dc67)) — @dependabot[bot]

## [0.3.1] - 2026-06-20

### Features

- ✨ feat(pages): render chart cards with version, description, and icon ([`a5a4da3`](https://github.com/jyje/hermes-agent-helm/commit/a5a4da31595c6121e6209dee0829b862d17e2150)) — @jyje

### Bug Fixes

- Fix(ci): skip non-chart placeholder dirs in release-chart docs build ([`9c1af95`](https://github.com/jyje/hermes-agent-helm/commit/9c1af95b030517b1d6c7de66890db92c7ae8b6b5)) — @jyje
- Fix(ci): always run release/next branch cleanup even if a prior step fails ([`bafee9f`](https://github.com/jyje/hermes-agent-helm/commit/bafee9f4f018c90757f78c7d1c2c0b0dd0a5bad5)) — @jyje
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
- Chore(deps): bump softprops/action-gh-release from 2 to 3 ([`10b27ff`](https://github.com/jyje/hermes-agent-helm/commit/10b27ff5e28aa2ab378345004c7b6eee22fd3443)) — @dependabot[bot]
- Chore(deps): bump azure/setup-helm from 4 to 5 ([`995a39a`](https://github.com/jyje/hermes-agent-helm/commit/995a39aaf2cba77ec7c5165992ecd88e362cca7d)) — @dependabot[bot]
- Chore(deps): bump actions/checkout from 4 to 6 ([`8945f28`](https://github.com/jyje/hermes-agent-helm/commit/8945f28104b676ff478ae7830beed4be8ee656a7)) — @dependabot[bot]
- Chore(deps): bump actions/github-script from 7 to 9 ([`2b6f700`](https://github.com/jyje/hermes-agent-helm/commit/2b6f700f227a5c02c1da4c60b86c4d0908ae88de)) — @dependabot[bot]
- Chore(deps): bump peter-evans/create-pull-request from 6 to 8 ([`2863bb2`](https://github.com/jyje/hermes-agent-helm/commit/2863bb2fbd39a863242b5ba456c4b7a17b3c4299)) — @dependabot[bot]
- 🎨 style(ci): add ⚡ emoji to version-comment workflow display name ([`e5573a2`](https://github.com/jyje/hermes-agent-helm/commit/e5573a222a8cdfcfd4de5e7942139ad1a9aa14f0)) — @jyje
- 🔧 chore(ci): skip the kind round-trip test on version-only changes ([`766f565`](https://github.com/jyje/hermes-agent-helm/commit/766f56519fe5b273b11abd741f04288b4b8821fc)) — @jyje
- 🎨 style(pages): unify theme between the index and chart docs pages ([`ff2a224`](https://github.com/jyje/hermes-agent-helm/commit/ff2a224c7c282f61a86093803edeb1e1e6718214)) — @jyje
- 🔧 chore(scripts): add .gitignore for Python cache ([`c8e5ae4`](https://github.com/jyje/hermes-agent-helm/commit/c8e5ae482fa9fbb2fe695f0ec0162ddbca7af75c)) — @jyje

