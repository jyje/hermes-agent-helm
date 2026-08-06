"""MkDocs build hooks.

Fix up ``docs/reference/*.md``-style links when whole-file-including root or
chart markdown into the site. Those source files (README.md, CONTRIBUTING.md,
the chart README, ...) are also read directly on GitHub, where such links
must stay repo-root-relative to keep working across forks, tags, and local
checkouts. That is a different base than the site itself: docs_dir already
strips the ``docs/`` prefix, so the same literal path breaks once spliced
into a page. Rather than hardcoding those links to the live site's absolute
URL (which would silently point every fork's homepage back at the upstream
site), rewrite them to the correct site-relative path for the exact page
they land on, computed with ``posixpath.relpath`` so it holds for any nesting
depth.

This intentionally reimplements *only* whole-file inclusion for the specific
pages below, instead of running for every ``--8<--`` on the site: those are
plain pymdownx.snippets, untouched, including nested/code-fenced includes
this hook does not need to understand.
"""

import posixpath
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent

# page.file.src_uri -> repo-relative source file it whole-file-includes via
# a single `--8<-- "path"` line. Keep in sync with the snippet directives in
# docs/index.md, docs/ko/index.md, docs/reference/contributing.md,
# docs/reference/argocd.md, and docs/**/reference/chart-readme.md.
_INCLUDES = {
    "index.md": "README.md",
    "ko/index.md": "README-ko.md",
    "reference/contributing.md": "CONTRIBUTING.md",
    "reference/argocd.md": "examples/argocd/README.md",
    "reference/chart-readme.md": "charts/hermes-agent/README.md",
    "ko/reference/chart-readme.md": "charts/hermes-agent/README-ko.md",
}

_LINK_RE = re.compile(
    r'(\]\(|href=")(?:\.\./)*docs/((?:ko/)?reference/[\w-]+\.md)(#[\w%-]*)?([)"])'
)


def _fix_links(text: str, page_dir: str) -> str:
    def repl(match: re.Match) -> str:
        prefix, target, anchor, suffix = match.groups()
        rel = posixpath.relpath(target, start=page_dir) if page_dir else target
        # Emit the final clean (directory-style) URL ourselves instead of
        # relying on MkDocs's own .md-to-URL rewriter: that rewriter walks
        # the parsed element tree and never sees raw HTML `<a href="...">`
        # blocks (e.g. the `<div align="center" markdown="1">` image
        # captions), which pymdownx's md_in_html stashes as opaque HTML, so
        # those would otherwise keep a literal, unresolvable `.md` path.
        clean = rel[: -len(".md")] + "/" if rel.endswith(".md") else rel
        return f"{prefix}{clean}{anchor or ''}{suffix}"

    return _LINK_RE.sub(repl, text)


def on_page_markdown(markdown, page, config, files):
    source = _INCLUDES.get(page.file.src_uri)
    if source is None:
        return markdown

    directive = f'--8<-- "{source}"'
    if directive not in markdown:
        return markdown

    included = (REPO_ROOT / source).read_text(encoding="utf-8")
    page_dir = posixpath.dirname(page.file.src_uri)
    return markdown.replace(directive, _fix_links(included, page_dir))
