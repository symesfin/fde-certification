"""Assert that opening a notebook changes nothing on disk.

Every other gate here measures a file at rest. This one measures what the file
*becomes* the moment a student touches it, which is a different question and,
until this script existed, an unasked one.

marimo does not read a `.py` and hand it back. It parses the file into an
internal representation and re-emits it from its own serializer, so a notebook
whose committed bytes are not already in marimo's canonical form is rewritten
the instant anyone opens it. The student then has a dirty working tree they did
not create, and — worse — any hand-edit marimo disagrees with is silently
reverted. Both happened in `01_Product_Engineering` and cost a day of native
testing to find, one notebook at a time, by opening each one and watching git.

That round-trip is reproducible offline in about a second, because the two
halves are importable: `deserialize` is the same loader the editor uses, and
`generate_filecontents_from_ir` is the same serializer it saves with. Load,
regenerate, compare bytes. A notebook that survives this is one that opening
cannot change.

**Two failure classes, and the difference decides how you fix it.** Most are
cosmetic — a cell signature marimo would wrap, an unused reference it prunes
from the export tuple, markdown it would re-indent — and `--fix` is the right
answer. A few change what the notebook *means*:

    ""  inside an r-string markdown cell  ->  "\\"      (corrupt Python, shown
                                                        to students as an example)
    a multi-line string literal whose contents sit at a lower indentation than
    the cell body gets indented along with the cell, changing the string's value

`--fix` would bake those in. Both classes look identical in a byte comparison,
so read the diff before running it — `--fix` is a formatter, not a repair.

Run: `python scripts/check_roundtrip.py [--fix] [path ...]`
"""

from __future__ import annotations

import difflib
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

# Same definition mirrors.py uses. A .py under sessions/ that does not build an
# App is a plain module living next to the notebooks -- an MCP server, a helper
# script -- and round-tripping it through the notebook serializer would wrap it
# in marimo boilerplate it never asked for.
NOTEBOOK_GLOB = "*/sessions/*.py"
MARIMO_MARKER = "app = marimo.App("


def notebooks() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.glob(NOTEBOOK_GLOB))
        if MARIMO_MARKER in path.read_text(encoding="utf-8")
    ]


def reopened(path: Path, source: str) -> str:
    """The bytes marimo would leave on disk after loading and saving `path`."""
    # Imported here, not at module scope: this file is a gate, and a gate that
    # cannot start because marimo is missing should say so at the call site.
    from marimo._ast.codegen import generate_filecontents_from_ir
    from marimo._ast.load import get_notebook_serializer

    return generate_filecontents_from_ir(
        get_notebook_serializer(path).deserialize(source)
    )


def main(argv: list[str]) -> int:
    fix = "--fix" in argv
    args = [arg for arg in argv if not arg.startswith("-")]

    if args:
        targets = []
        for arg in args:
            arg_path = Path(arg)
            resolved = arg_path if arg_path.is_absolute() else ROOT / arg_path
            if resolved.is_dir():
                targets += [
                    path
                    for path in sorted(resolved.rglob("*.py"))
                    if MARIMO_MARKER in path.read_text(encoding="utf-8")
                ]
            else:
                targets.append(resolved)
    else:
        targets = notebooks()

    drifted = []
    for path in targets:
        source = path.read_text(encoding="utf-8")
        try:
            canonical = reopened(path, source)
        except Exception as exc:
            print(f"✗ {path.relative_to(ROOT)}: cannot load — {type(exc).__name__}: {exc}")
            return 1
        if canonical == source:
            continue
        if fix:
            path.write_text(canonical, encoding="utf-8", newline="")
            drifted.append((path, None))
            continue
        diff = list(
            difflib.unified_diff(
                source.splitlines(keepends=True),
                canonical.splitlines(keepends=True),
                fromfile=f"{path.relative_to(ROOT)} (committed)",
                tofile=f"{path.relative_to(ROOT)} (after opening)",
                n=1,
            )
        )
        drifted.append((path, diff))

    if fix:
        for path, _ in drifted:
            print(f"✎ {path.relative_to(ROOT)}")
        print(
            f"\n✓ rewrote {len(drifted)} notebook(s) into marimo's canonical form. "
            f"Read the diff: --fix bakes in a corrupting rewrite as readily as a "
            f"cosmetic one, and regenerate the mirrors before committing."
        )
        return 0

    if drifted:
        for path, diff in drifted:
            changed = sum(
                1
                for line in diff
                if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
            )
            print(f"\n{'─' * 72}\n{path.relative_to(ROOT)}  ({changed} changed lines)")
            print("".join(diff[:60]).rstrip())
            if len(diff) > 60:
                print(f"  … {len(diff) - 60} more diff lines")
        print(
            f"\n✗ {len(drifted)} notebook(s) are rewritten when opened. A student who "
            f"opens one gets a dirty working tree they did not create, and anything "
            f"marimo disagrees with is reverted without a word.\n"
            f"  Read each diff first. Cosmetic drift: `--fix`. A changed string "
            f"literal or a mangled quote is a corruption — fix the source instead.\n"
            f"  Then `make mirrors`, because the .ipynb is generated from these bytes."
        )
        return 1

    print(f"✓ {len(targets)} notebook(s) are unchanged by opening them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
