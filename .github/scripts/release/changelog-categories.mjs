// Pure category-classification logic, split out of version-chart.mjs so it
// can be imported without running that script's side effects (changeset
// version, file writes, helm-docs). This is what lets
// changelog-categories.test.mjs exercise the exact coupling with
// .changeset/changelog-category.cjs's bullet-rendering format - the drift
// risk code review flagged in PR #193 - without a hand-copied duplicate of
// this regex living in the test itself.
//
// Keys must track .changeset/README.md's approved category list exactly -
// nothing more, nothing less - so an unapproved category (Refactor, Chore,
// ...) falls to "Other" instead of getting its own heading. Insertion order
// doubles as display order (see CATEGORY_ORDER below), matching the order
// .changeset/README.md lists them in.
export const CATEGORY_LABELS = {
  Feature: 'Features',
  Fix: 'Fixes',
  Security: 'Security',
  Dependency: 'Dependencies',
  Documentation: 'Documentation',
  Deprecated: 'Deprecated',
  Removed: 'Removed',
};
// Derived, never hand-duplicated: a label present only in CATEGORY_LABELS
// used to mean its bullets rendered nowhere - dropped, not just misgrouped,
// since the output loop only iterates CATEGORY_ORDER. Deriving it removes
// that failure mode entirely.
export const CATEGORY_ORDER = Object.values(CATEGORY_LABELS);
export const OTHER_LABEL = 'Other';

// Classify a single changelog bullet by the "Category(scope): Title" prefix
// .changeset/changelog-category.cjs writes at the start of every bullet's
// first line. Takes the FIRST LINE ONLY - a Word(...): -shaped substring
// anywhere in a continuation paragraph must not mis-group an otherwise
// non-conforming entry; it should fall to OTHER_LABEL instead.
export function categorizeBullet(firstLine) {
  const match = firstLine.match(/\b([A-Z][a-zA-Z]+)\([^)]+\):/);
  return (match && CATEGORY_LABELS[match[1]]) || OTHER_LABEL;
}
