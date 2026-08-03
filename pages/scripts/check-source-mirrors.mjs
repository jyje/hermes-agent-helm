// Some docs/reference pages hand-mirror a root-level file (README.md,
// CONTRIBUTING.md, ...) that lives outside docs/ so it renders with
// Starlight frontmatter and the "Open raw Markdown" / "Copy source" button.
// That mirror body is a plain copy, not build-time-injected, so it silently
// drifts whenever the source file changes without the mirror being updated
// in the same commit.
//
// Default: fails loudly when that happens (wired into deploy-docs.yaml CI).
// --write: rewrites every mirror's body from its current source instead —
// used by the release version-sync step so a version bump can never leave a
// mirror stale on its own.
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const pagesDirectory = fileURLToPath(new URL('..', import.meta.url));
const repoRoot = resolve(pagesDirectory, '..');
const write = process.argv.includes('--write');

// mirror (relative to repo root) -> source it must match (relative to repo root)
const MIRRORS = {
  'docs/reference/repository-readme.md': 'README.md',
  'docs/ko/reference/repository-readme.md': 'README-ko.md',
  'docs/reference/chart-readme.md': 'charts/hermes-agent/README.md',
  'docs/ko/reference/chart-readme.md': 'charts/hermes-agent/README-ko.md',
  'docs/reference/contributing.md': 'CONTRIBUTING.md',
  'docs/reference/security.md': 'SECURITY.md',
  'docs/ko/reference/security.md': 'SECURITY-ko.md',
  'docs/reference/argocd.md': 'examples/argocd/README.md',
  'docs/reference/helm-installation.md': 'examples/helm/README.md',
};

// Splits a mirror file into its header (frontmatter + raw-document-actions
// div, kept as-is) and its body (the copied source content).
function splitMirror(raw) {
  const frontmatterMatch = raw.match(/^---\n[\s\S]*?\n---\n/);
  if (!frontmatterMatch) throw new Error('missing YAML frontmatter');
  const afterFrontmatter = raw.slice(frontmatterMatch[0].length);

  const divMatch = afterFrontmatter.match(/^\n*<div class="raw-document-actions"[\s\S]*?<\/div>\n\n?/);
  if (!divMatch) throw new Error('missing <div class="raw-document-actions"> block');

  const header = frontmatterMatch[0] + divMatch[0];
  const body = afterFrontmatter.slice(divMatch[0].length).replace(/^\n+/, '').replace(/\n+$/, '');
  return { header, body };
}

const errors = [];

for (const [mirror, source] of Object.entries(MIRRORS)) {
  const mirrorPath = resolve(repoRoot, mirror);
  const sourcePath = resolve(repoRoot, source);
  const { header, body: mirrorBody } = splitMirror(readFileSync(mirrorPath, 'utf8'));
  const sourceContent = readFileSync(sourcePath, 'utf8').replace(/\n+$/, '');

  if (mirrorBody === sourceContent) continue;

  if (write) {
    writeFileSync(mirrorPath, `${header}${sourceContent}\n`);
    console.log(`Synced ${mirror} from ${source}.`);
  } else {
    errors.push(`${mirror} is out of sync with ${source} — copy the current body over (or run with --write).`);
  }
}

if (!write && errors.length > 0) {
  console.error(errors.map((error) => `- ${error}`).join('\n'));
  process.exitCode = 1;
} else if (!write) {
  console.log(`Validated ${Object.keys(MIRRORS).length} source-mirror pages against their root files.`);
}
