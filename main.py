"""mkdocs-macros-plugin hooks for this docs site.

Prototype for replacing the Astro ValuesOverlayList.astro component: a
values_overlays() macro that discovers charts/<chart>/values-*.yaml by
pattern at build time, so adding/removing an overlay file needs no matching
documentation page.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).parent


def define_env(env):
    @env.macro
    def values_overlays(chart: str) -> str:
        chart_dir = REPO_ROOT / "charts" / chart
        overlay_paths = sorted(chart_dir.glob("values-*.yaml"))

        sections = []
        for path in overlay_paths:
            source = path.read_text(encoding="utf-8")
            rel_path = f"charts/{chart}/{path.name}"
            sections.append(
                f'## {path.name}\n\n'
                f'[Open raw YAML](https://github.com/jyje/hermes-agent-helm/blob/main/{rel_path})\n\n'
                f'```yaml title="{rel_path}"\n{source}\n```\n'
            )
        return "\n".join(sections)
