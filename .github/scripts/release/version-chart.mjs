#!/usr/bin/env node
/**
 * Apply pending Changesets and synchronize the Helm release artefacts.
 *
 * Changesets owns the SemVer decision and CHANGELOG entry. This script is the
 * chart-specific bridge: it snapshots the pending summaries for Artifact Hub,
 * runs `changeset version`, then updates Chart.yaml and generated chart docs.
 * It intentionally never publishes anything.
 */
import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { CATEGORY_ORDER, OTHER_LABEL, categorizeBullet } from './changelog-categories.mjs';

const root = resolve(import.meta.dirname, '../../..');
const packageName = '@jyje/hermes-agent-helm';
const chartPath = resolve(root, 'charts/hermes-agent/Chart.yaml');
const changelogPath = resolve(root, 'CHANGELOG.md');
const statusPath = resolve(root, 'dist/release/changeset-status.json');

// .changeset/changelog-category.cjs keeps every bullet's "Type(scope): Title"
// prefix intact (see that file for why: apply-release-plan hardcodes the
// Major/Minor/Patch headers, so a changelog module can't replace them). This
// is the other half: regroup the section CHANGELOG.md just gained by that
// prefix instead. The category vocabulary itself lives in
// ./changelog-categories.mjs, shared with changelog-categories.test.mjs -
// keep that file and changelog-category.cjs's comment pointing at each other
// if either changes.

function run(command, args) {
  execFileSync(command, args, { cwd: root, stdio: 'inherit' });
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function readChangeset(id) {
  const source = readFileSync(resolve(root, '.changeset', `${id}.md`), 'utf8');
  const match = source.match(/^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
  if (!match) throw new Error(`Invalid Changeset format: ${id}`);
  const release = match[1].match(
    new RegExp(`^\\s*["']?${escapeRegExp(packageName)}["']?\\s*:\\s*(major|minor|patch)\\s*$`, 'm'),
  );
  if (!release) return null;
  const summary = match[2].replace(/\s+/g, ' ').trim();
  if (!summary) throw new Error(`Changeset ${id} has no summary`);
  return { id, type: release[1], summary };
}

function artifactHubKind(type) {
  return { major: 'changed', minor: 'added', patch: 'fixed' }[type];
}

// Rewrite CHANGELOG.md's "## <version>" section from
// "### Major/Minor/Patch Changes" (apply-release-plan's fixed grouping) into
// "### Features" / "### Fixes" / ... by reading the "Type(scope): Title"
// prefix changelog-category.cjs left on every bullet. A bullet whose author
// didn't follow that convention (e.g. an older manual entry, or a
// machine-generated one) falls into "### Other" rather than being dropped -
// this must never lose an entry, only regroup it.
function regroupChangelogByCategory(version) {
  const changelog = readFileSync(changelogPath, 'utf8');
  const heading = `## ${version}\n`;
  const start = changelog.indexOf(heading);
  if (start === -1) throw new Error(`CHANGELOG.md has no "${heading.trim()}" section to regroup`);
  const bodyStart = start + heading.length;
  const nextHeadingOffset = changelog.slice(bodyStart).search(/\n## /);
  const bodyEnd = nextHeadingOffset === -1 ? changelog.length : bodyStart + nextHeadingOffset + 1;
  const body = changelog.slice(bodyStart, bodyEnd);

  // One bullet = a "- " line at column 0, plus every following line that is
  // blank or indented (its continuation paragraph), up to the next "- " or
  // "### " line or the end of the section.
  const bullets = [...body.matchAll(/^-.*(?:\n(?:[ \t].*)?)*/gm)]
    .map((m) => m[0].replace(/\n+$/, ''))
    .filter((bullet) => bullet.trim().length > 0);
  if (!bullets.length) throw new Error(`No bullets found under "${heading.trim()}" - refusing to rewrite it empty`);

  const buckets = new Map();
  for (const bullet of bullets) {
    // Match only the bullet's first line - the "Category(scope): Title"
    // prefix changelog-category.cjs writes. Matching the whole bullet let a
    // Word(...): -shaped substring anywhere in the continuation paragraph
    // mis-group an otherwise non-conforming entry instead of it falling to
    // "Other".
    const firstLine = bullet.split('\n', 1)[0];
    const label = categorizeBullet(firstLine);
    if (!buckets.has(label)) buckets.set(label, []);
    buckets.get(label).push(bullet);
  }

  const orderedLabels = [...CATEGORY_ORDER, OTHER_LABEL].filter((label) => buckets.has(label));
  const rebuiltBody = `\n${orderedLabels
    .map((label) => `### ${label}\n\n${buckets.get(label).join('\n\n')}\n`)
    .join('\n')}\n`;

  writeFileSync(changelogPath, changelog.slice(0, bodyStart) + rebuiltBody + changelog.slice(bodyEnd));
}

function replaceChartVersionAndChanges(version, changes) {
  let chart = readFileSync(chartPath, 'utf8');
  chart = chart.replace(/^version:\s*[^\n]+$/m, `version: ${version}`);

  const annotation = /^  artifacthub\.io\/changes:\s*\|\n(?:^(?: {4,}.*|\s*)\n)*/m;
  const block = [
    '  artifacthub.io/changes: |',
    ...changes.flatMap(({ kind, description }) => [
      `    - kind: ${JSON.stringify(kind)}`,
      `      description: ${JSON.stringify(description)}`,
    ]),
    '',
  ].join('\n');
  if (!annotation.test(chart)) throw new Error('Artifact Hub changes annotation not found');
  chart = chart.replace(annotation, block);
  writeFileSync(chartPath, chart);
}

mkdirSync(resolve(root, 'dist/release'), { recursive: true });
run('pnpm', ['exec', 'changeset', 'status', '--output', statusPath]);

const status = JSON.parse(readFileSync(statusPath, 'utf8'));
const release = status.releases.find(({ name }) => name === packageName);
if (!release) throw new Error(`No pending release for ${packageName}`);

const entries = status.changesets
  .map(({ id }) => readChangeset(id))
  .filter(Boolean);
if (!entries.length) throw new Error(`No pending Changeset entries for ${packageName}`);

run('pnpm', ['exec', 'changeset', 'version']);
const packageVersion = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8')).version;
if (packageVersion !== release.newVersion) {
  throw new Error(`Changesets planned ${release.newVersion}, but wrote ${packageVersion}`);
}

regroupChangelogByCategory(packageVersion);

replaceChartVersionAndChanges(
  packageVersion,
  entries.map(({ type, summary }) => ({
    kind: artifactHubKind(type),
    description: summary.length > 160 ? `${summary.slice(0, 157).trimEnd()}...` : summary,
  })),
);

run('helm-docs', ['--chart-search-root=charts', '--template-files=README.md.gotmpl', '--badge-style=flat']);

for (const path of [
  resolve(root, 'examples/helm/README.md'),
  resolve(root, 'charts/hermes-agent/README-ko.md'),
]) {
  const source = readFileSync(path, 'utf8');
  writeFileSync(path, source.replaceAll(release.oldVersion, packageVersion));
}

console.log(`Prepared Hermes Agent chart v${packageVersion} from ${entries.length} Changeset(s).`);
