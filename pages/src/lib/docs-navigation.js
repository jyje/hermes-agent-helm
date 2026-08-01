import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const { load } = createRequire(import.meta.url)('js-yaml');
const manifest = load(readFileSync(resolve(process.cwd(), '../docs/navigation.yml'), 'utf8'));

export const normalizePath = (value, origin) => {
  const pathname = value.startsWith('/') ? value : new URL(value, origin).pathname;
  const normalized = pathname.replace(/\/+$/, '');
  return normalized || '/';
};

export const localeFromUrl = (url, basePath) => {
  const relativePath = url.pathname.slice(basePath.length).replace(/^\/+/, '');
  return relativePath === 'ko' || relativePath.startsWith('ko/') ? 'ko' : 'root';
};

export const navigationForLocale = (locale) => {
  const navigation = manifest?.locales?.[locale];
  if (!Array.isArray(navigation)) {
    throw new Error(`docs/navigation.yml does not define the ${locale} locale.`);
  }
  return navigation;
};

export const routeForPage = (page, locale, basePath) => {
  const withoutIndex = page === 'index' ? '' : page.replace(/\/index$/, '');
  const localePath = locale === 'root' ? '' : `${locale}/`;
  return normalizePath(`${basePath}/${localePath}${withoutIndex}`, 'http://localhost');
};

export const pageOrder = (nodes) => nodes.flatMap((node) => {
  if (typeof node === 'string') return [node];
  return [...(node.page ? [node.page] : []), ...pageOrder(node.children ?? [])];
});

export const linkMap = (entries, origin) => {
  const links = new Map();
  const collect = (items) => {
    for (const entry of items) {
      if (entry.type === 'link') links.set(normalizePath(entry.href, origin), entry);
      if (entry.type === 'group') collect(entry.entries);
    }
  };
  collect(entries);
  return links;
};
