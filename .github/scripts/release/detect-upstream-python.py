#!/usr/bin/env python3
"""Read Hermes' managed Python major/minor from its tagged pm/lock.json.

Used by cron-fetch-image.yaml. Dockerfile prose and unrelated package versions
are deliberately not runtime-version sources.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys


def python_minor(lock: object) -> str:
    try:
        version = lock["packages"]["python"]["version"]
    except (KeyError, TypeError) as exc:
        raise ValueError("pm/lock.json has no packages.python.version") from exc
    if not isinstance(version, str):
        raise ValueError("packages.python.version must be a string")
    match = re.fullmatch(r"(\d+)\.(\d+)\.\d+(?:\+[A-Za-z0-9.-]+)?", version)
    if match is None:
        raise ValueError("packages.python.version is not a supported Python release pin")
    return f"{match[1]}.{match[2]}"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: detect-upstream-python.py <pm-lock.json>", file=sys.stderr)
        return 2
    try:
        lock = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        result = python_minor(lock)
    except (OSError, ValueError) as exc:
        print(f"Cannot detect upstream Python: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
