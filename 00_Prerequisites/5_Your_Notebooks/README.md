# 5 · Your notebooks

Every session in this course is a **marimo** notebook. If you have used Jupyter,
most of this will feel familiar — but marimo runs on a different model, and the
one difference that matters will show up in your first thirty seconds.

You do not need to learn marimo before Session 1. You need it installed, and you
need to have opened one notebook.

---

## Why this course uses marimo

Three reasons, in the order they will matter to you.

| | Why it matters here |
| --- | --- |
| **A notebook that always runs top to bottom** | marimo works out execution order from a dependency graph rather than the order you happened to click. There is no hidden state, so "it works on my machine because I ran cell 4 twice" cannot happen. Every session in this course has to run start to finish on your machine, and this is what makes that true. |
| **Notebooks are `.py` files** | You can read the diff. You can review it. You can merge it. A `.ipynb` is JSON with output blobs baked in, which is why notebook merge conflicts are famously unresolvable. |
| **Each notebook declares its own dependencies** | Every session carries a small header listing exactly what it needs. `uv` reads it and builds a throwaway environment on the spot — so a notebook runs even if your main environment is broken, missing, or full of something else's packages. |

That third one is worth more than it sounds on a locked-down machine. It means a
session that fails for you is a problem with *that session*, not with your setup.

---

## Open one

You already have marimo — it came with `uv sync` in
[guide 3](../3_Clone_and_Run/README.md). From the repository root:

```bash
make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
```

**No `make` on Windows?** You do not need it. That target is one line:

```powershell
uv run marimo edit --sandbox 01_Product_Engineering\sessions\S1_Enterprise_Dev_Environment.py
```

A browser tab opens on `localhost`. That is the whole thing.

> `--sandbox` builds the environment from the notebook's own header rather than
> your root environment. It is slower the first time and immune to everything
> that usually goes wrong.

### Two ways to run a notebook

| | Command | Needs |
| --- | --- | --- |
| **Sandboxed** (the default, used everywhere in this course) | `uv run marimo edit --sandbox <file.py>` or `make nb F=<file.py>` | nothing installed; the notebook's own header lists its packages |
| **Root environment** | `uv run marimo edit <file.py>` | that week's package group: `make setup-week W=3` for Week 3, `W=4` for Week 4 |

The root environment is what `make setup` builds, and it is deliberately small:
the challenge apps, `make check` and the helpers run there, and the notebooks
do not need it. Some weeks' notebooks import packages the root environment does
not ship (Week 3's BM25 index, Qdrant and FastEmbed; Week 4's Ragas). Under
`--sandbox` that is handled for you. Without it, `ModuleNotFoundError` on the
first cell means you skipped `make setup-week W=<n>` — run it once and reopen.
`make env` (or `uv run python scripts/check_env.py`) tells you which week
groups your root environment has right now, and the command for any it lacks.
`make setup-all` installs every optional group at once (about 3 GB, mostly
torch).

One thing the two routes share: `uv run` syncs the root environment before it
starts marimo, even with `--sandbox`. So a stale `uv.lock` (someone changed
`pyproject.toml` and did not run `uv lock`) shows up as a *Missing packages*
popup on the sandboxed route too. That is `uv.lock`'s fault, not the
notebook's — `uv lock` once at the repo root fixes it.

---

## The one difference from Jupyter

**Edit a cell and everything downstream re-runs by itself.**

There is no "Restart & Run All" to prove you did not fool yourself, because the
stale-cell problem cannot occur. Delete a cell and its variables go with it. The
order cells appear on screen does not decide anything — the dependency graph
does — so you can move them freely.

That is the trade: you give up casual mutation, and you get a notebook that is
never quietly wrong.

### Where a Jupyter habit will bite

