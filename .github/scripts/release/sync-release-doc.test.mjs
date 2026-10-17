import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { syncReleaseDoc } from './sync-release-doc.mjs';

const root = new URL('../../../', import.meta.url);
const current = JSON.parse(readFileSync(new URL('package.json', root), 'utf8')).version;
const next = '99.123.456';

for (const locale of ['ko', 'ja', 'zh']) {
  test(`${locale}: current pins change but complete upgrade history and provenance survive`, () => {
    const source = readFileSync(new URL(`charts/hermes-agent/README-${locale}.md`, root), 'utf8');
    const result = syncReleaseDoc(source, current, next);
    assert.notEqual(result, source);
    assert.ok(result.includes(`![Version: ${next}](https://img.shields.io/badge/Version-${next}-`));
    assert.ok(result.includes(`--version ${next}`));
    assert.equal(result.split('\n')[0], source.split('\n')[0]);
    // Every other line, including translated history, must remain byte-identical.
    const prose = text => text.split('\n').filter(line => !line.includes('![Version: ')
      && !line.includes('--version ')).join('\n');
    assert.equal(prose(result), prose(source));
    assert.ok(result.includes('1.20.0'), 'historical Hermes v0.22 chart version remains');
    assert.equal(syncReleaseDoc(result, current, next), result, 'idempotent');
  });
}

test('explicit 1.20.0 to 1.21.0 bump only changes current artifact references', () => {
  const source = `![Version: 1.20.0](https://img.shields.io/badge/Version-1.20.0-informational?style=flat)
helm install example --version 1.20.0
helm install example --version=1.20.0
dist/hermes-agent-1.20.0.tgz
ghcr.io/jyje/hermes-agent-helm/hermes-agent:1.20.0
### Hermes v0.22 (chart 1.20.0)
Chart 1.20.0 changed the default image.
image: 1.20.0
helm install unrelated --version 1.20.0-other
helm install unrelated --version 11.20.0
`;
  const result = syncReleaseDoc(source, '1.20.0', '1.21.0');
  assert.equal(result, source.replace(/1\.20\.0/g, (match, offset) =>
    offset < source.indexOf('### Hermes') ? '1.21.0' : match));
});

test('installation and package examples use the current release', () => {
  const source = readFileSync(new URL('examples/helm/README.md', root), 'utf8');
  assert.equal(syncReleaseDoc(source, current, next), source.replaceAll(current, next));
});
