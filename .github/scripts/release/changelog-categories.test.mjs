// Regression test for the coupling code review flagged in PR #193: category
// classification (changelog-categories.mjs) depends on the exact bullet
// format .changeset/changelog-category.cjs renders, with nothing tying the
// two together before this test existed. Each case below runs the REAL
// getReleaseLine output through the REAL categorizeBullet - not a
// hand-copied fixture string - so a future format change in either file
// fails this test instead of silently mis-filing every bullet in the next
// real release under "### Other".
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { CATEGORY_LABELS, OTHER_LABEL, categorizeBullet } from './changelog-categories.mjs';

const require = createRequire(import.meta.url);
// getReleaseLine's credit-fetching branch (getCommitInfo) is a best-effort
// GitHub API call gated on changeset.commit being set. The bullet's first
// line - the only part categorizeBullet reads - is produced before that
// branch runs either way, so omitting `commit` here exercises the exact
// coupling under test without needing network access or a mock.
const { getReleaseLine } = require('../../../.changeset/changelog-category.cjs');

async function renderedFirstLine(summary) {
  const bullet = await getReleaseLine({ summary, commit: undefined }, 'minor', {
    repo: 'jyje/hermes-agent-helm',
  });
  // getReleaseLine returns "\n\n- <firstLine>...": strip the leading blank
  // lines and bullet marker the same way CHANGELOG.md's real body does.
  return bullet.replace(/^\n\n-\s?/, '').split('\n')[0];
}

for (const [category, label] of Object.entries(CATEGORY_LABELS)) {
  test(`${category}(scope): Title renders and categorizes as ${label}`, async () => {
    const firstLine = await renderedFirstLine(`${category}(scope): does the thing`);
    assert.equal(categorizeBullet(firstLine), label);
  });
}

test('an unapproved category falls to Other, not a crash', async () => {
  const firstLine = await renderedFirstLine('Refactor(scope): tidy up');
  assert.equal(categorizeBullet(firstLine), OTHER_LABEL);
});

test('a summary with no Category(scope): prefix falls to Other', async () => {
  const firstLine = await renderedFirstLine('bump the busybox init image');
  assert.equal(categorizeBullet(firstLine), OTHER_LABEL);
});
