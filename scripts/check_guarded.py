"""Run a notebook the way a student runs it, with the guarded cells open.

    uv run python scripts/check_guarded.py 04_Evals/sessions/S7_Practical_Evals.py

`make check` proves the two formats match. `make execute` proves the notebook
runs. **Neither one has ever executed a line inside a `mo.ui.run_button` guard**,
because during `marimo export` the button's value is `False` and `mo.stop` halts
the cell before its body runs. Every expensive cell in this repository is behind
such a guard, which means the most fragile code in the curriculum is the code CI
never touches. That is deliberate -- a CI run must not fire hundreds of model
calls -- but it is not a reason to leave it unrunnable on demand.

This script closes that hole, and it differs from the other gates in two ways
that each caught a real bug the others missed:

**It builds the environment from the notebook's own PEP 723 block**, the way
`--sandbox` does. Testing in the root environment hid a dependency that was
installed there by hand and declared nowhere -- so the notebook worked for the
author and failed on first contact with a student.

**It runs the cells inside a live asyncio event loop**, via `await app.embed()`,
the way the marimo kernel does. Executing a notebook as a plain script does not,
so an `asyncio.run(...)` call sails through every offline check and then raises
`RuntimeError: asyncio.run() cannot be called from a running event loop` the
moment the notebook is opened for real.

It costs real model calls. Run it before shipping a notebook whose guarded
cells changed, not on every save.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import importlib.util
import io
import pathlib
import re
import subprocess
import os
import sys
import time
import traceback
import warnings


# marimo writes the exported notebook to its own stdout. When that stdout is a
# pipe -- which it always is here -- Python picks the encoding from the OS, and
# on Windows that is cp1252. The breakout-room emoji in the notebooks is not in
# cp1252, so the child dies with UnicodeEncodeError before writing a byte, and
# `make check` fails on the machines most of the cohort actually uses.
# Setting the child's IO encoding explicitly is the only fix that works from
# this side; `encoding=` on subprocess.run only governs how WE decode the pipe.
def _utf8_env() -> dict[str, str]:
    return {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


# Windows consoles default to a code page that cannot encode the check marks
# these scripts print, so a redirected run dies with UnicodeEncodeError before
# reporting anything. Force UTF-8 on our own output rather than dropping to
# ASCII markers -- the students on managed Windows laptops are the ones running
# these gates.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCK = re.compile(r"# /// script\n(.*?)# ///", re.S)

# --------------------------------------------------------------------- stubs
#
# Forcing a guard open means replacing the widget with something whose `.value`
# is already truthy, before the notebook imports it.


class _Pressed:
    value = True

    def __init__(self, *args, **kwargs):
        pass

    def _mime_(self):
        return ("text/html", "<b/>")


class _Slider(_Pressed):
    value = 5


class _Check(_Pressed):
    value = False


def inline_deps(path: pathlib.Path) -> list[str]:
    match = BLOCK.search(path.read_text(encoding="utf-8"))
    if not match:
        return []
    body = "".join(line.lstrip("#").strip() for line in match.group(1).splitlines())
    inside = re.search(r"dependencies\s*=\s*\[(.*?)\]", body, re.S)
    return re.findall(r'"([^"]+)"', inside.group(1)) if inside else []


async def _run_here(path: pathlib.Path, force: bool) -> int:
    """Execute the notebook in *this* interpreter, inside the running loop."""
    warnings.filterwarnings("ignore")
    import marimo as mo

    if force:
        mo.ui.run_button, mo.ui.slider, mo.ui.checkbox = _Pressed, _Slider, _Check

    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    # Register before executing. `@app.class_definition` resolves the class back
    # through `sys.modules[__name__]`, so a module that was never registered
    # produces `NameError: name 'X' is not defined` from inside a cell that is
    # perfectly correct -- this gate reported a notebook broken when the notebook
    # was fine and the harness was not. `@app.function` happens not to need it,
    # which is why this hid until a notebook used a class.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    started = time.perf_counter()
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            await module.app.embed()
    except Exception:
        print(f"✗ {path.name}  ({time.perf_counter() - started:.1f}s)")
        print(traceback.format_exc()[-2500:])
        tail = buf.getvalue()[-800:]
        if tail.strip():
            print("--- captured output ---\n" + tail)
        return 1
    print(
        f"✓ {path.name}  ({time.perf_counter() - started:.1f}s) "
        f"— guards {'open' if force else 'closed'}, live event loop"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("notebook")
    ap.add_argument("--no-force", action="store_true",
                    help="leave guards closed, as a fresh open would")
    ap.add_argument("--here", action="store_true",
                    help="use the current environment instead of the notebook's declared one")
    args = ap.parse_args()

    path = pathlib.Path(args.notebook).resolve()
    if args.here:
        return asyncio.run(_run_here(path, not args.no_force))

    deps = inline_deps(path)
    print(f"{path.name}: resolving {len(deps)} declared dependencies")
    cmd = ["uv", "run", "--quiet", "--isolated", "--no-project"]
    for dep in deps:
        cmd += ["--with", dep]
    cmd += ["python", str(pathlib.Path(__file__).resolve()), str(path), "--here"]
    if args.no_force:
        cmd.append("--no-force")
    return subprocess.run(cmd, cwd=ROOT, env=_utf8_env()).returncode


if __name__ == "__main__":
    raise SystemExit(main())
