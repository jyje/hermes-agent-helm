"""MkDocs build hooks.

Fix up two kinds of link that stay correct on GitHub but break once
rendered on the site: whole-file-included root/chart markdown, and native
docs/**.md pages that link out to real repository files (chart values,
workflow YAML, CONTRIBUTING.md, ...) using paths that are also meant to be
read directly on GitHub. Those files must stay repo-relative to keep
working across forks, tags, and local checkouts; docs_dir strips the
``docs/`` prefix, and most such targets are not docs pages at all, so the
same literal relative path breaks once resolved on the site. Rather than
hardcoding an absolute link to the live site (which would silently point
every fork back at the upstream site) or leaving them broken, rewrite each
to whatever is actually correct for the page it lands on: a relative link
to the corresponding docs page where one exists, or an absolute GitHub URL
where it doesn't.

Also sets the footer's copyright line (on_config) to the current git
commit, license, and upstream-attribution facts, computed at build time
rather than hardcoded, since they'd otherwise drift out of sync with
whichever commit actually built the page.
"""

import posixpath
import re
import subprocess
from pathlib import Path

from markupsafe import Markup

REPO_ROOT = Path(__file__).parent
_GITHUB_BLOB = "https://github.com/jyje/hermes-agent-helm/blob/main/"
_GITHUB_TREE = "https://github.com/jyje/hermes-agent-helm/tree/main/"

# Repo-relative file -> the docs-site page (docs_dir-relative .md path) it
# corresponds to. Applies globally: these are facts about the repo, not
# about which page happens to link to them.
_SIBLING_PAGES = {
    "README.md": "index.md",
    "README-ko.md": "ko/index.md",
    "CONTRIBUTING.md": "reference/contributing.md",
    "SECURITY.md": "reference/security.md",
    "SECURITY-ko.md": "ko/reference/security.md",
    "charts/hermes-agent/README.md": "reference/chart-readme.md",
    "charts/hermes-agent/README-ko.md": "ko/reference/chart-readme.md",
}

# page.file.src_uri -> repo-relative source file it whole-file-includes via
# a single `--8<-- "path"` line. Keep in sync with the snippet directives
# in docs/index.md, docs/ko/index.md, docs/reference/contributing.md,
# docs/reference/argocd.md, docs/reference/security.md, and
# docs/**/reference/chart-readme.md.
_INCLUDES = {
    "index.md": "README.md",
    "ko/index.md": "README-ko.md",
    "reference/contributing.md": "CONTRIBUTING.md",
    "reference/argocd.md": "examples/argocd/README.md",
    "reference/security.md": "SECURITY.md",
    "ko/reference/security.md": "SECURITY-ko.md",
    "reference/chart-readme.md": "charts/hermes-agent/README.md",
    "ko/reference/chart-readme.md": "charts/hermes-agent/README-ko.md",
    "reference/helm-installation.md": "examples/helm/README.md",
}

# The dynamic docs/(ko/)?reference/*.md pattern (a link written relative to
# the repo root, targeting a page that *does* live under docs/), kept
# separate from the general repo-file resolution below because its repo
# path and its docs_dir-relative path differ only by the literal "docs/"
# prefix.
_DOCS_LINK_RE = re.compile(r'(?:\.\./)*docs/((?:ko/)?reference/[\w-]+\.md)')

# Stale "X-ko.md" sibling-file naming from the pre-MkDocs Astro/Starlight
# site, where locales were separate sibling files instead of today's
# parallel docs/ko/ tree. Only ever used for docs/reference/*.md pages.
_KO_SUFFIX_RE = re.compile(r'([\w-]+)-ko\.md')

# Any relative link: `[text](target)` (not an image `![...]`, though that
# distinction only matters for local, non-http image targets, and this repo
# has none) or a raw `href="target"`. Excludes bare-anchor same-page links
# and absolute URLs.
_LINK_RE = re.compile(r'(?<!!)(\]\(|href=")([^)"#][^)"#]*)((?:#[\w%-]*)?)([)"])')


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


