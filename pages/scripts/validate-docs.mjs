import { readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as yaml from 'js-yaml';

const pagesDirectory = fileURLToPath(new URL('..', import.meta.url));
const docsDirectory = resolve(pagesDirectory, '../docs');
const manifest = yaml.load(readFileSync(resolve(docsDirectory, 'navigation.yml'), 'utf8'));

const walkPages = (directory, prefix = '') => readdirSync(directory, { withFileTypes: true })
  .flatMap((entry) => {
    if (entry.name.startsWith('.') || entry.name.startsWith('_')) return [];
    const relativePath = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) return walkPages(resolve(directory, entry.name), relativePath);
    return /\.(?:md|mdx)$/.test(entry.name) ? [relativePath] : [];
  });

const manifestPages = (nodes) => nodes.flatMap((node) => {
  if (typeof node === 'string') return [node];
  return [...(node.page ? [node.page] : []), ...manifestPages(node.children ?? [])];
});

const pageIdFromFile = (file, locale) => {
  const localePrefix = locale === 'root' ? '' : `${locale}/`;
  return file
    .slice(localePrefix.length)
    .replace(/\.(?:md|mdx)$/, '');
};

const errors = [];
const allFiles = walkPages(docsDirectory);

for (const file of allFiles) {
  const source = readFileSync(resolve(docsDirectory, file), 'utf8');
  const frontmatterMatch = source.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  const frontmatter = frontmatterMatch ? yaml.load(frontmatterMatch[1]) : undefined;
  if (!frontmatter || typeof frontmatter.title !== 'string' || frontmatter.title.trim() === '') {
    errors.push(`${file}: missing a title in YAML frontmatter`);
  }
}

for (const [locale, navigation] of Object.entries(manifest?.locales ?? {})) {
  if (!Array.isArray(navigation)) {
    errors.push(`navigation.yml: locale ${locale} must be an array`);
    continue;
  }

  const pages = manifestPages(navigation);
  const duplicates = pages.filter((page, index) => pages.indexOf(page) !== index);
  for (const page of new Set(duplicates)) {
    errors.push(`navigation.yml: ${locale}/${page} is listed more than once`);
  }

  const localePrefix = locale === 'root' ? '' : `${locale}/`;
  const localeFiles = allFiles.filter((file) => locale === 'root'
    ? !file.startsWith('ko/')
    : file.startsWith(localePrefix));
  const filePages = new Set(localeFiles.map((file) => pageIdFromFile(file, locale)));

  for (const page of pages) {
    if (!filePages.has(page)) errors.push(`navigation.yml: missing page ${locale}/${page}`);
  }
  for (const page of filePages) {
    if (!pages.includes(page)) errors.push(`navigation.yml: unlisted page ${locale}/${page}`);
  }
}

if (errors.length > 0) {
  console.error(errors.map((error) => `- ${error}`).join('\n'));
  process.exitCode = 1;
} else {
  console.log(`Validated ${allFiles.length} documentation pages against docs/navigation.yml.`);
}
