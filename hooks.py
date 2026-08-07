"""MkDocs build hooks.

Fix up links when whole-file-including root or chart markdown into the
site. Those source files (README.md, CONTRIBUTING.md, the chart README,
...) are also read directly on GitHub, where every relative link in them is
repo-root-relative by convention, and must stay that way to keep working
across forks, tags, and local checkouts. That is a different base than the
site itself: docs_dir strips the ``docs/`` prefix, and most targets (a
sibling values-*.yaml, LICENSE, .github/workflows/, CONTRIBUTING.md itself,
...) are not docs pages at all, so the same literal relative path breaks
once spliced into a page. Rather than hardcoding those links to the live
site's absolute URL (which would silently point every fork's homepage back
at the upstream site) or leaving them broken, rewrite each to whatever is
actually correct for the page it lands on: a relative link to the
corresponding docs page where one exists, or an absolute GitHub URL where
it doesn't.

This intentionally reimplements *only* whole-file inclusion for the
specific pages below, instead of running for every ``--8<--`` on the site:
those are plain pymdownx.snippets, untouched, including nested/code-fenced
includes this hook does not need to understand.
"""

import posixpath
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent
_GITHUB_BLOB = "https://github.com/jyje/hermes-agent-helm/blob/main/"
_GITHUB_TREE = "https://github.com/jyje/hermes-agent-helm/tree/main/"

# page.file.src_uri -> (repo-relative source file it whole-file-includes,
# {repo-relative link target -> docs-site page this corresponds to, as a
#  docs_dir-relative .md path}). Everything else that source file links to
# relatively falls back to an absolute GitHub blob/tree URL. Keep in sync
# with the snippet directives in docs/index.md, docs/ko/index.md,
# docs/reference/contributing.md, docs/reference/argocd.md, and
# docs/**/reference/chart-readme.md.
_INCLUDES = {
    "index.md": (
        "README.md",
        {
            "README.md": "index.md",
            "README-ko.md": "ko/index.md",
            "CONTRIBUTING.md": "reference/contributing.md",
            "SECURITY.md": "reference/security.md",
            "charts/hermes-agent/README.md": "reference/chart-readme.md",
        },
    ),
    "ko/index.md": (
        "README-ko.md",
        {
            "README.md": "index.md",
            "README-ko.md": "ko/index.md",
            "CONTRIBUTING.md": "reference/contributing.md",
            "SECURITY-ko.md": "ko/reference/security.md",
            "charts/hermes-agent/README-ko.md": "ko/reference/chart-readme.md",
        },
    ),
    "reference/contributing.md": ("CONTRIBUTING.md", {}),
    "reference/argocd.md": ("examples/argocd/README.md", {}),
    "reference/chart-readme.md": (
        "charts/hermes-agent/README.md",
        {
            "README.md": "reference/chart-readme.md",
            "README-ko.md": "ko/reference/chart-readme.md",
        },
    ),
    "ko/reference/chart-readme.md": (
        "charts/hermes-agent/README-ko.md",
        {
            "README.md": "reference/chart-readme.md",
            "README-ko.md": "ko/reference/chart-readme.md",
        },
    ),
}

# The dynamic docs/(ko/)?reference/*.md pattern (a link written relative to
# the repo root, targeting a page that *does* live under docs/), separate
# from the general repo-file resolution below because its repo path and its
# docs_dir-relative path differ only by the literal "docs/" prefix.
_DOCS_LINK_RE = re.compile(r'(?:\.\./)*docs/((?:ko/)?reference/[\w-]+\.md)')

# Any other relative link: `[text](target)` (not an image `![...]`) or a raw
# `href="target"`. Excludes bare-anchor same-page links and absolute URLs.
_LINK_RE = re.compile(r'(?<!!)(\]\(|href=")([^)"#][^)"]*)((?:#[\w%-]*)?)([)"])')


def _page_clean_path(docs_md_path: str) -> str:
    """docs_dir-relative .md path -> the site's directory-style form, e.g.
    "reference/teams.md" -> "reference/teams", "ko/index.md" -> "ko",
    "index.md" -> "." (site root)."""
    clean = docs_md_path[:-3] if docs_md_path.endswith(".md") else docs_md_path
    if clean == "index":
        return "."
    if clean.endswith("/index"):
        return clean[: -len("/index")]
    return clean


def _relative_url(target_docs_md_path: str, current_page) -> str:
    target_clean = _page_clean_path(target_docs_md_path)
    current_dir = current_page.url.rstrip("/") or "."
    rel = posixpath.relpath(target_clean, start=current_dir)
    return "./" if rel == "." else rel + "/"


def _fix_links(text: str, page, source: str, sibling_pages: dict) -> str:
    source_dir = posixpath.dirname(source)

    def repl(match: re.Match) -> str:
        prefix, target, anchor, suffix = match.groups()

        if target.startswith(("http://", "https://", "mailto:")):
            return match.group(0)

        docs_match = _DOCS_LINK_RE.fullmatch(target)
        if docs_match:
            return f"{prefix}{_relative_url(docs_match.group(1), page)}{anchor}{suffix}"

        repo_path = posixpath.normpath(posixpath.join(source_dir, target))
        if target.endswith("/") and not repo_path.endswith("/"):
            repo_path += "/"

        docs_page = sibling_pages.get(repo_path)
        if docs_page:
            return f"{prefix}{_relative_url(docs_page, page)}{anchor}{suffix}"

        base = _GITHUB_TREE if repo_path.endswith("/") else _GITHUB_BLOB
        return f"{prefix}{base}{repo_path}{anchor}{suffix}"

    return _LINK_RE.sub(repl, text)


def on_page_markdown(markdown, page, config, files):
    entry = _INCLUDES.get(page.file.src_uri)
    if entry is None:
        return markdown
    source, sibling_pages = entry

    directive = f'--8<-- "{source}"'
    if directive not in markdown:
        return markdown

    included = (REPO_ROOT / source).read_text(encoding="utf-8")
    return markdown.replace(directive, _fix_links(included, page, source, sibling_pages))
