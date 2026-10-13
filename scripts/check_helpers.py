"""Every tier-2 helper must have a named consumer in the curriculum.

The failure this prevents happened twice in this repo. Helpers get written
against an imagined future week, nothing references them, and they rot -- code
with tests and no callers, which reads as maintained and is not.

The rule is NOT "a notebook must import it." Tier 2 is deliberately app-side:
the sessions teach `completion()` and `span()` from scratch, and the packaged
version is what the student's own application imports. A markdown code block
showing `from helpers.trace import Tracer` is a legitimate reference.

What is not legitimate is zero mentions anywhere. If no week teaches toward it
and no challenge asks for it, it should be deleted rather than maintained.

One exception, declared rather than silent: a repository that publishes the
weeks incrementally carries helpers whose consuming week has not arrived yet.
Those are listed under `[tool.fde].helpers-pending` in pyproject.toml and are
reported as pending, not failing -- and the moment one of them *does* gain a
consumer, this gate fails until the entry is removed, so the list cannot rot.
"""

from __future__ import annotations

import sys
import tomllib
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
OK, BAD, WAIT = "✓", "✗", "⏳"

# Tier 1 is imported by every notebook via `from helpers import nb, ui`; it does
# not need a per-module mention.
TIER1 = {"nb", "config", "display", "ui", "__init__"}


def curriculum_text() -> list[tuple[Path, str]]:
    out = []
    for pattern in ("*/sessions/*.py", "*/challenge/*.md", "*/README.md"):
        for path in ROOT.glob(pattern):
            if "/.venv/" in path.as_posix():
                continue
            out.append((path, path.read_text("utf-8")))
    return out


def pending() -> set[str]:
    """Helpers declared as waiting for their week, from pyproject.toml."""
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return set(tomllib.load(handle).get("tool", {}).get("fde", {}).get("helpers-pending", []))


def main() -> int:
    waiting = pending()
    helpers = sorted(
        path.stem for path in (ROOT / "helpers").glob("*.py") if path.stem not in TIER1
    )
    if not helpers:
        print(f"{OK} no tier-2 helpers")
        return 0

    texts = curriculum_text()
    orphans, stale = [], []
    for name in helpers:
        needles = (f"helpers/{name}", f"helpers.{name}", f"helpers import {name}")
        where = [path for path, body in texts if any(needle in body for needle in needles)]
        if not where and name in waiting:
            print(f"{WAIT} helpers/{name}.py  pending -- its week is not in this repository yet")
        elif not where:
            orphans.append(name)
        else:
            rels = sorted({path.relative_to(ROOT).parts[0] for path in where})
            print(f"{OK} helpers/{name}.py  ← {', '.join(rels)}")
            if name in waiting:
                stale.append(name)

    for name in orphans:
        print(
            f"{BAD} helpers/{name}.py is referenced by no session, challenge, or week "
            f"README.\n"
            f"  Either name its consumer -- the week that teaches toward it or the\n"
            f"  challenge that asks for it -- or delete it. A helper with tests and\n"
            f"  no callers reads as maintained and is not."
        )
    for name in stale:
        print(
            f"{BAD} helpers/{name}.py is listed in [tool.fde].helpers-pending but now has a\n"
            f"  consumer. Remove it from the list in pyproject.toml."
        )
    return 1 if (orphans or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
