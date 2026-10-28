"""Open a notebook from the root environment, with its week's packages installed.

    uv run python scripts/nb.py 04_Evals/sessions/S7_Practical_Evals.py

The stable route on a managed Windows laptop. `marimo edit --sandbox` builds a
fresh environment and launches the `marimo.exe` inside it; an Application
Control policy that blocks executables it has not seen before stops that with
"os error 4551" every time a notebook's header changes. This script never
launches a new executable: it syncs the notebook's week group into `.venv`
(`uv sync --inexact`, so other weeks' groups stay installed) and starts marimo
through the interpreter that is already running -- `python -m marimo`, with
`--no-sandbox` so there is no prompt.

Same notebook, same pins: a week group carries the same specifiers as the
notebook's PEP 723 header, and `scripts/mirrors.py` keeps them equal.

Any extra arguments are passed to `marimo edit` (for example `--port 2719`).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEEK_DIR_RE = re.compile(r"^(\d\d)_")

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def week_group_for(notebook: Path) -> str | None:
    """`04_Evals/sessions/S7.py` -> `week4`, if pyproject.toml has that group."""
    try:
        relative = notebook.resolve().relative_to(ROOT)
    except ValueError:
        return None
    match = WEEK_DIR_RE.match(relative.parts[0]) if relative.parts else None
    if not match:
        return None
    group = f"week{int(match.group(1))}"
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return group if group in data.get("dependency-groups", {}) else None


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    notebook = Path(argv[0])
    if not notebook.exists():
        print(f"✗ no such notebook: {notebook}")
        return 2

    group = week_group_for(notebook)
    if group:
        print(f"→ uv sync --inexact --group {group}")
        synced = subprocess.run(["uv", "sync", "--inexact", "--group", group], cwd=ROOT)
        if synced.returncode:
            print(f"✗ uv sync failed; is uv on your PATH? Fix that, then rerun.")
            return synced.returncode
    else:
        print("→ no week group for this path; opening from the root environment as is")

    # sys.executable is .venv's python when run via `uv run` -- an executable the
    # machine already trusts. No `marimo.exe`, no sandbox, no prompt.
    command = [sys.executable, "-m", "marimo", "edit", "--no-sandbox", str(notebook), *argv[1:]]
    print("→", " ".join(command[1:]))
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
