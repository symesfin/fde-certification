# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "deepagents>=0.7.6",
#     "langgraph>=1.2",
#     "langchain-openai>=1.5",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Loop Engineering")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 14: Loop Engineering with Deep Agents

    ## 👋 Introduction

    This session is about memory around **your own workflow**: the harness
    you use to get work done with an agent.

    Two ideas drive it, and they turn out to be the same idea:

    - **The spec is the artifact that lasts.** The code is generated from it.
      If the spec is right and the checker is right, you can regenerate the
      code at any time.
    - **A long agent run gets worse as it goes.** Context degrades
      and mistakes compound. By turn forty you can be debugging the agent's
      confusion instead of the problem. So restart from the spec.

    A **Ralph loop** puts both ideas to work. Run a fresh agent against the
    spec, check the result, write down what was learned, and restart. It has
    a budget, carries no conversation from one attempt to the next, and says
    why it stopped. **Loop engineering** is designing everything around the
    agent that makes this work. By the end of this session you will have
    built it around a **LangChain Deep Agent**:

    - a fresh `create_deep_agent(...)` every iteration
    - its files in a LangGraph store
    - its notes in an `AGENTS.md` it reads before it starts

    **You will be able to:**

    - write a spec whose acceptance criteria a machine can check
    - write a checker, then attack it with the laziest code that passes
    - run a loop with three exits — passed, budget exhausted, no progress —
      and test it with scripted agents before spending a model call
    - make a deep agent one iteration of that loop, and read its notes from
      a file the harness writes
    - keep the notes between runs, keyed to the spec, and count whether the
      second run is cheaper

    **Key concepts you will see in code:** `create_deep_agent`, `memory=`,
    `StoreBackend`, `FilesystemPermission`, a `thread_id` per iteration, and
    `recursion_limit` as a budget.

    **Where you end up:** a framework gives you the agent, its files and its
    memory in one call. It does not give you the stop condition. **The
    checker is the most important thing you write**, because a loop will
    produce whatever it accepts, faster and with more confidence than you
    would.

    ## 💼 Business Case Study

    Ryan is a platform engineer at a freight and logistics company. He runs
    the internal ops assistant that warehouse leads, finance and the service
    desk all use. The service desk forwards tickets to it as raw text, like
    `TKT-4471: VPN is down, urgent`. Before the assistant can route anything,
    it needs each ticket as a record: an id, a summary, an urgency.

    That function is small. It is the kind of work he would hand an agent
    and not want to watch. So his question is **what has to be true for him
    to walk away while the agent writes it?** The answer is three things he
    writes himself: a spec, a checker, and a loop that stops and says why.
    Three facts shape the build:

    | The fact | What it means for the build |
    | --- | --- |
    | Urgency decides which queue a ticket lands in | The checker asserts the *right* urgency, not *an* urgency |
    | Nobody is watching the run | The loop needs a budget and a no-progress exit, and has to say why it stopped |
    | The same kind of function gets written again next month | What a run learned is kept, keyed to the spec, and the saving is counted |

    ## 📜 Table of Contents

    - 🏗️ By the End of the Sesh
    - ✅ Task 1: A spec is three things
    - ✅ Task 2: The checker, and attacking it
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #4
    - ✅ Task 3: The loop, with its notes in a file
    - ✅ Task 4: A fresh deep agent every iteration
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #5
    - ✅ Task 5: The notes are procedural memory
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #6
    - 🏭 What we Built vs. What's in Production
    - 👋 Conclusion
    - 📖 Official Documentation

    > 📓 **Not covered here:** the loop as plain Python with no framework.
    > The same loop can be written by hand, with the notes as a Python list
    > and a model called directly; the spec, the checker and the cheat would
    > be identical.

    ---
    ## 🧑‍💻 Setup

    Set `LLM_MODEL` in `.env` to any chat model that can call tools. A deep
    agent writes its answer to a file with a tool call. Tasks 1 to 3 make no
    model calls. A small model that runs on a laptop:

    ```bash
    unsloth run --model unsloth/Qwen3-4B-GGUF:Q4_K_M -p 8893
    ```
    """)
    return


@app.cell
def _(mo):
    import hashlib
    from contextlib import suppress
    import os
    import sys
    import time
    import uuid
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    print(f"✅ {CFG.root.name}   model: {CFG}")
    return CFG, hashlib, os, suppress, time, ui, uuid


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell holds what every task shares: the model, and the two
    pieces of Deep Agents the loop is built on.

    - **`StoreBackend`** is where a deep agent's files live. Deep agents work
      in a virtual filesystem (`write_file`, `read_file`, `edit_file` and
      friends), and the backend decides what is underneath it. This one is a
      LangGraph store, so the files outlive any one run of the agent. The
      notes need exactly that. The store's `namespace` is the drawer the
      files go in, and here it is **the hash of the spec**. Change the spec
      and the loop starts in an empty drawer, so notes about an old spec are
      never read against a new one.
    - **`NOTES`** is the path of the notes file, `/AGENTS.md`. The name is
      deliberate. It is the same convention as the `CLAUDE.md` or
      `AGENTS.md` your coding agent reads before every session, and Task 4
      hands it to the deep agent the same way.

    **The model is LangChain's `ChatOpenAI`**, reading `LLM_MODEL` from your
    `.env`. `CFG.without_server_tools(...)` asks a local server not to add
    its own tools to a request. A deep agent always sends its own tools, so
    here the line does nothing. It stays so every model call is built the
    same way.
    """)
    return