def _resolve(target: str, anchor: str, page, source_dir: str) -> str | None:
    """Return the corrected URL for `target`, or None to leave it alone."""
    if target.startswith(("http://", "https://", "mailto:", "/")):
        return None  # already absolute (site-absolute or external): leave alone

    docs_match = _DOCS_LINK_RE.fullmatch(target)
    if docs_match:
        return _relative_url(docs_match.group(1), page) + anchor

    repo_path = posixpath.normpath(posixpath.join(source_dir, target))
    if target.endswith("/") and not repo_path.endswith("/"):
        repo_path += "/"

    # A real repo file this exact path resolves to (e.g. root README-ko.md,
    # or charts/hermes-agent/README-ko.md when source_dir put it there)
    # always wins over the generic "-ko.md" guess below, which exists only
    # for filenames that were never real files even in the pre-MkDocs site.
    # Both checks run before the docs/-tree guard: the repo path of a stale
    # "X-ko.md" reference or a genuinely known sibling file can themselves
    # land inside "docs/..." text (e.g. "docs/reference/roadmap-ko.md"),
    # which is not an in-tree page either and must not be left untouched.
    docs_page = _SIBLING_PAGES.get(repo_path)
    if docs_page:
        return _relative_url(docs_page, page) + anchor

    ko_match = _KO_SUFFIX_RE.fullmatch(target)
    if ko_match:
        return _relative_url(f"ko/reference/{ko_match.group(1)}.md", page) + anchor

    if repo_path == "docs" or repo_path.startswith("docs/"):
        return None  # inside the docs tree: a normal, already-working link

    base = _GITHUB_TREE if repo_path.endswith("/") else _GITHUB_BLOB
    return base + repo_path + anchor


def _fix_links(text: str, page, source_dir: str) -> str:
    def repl(match: re.Match) -> str:
        prefix, target, anchor, suffix = match.groups()
        resolved = _resolve(target, anchor, page, source_dir)
        if resolved is None:
            return match.group(0)
        return f"{prefix}{resolved}{suffix}"

    return _LINK_RE.sub(repl, text)


def on_page_markdown(markdown, page, config, files):
    source = _INCLUDES.get(page.file.src_uri)
    if source is not None:
        # Whole-file-include page: fix only the spliced-in content, using
        # the included source's own directory. The rest of the page's
        # already-native markdown (frontmatter, any text around the
        # directive) is left untouched rather than re-scanned, so an
        # already-corrected link can never be re-resolved a second time
        # against the wrong base and come out wrong.
        directive = f'--8<-- "{source}"'
        if directive not in markdown:
            return markdown
        included = (REPO_ROOT / source).read_text(encoding="utf-8")
        fixed = _fix_links(included, page, posixpath.dirname(source))
        return markdown.replace(directive, fixed)

    # Native docs/**.md page that links out to real repo files directly.
    # Only escaping (`../`-prefixed) or otherwise-repo-rooted targets are
    # ever touched; the `docs/`-tree guard in `_resolve` leaves ordinary
    # same-tree page links (the vast majority) alone.
    return _fix_links(markdown, page, posixpath.dirname("docs/" + page.file.src_uri))


def _git_head() -> tuple[str, str]:
    """(full sha, short sha) of the commit currently checked out, or
    ("unknown", "unknown") outside a git checkout (e.g. a source tarball)."""
    try:
        full = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        short = subprocess.run(
            ["git", "rev-parse", "--short=8", "HEAD"], cwd=REPO_ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        return full, short
    except Exception:
        return "unknown", "unknown"


def on_config(config):
    # The footer's copyright line, not the release version: this repo
    # deploys docs on every push to main, far more often than it cuts a
    # chart release, so "which commit is this page from" is the fact
    # worth surfacing here, not Chart.yaml's version.
    full_sha, short_sha = _git_head()
    commit_link = (
        f'<a href="https://github.com/jyje/hermes-agent-helm/commit/{full_sha}">{short_sha}</a>'
        if full_sha != "unknown"
        else "unknown commit"
    )
    config["copyright"] = Markup(
        '<a href="https://github.com/jyje/hermes-agent-helm">jyje/hermes-agent-helm</a> (MIT) &middot; '
        "unofficial, unaffiliated with Nous Research &middot; "
        'based on <a href="https://github.com/NousResearch/hermes-agent">Hermes Agent</a> (MIT) &middot; '
        f"{commit_link}"
    )
    return config
