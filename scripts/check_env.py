"""Is a week's package group installed in the root environment?

    uv run python scripts/check_env.py 3        # one week
    uv run python scripts/check_env.py          # every week group

Reads `[dependency-groups].weekN` from pyproject.toml, so the list can never
drift from what `uv sync --group weekN` installs. Distribution names are mapped
to import names through the installed metadata (`rank-bm25` -> `rank_bm25`,
`llama-index-core` -> `llama_index`), which is why this is a script and not a
one-liner you have to get right by hand.

Exit code 1 if anything is missing, with the command that fixes it.
"""

from __future__ import annotations

import importlib
import importlib.metadata as md
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def week_groups() -> dict[str, list[str]]:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    groups = data.get("dependency-groups", {})
    out: dict[str, list[str]] = {}
    for group, entries in groups.items():
        if not group.startswith("week"):
            continue
        names = []
        for raw in entries:
            match = REQ_NAME_RE.match(raw.split("#", 1)[0])
            if match:
                names.append(match.group(1))
        out[group] = names
    return out


def import_names(dist: str) -> list[str]:
    """Top-level modules a distribution provides, from the installed metadata."""
    wanted = normalise(dist)
    for module, dists in md.packages_distributions().items():
        if any(normalise(candidate) == wanted for candidate in dists):
            yield module


def check(group: str, dists: list[str]) -> list[str]:
    missing = []
    for dist in dists:
        try:
            md.version(dist)
        except md.PackageNotFoundError:
            missing.append(dist)
            continue
        modules = [name for name in import_names(dist) if not name.startswith("_")]
        if not modules:
            continue  # installed, but exposes no importable top-level module we can name
        try:
            importlib.import_module(modules[0])
        except Exception as error:  # an installed package that fails to import is also "missing"
            missing.append(f"{dist} ({type(error).__name__}: {str(error)[:80]})")
    return missing


def main(argv: list[str]) -> int:
    groups = week_groups()
    if not groups:
        print("no weekN groups in pyproject.toml")
        return 0
    selected = groups if not argv else {f"week{argv[0].removeprefix('week')}": None}
    bad = 0
    for group in selected:
        dists = groups.get(group)
        if dists is None:
            print(f"✗ {group}: no such group in pyproject.toml (have {', '.join(groups)})")
            return 2
        missing = check(group, dists)
        if missing:
            bad += 1
            print(f"✗ {group}: {len(dists) - len(missing)}/{len(dists)} installed; missing {', '.join(missing)}")
            print(f"  fix:  uv sync --inexact --group {group}     (or: make setup-week W={group.removeprefix('week')})")
        else:
            print(f"✓ {group}: {len(dists)}/{len(dists)} installed and importable")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
