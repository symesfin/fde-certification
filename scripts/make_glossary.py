"""Regenerate GLOSSARY.md from every week README's `### Terms you'll meet` table.

The glossary is a view, not a source. Each week README owns its own terms table
(the conversion spec puts it under `## 📊 What the notebooks measure`); this
script collects those rows, sorts them, and writes the root `GLOSSARY.md`. Add
or fix a term in the week README, then run:

    uv run python scripts/make_glossary.py          # rewrite GLOSSARY.md
    uv run python scripts/make_glossary.py --check  # exit 1 if it is stale (CI)

Weeks whose README has no terms table yet are skipped and listed, so a missing
week is visible rather than silently absent.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "GLOSSARY.md"
OK, BAD = "✓", "✗"

HEADER = """# Glossary

Every term the course leans on, in one place, alphabetically — with the week
where it first bites. Each line is the same one-sentence version that appears
in that week's README under *Terms you'll meet*; this file just collects them,
so you can look something up without remembering which week introduced it.

None of these needs to be known in advance. If a session uses a word before
this file defines it, that is a bug in the course — say so in the notebook
feedback form.

| Term | The one-sentence version | Where it bites |
| --- | --- | --- |
"""

FOOTER = """
---

*Maintainers: this file is generated from the `### Terms you'll meet` table in
each week's README — add a term there, then run
`uv run python scripts/make_glossary.py`. Do not edit the table above by hand;
`--check` in CI will fail if it drifts. Weeks without a terms table yet: {missing}.*
"""

TABLE = re.compile(r"### Terms you.ll meet.*?\n(\|.*?)(?:\n\n|\n---|\Z)", re.S)


def collect() -> tuple[list[tuple[str, str, str, int]], list[int]]:
    rows, missing = [], []
    for readme in sorted(ROOT.glob("[0-9][0-9]_*/README.md")):
        week = int(readme.parent.name[:2])
        if week == 0:
            continue
        match = TABLE.search(readme.read_text(encoding="utf-8"))
        if not match:
            missing.append(week)
            continue
        for line in match.group(1).splitlines()[2:]:  # skip header + rule
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 3:
                term = re.sub(r"\*\*", "", cells[0]).strip()
                rows.append((term, cells[1], cells[2], week))
    rows.sort(key=lambda row: (row[0].lower().lstrip("`"), row[3]))
    return rows, missing


def render() -> str:
    rows, missing = collect()
    body = "\n".join(f"| **{term}** | {definition} | Week {week}: {where} |" for term, definition, where, week in rows)
    miss = ", ".join(str(week) for week in missing) or "none"
    return HEADER + body + "\n" + FOOTER.format(missing=miss)


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current == text:
            print(f"{OK} GLOSSARY.md is current")
            return 0
        print(f"{BAD} GLOSSARY.md is stale — run: uv run python scripts/make_glossary.py")
        return 1
    OUT.write_text(text, encoding="utf-8")
    rows, missing = collect()
    print(f"{OK} wrote GLOSSARY.md: {len(rows)} terms; weeks without a table: {missing or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
