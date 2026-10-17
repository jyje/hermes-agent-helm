/** Update current release references without rewriting historical prose. */
export function syncReleaseDoc(source, oldVersion, newVersion) {
  const old = oldVersion.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return source
    .replace(new RegExp(`!\\[Version: ${old}\\]\\(https://img\\.shields\\.io/badge/Version-${old}(-[^)\\n]*\\))`, 'g'),
      `![Version: ${newVersion}](https://img.shields.io/badge/Version-${newVersion}$1`)
    .replace(new RegExp(`(--version(?:[ \\t]+|=))${old}(?=[ \\t\\r\\n\\\\]|$)`, 'gm'), `$1${newVersion}`)
    .replace(new RegExp(`(dist/hermes-agent-)${old}(\\.tgz)`, 'g'), `$1${newVersion}$2`)
    .replace(new RegExp(`(ghcr\\.io/jyje/hermes-agent-helm/hermes-agent:)${old}(?=[\\s\x60]|$)`, 'gm'), `$1${newVersion}`);
}
