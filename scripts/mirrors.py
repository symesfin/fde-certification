#!/usr/bin/env python3
"""Keep the committed .ipynb mirrors honest.

marimo `.py` notebooks are the source of truth. The `.ipynb` files next to them are
generated, so that students who can't install marimo (or who open the repo in Colab)
still get something runnable. Generated files rot the moment someone edits one by
hand, so this script is the gate that stops that.

    python scripts/mirrors.py --check     # verify; exits 1 on any problem
    python scripts/mirrors.py --write     # regenerate every mirror
    python scripts/mirrors.py --sync-pins # rewrite the marimo pin in every notebook

Four checks:

  A  freshness   -- the mirror byte-matches a fresh export of its .py
  B  version pin -- the installed marimo matches the exact pin in pyproject.toml
  C  deps        -- each notebook's PEP 723 block agrees with the root pyproject
  D  outputs     -- no execution outputs leaked into a committed mirror

Check B runs first and hard-fails, because `marimo export ipynb` writes its own
version into the notebook metadata. Exporting under the wrong marimo rewrites all
twenty mirrors with a diff that has nothing to do with your change.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import os
import sys
import tomllib
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
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"

# A marimo notebook is a .py under a sessions/ directory that builds a marimo App.
# Deliberately NOT **/*.py -- that would sweep up app.py, llm.py, and helpers/.
NOTEBOOK_GLOB = "*/sessions/*.py"
MARIMO_MARKER = "app = marimo.App("

PEP723_RE = re.compile(r"^# /// script\n(.*?)^# ///\n", re.MULTILINE | re.DOTALL)
REQ_NAME_RE = re.compile(r"^([A-Za-z0-9._-]+)")

OK, BAD = "✓", "✗"


# --------------------------------------------------------------------------- utils


def fail(msg: str) -> None:
    print(f"{BAD} {msg}", file=sys.stderr)


def notebooks() -> list[Path]:
    found = [
        path
        for path in sorted(ROOT.glob(NOTEBOOK_GLOB))
        if MARIMO_MARKER in path.read_text(encoding="utf-8")
    ]
    return found


def root_config() -> tuple[str, dict[str, str], set[str]]:
    """Return (marimo pin, {package: full specifier}, sandbox-only allowlist)."""
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    specs: dict[str, str] = {}
    for raw in data["project"]["dependencies"]:
        spec = raw.split("#", 1)[0].strip()
        name = REQ_NAME_RE.match(spec)
        if name:
            specs[name.group(1).lower()] = spec
    allow = {
        name.lower() for name in data.get("tool", {}).get("fde", {}).get("sandbox-only", [])
    }
    # The per-week groups (`week3 = [...]`) are the root pins for sandbox-only
    # packages: a notebook may declare them without a root dependency, but the
    # specifier it declares must match the one its week group installs.
    for group, entries in data.get("dependency-groups", {}).items():
        if not group.startswith("week"):
            continue
        for raw in entries:
            spec = raw.split("#", 1)[0].strip()
            name = REQ_NAME_RE.match(spec)
            if name:
                specs.setdefault(name.group(1).lower(), spec)
    return specs["marimo"].removeprefix("marimo=="), specs, allow


def parse_pep723(source: str) -> list[str] | None:
    """Pull the dependency list out of a notebook's inline script metadata."""
    match = PEP723_RE.search(source)
    if not match:
        return None
    body = "".join(
        line.removeprefix("# ").removeprefix("#") + "\n"
        for line in match.group(1).splitlines()
    )
    return tomllib.loads(body).get("dependencies", [])


def export(nb: Path) -> str:
    """Export to stdout. Writes nothing, so --check can never mutate the tree."""
    result = subprocess.run(
        [
            sys.executable, "-m", "marimo", "export", "ipynb",
            str(nb),
            "--sort", "topological",   # pinned; the default could change under us
        ],
        capture_output=True,
        text=True,
        env=_utf8_env(),
        # Explicit: marimo emits UTF-8, but a bare text=True decodes with the
        # OS default. On a Windows code page that is mojibake at best and a
        # UnicodeDecodeError at worst, on the machines least able to debug it.
        encoding="utf-8",
        cwd=ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"marimo export failed for {rel(nb)}:\n{result.stderr}")
    return result.stdout


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# -------------------------------------------------------------------------- checks


def check_version(pin: str) -> bool:
    """B -- must run before any export."""
    import marimo

    if marimo.__version__ == pin:
        print(f"{OK} marimo {pin}")
        return True
    fail(
        f"marimo version mismatch: installed {marimo.__version__}, pinned {pin}.\n"
        f"  The .ipynb metadata embeds the marimo version, so exporting under the\n"
        f"  wrong one rewrites every mirror in the repo with an unrelated diff.\n"
        f"  Fix:  uv sync\n"
        f"  Deliberately bumping marimo? See 'The marimo bump ritual' in CLAUDE.md."
    )
    return False


