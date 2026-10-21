.PHONY: help setup setup-local setup-harness setup-week setup-all env mirrors check execute nb guarded clean

help:
	@echo "setup     install the root env (uv sync; KEEPS every optional group already present)"
	@echo "setup-local  add the optional local-model group (torch, transformers)"
	@echo "setup-harness  add the optional harness group (langgraph, deepagents)"
	@echo "setup-week W=3  add one week's notebook packages (needed to open its notebooks WITHOUT --sandbox)"
	@echo "env W=3   report whether a week's packages are installed in the root env (no changes)"
	@echo "setup-all    every optional group at once (~3 GB, mostly torch)"
	@echo "mirrors   regenerate every .ipynb from its marimo .py"
	@echo "check     what CI runs: mirrors, pins, deps, links, tests"
	@echo "execute  actually RUN every notebook, both .py and .ipynb"
	@echo "nb F=path open a notebook in its own sandbox (no root env needed)"
	@echo "guarded F=path  run ONE notebook with its guards open, in its own env (costs model calls)"

# `uv sync` is exact: it removes anything not in the groups it was asked for.
# So a plain `uv sync` silently uninstalls whichever optional group a student
# installed on purpose. They then hit ModuleNotFoundError in a notebook that
# worked yesterday, having done nothing wrong, and nothing in the output said a
# package was removed. Keep every group that is already there.
#
# `group:marker` -- the marker is a package that ONLY that group installs, never
# a transitive dependency of the base environment (`pydantic` would be wrong:
# litellm pulls it in regardless). `rank_bm25` and `ragas` are pulled by nothing
# else, so they are true signals for their week groups.
OPTIONAL_GROUPS = local:torch harness:langgraph week3:rank_bm25 week4:ragas
WEEK_GROUPS = week3 week4

setup:
	@groups=""; \
	for pair in $(OPTIONAL_GROUPS); do \
		g=$${pair%%:*}; marker=$${pair##*:}; \
		if uv run --no-sync python -c "import $$marker" >/dev/null 2>&1; then \
			echo "keeping optional group already installed: $$g"; \
			groups="$$groups --group $$g"; \
		fi; \
	done; \
	echo "uv sync$$groups"; \
	uv sync $$groups

setup-local:
	uv sync --group local

# The two framework notebooks in the harness appendix. Opt-in for the same reason
# `local` is: nothing else in the curriculum wants the LangChain stack.
setup-harness:
	uv sync --group harness

# One group per week whose notebooks need packages the root environment does not
# ship (see [dependency-groups] in pyproject.toml). You do not need this to open a
# notebook with `make nb` / `--sandbox`; you do need it to open that week's
# notebooks from the root environment, or to `make execute` them.
#   make setup-week W=3
setup-week:
	@test -n "$(W)" || { echo "usage: make setup-week W=<week number>, e.g. W=3"; exit 2; }
	uv sync --inexact --group week$(W)
	uv run python scripts/check_env.py $(W)

setup-all:
	uv sync --group local --group harness $(foreach g,$(WEEK_GROUPS),--group $(g))

# Which week groups are installed right now? Reads the groups from pyproject.toml
# and imports each package, so it cannot drift from what `uv sync` installs.
#   make env          every week group
#   make env W=3      one week
env:
	uv run python scripts/check_env.py $(W)

mirrors:
	uv run python scripts/mirrors.py --write

check:
	uv run python scripts/mirrors.py --check
	uv run python scripts/check_links.py
	uv run python scripts/check_standalone.py
	uv run python scripts/check_roundtrip.py
	uv run python scripts/check_deliverables.py
	uv run --group dev python scripts/check_manifests.py
	uv run python scripts/check_helpers.py
	uv run --group dev python -m pytest tests/ -q

# Runs every notebook in both formats. Minutes, not seconds, so it is not
# part of `check` -- but it is the only thing that proves they work.
#   make execute F=03_Retrieval    to scope it to one week
# Installs every week group first, because the notebooks run from the root env here.
execute:
	uv run --group dev --group harness $(foreach g,$(WEEK_GROUPS),--group $(g)) python scripts/check_execute.py $(F)

# Open any notebook standalone, using only its PEP 723 inline dependencies.
#   make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
nb:
	uv run marimo edit --sandbox $(F)

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

# The only gate that executes the code inside `mo.ui.run_button` guards, in the
# environment the notebook declares, inside a live event loop. Costs real model
# calls, so it is per-notebook and never part of `make check`.
guarded:
	uv run python scripts/check_guarded.py $(F)
