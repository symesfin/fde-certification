"""Enforce the standalone-notebook rule.

`CLAUDE.md` states it: a notebook refers to itself and its own content, nothing
else. The test is mechanical — *would this sentence need editing if the course
were reordered, or if remedial content were inserted before this session?*

This replaces the `git grep` one-liner that used to be the gate. That version
matched line by line, and prose is hard-wrapped, so any forbidden phrase that
happened to straddle a line break was invisible. Three shipped violations were
found that way:

    "...re-run Week\n    1's challenge app..."          -> 'Week 1'
    "...has had since day\n    one, which existed..."   -> 'since day one'
    "| Week |\n| 3 - Retrieval |"                       -> a cross-week table

The first two are fixed by normalising whitespace before matching. The third is
not a phrase at all — it is a table whose header and cells are separately
innocent — so `_cross_week_table` looks for that shape directly.

Run: `python scripts/check_standalone.py [path ...]`
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

# Phrases that tie a notebook to a position in the course.
FORBIDDEN = [
    (re.compile(r"\b(?:Week|Weeks)\s+\d+", re.I), "names a course week"),
    # Spelled-out ordinals and cardinals slipped past the digit form above -- a
    # real violation shipped as "in week nine". Prose is where this rule gets
    # broken, and prose is exactly where people write numbers as words.
    # The lookbehind is load-bearing: without it this fires on the "week one"
    # inside "a twenty-minute step or a two-week one", which is not a course
    # week at all. A hyphenated compound is a different word.
    (
        re.compile(
            r"(?<![\w-])(?:Week|Weeks)\s+"
            r"(?:one|two|three|four|five|six|seven|eight|nine|ten|"
            r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b",
            re.I,
        ),
        "names a course week (spelled out)",
    ),
    (re.compile(r"\bTC\s?\d+\b"), "names a technical challenge by number"),
    # "Session N" used to be forbidden here. It is allowed now, deliberately:
    # the AIM notebook template titles every notebook `# Session N: <Title>`,
    # and a notebook naming its own position is not the failure this gate was
    # written for. The failure is a notebook narrating its *neighbours* -- "the
    # eval harness you built in Session 1" -- and that is still caught, by the
    # cross-week rules above and by the no-linking-siblings rule below. If a
    # reorder ever happens, 20 H1 titles need editing; 20 dangling references
    # would have needed finding first.
    (re.compile(r"\bthis\s+course\b", re.I), "says 'this course'"),
    (re.compile(r"\bsince\s+day\s+one\b", re.I), "temporal clause"),
    (re.compile(r"\ball\s+along\b", re.I), "temporal clause"),
    (re.compile(r"\bweeks\s+ago\b", re.I), "temporal clause"),
    (re.compile(r"\balready\s+(?:built|wrote)\b", re.I), "temporal clause"),
    (re.compile(r"\bwhen\s+you\s+scoped\b", re.I), "temporal clause"),
    # A path into another numbered week directory.
    (re.compile(r"/\d{2}_[A-Z][A-Za-z_]+/"), "path into another week directory"),
    # A markdown link to a sibling session notebook. A notebook that points at
    # another lesson stops being readable on its own, and the mirror inherits
    # the dangling reference -- the same reason week numbers are banned. Name
    # the topic instead of linking the file.
    (
        re.compile(r"\]\(\.?/?S\d+_[A-Za-z0-9_]+\.(?:py|ipynb)\)"),
        "links to a sibling session notebook",
    ),
    # A link back out to the week README. Same problem in the other direction:
    # the notebook becomes a fragment of a page rather than a whole document.
    (
        re.compile(r"\]\(\.\./README\.md(?:#[^)]*)?\)"),
        "links out to the week README",
    ),
]

# `00_Prerequisites/` is unnumbered setup that survives any reorder, and
# `CLAUDE.md` explicitly allows linking to it.
ALLOWED = re.compile(r"00_Prerequisites/")

# A markdown table with a bare "Week" header column: the header and the cells are
# each innocent, so phrase matching never sees it.
_TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")


def _cross_week_table(text: str) -> list[tuple[int, str]]:
    """Find tables whose first column is a week number in disguise."""
    out = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not _TABLE_ROW.match(line):
            continue
        first = line.strip().strip("|").split("|")[0].strip().strip("*").lower()
        if first not in {"week", "weeks"}:
            continue
        # Header found. Do the rows below it start with a bare number?
        numeric = 0
        for follow in lines[index + 1: index + 8]:
            if not _TABLE_ROW.match(follow):
                break
            cell = follow.strip().strip("|").split("|")[0].strip().strip("*")
            if re.match(r"^\d+\b", cell):
                numeric += 1
        if numeric >= 2:
            out.append((index + 1, f"table keyed by week number ({numeric} rows)"))
    return out


def check(path: Path) -> list[tuple[int, str, str]]:
    text = path.read_text(encoding="utf-8")

    # Map every offset in the whitespace-normalised text back to a line number,
    # so a phrase split across a hard wrap still reports where it lives.
    flat_chars, line_of = [], []
    line = 1
    prev_space = False
    for ch in text:
        if ch == "\n":
            line += 1
        if ch.isspace():
            if prev_space:
                continue
            flat_chars.append(" ")
            line_of.append(line)
            prev_space = True
        else:
            flat_chars.append(ch)
            line_of.append(line)
            prev_space = False
    flat = "".join(flat_chars)

    findings = []
    for pattern, why in FORBIDDEN:
        for match in pattern.finditer(flat):
            if ALLOWED.search(flat[max(0, match.start() - 40): match.end() + 40]):
                continue
            findings.append((line_of[match.start()], match.group(0).strip(), why))
    for lineno, why in _cross_week_table(text):
        findings.append((lineno, "| Week | ...", why))

    return sorted(findings)


def main(argv: list[str]) -> int:
    if argv:
        targets = [Path(arg) for arg in argv]
    else:
        targets = sorted(ROOT.glob("*/sessions/*.py"))

    total = 0
    for path in targets:
        findings = check(path)
        if not findings:
            continue
        total += len(findings)
        rel = path.relative_to(ROOT) if path.is_absolute() else path
        for lineno, snippet, why in findings:
            print(f"{rel}:{lineno}: {snippet!r} — {why}")

    if total:
        print(
            f"\n✗ {total} standalone-rule violation(s). A notebook refers to itself "
            f"and its own content, nothing else — name the thing, not the week."
        )
        return 1

    print(f"✓ {len(targets)} notebook(s) are standalone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
