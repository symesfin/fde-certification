"""Shared helpers for the FDE curriculum.

Two tiers, and the split matters:

**Tier 1** — `nb`, `config`, `display`, `ui`. Needs only stdlib, `python-dotenv`,
and `marimo`. Re-exported here, so `from helpers import nb, show` always works,
including in a notebook running under `marimo edit --sandbox` with a minimal
dependency set.

**Tier 2** — `judge`, `vectorstore`, `rag`, `sdg`. Pulls in litellm, a vector store,
and so on. Import these explicitly (`from helpers import judge`) and declare the
third-party packages in your notebook's PEP 723 block.

**This module must never import tier 2.** Doing so would drag litellm into every
sandbox, and notebooks that don't need it would fail to start.

The boundary rule for what belongs here at all: keep the from-scratch teaching code
in the notebook; only pure plumbing moves into `helpers/`. If reading it is the
lesson, it stays in the lesson.
"""

from .config import Config
from .display import show, stream_chat, stream_md
from .nb import bootstrap, find_root
from .ui import lines, spinner, table, track

__all__ = [
    "Config",
    "bootstrap",
    "find_root",
    "lines",
    "show",
    "spinner",
    "stream_chat",
    "stream_md",
    "table",
    "track",
]