@app.cell
def _(CFG, hashlib, os):
    from deepagents import FilesystemPermission, create_deep_agent
    from deepagents.backends import StoreBackend
    from langchain_openai import ChatOpenAI
    from langgraph.errors import GraphRecursionError
    from langgraph.store.memory import InMemoryStore

    llm_kwargs = CFG.without_server_tools(CFG.kwargs())
    MODEL = ChatOpenAI(
        model=llm_kwargs["model"].removeprefix("openai/"),
        base_url=llm_kwargs.get("api_base"),
        api_key=CFG.api_key or os.environ.get("OPENAI_API_KEY", "not-needed"),
        default_headers=llm_kwargs.get("extra_headers"),
        extra_body=llm_kwargs.get("extra_body"),
        temperature=0, timeout=600, max_retries=2,
    )
    NOTES = "/AGENTS.md"
    # Small models paste code into their reply unless told plainly to use the tool.
    CODER_PROMPT = ("You write Python to a spec. Save the implementation to /solution.py by calling "
                    "the write_file tool. Do not paste the code in your reply. Then stop.")

    def notes_drawer(store, spec: str):
        """A deep-agents filesystem in the store, keyed by the spec it is about."""
        spec_key = hashlib.sha256(spec.encode()).hexdigest()[:12]
        return StoreBackend(namespace=lambda runtime: ("loop-notes", spec_key), store=store)

    def read_notes(backend) -> list[str]:
        """The notes file, one note per `- ` line. No file means no notes yet."""
        found = backend.download_files([NOTES])[0]
        text = found.content.decode() if found.content else ""
        return [line[2:] for line in text.splitlines() if line.startswith("- ")]

    def write_notes(backend, notes: list[str]) -> None:
        body = "\n".join(f"- {note}" for note in notes)
        backend.write(NOTES, "# What previous attempts at this spec got wrong\n\n" + body + "\n")

    return (
        CODER_PROMPT,
        FilesystemPermission,
        GraphRecursionError,
        InMemoryStore,
        MODEL,
        NOTES,
        create_deep_agent,
        notes_drawer,
        read_notes,
        write_notes,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ By the End of the Sesh

    This is the whole job:

    - a fresh deep agent for every iteration, which reads the notes file
      before it starts and writes its code to a file
    - a checker you wrote, deciding whether to stop
    - a note appended for every failure

    Each task below unrolls one part of it.
    """)
    return


@app.cell
def _(CFG, mo):
    sesh_button = mo.ui.run_button(label=f"Run the loop with a deep agent on {CFG.llm_model} (up to 5 iterations)")
    sesh_button
    return (sesh_button,)


@app.cell
def _(
    CODER_PROMPT,
    FilesystemPermission,
    GraphRecursionError,
    InMemoryStore,
    MODEL,
    NOTES,
    SPEC,
    create_deep_agent,
    mo,
    notes_drawer,
    read_notes,
    sesh_button,
    suppress,
    ui,
    uuid,
    write_notes,
):
    mo.stop(not sesh_button.value, mo.md("*Click above to run it.*"))

    sesh_files = notes_drawer(InMemoryStore(), SPEC)
    sesh_history = []
    for sesh_iteration in range(1, 6):
        sesh_agent = create_deep_agent(              # fresh every iteration
            model=MODEL, backend=sesh_files, memory=[NOTES],
            system_prompt=CODER_PROMPT,
            permissions=[FilesystemPermission(operations=["write"], paths=[NOTES], mode="deny")],
        )
        sesh_files.delete("/solution.py")
        with mo.status.spinner(title=f"Iteration {sesh_iteration}…"), suppress(GraphRecursionError):
            sesh_agent.invoke({"messages": [("user", SPEC)]},
                              {"configurable": {"thread_id": str(uuid.uuid4())}, "recursion_limit": 12})
        sesh_file = sesh_files.download_files(["/solution.py"])[0]
        sesh_code = sesh_file.content.decode() if sesh_file.content else ''
        sesh_namespace = {}
        try:
            exec(compile(sesh_code, "<solution>", "exec"), sesh_namespace)
            sesh_result = check_strict(sesh_namespace)
        except Exception as sesh_error:
            sesh_result = {"passed": False, "failures": [f"did not run: {sesh_error}"]}
        sesh_history.append({"iteration": sesh_iteration, "failures": len(sesh_result["failures"])})
        if sesh_result["passed"]:
            break
        sesh_notes = read_notes(sesh_files) + ["; ".join(sesh_result["failures"][:3])]
        write_notes(sesh_files, sesh_notes)
        if len(sesh_notes) >= 2 and sesh_notes[-1] == sesh_notes[-2]:
            break                                    # no progress: stop and tell a human

    mo.vstack([ui.table(sesh_history, title="✅ passed" if sesh_result["passed"] else "🛑 stopped"),
               mo.md(f"```python\n{sesh_code}\n```")])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 1: A spec is three things

    A spec for a loop needs three things, and a spec missing any of them
    cannot drive one:

    1. **The goal**, in a sentence.
    2. **Acceptance criteria** a machine can check.
    3. **Constraints:** what must not change.

    The second is the one to get right. "The output should be good" is
    not checkable. The loop cannot tell when it is done, so you end up
    sitting and watching it.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S14_Loop_Engineering_task1")
    return


@app.cell
def _():
    from textwrap import dedent

    SPEC = dedent("""
        # Goal
        A function `normalise_ticket(raw: str) -> dict` that turns a raw support
        ticket into a structured record.

        # Acceptance criteria
        - Returns a dict with exactly the keys: id, summary, urgency
        - `id` matches the pattern TKT-<digits>, or is None if absent
        - `urgency` is one of: low, normal, high
        - Never raises. Malformed input returns urgency='normal' and summary=''

        # Constraints
        - Standard library only
        - No network calls
        - Under 30 lines
    """).strip()

    print(SPEC)
    return (SPEC,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Every acceptance criterion there can be run as code.

    ---
    ## ✅ Task 2: The checker, and attacking it

    The checker is the loop's stop condition, so it is the most important
    thing you write. It has to be **strict**. A lenient checker ends the loop
    early with something that does not work.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S14_Loop_Engineering_task2")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here is a reasonable first attempt. Read it before you scroll: it runs
    four cases from the spec and asserts the shape of what comes back.
    """)
    return


