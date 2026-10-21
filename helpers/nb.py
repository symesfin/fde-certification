"""The four things every notebook does before it does anything else.

Notebooks in this repo have to run two ways: inside the root `uv` environment, and
standalone under `marimo edit --sandbox`, where there is no root venv and `helpers/`
is not on `sys.path`. `bootstrap()` works identically in both, because it derives
everything from the notebook's own location on disk rather than from the
environment. That is the whole trick.

Tier 1: stdlib + python-dotenv only.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .config import Config, from_env

_MARKER = "pyproject.toml"


def find_root(start: Path | None = None) -> Path:
    """Walk up from a notebook to the repo root.

    Prefers marimo's own `notebook_dir()` when available, because it reports the
    notebook file's location regardless of the working directory the server was
    launched from — which is what makes this sandbox-safe.
    """
    if start is None:
        try:
            import marimo as mo

            start = Path(mo.notebook_dir() or Path.cwd())
        except Exception:
            start = Path.cwd()

    for candidate in (start, *start.parents):
        if (candidate / _MARKER).exists() and (candidate / "helpers").is_dir():
            return candidate

    raise RuntimeError(
        f"Could not find the repo root above {start}.\n"
        f"Expected a directory containing both {_MARKER} and helpers/."
    )


def bootstrap(*, require: tuple[str, ...] = (), start: Path | None = None) -> Config:
    """Locate the repo root, load `.env`, check required keys, return the config.

    Args:
        require: env var names that must be set. Fails loudly and early with a
            message naming `.env.template`, rather than at the first model call
            with a 401 from somewhere three frames down.

    Returns:
        A `Config` with resolved paths and model settings.
    """
    root = find_root(start)

    # Put the repo root on the path so `from helpers import ...` keeps working in
    # cells that run after this one.
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:  # pragma: no cover
        raise ModuleNotFoundError(
            "python-dotenv is missing. If you are running under --sandbox, add\n"
            '    "python-dotenv>=1.2",\n'
            "to this notebook's PEP 723 dependency block."
        ) from None

    load_dotenv(root / ".env")
    load_dotenv()  # a .env beside the notebook wins nothing, but is allowed

    import os

    missing = [name for name in require if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}.\n"
            f"Copy {root / '.env.template'} to {root / '.env'} and fill it in."
        )

    _quiet_litellm()
    return from_env(root)


def _quiet_litellm() -> None:
    """Stop LiteLLM printing a red "Provider List" line on every call.

    It prints that whenever a model is missing from its price list -- any gateway
    alias -- even though the call succeeds. The only switch is a module attribute.
    `import_module`, not an import statement, because tier 1 may not import
    litellm; `find_spec` first, so a sandbox without it is left alone.
    """
    import importlib
    import importlib.util

    if importlib.util.find_spec("litellm") is not None:
        importlib.import_module("litellm").suppress_debug_info = True