| Habit | What happens | Do this instead |
| --- | --- | --- |
| Defining the same variable in two cells | Hard error | Rename by stage — `df_raw`, `df_clean` |
| `results.append(...)` in a later cell | Invisible to the graph. Nothing downstream re-runs and nothing warns you | Build the new value in one cell |
| `!pip install`, `%%time`, `%matplotlib` | Not supported — this is a `.py` file | Dependencies live in the notebook's header |
| `for doc in docs:` | `doc` leaks into global scope | `for _doc in docs:` — a leading underscore means cell-private |
| Reading a slider's `.value` in the cell that created it | Always returns the default | Create it in one cell, read it in another |

The second row is the one that actually costs people time, because it fails
silently rather than loudly.

---

## Nothing expensive runs when you open a notebook

Every cell that costs money or minutes sits behind a button. Opening a session
fires no model calls and spends nothing.

So if a cell looks like it did nothing, look for the button — it is waiting for
you. This is deliberate: reactive execution plus unguarded model calls would
mean re-billing you every time you touched anything.

---

## The `.ipynb` next to each notebook is generated

Each session ships as two files:

```
S1_Enterprise_Dev_Environment.py      <- the notebook. Edit this one
S1_Enterprise_Dev_Environment.ipynb   <- generated from it. Never edit this one
```

The `.ipynb` exists so the material is readable on GitHub and runnable by anyone
who cannot install marimo. It is regenerated from the `.py`, and CI fails if the
two disagree.

**If you hit a merge conflict in an `.ipynb`, do not resolve it by hand:**

```bash
git checkout --ours <file>.ipynb
make mirrors
```

On Windows, where you have no `make`, that second line is:

```powershell
uv run python scripts\mirrors.py --write
```

Regenerating is the only correct fix. Hand-editing produces the right bytes by
the wrong route, and the checks below will say so.

### Every `make` target, without `make`

`make` is a Unix tool and you do not need it. Each target is one or two
commands, and these are the ones worth knowing:

| Instead of | Run |
| --- | --- |
| `make nb F=<file.py>` | `uv run marimo edit --sandbox <file.py>` |
| `make mirrors` | `uv run python scripts\mirrors.py --write` |
| `make check` | the eight commands below |

`make check` is the full gate suite. Nothing here needs a model or a network,
so it cannot cost you anything or flake:

```powershell
uv run python scripts\mirrors.py --check
uv run python scripts\check_links.py
uv run python scripts\check_standalone.py
uv run python scripts\check_roundtrip.py
uv run python scripts\check_deliverables.py
uv run --group dev python scripts\check_manifests.py
uv run python scripts\check_helpers.py
uv run --group dev python -m pytest tests/ -q
```

You will rarely need these — they are what CI runs on every change. They are
here so that "run `make check`" never means "install a build tool first".

---

## 🧯 If it's blocked

### marimo will not install

Use the `.ipynb` mirrors instead. Open them in Jupyter, VS Code, or Colab —
they are committed, executed in CI, and contain the same material. You lose
reactive execution and the interactive widgets; you lose no content.

```bash
uv run jupyter lab      # or just open the .ipynb in VS Code
```

Write down what blocked the install in
[`use_case/ecosystem.md`](../../use_case/ecosystem.md). A machine that cannot
install a Python package from PyPI has a constraint worth naming.

### The browser tab never opens

marimo prints a `http://localhost:2718/...` URL to the terminal. Copy it into
your browser by hand — the access token is in the URL, so it will work. This is
common in WSL and on machines with no default browser configured.

### The port is already in use

```bash
uv run marimo edit --sandbox --port 2719 <file.py>
```

---

## ✅ Ready

- [ ] `make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py` opens a notebook in your browser
- [ ] The setup cell prints `✅` with your model name
- [ ] You know the `.ipynb` is generated and you should not edit it

Go back to the [checklist](../README.md#-you-are-ready-when) and confirm every
box.

---

## ➡️ Then, before Session 2

Start [**Getting to Concreteness**](https://bit.ly/fde-concreteness) — it is the
highest-leverage forty minutes of the cohort, and Session 2 halts without it. It
needs no model, no tooling, and no network, so you can do it even if something
above is still blocked.