@app.function
def check(module_namespace: dict) -> dict:
    """Run the acceptance criteria. Returns {passed, failures}."""
    failures = []
    fn = module_namespace.get("normalise_ticket")

    if not callable(fn):
        return {"passed": False, "failures": ["normalise_ticket is not defined"]}

    cases = [
        ("TKT-4471: VPN is down, urgent", {"id": "TKT-4471", "urgency": "high"}),
        ("printer jam, whenever you get a chance", {"id": None, "urgency": "low"}),
        ("TKT-12: need this today", {"id": "TKT-12", "urgency": "normal"}),
        ("", {"id": None, "urgency": "normal"}),
    ]

    for raw, expect in cases:
        try:
            got = fn(raw)
        except Exception as exc:
            failures.append(f"raised on {raw!r}: {type(exc).__name__}")
            continue
        if not isinstance(got, dict):
            failures.append(f"returned {type(got).__name__}, not dict, for {raw!r}")
            continue
        if set(got) != {"id", "summary", "urgency"}:
            failures.append(f"keys were {sorted(got)} for {raw!r}")
        if got.get("id") != expect["id"]:
            failures.append(f"id was {got.get('id')!r}, expected {expect['id']!r}")
        if got.get("urgency") not in {"low", "normal", "high"}:
            failures.append(f"urgency {got.get('urgency')!r} not in the allowed set")

    return {"passed": not failures, "failures": failures}


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    That checker looks strict. Before trusting it with the loop's stop
    button, do what a second model would do if you asked it to *pass the
    checker without solving the problem*.

    Here is an implementation that ignores the ticket text entirely. It has
    no urgency logic and no summary. It returns a constant for both.
    """)
    return


@app.cell
def _(ui):
    CHEAT = """
    import re
    def normalise_ticket(raw):
        raw = raw or ''
        m = re.search(r'TKT-\\d+', raw)
        return {'id': m.group() if m else None, 'summary': '', 'urgency': 'normal'}
    """

    cheat_namespace = {}
    exec(compile(CHEAT, "<cheat>", "exec"), cheat_namespace)
    cheat_verdict = check(cheat_namespace)

    ui.table(
        [{"input": raw_ticket or "(empty)", "what it returns": str(cheat_namespace["normalise_ticket"](raw_ticket))[:64]}
         for raw_ticket in ["TKT-4471: VPN is down, urgent",
                            "printer jam, whenever you get a chance"]],
        title=f"The cheat — checker says passed={cheat_verdict['passed']}, "
              f"{len(cheat_verdict['failures'])} failures",
    )
    return (CHEAT,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **It passes.** A function that never looks at the text satisfies every
    criterion the checker actually tests. The loop would have stopped on
    iteration one and handed you this.

    The checker has two holes:

    | Criterion | What the checker asserts | What it should assert |
    | --- | --- | --- |
    | `urgency` | that it is *one of* low/normal/high | that it is **the right one** for this input |
    | `summary` | nothing at all | that it reflects the input |

    Checking membership instead of value is an easy way for a checker to go
    lenient, because it looks like a real assertion. `urgency in {...}`
    reads as validation and tests almost nothing. Every constant passes it.

    The fix is to compare against the expected value:
    """)
    return


@app.function
def check_strict(module_namespace: dict) -> dict:
    """The same cases, asserting the values rather than the shape."""
    failures = []
    fn = module_namespace.get("normalise_ticket")

    if not callable(fn):
        return {"passed": False, "failures": ["normalise_ticket is not defined"]}

    cases = [
        ("TKT-4471: VPN is down, urgent", {"id": "TKT-4471", "urgency": "high"}),
        ("printer jam, whenever you get a chance", {"id": None, "urgency": "low"}),
        ("TKT-12: need this today", {"id": "TKT-12", "urgency": "normal"}),
        ("", {"id": None, "urgency": "normal"}),
    ]

    for raw, expect in cases:
        try:
            got = fn(raw)
        except Exception as exc:
            failures.append(f"raised on {raw!r}: {type(exc).__name__}")
            continue
        if not isinstance(got, dict):
            failures.append(f"returned {type(got).__name__}, not dict, for {raw!r}")
            continue
        if set(got) != {"id", "summary", "urgency"}:
            failures.append(f"keys were {sorted(got)} for {raw!r}")
            continue
        if got.get("id") != expect["id"]:
            failures.append(f"id was {got.get('id')!r}, expected {expect['id']!r}")
        # The value, not the membership.
        if got.get("urgency") != expect["urgency"]:
            failures.append(
                f"urgency was {got.get('urgency')!r}, expected {expect['urgency']!r} "
                f"for {raw!r}"
            )
        # And summary has to come from somewhere.
        if raw and not got.get("summary"):
            failures.append(f"summary was empty for non-empty input {raw!r}")

    return {"passed": not failures, "failures": failures}