def check_deps(nb: Path, pin: str, specs: dict[str, str], allow: set[str]) -> bool:
    """C -- the notebook's sandbox deps must agree with the root env."""
    deps = parse_pep723(nb.read_text(encoding="utf-8"))
    if deps is None:
        fail(f"{rel(nb)} has no PEP 723 block; it cannot run under --sandbox")
        return False

    ok = True
    declared = {}
    for raw in deps:
        spec = raw.strip()
        name = REQ_NAME_RE.match(spec)
        if name:
            declared[name.group(1).lower()] = spec

    if declared.get("marimo") != f"marimo=={pin}":
        fail(f"{rel(nb)}: marimo must be pinned as `marimo=={pin}`, got {declared.get('marimo')!r}")
        ok = False

    for name, spec in declared.items():
        if name == "marimo":
            continue
        if name in allow and name not in specs:
            continue  # sandbox-only with no week group pin (torch, the harness stack): the notebook's call
        if name not in specs:
            fail(
                f"{rel(nb)}: `{spec}` is in neither [project.dependencies] nor "
                f"[tool.fde].sandbox-only.\n"
                f"  Add it to one of them in pyproject.toml."
            )
            ok = False
        elif specs[name] != spec:
            fail(f"{rel(nb)}: `{spec}` disagrees with the root pin `{specs[name]}`")
            ok = False

    # helpers tier 1 needs python-dotenv present in the sandbox.
    if "from helpers" in nb.read_text(encoding="utf-8") and "python-dotenv" not in declared:
        fail(f"{rel(nb)} imports helpers but does not declare `python-dotenv`")
        ok = False
    return ok


