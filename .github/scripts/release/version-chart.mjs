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

const root = resolve(import.meta.dirname, '../../..');
const packageName = '@jyje/hermes-agent-helm';
const chartPath = resolve(root, 'charts/hermes-agent/Chart.yaml');
const statusPath = resolve(root, 'dist/release/changeset-status.json');

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
  .filter(Boolean)
  .slice(0, 3);
if (!entries.length) throw new Error(`No pending Changeset entries for ${packageName}`);

run('pnpm', ['exec', 'changeset', 'version']);
const packageVersion = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8')).version;
if (packageVersion !== release.newVersion) {
  throw new Error(`Changesets planned ${release.newVersion}, but wrote ${packageVersion}`);
}

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
