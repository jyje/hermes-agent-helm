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
//      CHANGELOG.md. The category vocabulary lives in
//      .github/scripts/release/changelog-categories.mjs; this file does not
//      need to know it, but changelog-categories.test.mjs runs this file's
//      getReleaseLine for real to keep the two in sync - keep that test
//      updated if this bullet format ever changes.
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
    // The commit link needs no API call - repo + SHA is enough to build
    // GitHub's canonical commit URL - so it's written first and unconditionally.
    // This is the traceability floor: Changesets' own default changelog
    // always embeds this same short SHA locally, so a GitHub lookup failing
    // below must not regress below that baseline to a bare, linkless bullet.
    const shortSha = changeset.commit.slice(0, 7);
    credit = ` [\`${shortSha}\`](https://github.com/${repo}/commit/${changeset.commit})`;

    // The PR link and author credit are best-effort enhancements on top of
    // that floor: a commit that isn't pushed/indexed on GitHub yet (or any
    // other API hiccup) resolves to undefined here rather than failing the
    // whole release. Still log it: a silently degraded credit line is easy
    // to miss until someone reads a real release.
    const info = await getCommitInfo({ commit: changeset.commit, repo }).catch((error) => {
      console.warn(`[changelog-category] getCommitInfo(${changeset.commit}) failed: ${error.message}`);
      return undefined;
    });
    if (info?.pull?.markdownLink) credit = ` ${info.pull.markdownLink}${credit}`;
    if (info?.author?.markdownLink && !maintainers.has(info.author.login)) {
      credit += BOT_LOGIN_PATTERN.test(info.author.login)
        ? ` - 🤖 automated by ${info.author.markdownLink}`
        : ` - thanks ${info.author.markdownLink}!`;
    }
  }

  return `\n\n-${credit ? `${credit} -` : ''} ${firstLine}${continuation}`;
}

async function getDependencyReleaseLine() {
  // This chart has no internal monorepo dependents to report.
  return '';
}

module.exports = { getReleaseLine, getDependencyReleaseLine };
