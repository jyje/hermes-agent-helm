#!/usr/bin/env python3
"""Decide whether a PR needs external model/messenger checks.

The broader functional matrix remains independent. Documentation and release
tooling can still install the chart without depending on free-tier model uptime.
"""
import argparse
import re
import subprocess


def requires_live_chat(paths: list[str], app_version_changed: bool) -> bool:
    if app_version_changed:
        return True
    for path in paths:
        if path.startswith("charts/hermes-agent/"):
            name = path.removeprefix("charts/hermes-agent/")
            if name == "Chart.yaml" or re.fullmatch(r"README(?:-[a-z]+)?\.md(?:\.gotmpl)?", name):
                continue
            return True
        if path in {
            ".github/scripts/lib.sh",
            ".github/scripts/test-chart.sh",
            ".github/workflows/validate-chart.yaml",
            ".github/workflows/verify-release.yaml",
        } or (path.startswith(".github/scripts/scenario-") and path.endswith(".sh")):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()
    # Missing history must keep live coverage rather than silently skip it.
    known = subprocess.run(["git", "cat-file", "-e", args.base], capture_output=True)
    if known.returncode != 0:
        print("live_chat=true")
        return
    paths = subprocess.check_output(
        ["git", "diff", "--name-only", args.base, args.head], text=True
    ).splitlines()
    chart_diff = subprocess.check_output(
        ["git", "diff", "--unified=0", args.base, args.head, "--", "charts/hermes-agent/Chart.yaml"],
        text=True,
    )
    app_changed = bool(re.search(r"^\+appVersion:", chart_diff, re.MULTILINE))
    print(f"live_chat={str(requires_live_chat(paths, app_changed)).lower()}")


if __name__ == "__main__":
    main()
