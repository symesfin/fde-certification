#!/usr/bin/env python3
"""Stamp a new session notebook with the canonical skeleton.

Every session notebook has the same shape — the PEP 723 header, the bootstrap cell,
the Build/Ship/Share block, the task rhythm. Getting that wrong once means fixing it
in twenty files later, so it comes out of one template.

    python scripts/new_session.py 03_Retrieval S1 "Retrieval Variants"

Writes `03_Retrieval/sessions/S1_Retrieval_Variants.py`, then tell you to run
`make mirrors`.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = '''# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo=={pin}",
#     "python-dotenv>=1.2",
# ]
# ///

import marimo

__generated_with = "{pin}"
app = marimo.App(width="medium", app_title="{title}")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # {title}

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - Task 1: TODO
    - ❓ Question #1
    - Conclusion
    - Additional Context
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    The tools this notebook actually uses, and what each is used for *here*.
    Open every URL by hand before shipping.

    | Tool | Used here for | Docs |
    | --- | --- | --- |
    | TODO | TODO | TODO |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    TODO — one paragraph on why this matters, framed the way it would land with
    a colleague rather than a classroom.

    **Estimated time:** 25–35 minutes

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb

    CFG = nb.bootstrap(require=("OPENAI_API_KEY",))
    print(f"✅ {{CFG}}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — TODO
    """)
    return


@app.cell
def _():
    # TODO — one focused idea per task. Build the primitive from scratch first;
    # the library comes later, once the student can say what it added.
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #1:

    TODO — a discussion prompt answerable in one to three sentences. It must
    point at something the student has to *decide* in this week's challenge;
    a question that hints at nothing graded is one they will skip, correctly.

    **Answer:**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    # Conclusion

    TODO — what the student built, and the idea to take away.

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | TODO | TODO | TODO |
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    # Additional Context

    Where to go next, for anyone who wants to keep pulling on this.

    - [TODO]() — TODO, why it is worth reading
    - **Keep building:** TODO — a stretch goal worth a real afternoon
    """)
    return


if __name__ == "__main__":
    app.run()
'''


def marimo_pin() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    for dep in data["project"]["dependencies"]:
        if dep.split("#")[0].strip().startswith("marimo=="):
            return dep.split("#")[0].strip().removeprefix("marimo==").strip('", ')
    raise SystemExit("no exact marimo pin found in pyproject.toml")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("week", help="week directory, e.g. 03_Retrieval")
    ap.add_argument("session", help="S1 or S2")
    ap.add_argument("title", help='human title, e.g. "Retrieval Variants"')
    args = ap.parse_args()

    week_dir = ROOT / args.week
    if not week_dir.is_dir():
        raise SystemExit(f"{args.week} does not exist — create the week directory first")

    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.title).strip("_")
    target = week_dir / "sessions" / f"{args.session}_{slug}.py"
    if target.exists():
        raise SystemExit(f"{target.relative_to(ROOT)} already exists")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        TEMPLATE.format(pin=marimo_pin(), title=args.title), encoding="utf-8"
    )

    rel = target.relative_to(ROOT)
    print(f"✓ {rel}")
    print(f"\n  edit:     make nb F={rel}")
    print(f"  mirror:   make mirrors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
