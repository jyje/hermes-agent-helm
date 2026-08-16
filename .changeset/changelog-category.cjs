// Custom Changesets changelog formatter.
//
// Split into two responsibilities that live in two different places on
// purpose:
//
//   1. Per-bullet line format (THIS file, wired via .changeset/config.json's
//      "changelog" field): link the PR/commit and credit the commit author,
//      the same way @changesets/changelog-github does - reusing
//      @changesets/get-github-info rather than reimplementing GitHub lookups.
//      https://github.com/changesets/changesets/blob/main/packages/changelog-github/src/index.ts
//
//   2. Category grouping ("### Features" / "### Fixes" / ... instead of
//      "### Major Changes" / "### Minor Changes" / "### Patch Changes"):
//      NOT controllable from here. @changesets/apply-release-plan hardcodes
//      those headers (`### ${capitalize(type)} Changes`) in
//      generateMarkdownForVersionType, upstream of any changelog module:
//      https://github.com/changesets/changesets/blob/main/packages/apply-release-plan/src/get-changelog-entry.ts
//      So this file leaves the "Type(scope): Title" prefix visible in every
//      bullet - that prefix is the parseable signal
//      .github/scripts/release/version-chart.mjs's regroupChangelogByCategory
//      uses in a second pass, right after `changeset version` writes
//      CHANGELOG.md. The category vocabulary lives there; this file does not
//      need to know it.
const { getCommitInfo } = require('@changesets/get-github-info');

// GitHub stamps every bot identity's login with a literal "[bot]" suffix
// (dependabot[bot], jyje-bot[bot], github-actions[bot], ...) - that's the
// platform's own signal, so this repo doesn't have to hand-maintain a bot
// roster next to `maintainers` in .changeset/config.json. A bot's commits
// are automation the maintainer already approved (its workflow triggers,
// its PRs get reviewed), not an outside contribution and not invisible
// maintainer work either - so it gets its own credit phrasing, distinct
// from both "thanks" (outside human) and no-credit (maintainer).
const BOT_LOGIN_PATTERN = /\[bot\]$/;

async function getReleaseLine(changeset, _type, options) {
  const repo = options?.repo;
  if (!repo) {
    throw new Error(
      'Provide a repo: "changelog": ["./changelog-category.cjs", { "repo": "org/repo" }]',
    );
  }
  const maintainers = new Set(options?.maintainers ?? []);

  const [firstLine, ...futureLines] = changeset.summary.trim().split('\n');
  const continuation = futureLines.length
    ? `\n\n  ${futureLines.join('\n').trim().replace(/\n/g, '\n  ')}`
    : '';

  let credit = '';
  if (changeset.commit) {
    // A commit that isn't pushed/indexed on GitHub yet (or any API hiccup)
    // resolves to undefined here - degrade to a plain, linkless bullet
    // rather than fail the whole release. Still log it: a silently missing
    // credit line is easy to miss until someone reads a real release.
    const info = await getCommitInfo({ commit: changeset.commit, repo }).catch((error) => {
      console.warn(`[changelog-category] getCommitInfo(${changeset.commit}) failed: ${error.message}`);
      return undefined;
    });
    const parts = [info?.pull?.markdownLink, info?.commit?.markdownLink].filter(Boolean);
    if (parts.length) credit += ` ${parts.join(' ')}`;
    if (info?.author?.markdownLink && !maintainers.has(info.author.login)) {
      credit += BOT_LOGIN_PATTERN.test(info.author.login)
        ? ` — 🤖 automated by ${info.author.markdownLink}`
        : ` — thanks ${info.author.markdownLink}!`;
    }
  }

  return `\n\n-${credit ? `${credit} -` : ''} ${firstLine}${continuation}`;
}

async function getDependencyReleaseLine() {
  // This chart has no internal monorepo dependents to report.
  return '';
}

module.exports = { getReleaseLine, getDependencyReleaseLine };