def check_outputs(mirror: Path) -> bool:
    """D -- someone ran the mirror in Jupyter and committed it."""
    try:
        doc = json.loads(mirror.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{rel(mirror)} is not valid JSON: {exc}")
        return False

    for index, cell in enumerate(doc.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs") or cell.get("execution_count") is not None:
            fail(
                f"{rel(mirror)} cell {index} has execution outputs.\n"
                f"  You ran the mirror -- that's fine, just don't commit it.\n"
                f"  Fix:  git checkout {rel(mirror)}"
            )
            return False
    return True


TIER1 = ("nb.py", "config.py", "display.py", "ui.py", "__init__.py")
TIER1_ALLOWED = {"marimo", "dotenv", "helpers"}  # plus anything in the stdlib


def check_tier1_purity() -> bool:
    """E -- tier 1 must import nothing heavy.

    Every notebook imports tier 1, including ones running in a minimal sandbox. One
    stray `import litellm` at module scope in `helpers/__init__.py` would break every
    notebook that didn't happen to declare litellm.
    """
    import ast

    helpers = ROOT / "helpers"
    if not helpers.is_dir():
        return True

    stdlib = sys.stdlib_module_names
    ok = True

    for name in TIER1:
        module = helpers / name
        if not module.exists():
            continue
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                # Relative imports (`from .config import ...`) stay inside tier 1.
                roots = [] if node.level else [(node.module or "").split(".")[0]]
            else:
                continue
            for root_name in roots:
                if root_name in stdlib or root_name in TIER1_ALLOWED:
                    continue
                fail(
                    f"helpers/{name} imports `{root_name}`, which is not tier 1.\n"
                    f"  Tier 1 is stdlib + marimo + python-dotenv only, because every\n"
                    f"  notebook imports it -- including sandboxed ones.\n"
                    f"  Move this into a tier-2 module and import it inside a function."
                )
                ok = False

    if ok:
        print(f"{OK} helpers tier 1 is clean")
    return ok


def check_timeouts(notebooks) -> bool:
    """F -- every model call sets an explicit timeout.

    Week 3 measured what an inherited default costs: a request that outruns the
    client timeout is cancelled server-side, the completed work is discarded, and
    a naive retry re-sends the identical request to fail identically. Forty
    minutes, no result, and an error naming nothing useful.

    The notebooks teach `completion()` from scratch on purpose, so this cannot be
    fixed by routing everything through helpers/llm.py. It has to be a gate.
    """
    import ast

    ok = True
    for nb in notebooks:
        try:
            tree = ast.parse(nb.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None) or ""
            if name.lstrip("_") not in {"completion", "embedding"}:
                continue
            if any(keyword.arg == "timeout" for keyword in node.keywords):
                continue
            # `**kwargs` may carry it; we cannot see inside, so allow it.
            if any(keyword.arg is None for keyword in node.keywords if keyword.arg is None):
                pass
            fail(
                f"{rel(nb)}:{node.lineno} calls {name}() with no explicit timeout.\n"
                f"  An inherited library default is how a call hangs for forty\n"
                f"  minutes and returns nothing. Pass timeout= explicitly."
            )
            ok = False

    if ok:
        print(f"{OK} every model call sets an explicit timeout")
    return ok


def check_fresh(nb: Path, mirror: Path) -> bool:
    """A -- the core check."""
    fresh = export(nb)
    if not mirror.exists():
        fail(f"{rel(mirror)} is missing\n  Fix:  make mirrors")
        return False

    current = mirror.read_text(encoding="utf-8")
    if current == fresh:
        return True

    diff = list(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            fresh.splitlines(keepends=True),
            fromfile=f"committed/{mirror.name}",
            tofile=f"fresh/{mirror.name}",
            n=1,
        )
    )
    fail(f"{rel(mirror)} is stale")
    for line in diff[:40]:
        print("   " + line.rstrip(), file=sys.stderr)
    if len(diff) > 40:
        print(f"   ... {len(diff) - 40} more lines", file=sys.stderr)
    print(
        f"  Fix:  python scripts/mirrors.py --write {rel(nb)}\n"
        f"  Never hand-edit a .ipynb -- the .py next to it is the source of truth.",
        file=sys.stderr,
    )
    return False


# --------------------------------------------------------------------------- modes


def do_check(targets: list[Path], pin: str, specs, allow) -> int:
    if not check_version(pin):
        return 1

    ok = check_tier1_purity()
    ok = check_timeouts(targets) and ok

    if not targets:
        print("no marimo notebooks yet - nothing to check")
        return 0 if ok else 1

    for nb in targets:
        mirror = nb.with_suffix(".ipynb")
        ok &= check_deps(nb, pin, specs, allow)
        ok &= check_fresh(nb, mirror)
        if mirror.exists():
            ok &= check_outputs(mirror)
        if ok:
            print(f"{OK} {rel(mirror)}")
    return 0 if ok else 1


def do_write(targets: list[Path], pin: str) -> int:
    if not check_version(pin):
        return 1
    for nb in targets:
        mirror = nb.with_suffix(".ipynb")
        fresh = export(nb)
        changed = not mirror.exists() or mirror.read_text(encoding="utf-8") != fresh
        mirror.write_text(fresh, encoding="utf-8")
        print(f"{OK} {rel(mirror)}" + ("  (updated)" if changed else "  (unchanged)"))
    return 0


def do_sync_pins(targets: list[Path], pin: str) -> int:
    """Rewrite the marimo pin inside every notebook's PEP 723 block."""
    pattern = re.compile(r'("|)marimo==[0-9][^"\',]*\1')
    for nb in targets:
        source = nb.read_text(encoding="utf-8")
        match = PEP723_RE.search(source)
        if not match:
            fail(f"{rel(nb)} has no PEP 723 block; skipped")
            continue
        block = match.group(0)
        updated = pattern.sub(f'"marimo=={pin}"', block)
        if updated != block:
            nb.write_text(source.replace(block, updated), encoding="utf-8")
            print(f"{OK} {rel(nb)}  -> marimo=={pin}")
        else:
            print(f"  {rel(nb)}  (already {pin})")
    print("\nNow run: uv lock && make mirrors -- and commit nothing else with it.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify; exit 1 on problems")
    mode.add_argument("--write", action="store_true", help="regenerate mirrors")
    mode.add_argument("--sync-pins", action="store_true", help="rewrite the marimo pin")
    ap.add_argument("paths", nargs="*", type=Path, help="notebooks (default: all)")
    args = ap.parse_args()

    pin, specs, allow = root_config()

    if args.paths:
        # Accept directories as well as files -- `--write 04_Evals/sessions/` is
        # the obvious thing to type, so it should work.
        targets = []
        for path in args.paths:
            resolved = path.resolve()
            if resolved.is_dir():
                targets += [
                    notebook for notebook in sorted(resolved.rglob("*.py"))
                    if MARIMO_MARKER in notebook.read_text(encoding="utf-8")
                ]
            else:
                targets.append(resolved)
        if not targets:
            fail(f"no marimo notebooks found in {', '.join(str(path) for path in args.paths)}")
            return 1
    else:
        targets = notebooks()

    if args.check:
        return do_check(targets, pin, specs, allow)
    if args.write:
        return do_write(targets, pin)
    return do_sync_pins(targets, pin)


if __name__ == "__main__":
    sys.exit(main())
