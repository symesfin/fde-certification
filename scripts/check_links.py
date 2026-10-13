#!/usr/bin/env python3
"""Verify every relative link in the repo's markdown actually points at something.

Cheap insurance against the thing that always breaks when directories move: a
README quietly pointing at a path that no longer exists. Students hit those, we
don't, because we already know where everything is.

External links (http/https/mailto) and in-page anchors are not checked.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Windows consoles default to a code page that cannot encode the check marks
# these scripts print, so a redirected run dies with UnicodeEncodeError before
# reporting anything. Force UTF-8 on our own output rather than dropping to
# ASCII markers -- the students on managed Windows laptops are the ones running
# these gates.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".ruff_cache", "assets"}

# [text](target) in markdown, plus src="..."/href="..." for the HTML blocks the
# READMEs use for images and layout.
MD_LINK = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?\s*(?:\"[^\"]*\")?\)")
HTML_ATTR = re.compile(r'(?:src|href)\s*=\s*"([^"]+)"')


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#", "data:", "//"))


def gitignored() -> set[Path]:
    """Every ignored path under ROOT, so a scratch folder of downloaded copies
    (`Claude outputs/`, say) does not fail the gate for links that resolve only
    from where the copy came from. Falls back to nothing if git is unavailable
    -- a snapshot without `.git` is then checked in full, which is the safe
    direction."""
    import subprocess

    try:
        out = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {(ROOT / line.rstrip("/")).resolve() for line in out.splitlines() if line.strip()}


def markdown_files() -> list[Path]:
    ignored = gitignored()
    return [
        path
        for path in sorted(ROOT.rglob("*.md"))
        if not any(part in SKIP_DIRS for part in path.parts)
        and not any(parent in ignored for parent in (path.resolve(), *path.resolve().parents))
    ]


def main() -> int:
    broken: list[tuple[Path, int, str]] = []
    checked = 0

    for md in markdown_files():
        try:
            lines = md.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for lineno, line in enumerate(lines, 1):
            for match in (*MD_LINK.finditer(line), *HTML_ATTR.finditer(line)):
                target = match.group(1).strip()
                if is_external(target) or not target:
                    continue
                # Drop any in-page anchor: ../foo/README.md#section
                path_part = unquote(target.split("#", 1)[0])
                if not path_part:
                    continue
                checked += 1
                if not (md.parent / path_part).resolve().exists():
                    broken.append((md, lineno, target))

    for md, lineno, target in broken:
        print(
            f"✗ {md.relative_to(ROOT)}:{lineno} -> {target}  (does not exist)",
            file=sys.stderr,
        )

    if broken:
        print(f"\n{len(broken)} broken link(s) of {checked} checked", file=sys.stderr)
        return 1

    print(f"✓ {checked} relative links OK across {len(markdown_files())} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
