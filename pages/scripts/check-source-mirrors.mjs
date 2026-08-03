// Some docs/reference pages hand-mirror a root-level file (README.md,
// CONTRIBUTING.md, ...) that lives outside docs/ so it renders with
// Starlight frontmatter and the "Open raw Markdown" / "Copy source" button.
// That mirror body is a plain copy, not build-time-injected, so it silently
// drifts whenever the source file changes without the mirror being updated
// in the same commit. This script fails loudly when that happens.
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const pagesDirectory = fileURLToPath(new URL('..', import.meta.url));
const repoRoot = resolve(pagesDirectory, '..');

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

const mirrorBody = (raw) => {
  const withoutFrontmatter = raw.replace(/^---\n[\s\S]*?\n---\n/, '');
  const withoutRawActions = withoutFrontmatter.replace(
    /<div class="raw-document-actions"[\s\S]*?<\/div>\n\n?/,
    '',
  );
  return withoutRawActions.replace(/^\n+/, '').replace(/\n+$/, '');
};

const errors = [];

for (const [mirror, source] of Object.entries(MIRRORS)) {
  const mirrorPath = resolve(repoRoot, mirror);
  const sourcePath = resolve(repoRoot, source);
  const mirrorContent = mirrorBody(readFileSync(mirrorPath, 'utf8'));
  const sourceContent = readFileSync(sourcePath, 'utf8').replace(/\n+$/, '');
  if (mirrorContent !== sourceContent) {
    errors.push(`${mirror} is out of sync with ${source} — copy the current body over.`);
  }
}

if (errors.length > 0) {
  console.error(errors.map((error) => `- ${error}`).join('\n'));
  process.exitCode = 1;
} else {
  console.log(`Validated ${Object.keys(MIRRORS).length} source-mirror pages against their root files.`);
}
