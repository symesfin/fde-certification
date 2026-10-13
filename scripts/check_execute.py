"""Actually run both formats. The mirror gate only proves they are byte-identical.

`scripts/mirrors.py` re-exports every `.py` and byte-compares it to the committed
`.ipynb`. That catches drift and nothing else: a notebook that raises on cell
three exports identically to one that works.

This runs them.

  --py     execute the marimo .py    (via `marimo export ipynb --include-outputs`)
  --ipynb  execute the mirror        (via nbclient, a real Jupyter kernel)

Guarded cells are expected to halt. Every expensive cell in this curriculum sits
behind `mo.ui.run_button` + `mo.stop(...)`, and in marimo `mo.stop` raises a
`MarimoStopError` that the runtime catches. A plain Jupyter kernel has nothing to
catch it, so the same guard surfaces as an uncaught exception and stops "Run
All". That is reported separately from a real failure, because it is a property
of the export format rather than a bug in the notebook.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import os
import sys
import tempfile
from pathlib import Path


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
#
# `line_buffering=True` is the other half, and it is not cosmetic. Python block-
# buffers stdout whenever it is a pipe rather than a terminal, so `make execute
# | tee log.txt` prints nothing for the entire run and then everything at once.
# This gate takes minutes at best, so the student who pipes it sits in front of
# a silent terminal with no way to tell work from a hang -- which is how the
# defect below stayed hidden for as long as it did.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

ROOT = Path(__file__).resolve().parent.parent
OK, BAD, WARN = "✓", "✗", "!"
# Both mean "a guard upstream fired", not "the notebook is broken".
GUARDS = ("MarimoStopError", "ancestor-stopped")


def is_notebook(path: Path) -> bool:
    """`sessions/` also holds plain scripts -- the MCP server in Week 5, for one.
    Only marimo notebooks have an App, and only they can be exported."""
    try:
        return "app = marimo.App(" in path.read_text("utf-8")
    except OSError:
        return False


def notebooks(targets: list[str] | None) -> list[Path]:
    if targets:
        out: list[Path] = []
        for target in targets:
            path = Path(target)
            path = (path if path.is_absolute() else ROOT / path).resolve()
            out.extend(sorted(path.glob("**/sessions/*.py")) if path.is_dir() else [path])
        # An explicitly named file is checked even so; a directory sweep is filtered.
        return [path for path in out if path.suffix == ".py" and is_notebook(path)]
    return [path for path in sorted(ROOT.glob("*/sessions/*.py")) if is_notebook(path)]


def errors_in(nb: dict) -> list[tuple[int, str, str]]:
    out = []
    for index, cell in enumerate(nb.get("cells", [])):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                out.append((index, output.get("ename", "?"), str(output.get("evalue", ""))[:160]))
    return out


def run_py(path: Path, timeout: int) -> tuple[str, list]:
    """Execute the marimo notebook and report any cell that errored."""
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "out.ipynb"
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "marimo", "export", "ipynb",
                 "--include-outputs", str(path), "-o", str(dest), "-f"],
                capture_output=True, text=True, encoding="utf-8",
                env=_utf8_env(), timeout=timeout, cwd=ROOT,
                # A notebook with inline dependencies makes marimo ask whether
                # to build a sandbox venv for it. `capture_output` redirects
                # stdout and stderr but NOT stdin, so the child inherits the
                # terminal, sees a tty, and asks -- while the question itself
                # goes to the captured stderr where nobody can read it. The run
                # then blocks until the timeout, on every notebook, with no
                # output to explain why. That is why this gate passes in CI,
                # which has no tty, and hangs for every human who runs it.
                #
                # `input` rather than `stdin=DEVNULL`, and the difference is a
                # Windows quirk worth knowing: DEVNULL opens NUL, NUL is a
                # character device, and Python's isatty() reports a character
                # device as a terminal. So marimo asks anyway, gets EOF, and
                # aborts -- fast instead of hung, but still failing. A pipe is
                # not a character device on either platform, so this takes the
                # non-interactive branch everywhere; the "n" is insurance in
                # case some other path asks something.
                input="n\n",
            )
        except subprocess.TimeoutExpired:
            return "timeout", [(-1, "Timeout", f"exceeded {timeout}s")]
        if not dest.exists():
            return "failed", [(-1, "ExportFailed", (proc.stderr or proc.stdout)[-300:])]
        return "ok", errors_in(json.loads(dest.read_text("utf-8")))


def run_ipynb(path: Path, timeout: int) -> tuple[str, list]:
    """Execute the mirror in a real Jupyter kernel."""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ModuleNotFoundError:
        return "skipped", [(-1, "MissingDep", "uv sync --group dev")]

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb, timeout=timeout, kernel_name="python3", allow_errors=True,
        resources={"metadata": {"path": str(path.parent)}},
    )
    try:
        client.execute()
    except Exception as exc:
        return "failed", [(-1, type(exc).__name__, str(exc)[:200])]
    return "ok", errors_in(nb)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*")
    ap.add_argument("--py", action="store_true")
    ap.add_argument("--ipynb", action="store_true")
    ap.add_argument("--timeout", type=int, default=420)
    args = ap.parse_args()
    do_py = args.py or not args.ipynb
    do_ipynb = args.ipynb or not args.py

    failures = 0
    for path in notebooks(args.targets):
        rel = path.relative_to(ROOT)
        for label, fn, enabled, target in (
            ("py   ", run_py, do_py, path),
            ("ipynb", run_ipynb, do_ipynb, path.with_suffix(".ipynb")),
        ):
            if not enabled:
                continue
            if not target.exists():
                print(f"{BAD} {label} {rel}  -- missing")
                failures += 1
                continue
            status, errs = fn(target, args.timeout)
            guards = [error for error in errs if error[1] in GUARDS]
            # In Jupyter a guard raises instead of halting, so the variables that
            # cell would have defined never exist and every dependent cell dies
            # with NameError. That is the guard working, one format removed --
            # not a broken notebook. Only count NameErrors that appear BEFORE
            # any guard fired, which are the real ones.
            first_guard = min((error[0] for error in guards), default=None)
            cascade = [
                error for error in errs
                if error[1] == "NameError" and first_guard is not None and error[0] > first_guard
            ]
            real = [error for error in errs if error[1] not in GUARDS and error not in cascade]
            if status != "ok":
                print(f"{BAD} {label} {rel}  -- {status}: {errs[0][2] if errs else ''}")
                failures += 1
            elif real:
                print(f"{BAD} {label} {rel}  -- {len(real)} error(s)")
                for index, name, val in real[:3]:
                    print(f"      cell {index}: {name}: {val}")
                failures += 1
            elif guards or cascade:
                tail = f", {len(cascade)} dependent cell(s) cascaded" if cascade else ""
                print(f"{WARN} {label} {rel}  -- ran; "
                      f"{len(guards)} guarded cell(s) halted{tail}")
            else:
                print(f"{OK} {label} {rel}")
    if failures:
        print(f"\n{BAD} {failures} execution failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