@app.cell
def _():
    ATTEMPTS = [
        # 1: wrong keys
        "def normalise_ticket(raw):\n    return {'id': None, 'text': raw}",
        # 2: right keys, crashes on empty input
        "import re\n"
        "def normalise_ticket(raw):\n"
        "    tid = re.search(r'TKT-\\d+', raw).group()\n"
        "    return {'id': tid, 'summary': raw[:40], 'urgency': 'normal'}",
        # 3: correct
        "import re\n"
        "def normalise_ticket(raw):\n"
        "    raw = raw or ''\n"
        "    m = re.search(r'TKT-\\d+', raw)\n"
        "    low = raw.lower()\n"
        "    if 'urgent' in low or 'asap' in low:\n"
        "        urg = 'high'\n"
        "    elif 'whenever' in low or 'no rush' in low:\n"
        "        urg = 'low'\n"
        "    else:\n"
        "        urg = 'normal'\n"
        "    return {'id': m.group() if m else None, 'summary': raw[:40], 'urgency': urg}",
    ]
    return (ATTEMPTS,)


@app.cell
def _(ATTEMPTS, CHEAT, ui):
    def run_both_checkers(code):
        candidate_namespace = {}
        try:
            exec(compile(code, "<candidate>", "exec"), candidate_namespace)
        except Exception as exc:
            return {"passed": False, "failures": [str(exc)]}, {"passed": False, "failures": [str(exc)]}
        return check(candidate_namespace), check_strict(candidate_namespace)

    ui.table(
        [{"implementation": name,
          "lenient `check`": "✅ passed" if lenient_result["passed"] else f"🛑 {len(lenient_result['failures'])} failures",
          "`check_strict`": "✅ passed" if strict_result["passed"] else f"🛑 {len(strict_result['failures'])} failures"}
         for name, (lenient_result, strict_result) in [
             ("the cheat (ignores the text)", run_both_checkers(CHEAT)),
             ("a real implementation", run_both_checkers(ATTEMPTS[2])),
         ]],
        title="Same two implementations, two checkers",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cheat now fails and the real implementation still passes! You need
    both results. The second one shows the hardening did not just make the
    checker stricter about the wrong thing.

    > **Spend your time here.** The loop cannot be better than its stop
    > condition. Budgets, notes and no-progress detection are all machinery
    > around one boolean. If that boolean is wrong, the machinery delivers
    > broken code faster.

    Do this to your own checkers: write the laziest thing that could pass.
    If it does pass, you have found a missing acceptance criterion.

    > **🏢 In the enterprise:** Deep Agents ships a `RubricMiddleware` that
    > runs a *grader model* against a rubric and loops until the grader is
    > satisfied. That is a stop condition too, a model judging a model.
    > Whenever the criterion could have been code, it is the lenient checker
    > with extra steps. Use a grader where the acceptance criterion needs
    > judgement (tone, a summary's faithfulness). Use code everywhere a value
    > can be compared. The choice decides what your team can defend when the
    > loop ships something wrong.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #4

    Take one check from your own eval harness or test suite and write the
    laziest implementation that would pass it: a constant, an echo of the
    input, an empty string. Does it pass? If it does, which assertion checks
    membership or shape where it should check the value, and what would the
    value check be?

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 3: The loop, with its notes in a file

    A fresh agent runs every iteration. It gets the spec and the
    **accumulated notes** from previous failures. It does not get the
    previous conversation.

    The whole design rests on that. Notes are small, curated, and true. A
    conversation is long and full of dead ends, and by turn thirty the agent
    is mostly reading its own mistakes.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S14_Loop_Engineering_task3")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The notes live in `/AGENTS.md`, in the store, so they outlive the run.
    Task 5 needs that. The checker and the agent are **parameters**. Any
    callable that takes a spec and the notes and returns code will do. That
    lets the next cells test the loop with scripted agents before a model is
    involved.
    """)
    return


@app.cell
def _(read_notes, write_notes):
    def ralph_loop(spec: str, attempt_fn, notes_file, max_iterations: int = 5, checker=None) -> dict:
        """Run until the checker passes, the budget runs out, or progress stops.

        `attempt_fn(spec, notes) -> code` is any callable. `notes_file` is a
        deep-agents backend; whatever notes are already in it seed the run.
        """
        checker = checker or check_strict
        seeded = len(read_notes(notes_file))     # notes we arrived with, not ones we learned here
        history = []

        for iteration in range(1, max_iterations + 1):
            code = attempt_fn(spec, read_notes(notes_file))
            namespace = {}
            try:
                exec(compile(code, f"<attempt-{iteration}>", "exec"), namespace)
                result = checker(namespace)
            except Exception as exc:
                result = {"passed": False, "failures": [f"did not compile: {exc}"]}
            history.append({"iteration": iteration, "failures": len(result["failures"]),
                            "first failure": (result["failures"] or ["—"])[0][:60]})

            if result["passed"]:
                return {"ok": True, "iterations": iteration, "code": code, "history": history}

            # The note is the memory: what the checker saw, short and specific.
            notes = read_notes(notes_file) + ["; ".join(result["failures"][:3])]
            write_notes(notes_file, notes)

            # Two identical failures in this run: the loop is stuck. Stop and say so.
            learned_here = notes[seeded:]
            if len(learned_here) >= 2 and learned_here[-1] == learned_here[-2]:
                return {"ok": False, "iterations": iteration, "code": code, "history": history,
                        "why": "no progress between attempts"}

        return {"ok": False, "iterations": max_iterations, "code": code, "history": history,
                "why": "budget exhausted"}

    return (ralph_loop,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The loop has two ways to stop besides success:

    - **Budget exhausted.** Loops without a cap are how people wake up to a
      very large bill.
    - **No progress.** Two identical failures mean the agent cannot see the
      problem, and a third attempt will not help. Stop and tell a human.

    > A loop with no way to fail can run forever. Make it say *why* it
    > stopped.

    Before spending model calls, check the loop works, the same way you would
    test an eval harness before trusting it. We use three scripted agents,
    each in a fresh store:

    - one that gets less wrong each time
    - one that never improves
    - one that writes the cheat first, run against both checkers
    """)
    return


@app.cell
def _(ATTEMPTS, CHEAT, InMemoryStore, SPEC, notes_drawer, ralph_loop, ui):
    def scripted_agent(spec, notes):
        """Returns progressively better attempts. Deterministic, no model."""
        return ATTEMPTS[min(len(notes), len(ATTEMPTS) - 1)]

    def stuck_agent(spec, notes):
        """Never improves. The loop should notice and stop early."""
        return "def normalise_ticket(raw):\n    return {'id': None, 'text': raw}"

    def lazy_agent(spec, notes):
        """Writes the cheat first, and only tries properly if told it failed."""
        return CHEAT if not notes else ATTEMPTS[2]

    SCRIPTED_RUNS = {
        "scripted, strict checker": ralph_loop(SPEC, scripted_agent, notes_drawer(InMemoryStore(), SPEC)),
        "stuck, budget of 10": ralph_loop(SPEC, stuck_agent, notes_drawer(InMemoryStore(), SPEC), max_iterations=10),
        "lazy, lenient `check`": ralph_loop(SPEC, lazy_agent, notes_drawer(InMemoryStore(), SPEC), checker=check),
        "lazy, `check_strict`": ralph_loop(SPEC, lazy_agent, notes_drawer(InMemoryStore(), SPEC)),
    }
    ui.table(
        [{"run": name, "outcome": "✅ passed" if run["ok"] else f"🛑 {run['why']}", "iterations": run["iterations"],
          "shipped": "nothing" if not run["ok"] else ("the cheat" if run["code"] == CHEAT else "a real implementation")}
         for name, run in SCRIPTED_RUNS.items()],
        title="The loop, tested without a model",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the rows in order.

    - The scripted agent passed on its third iteration: the notes went into
      the file, came back out, and changed what the agent did.
    - The stuck agent had ten iterations of budget and stopped after two.
      The no-progress detector did its job. That is what lets you leave a
      loop running without babysitting it.
    - **The lazy agent against the lenient checker succeeded in one
      iteration and shipped the cheat.** Nothing errored, the history is
      clean, and the loop reported success. Against `check_strict` the same
      agent was told it failed, and its second attempt was real.

    This is why the checker is the most important thing you write. A loop
    amplifies its stop condition. It will produce whatever the checker
    accepts, faster and with more confidence than you would.

    ---
    ## ✅ Task 4: A fresh deep agent every iteration

    Now the agent is real. `create_deep_agent` is one call that returns an
    agent loop with a planning tool, a virtual filesystem and subagents
    already wired in. Three of its arguments do the work here:

    - **`backend=`** is the notes drawer from Setup. The agent's
      `write_file('/solution.py', ...)` lands in the store, where the
      harness reads it back.
    - **`memory=[NOTES]`** loads `/AGENTS.md` into the agent's system prompt
      before it starts, the same move your coding agent makes with
      `CLAUDE.md`. The *framework* reads the file. The loop never pastes the
      notes into the prompt itself.
    - **`permissions=`** denies writes to the notes file. Deep Agents' memory
      prompt encourages the agent to edit its own memory as it learns. Here
      the notes are what *the checker* observed, so only the harness writes
      them. It is the rule for any episodic record: write down what happened,
      not the model's account of it.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S14_Loop_Engineering_task4")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One line of `CODER_PROMPT` is there because it was measured. With
    *"Write only the Python code to /solution.py with write_file"*, the small
    model above pasted the code into its reply instead of calling the tool.
    It did that on all five tries measured, thinking on and off.
    `/solution.py` stayed empty, and the loop stopped on *no progress* after
    two iterations. With *call the write_file tool, do not paste the code*,
    it wrote the file in every one of the 34 iterations measured since. The
    checker caught the empty file either way.

    A new agent and a new `thread_id` every iteration is what makes it
    *fresh*. No message from the last attempt is in its context, only the
    spec and the file. `recursion_limit=12` is the per-iteration budget,
    about five tool rounds. It stops one confused iteration from eating the
    run.
    """)
    return


@app.cell
def _(
    CODER_PROMPT,
    FilesystemPermission,
    GraphRecursionError,
    MODEL,
    NOTES,
    create_deep_agent,
    mo,
    time,
    uuid,
):
    def deep_agent_attempt(files, usage: list):
        """An attempt_fn for ralph_loop: a fresh deep agent, its answer read from a file."""
        def attempt(spec: str, notes: list) -> str:
            agent = create_deep_agent(
                model=MODEL, backend=files, memory=[NOTES],
                system_prompt=CODER_PROMPT,
                permissions=[FilesystemPermission(operations=["write"], paths=[NOTES], mode="deny")],
            )
            files.delete("/solution.py")                # never re-check last iteration's file
            started, seen = time.perf_counter(), []
            with mo.status.spinner(title=f"Iteration {len(usage) + 1}: a fresh deep agent, {len(notes)} note(s) loaded…"):
                try:                                    # stream, so the trace survives a budget stop
                    for update in agent.stream({"messages": [("user", spec)]}, stream_mode="updates",
                                               config={"configurable": {"thread_id": str(uuid.uuid4())}, "recursion_limit": 12}):
                        for node_update in update.values():
                            new_messages = node_update.get("messages") if isinstance(node_update, dict) else None
                            seen.extend(new_messages if isinstance(new_messages, list) else [])
                    stopped = "answered"
                except GraphRecursionError:              # out of steps: the checker sees whatever was written
                    stopped = "recursion_limit"
            usage.append({
                "tools called": " → ".join(call["name"] for message in seen for call in getattr(message, "tool_calls", None) or []),
                "input tokens": sum((getattr(message, "usage_metadata", None) or {}).get("input_tokens", 0) for message in seen),
                "seconds": round(time.perf_counter() - started, 1), "stopped": stopped,
            })
            written = files.download_files(["/solution.py"])[0]
            return written.content.decode() if written.content else ""
        return attempt

    return (deep_agent_attempt,)


@app.cell
def _(CFG, mo):
    live_button = mo.ui.run_button(label=f"▶️  Run the loop with a deep agent on {CFG.llm_model} (up to 5 iterations)")
    live_button
    return (live_button,)


@app.cell
def _(
    InMemoryStore,
    SPEC,
    deep_agent_attempt,
    live_button,
    mo,
    notes_drawer,
    ralph_loop,
    ui,
):
    mo.stop(not live_button.value, mo.md("*Click above to run it for real.*"))

    NOTES_STORE = InMemoryStore()                  # Task 5 runs again from this same store
    cold_usage = []
    COLD_RUN = ralph_loop(SPEC, deep_agent_attempt(notes_drawer(NOTES_STORE, SPEC), cold_usage), notes_drawer(NOTES_STORE, SPEC))

    mo.vstack([
        ui.table([{**step, **spent} for step, spent in zip(COLD_RUN["history"], cold_usage)],
                 title=f"{'✅ passed' if COLD_RUN['ok'] else '🛑 ' + COLD_RUN.get('why', '')} "
                       f"after {COLD_RUN['iterations']} iteration(s)"),
        mo.md(f"```python\n{COLD_RUN['code']}\n```"),
    ])
    return COLD_RUN, NOTES_STORE, cold_usage


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the `input tokens` column before the code. Every model call starts
    at about 3,700 tokens before the spec is read. That is the deep agent's
    own system prompt plus the schemas of the tools it hands the model
    (planning, files, subagents), whether this task needs them or not. It is
    the price of the framework per call, and a loop pays it every iteration.

    Then read `tools called`. Sometimes the agent writes the file and stops.
    Sometimes, having written it, it calls `task`. That hands "verify the
    function" to the general-purpose **subagent Deep Agents adds by
    default**. The subagent cannot run code either. It asks back for
    clarification, is asked again, and so on, until `recursion_limit` stops
    the iteration. The file was already written, so the checker still gets
    its turn. The budget kept a confused iteration from becoming a confused
    hour. Nobody asked for that subagent. It came with the call.

    ### What the small model did

    Measured with the 4B model above (thinking off, for speed), six runs of
    this loop: **none passed.** Every run stopped on its own after 2 to 5
    iterations, five on *no progress* and one on the budget. Each one said
    which acceptance criterion it was stuck on. Mostly the model never
    connected *urgent* in the ticket to `high`, or *whenever* to `low`.
    The loop refused to ship something that does not meet the spec, and it
    told you why. That is the behaviour you want on the day nobody is
    watching.

    ### What a hosted model did

    Measured once with `gpt-4.1-mini`: **passed after 3 iterations**, 5 → 2
    → 0 failures. Every iteration called `write_file` once and stopped on
    `answered`; no subagent, no recursion limit. Each note fixed the thing it
    named: iteration 2 had learned *urgent → high* and still missed
    *whenever → low*; iteration 3 had both. Roughly 6,300 input tokens a
    call, so the whole loop cost under a cent. This is the loop working as
    designed: not one-shot, not stuck, each attempt cheaper to understand
    than a forty-turn conversation would be.

    ### If it passed on iteration one

    It may, with a stronger model. A strong model may one-shot a spec this
    small, because the *task* is too easy to need a loop. The loop earns its
    place when the spec is big enough that one attempt reliably misses
    something. To decide whether you need one, ask: **would you have run
    this by hand more than three times?**

    If the answer is no, write the spec, run it once, and move on. The spec
    was still worth writing.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #5

    Your loop's stop condition is code you wrote. For one piece of your own
    work: what is the checker, what is the iteration budget, and what does
    one iteration cost in tokens and seconds? Then say whether you would
    trust a grader model as the stop condition instead — and for which
    criterion it would be the right call.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 5: The notes are procedural memory

    The notes accumulate *within* a run. If you throw them away at the end,
    the next similar task rediscovers the same mistakes and pays for them
    again.

    Procedural memory fills exactly that gap: **a learned how-to, kept, so
    the second attempt is cheaper than the first.** The notes already are
    that. They are a file in a store, keyed by the spec, so they outlive the
    run. The second run is the same call, against the same store, and we
    count it.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S14_Loop_Engineering_task5")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    First, with no model, the property that makes keeping notes safe. The
    drawer is the hash of the spec, so notes written under one spec are
    invisible under any other. Then the warm run, which reads the store
    Task 4 filled. Press Task 4's button first.
    """)
    return


@app.cell
def _(InMemoryStore, SPEC, notes_drawer, read_notes, ui, write_notes):
    drawer_store = InMemoryStore()
    write_notes(notes_drawer(drawer_store, SPEC), ["urgency was 'normal', expected 'high'"])
    ui.table(
        [{"read with": "the same SPEC", "notes found": len(read_notes(notes_drawer(drawer_store, SPEC)))},
         {"read with": "SPEC plus one space", "notes found": len(read_notes(notes_drawer(drawer_store, SPEC + " ")))}],
        title="One store, one note, two specs: change the spec and the drawer is empty",
    )
    return


@app.cell
def _(CFG, mo):
    warm_button = mo.ui.run_button(label=f"▶️  Run it again from the same store with {CFG.llm_model} (press Task 4's button first)")
    warm_button
    return (warm_button,)


@app.cell
def _(
    COLD_RUN,
    NOTES_STORE,
    SPEC,
    cold_usage,
    deep_agent_attempt,
    mo,
    notes_drawer,
    ralph_loop,
    read_notes,
    ui,
    warm_button,
):
    mo.stop(not warm_button.value, mo.md("*Click above to run it.*"))

    learned_notes = read_notes(notes_drawer(NOTES_STORE, SPEC))
    warm_usage = []
    WARM_RUN = ralph_loop(SPEC, deep_agent_attempt(notes_drawer(NOTES_STORE, SPEC), warm_usage), notes_drawer(NOTES_STORE, SPEC))

    mo.vstack([
        ui.table(
            [{"run": "1 — cold", "seeded with": "nothing", "iterations": COLD_RUN["iterations"],
              "passed": "✅" if COLD_RUN["ok"] else "🛑", "input tokens": sum(step["input tokens"] for step in cold_usage)},
             {"run": "2 — warm", "seeded with": f"{len(learned_notes)} note(s) from run 1", "iterations": WARM_RUN["iterations"],
              "passed": "✅" if WARM_RUN["ok"] else "🛑", "input tokens": sum(step["input tokens"] for step in warm_usage)}],
            title="Same spec, same store, counted on a model",
        ),
        mo.md("**What run 1 wrote down, and run 2 started from:**\n\n"
              + ("\n".join(f"- `{note[:96]}`" for note in learned_notes) or "*nothing — run 1 passed first time*")),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Expect this to be messier than the scripted agent in Task 3, which
    improved *by construction* as notes accumulated. A real model sometimes
    ignores a note, sometimes re-derives what it was told, and occasionally
    does worse with context than without. Every iteration saved is a model
    call not made. But you have to count them on a model, and one run of
    either configuration is a sample of one.

    On the 4B model we ran three cold-then-warm pairs. In two of the three,
    the warm run **started further along**. Its first failure was the one
    the cold run reached last (*low* urgency, after *high* was fixed). None
    of the warm runs passed. Cold runs took 2, 2 and 5 iterations, warm runs
    5, 4 and 2. So on a weak model, memory had a real effect on where the
    loop started, no effect on whether it finished, and the sample is far
    too small to claim a saving.

    On `gpt-4.1-mini`, one pair: cold passed in 3 iterations for 19,223
    input tokens; warm, seeded with the cold run's two notes, passed in **1
    iteration for 6,592**. The first attempt already handled *urgent* and
    *whenever*, because the notes said so. That is the saving S13 Task 3
    counted, measured on a model: a third of the calls, a third of the
    tokens. Still a sample of one. Run it twice more before you put it on
    Ryan's page.

    > Keep the scripted demo and the live run apart in your head. A demo
    > that improves because you wrote it to improve is easy to build and easy
    > to believe. Ask of anything a vendor shows you: *what in this system
    > would have to be true for the number to come out differently?* If
    > nothing could, you are looking at an illustration.

    Two cautions from procedural memory apply here too.

    **A note that was true once can stop being true.** A procedure retrieved
    instead of thought about is worse than no procedure, because it is
    applied confidently. When the spec changes, the notes from the old spec
    are misinformation. That is why the drawer is the hash of the spec. The
    table above shows the rule working: add one space to the spec, and the
    note is gone.

    **Notes grow.** Seeding run fifty with forty-nine runs of accumulated
    failures reproduces the long-context problem the loop existed to avoid.
    Keep the notes that describe *the shape of the mistake*, drop the ones
    about a specific attempt, and cap the list.

    ### Where this actually applies

    Ralph loops need a **machine-checkable acceptance criterion**, and not
    all work has one.

    | Good fit | Poor fit |
    | --- | --- |
    | Code with tests | Prose, design, judgement calls |
    | Data transforms with a schema | "Make this better" |
    | Migrations with a verifier | Anything needing taste |
    | Anything you would otherwise do 40 times | One-off exploration |

    If you keep a `CLAUDE.md` or an `AGENTS.md`, you have been doing
    spec-driven development already. **That file is a spec:** a written
    statement of how work should be done, which a fresh agent reads before
    every session. When the agent gets the same thing wrong twice, you fix
    the file, not the prompt. That is the note-taking step of this loop, done
    by hand. This session automated it and put a bound on it.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #6

    Pick one piece of work you would hand a loop. Write its spec's
    acceptance criteria. If you cannot, that is the finding: the task is not
    loop-shaped. Then: which notes from a run would you keep, what
    should the drawer be keyed by, and what change should expire them?

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ By the End of the Sesh

    The code you saw at the start, now that every line of it has been
    unrolled (`SPEC`, `check_strict` and the notes helpers are in the cells
    above it):

    ```python
    mo.stop(not sesh_button.value, mo.md("*Click above to run it.*"))

    sesh_files = notes_drawer(InMemoryStore(), SPEC)
    sesh_history = []
    for sesh_iteration in range(1, 6):
        sesh_agent = create_deep_agent(              # fresh every iteration
            model=MODEL, backend=sesh_files, memory=[NOTES],
            system_prompt=CODER_PROMPT,
            permissions=[FilesystemPermission(operations=["write"], paths=[NOTES], mode="deny")],
        )
        sesh_files.delete("/solution.py")
        with mo.status.spinner(title=f"Iteration {sesh_iteration}…"), suppress(GraphRecursionError):
            sesh_agent.invoke({"messages": [("user", SPEC)]},
                              {"configurable": {"thread_id": str(uuid.uuid4())}, "recursion_limit": 12})
        sesh_file = sesh_files.download_files(["/solution.py"])[0]
        sesh_code = sesh_file.content.decode() if sesh_file.content else ''
        sesh_namespace = {}
        try:
            exec(compile(sesh_code, "<solution>", "exec"), sesh_namespace)
            sesh_result = check_strict(sesh_namespace)
        except Exception as sesh_error:
            sesh_result = {"passed": False, "failures": [f"did not run: {sesh_error}"]}
        sesh_history.append({"iteration": sesh_iteration, "failures": len(sesh_result["failures"])})
        if sesh_result["passed"]:
            break
        sesh_notes = read_notes(sesh_files) + ["; ".join(sesh_result["failures"][:3])]
        write_notes(sesh_files, sesh_notes)
        if len(sesh_notes) >= 2 and sesh_notes[-1] == sesh_notes[-2]:
            break                                    # no progress: stop and tell a human

    mo.vstack([ui.table(sesh_history, title="✅ passed" if sesh_result["passed"] else "🛑 stopped"),
               mo.md(f"```python\n{sesh_code}\n```")])
    ```

    - `SPEC` is Task 1: a goal, criteria a machine can check, constraints.
    - `check_strict` is Task 2, and it is the line that decides everything
      else. The lenient `check` would have stopped this loop on the cheat.
    - The `for` loop with its two `break`s is Task 3: passed, or no progress,
      or the budget of five runs out.
    - `create_deep_agent` with `memory=`, `permissions=` and a new
      `thread_id` is Task 4: a fresh agent that reads the notes and cannot
      rewrite them.
    - `notes_drawer(..., SPEC)` is Task 5: the notes are keyed by the spec,
      so a second run against the same store starts warm, and a changed spec
      starts cold.

    ---
    ## 🏭 What we Built vs. What's in Production

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Running the code | `exec` on generated code, in the notebook's process | A sandboxed worker (Deep Agents' sandbox backends, or a container), resource-limited, no network |
    | The checker | Four hand-written cases | The real test suite, plus a linter and a type checker, and an adversarial pass on every checker in CI |
    | The notes | Failure strings in `/AGENTS.md` | A structured failure log, deduplicated and ranked, capped in length |
    | The notes' home | An `InMemoryStore`, gone on restart | The same `StoreBackend` over Postgres, keyed by spec and expired with it |
    | The budget | Five iterations, `recursion_limit=12` each | Token, cost and wall-clock ceilings per run, alerted on |
    | Stopping | Two identical failures, then stop | Escalation to a human with the full history attached |
    | The spec | One string in a notebook | Specs in the repo, reviewed like code, versioned with what they produce |

    ---
    ## 👋 Conclusion

    We wrote the three things a loop cannot do without (a spec, a checker,
    and a stop condition) and let a framework supply the rest:

    - The checker came first, and we attacked it. A constant passed it, and
      the loop would have shipped that constant with a clean history.
    - We tested the loop with scripted agents before a model was involved.
    - A fresh deep agent ran every iteration. It read its notes from a file
      the way your coding agent reads `CLAUDE.md`, and could not rewrite
      them.
    - The notes outlived the run, keyed to the spec, and we counted the
      second run.

    The loop plan for Ryan's ticket function, filled in:

    - a spec in the repo
    - a checker that compares values and has been attacked
    - a budget and a no-progress exit
    - notes the harness writes from what the checker saw
    - a drawer keyed by the spec, so a changed spec starts clean

    `create_deep_agent` gave you the agent, its files and its memory in one
    call. The checker at the bottom of the loop is yours to write, and now
    you know how to attack it!

    Now build 🏗️, ship 🚢, and share 📤
    [this week's challenge](../challenge/README.md).

    ---
    ## 📖 Official Documentation

    | Tool | Used here for | Docs |
    | --- | --- | --- |
    | Deep Agents | `create_deep_agent`, what it wires in, and the agent harness it is | [docs.langchain.com — Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview) |
    | Deep Agents backends | `StoreBackend`, files in a LangGraph store that outlive a run | [docs.langchain.com — Deep Agents backends](https://docs.langchain.com/oss/python/deepagents/backends) |
    | Deep Agents memory | `memory=["/AGENTS.md"]`, a file loaded into the system prompt | [docs.langchain.com — Deep Agents memory](https://docs.langchain.com/oss/python/deepagents/memory) |
    | LangGraph store | `InMemoryStore`, namespaces, and swapping in a persistent store | [docs.langchain.com — LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory) |
    | LangChain OpenAI | `ChatOpenAI`, the model through any OpenAI-compatible endpoint | [docs.langchain.com — ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai) |
    | AGENTS.md | the convention the notes file follows | [agents.md](https://agents.md/) |
    """)
    return


if __name__ == "__main__":
    app.run()
