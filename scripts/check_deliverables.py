#!/usr/bin/env python3
"""Every copy of a week's deliverables block must be byte-identical.

The block appears three times per week -- once at the top of the week README,
and at both the top and bottom of the challenge README -- because a student
reads those three places at different moments and each has to be complete on
its own. Three copies of the same text is a drift bug waiting to happen: the
one at the bottom of the challenge is the one nobody remembers to update, and
a student who reads it comes away with the wrong list.

This is the same argument mirrors.py makes about generated notebooks. Rather
than trusting people to keep copies in sync, compare them.

A week with no block is skipped, not failed -- conversion is per week.

    uv run python scripts/check_deliverables.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows consoles default to a code page that cannot encode the check marks
# these scripts print, so a redirected run dies with UnicodeEncodeError before
# reporting anything. Force UTF-8 on our own output rather than dropping to
# ASCII markers -- the students on managed Windows laptops are the ones running
# these gates.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
# The marker may carry a note after the keyword (`<!-- deliverables:start — this
# block is repeated verbatim in ... -->`) so a reader of the raw file learns what
# it is for. Only the keyword is matched; the note is free text.
BLOCK = re.compile(
    r"<!--\s*deliverables:start\b[^>]*-->\n(.*?)\n<!--\s*deliverables:end\b[^>]*-->",
    re.S,
)
# An unpaired marker is its own failure: it means someone deleted half a block,
# and the regex above would silently find nothing rather than complain.
START = re.compile(r"<!--\s*deliverables:start\b[^>]*-->")
END = re.compile(r"<!--\s*deliverables:end\b[^>]*-->")


def week_dirs() -> list[Path]:
    return sorted(path for path in ROOT.glob("[0-9][0-9]_*") if path.is_dir())


def blocks_in(path: Path) -> tuple[list[str], str | None]:
    """Return the blocks in a file, plus an error string if markers are unpaired."""
    if not path.exists():
        return [], None
    text = path.read_text(encoding="utf-8")
    n_start, n_end = len(START.findall(text)), len(END.findall(text))
    if n_start != n_end:
        return [], f"{n_start} start marker(s) but {n_end} end marker(s)"
    return [match.group(1) for match in BLOCK.finditer(text)], None


def main() -> int:
    failures: list[str] = []
    checked = 0

    for week in week_dirs():
        sources = [week / "README.md", week / "challenge" / "README.md"]
        found: list[tuple[Path, str]] = []

        for src in sources:
            blocks, err = blocks_in(src)
            if err:
                failures.append(f"{src.relative_to(ROOT)}: {err}")
                continue
            found.extend((src, block) for block in blocks)

        if not found:
            continue  # this week has not been converted yet

        checked += 1
        first_src, first = found[0]
        for src, block in found[1:]:
            if block != first:
                failures.append(
                    f"{src.relative_to(ROOT)}: deliverables block differs from "
                    f"{first_src.relative_to(ROOT)}"
                )

        # The block earns its keep by being in all three places.
        if len(found) != 3:
            where = ", ".join(str(src.relative_to(ROOT)) for src, _ in found)
            failures.append(
                f"{week.name}: found {len(found)} deliverables block(s), expected 3 "
                f"(week README once, challenge README twice) -- in {where}"
            )

        if not failures:
            print(f"✓ {week.name}  3 copies, identical")

    if failures:
        print()
        for failure in failures:
            print(f"✗ {failure}")
        print(f"\n✗ {len(failures)} deliverables problem(s).")
        return 1

    if checked == 0:
        print("no deliverables blocks found — nothing to check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
