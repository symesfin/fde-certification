# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "langmem>=0.0.30",
#     "langgraph>=1.2",
#     "langchain-openai>=1.5",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Three Kinds of Memory")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 13: Three Kinds of Memory, with LangMem

    ## 👋 Introduction

    "Memory" is one word for three different problems.

    | Kind | Holds | Test |
    | --- | --- | --- |
    | **Semantic** | Facts | Ask for a fact from 30 turns ago |
    | **Procedural** | Learned how-to | Is the second attempt cheaper than the first? |
    | **Episodic** | What happened | Can it explain a decision it made? |

    We build them separately, because they fail in different ways and the
    fixes are unrelated. By the end of this session you will have built all
    three with **LangMem**, a memory library, on a **LangGraph store**, and
    run the test that catches each one failing. Your challenge asks for one
    kind in your own app and three tests that target it. This notebook runs
    those tests on a small world you can see all of.

    **You will be able to:**

    - put, get and search a LangGraph store, and say what its namespaces and
      keys are for
    - extract facts from a conversation with a LangMem memory manager, watch
      them go stale, and fix it with a schema that supersedes on write
    - turn a log of failed attempts into a stored procedure, and count the
      attempts it saves
    - compare an episode the model wrote about itself with the log of what
      actually happened
    - run the leakage test: two users, same question, no crossover

    **Key concepts you will see in code:** `InMemoryStore`, namespaces with
    `{langgraph_user_id}`, `create_memory_store_manager`,
    `create_memory_manager`, Pydantic schemas as memory shapes,
    `enable_inserts=False`, and `create_manage_memory_tool` /
    `create_search_memory_tool`.

    **Where you end up:** a framework will extract and store memories for you
    in a few lines. It will not tell you when they are stale, wrong, or
    somebody else's. **Memory can degrade quietly.** It piles up entries,
    goes stale, and retrieves the wrong one, and you cannot tell from using
    it. So each kind here comes with the test that catches its failure.

    ## 💼 Business Case Study

    Ryan is a platform engineer at a freight and logistics company with
    depots across Ireland and the north of England. He runs the internal ops
    assistant. Warehouse leads, finance and the service desk all ask it the
    same kinds of questions: *where is this shipment now, can I expense this,
    who should take this ticket.* Today it forgets everything between
    conversations, and people are tired of telling it which team they are on.

    His head of operations has asked for memory. Ryan has a harder job. Before
    it ships, he has to show that the assistant remembers the **right**
    things, for the **right** person, and can say **why** it did what it did.
    Four facts shape the build:

    | The fact | What it means for the build |
    | --- | --- |
    | People move teams and offices; deadlines and limits change | A stored fact goes stale. The test is *does it recall the current value* |
    | The same tasks recur — depot lookups, expense rules | A learned how-to should make the second attempt cheaper, and that is counted |
    | Routing and approval decisions get audited | Episodic records come from the tool log, not from the model's account of itself |
    | Hundreds of staff share one assistant | Memory is keyed by user, and the leakage test runs with everything else |

    ## 📜 Table of Contents

    - 🏗️ By the End of the Sesh
    - ✅ Task 1: The store, and the escalation ladder
    - ✅ Task 2: Semantic memory, and the test that catches it
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #1
    - ✅ Task 3: Procedural memory, counted
    - ✅ Task 4: Episodic memory, checked against the log
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #2
    - ✅ Task 5: What actually goes wrong, and the leakage test
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #3
    - 🏭 What we Built vs. What's in Production
    - 👋 Conclusion
    - 📖 Official Documentation

    > 📓 **Not covered here:** the storage layer underneath. The same three
    > kinds can be built by hand on SQLite full-text search, with the index
    > triggers that keep it in sync. Here the store is LangGraph's, and the
    > lesson is the tests.

    ---
    ## 🧑‍💻 Setup

    Set `LLM_MODEL` in `.env` to any chat model that can call tools. LangMem
    extracts memories by asking the model to fill in a schema through a tool
    call. Tasks 1 and 5 make no model calls at all. A small model that runs on
    a laptop:

    ```bash
    unsloth run --model unsloth/Qwen3-4B-GGUF:Q4_K_M -p 8893
    ```
    """)
    return


@app.cell
def _(mo):
    import os
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    print(f"✅ {CFG.root.name}   model: {CFG}")
    return CFG, os, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Everything the tasks share lives in the next cell: the model, and the
    three **schemas** that give each kind of memory its shape.

    **The model is LangChain's `ChatOpenAI`**, which LangMem drives. It reads
    `LLM_MODEL` from your `.env` and works with any OpenAI-compatible endpoint,
    including a local server or your firm's gateway.

    One line needs explaining: `CFG.without_server_tools(...)`. Some local
    servers (Unsloth's among them) add their own tools to any request that
    sends none, about 1,400 extra prompt tokens. This line asks them not to.
    Measured on the model above, a three-word reply cost **1,374 prompt tokens
    without it and 18 with it**. A request that passes its own tools still
    gets them. On a hosted provider the line changes nothing.

    A **schema** is a Pydantic model, and it is the most important decision in
    each task. LangMem asks the model to fill it in, so the fields are what
    gets remembered. Task 2 shows that one choice decides whether a fact can
    go stale: is the schema a *collection* of entries, or *one record per
    user*?
    """)
    return


@app.cell
def _(CFG, os):
    from langchain_openai import ChatOpenAI
    from langgraph.store.memory import InMemoryStore
    from langmem import (
        create_manage_memory_tool,
        create_memory_manager,
        create_memory_store_manager,
        create_search_memory_tool,
    )
    from pydantic import BaseModel, Field

    llm_kwargs = CFG.without_server_tools(CFG.kwargs())
    MODEL = ChatOpenAI(
        model=llm_kwargs["model"].removeprefix("openai/"),
        base_url=llm_kwargs.get("api_base"),
        api_key=CFG.api_key or os.environ.get("OPENAI_API_KEY", "not-needed"),
        default_headers=llm_kwargs.get("extra_headers"),
        extra_body=llm_kwargs.get("extra_body"),
        temperature=0, timeout=600, max_retries=2,
    )

    class UserProfile(BaseModel):
        """One live record per user. Update a field in place when it changes."""
        team: str | None = Field(None, description="The team the user works in now")
        office: str | None = Field(None, description="The office the user works from")
        answer_style: str | None = Field(None, description="How the user likes answers")

    class Procedure(BaseModel):
        """A learned how-to: the approach that worked for a task, and what to avoid."""
        task: str
        approach_that_worked: str = Field(description="The one approach that finally succeeded, in the log's own words. Not the steps tried before it.")
        avoid: list[str] = Field(default_factory=list, description="Approaches that failed, and why")

    PROCEDURE_RULE = (
        "approach_that_worked is ONLY the final approach that succeeded, as one short phrase in the log's words. "
        "Every earlier attempt goes in avoid, not in approach_that_worked."
    )

    class Episode(BaseModel):
        """One thing the agent did: what it saw, what it did, why, and the result."""
        observation: str
        action: str
        reasoning: str
        result: str

    def as_user(user_id: str) -> dict:
        """The config LangMem reads `{langgraph_user_id}` from."""
        return {"configurable": {"langgraph_user_id": user_id}}

    return (
        Episode,
        InMemoryStore,
        MODEL,
        PROCEDURE_RULE,
        Procedure,
        UserProfile,
        as_user,
        create_manage_memory_tool,
        create_memory_manager,
        create_memory_store_manager,
        create_search_memory_tool,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ By the End of the Sesh

    This is the whole job:

    - one store
    - a profile that supersedes on write (a changed fact replaces the old one)
    - a procedure learned from a log of failed attempts
    - an episode written from the tool calls that actually happened

    Each task below unrolls one part of it and adds the test that catches it
    failing.
    """)
    return


@app.cell
def _(mo):
    sesh_button = mo.ui.run_button(label="Build all three kinds of memory (2 model calls)")
    sesh_button
    return (sesh_button,)


@app.cell
def _(
    ATTEMPT_LOGS,
    InMemoryStore,
    MODEL,
    PROCEDURE_RULE,
    Procedure,
    TRAJECTORY,
    UserProfile,
    as_user,
    create_memory_manager,
    create_memory_store_manager,
    mo,
    observed_calls,
    sesh_button,
    ui,
):
    mo.stop(not sesh_button.value, mo.md("*Click above to build it.*"))

    sesh_store = InMemoryStore()

    # Semantic: one live profile per user, updated in place.
    sesh_profile = create_memory_store_manager(
        MODEL, schemas=[UserProfile], enable_inserts=False,
        namespace=("profile", "{langgraph_user_id}"), store=sesh_store,
    )
    sesh_profile.invoke({"messages": [
        {"role": "user", "content": "I'm on the Revenue Systems team. Keep answers under 100 words."},
        {"role": "assistant", "content": "Noted."},
        {"role": "user", "content": "Update: I moved to Data Platform in June."},
    ]}, config=as_user("tomas"))

    # Procedural: what worked, learned from a log of attempts, keyed by the task.
    sesh_learn = create_memory_manager(MODEL, schemas=[Procedure], enable_updates=False, instructions=PROCEDURE_RULE)
    sesh_learned = sesh_learn.invoke({"messages": [{"role": "user", "content": ATTEMPT_LOGS["find shipment depot"]}]})
    if sesh_learned:
        sesh_store.put(("procedures",), "find shipment depot", sesh_learned[0].content.model_dump())

    # Episodic: written from the tool calls that happened, not from the model.
    sesh_store.put(("episodes", "tomas"), "TKT-4471", {"calls": observed_calls(TRAJECTORY)})

    ui.table(
        [{"namespace": "/".join(sesh_item.namespace), "key": sesh_item.key, "value": str(sesh_item.value)[:110]}
         for sesh_namespace in [("profile", "tomas"), ("procedures",), ("episodes", "tomas")]
         for sesh_item in sesh_store.search(sesh_namespace)],
        title="One store, three kinds of memory",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 1: The store, and the escalation ladder

    Before the three kinds, the storage question. Memory storage climbs a
    ladder, and each step exists because the previous one broke.

    | Step | Breaks when |
    | --- | --- |
    | A dict in memory | The process restarts |
    | JSON on disk | Two things write at once |
    | SQLite | You need to search by meaning, not by key |
    | A vector store | — but now you have an index to keep in sync |

    **Most systems should stop at SQLite.** It is transactional, it does
    full-text search, it is one file, and it needs no server. A vector store
    adds search by meaning. It also adds an index that can drift out of sync
    with your source of truth, and nothing warns you when it does.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S13_Three_Kinds_of_Memory_task1")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    LangGraph's **store** is that ladder behind one interface. `InMemoryStore`
    is the first rung, a dict. The same `put`, `get` and `search` calls work
    against SQLite or Postgres when you swap the class. Two ideas carry the
    rest of the session:

    - **A namespace is a tuple, and it is your isolation boundary.**
      `("profile", "tomas")` is Tomás's drawer. Task 5 is what happens when
      the user is left out of it.
    - **A key is unique within its namespace, so `put` with the same key
      overwrites.** That one property is supersede-on-write, and Task 2 is
      what happens without it.

    The cell below shows both. It also shows a default to understand before
    you rely on `search`: **without an embedding index, the `query` argument
    is ignored.** You get the first items in the namespace, unranked, up to
    `limit`. That is fine for a profile and a few procedures. Task 2 shows
    what it does to a collection of facts, six entries in.
    """)
    return


@app.cell
def _(InMemoryStore, ui):
    ladder_store = InMemoryStore()
    ladder_store.put(("facts", "tomas"), "user.team", {"content": "The user's team is Revenue Systems."})
    ladder_store.put(("facts", "tomas"), "user.office", {"content": "The user's office is Dublin."})
    ladder_store.put(("facts", "tomas"), "ledger", {"content": "Ledger's nightly batch must finish before 04:00."})

    # Same key: this replaces the old fact rather than adding a second one.
    ladder_store.put(("facts", "tomas"), "user.team", {"content": "The user moved to Data Platform in June."})

    ui.table(
        [{"key": ladder_item.key, "content": ladder_item.value["content"]}
         for ladder_item in ladder_store.search(("facts", "tomas"), query="which office is the user in")],
        title="search(query='which office is the user in') with no index: every item, unranked",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three items, not four: the second `put` to `user.team` replaced the first.
    And the office question did not put the office first, because nothing
    ranked anything. Both come from the store, and both shape everything
    LangMem does on top of it.

    ---
    ## ✅ Task 2: Semantic memory, and the test that catches it

    Semantic memory is facts the agent should know later. It is the obvious
    kind.

    **The failure is retrieving the *wrong* fact confidently**, or a fact that
    used to be true.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S13_Three_Kinds_of_Memory_task2")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `create_memory_store_manager` is LangMem's whole semantic-memory loop in
    one object. It does three things:

    1. searches the user's namespace for what is already there
    2. shows that, plus the new conversation, to the model
    3. writes back whatever the model decides to insert or update

    Its default schema is a **collection**: free-text entries, as many as the
    model likes.

    ### The eval: staleness

    Facts expire. The user moves team, or the batch deadline changes. A
    memory system that stores "the user's team is Revenue Systems" forever
    will confidently tell you that two years after they left. So the test is
    **"does it recall the *current* value?"** It is in the next cell, before
    any model runs. So is Tomás's memory after a few weeks of use: six facts
    from earlier conversations, his team the most recent of them.
    """)
    return


@app.cell
def _():
    EARLIER_FACTS = [
        "The user's office is Dublin.",
        "The user prefers answers under 100 words.",
        "The user approves POs up to $50k; above that, escalate to Finance.",
        "The user is on call for Ledger's nightly batch, which must finish before 04:00.",
        "The user files expenses in Concur, not by email.",
        "The user's team is Revenue Systems.",
    ]
    TEAM_CHANGE = [{"role": "user", "content": "Update: I moved to the Data Platform team in June."},
                   {"role": "assistant", "content": "Noted."}]

    def staleness_test(store, namespace: tuple) -> dict:
        """Recall everything about the user. The current team must be there; the old one must not."""
        recalled = " ".join(str(item.value) for item in store.search(namespace, limit=100))
        return {
            "entries": len(store.search(namespace, limit=100)),
            "current value recalled": "Data Platform" in recalled,
            "old value gone": "Revenue Systems" not in recalled,
            "passed": "Data Platform" in recalled and "Revenue Systems" not in recalled,
        }

    return EARLIER_FACTS, TEAM_CHANGE, staleness_test


@app.cell
def _(CFG, mo):
    semantic_button = mo.ui.run_button(label=f"▶️  Tell both schemas about the team change with {CFG.llm_model} (2 model calls)")
    semantic_button
    return (semantic_button,)


@app.cell
def _(
    EARLIER_FACTS,
    InMemoryStore,
    MODEL,
    TEAM_CHANGE,
    UserProfile,
    as_user,
    create_memory_store_manager,
    mo,
    semantic_button,
    staleness_test,
    ui,
):
    mo.stop(not semantic_button.value, mo.md("*Click above to run it.*"))

    # Six facts from earlier conversations, as LangMem itself stores them.
    collection_store = InMemoryStore()
    for fact_number, earlier_fact in enumerate(EARLIER_FACTS):
        collection_store.put(("memories", "tomas"), f"fact-{fact_number}", {"kind": "Memory", "content": {"content": earlier_fact}})
    profile_store = InMemoryStore()
    profile_store.put(("profile", "tomas"), "profile", {"kind": "UserProfile", "content": {
        "team": "Revenue Systems", "office": "Dublin", "answer_style": "under 100 words"}})

    shown = [item.key for item in collection_store.search(("memories", "tomas"), limit=5)]
    collection_manager = create_memory_store_manager(MODEL, namespace=("memories", "{langgraph_user_id}"), store=collection_store)
    profile_manager = create_memory_store_manager(
        MODEL, schemas=[UserProfile], enable_inserts=False,
        namespace=("profile", "{langgraph_user_id}"), store=profile_store,
    )
    with mo.status.spinner(title="One conversation, two schemas…"):
        collection_manager.invoke({"messages": TEAM_CHANGE}, config=as_user("tomas"))
        profile_manager.invoke({"messages": TEAM_CHANGE}, config=as_user("tomas"))

    mo.vstack([
        mo.md(f"**What the collection's manager was shown before it wrote** (its default `query_limit=5`): `{shown}`"),
        ui.table([{"key": item.key, "content": str(item.value["content"])[:90]}
                  for item in collection_store.search(("memories", "tomas"), limit=100)], title="Default schema: a collection"),
        ui.table([{"key": item.key, "content": str(item.value["content"])} for item in profile_store.search(("profile", "tomas"))],
                 title="UserProfile: one record, updated in place"),
        ui.table([{"schema": "collection (default)", **staleness_test(collection_store, ("memories", "tomas"))},
                  {"schema": "UserProfile, enable_inserts=False", **staleness_test(profile_store, ("profile", "tomas"))}],
                 title="The staleness test"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the line above the first table before the tables. The manager
    searched Tomás's namespace and was shown five entries. **The team fact,
    the sixth, was not one of them.** There is no index, so the search
    returned the first items in the drawer, and LangMem keeps the top
    `query_limit=5`. The model could not update a fact it was never shown, so
    it added a new one. It did that on every run measured on the model above,
    with thinking on and off. Both teams are now in Tomás's memory, and
    nothing marks which is current. **That is the bug**, and you only see it
    if you test for it. It already happens at six facts. For a real user, it
    is the normal case.

    Three fixes, in increasing order of correctness:

    1. **Recency ordering:** prefer the newest. Cheap, and wrong whenever an
       old fact is more specific.
    2. **Supersede on write:** when writing a fact about the same subject,
       retire the previous one.
    3. **Validity windows:** store `valid_from` / `valid_to`. Correct, and
       more machinery than most systems need.

    Number 2 is the default we recommend. The `UserProfile`
    schema is how you get it here: **one record per user, with a field per
    subject, and `enable_inserts=False`** so the model can only update it.
    One record is always inside the search window, so the model always sees
    the old value it is replacing. The schema makes each subject a field, so
    you never have to remember to check for an old entry. One record, one
    team, and the staleness test passes!

    > **🏢 In the enterprise:** the profile is the right shape for facts
    > about a *person* (team, office, preferences), because there is exactly
    > one current value. Facts about the *world* ("Ledger's batch must finish
    > before 04:00") belong to whoever owns that system. A change made by the
    > Ledger team has to reach every user at once, so it belongs in a document
    > someone maintains, not a memory the model extracted. Deciding which
    > facts are yours to remember is the first design decision.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #1

    Your app gets one kind of memory, not three. Which facts, procedures or
    events does your use case actually need to carry from one conversation to
    the next? Which of the facts you would keep can change? For each one,
    would you supersede on write, order by recency, or keep validity windows,
    and what is the subject key?

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 3: Procedural memory, counted

    Procedural memory is a **learned how-to**. The agent worked something out
    once and should not have to work it out again. This kind has the clearest
    business case, because its eval is a cost measurement. Nobody has to judge
    whether an answer was correct.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S13_Three_Kinds_of_Memory_task3")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Here is a tiny world to count against. Each task has several plausible
    approaches and one that works. An agent without a procedure tries them in
    the order they occur to it. `solve()` does the real count, with nothing
    faked. The logs are what the assistant went through the first time,
    written as it happened.

    Two choices are deliberate:

    - **The procedure is stored under the task the agent was doing.** The
      harness knows that task. A name the model wrote could be anything.
    - **`solve()` scores each approach by the words it shares with
      `approach_that_worked`, and breaks ties against `avoid`.** The
      model does not copy the log's wording: it writes "Queried Atlas API
      endpoint" for "query Atlas", and sometimes lists every step it tried.
      An exact-text match misses the first and, worse, picks "search the
      internal wiki" out of the second and puts the wrong approach first.
      The tie-breaker that stops that is position: in a narrated log the
      approach that worked comes last. This is the rule a person would apply, and it
      is the reason the schema asks for *the one approach that finally
      succeeded*, in the log's words.
    """)
    return


@app.cell
def _(InMemoryStore, ui):
    APPROACHES = {
        "find shipment depot": (
            ["read the Ledger record", "search the wiki", "ask in #ops", "query Atlas /shipments/{id}"],
            "query Atlas /shipments/{id}",
        ),
        "expense filing": (["search the internal wiki", "email finance", "check Concur"], "check Concur"),
        "reset a scanner": (["power cycle it", "reseat the battery", "call the vendor"], "call the vendor"),
    }
    ATTEMPT_LOGS = {
        "find shipment depot": "Task: find shipment SH-2231's current depot.\n"
            "1. read the Ledger record -> said Leeds; wrong, Ledger lags by up to 20 minutes.\n"
            "2. search the wiki -> no answer.\n3. ask in #ops -> nobody replied for an hour.\n"
            "4. query Atlas /shipments/{id} -> scan_events[-1].depot = Wakefield. Correct.",
        "expense filing": "Task: can I expense a train ticket to the Wakefield depot?\n"
            "1. search the internal wiki -> page says no; it is out of date.\n"
            "2. email finance -> told to check Concur.\n3. check Concur -> policy allows it. Correct.",
    }

    def stems(text: str) -> set[str]:
        """Words of four letters or more, cut to four, so 'query' meets 'Queried' and 'check' meets 'Checked'."""
        return {word.strip(".,;:()[]{}'\"").lower()[:4] for word in text.replace("/", " ").split() if len(word.strip(".,;:()[]{}'\"")) >= 4}

    def recall(procedure, options: list[str]) -> str | None:
        """The option the procedure points at: most words shared with what worked, minus words shared with what to avoid."""
        if not procedure:
            return None
        text = procedure.value["approach_that_worked"].lower()
        worked, avoid = stems(text), stems(" ".join(procedure.value["avoid"]))
        last_seen = {option: max((text.rfind(stem) for stem in stems(option)), default=-1) for option in options}
        # Rank by the share of an approach's words found in what worked. Ties go to the approach mentioned last
        # (a narrated log is chronological, and the one that worked comes at the end), then to the one avoid mentions less.
        scores = {option: (len(stems(option) & worked) / len(stems(option)), last_seen[option], -len(stems(option) & avoid))
                  for option in options}
        best = max(scores, key=scores.get)
        return best if scores[best][0] > 0 else None

    def solve(store, task: str) -> dict:
        """Try approaches until one works. Count the attempts. That is the metric."""
        options, works = APPROACHES[task]
        remembered = recall(store.get(("procedures",), task), options)
        order = [remembered] + [option for option in options if option != remembered] if remembered else options
        attempts = 0
        for option in order:
            attempts += 1
            if option == works:
                break
        return {"task": task, "had a procedure": "yes" if remembered else "no",
                "approaches tried": attempts, "of possible": len(options)}

    ui.table([solve(InMemoryStore(), task) for task in APPROACHES],
             title="First time, empty store: every task works through its wrong turns")
    return ATTEMPT_LOGS, solve


@app.cell
def _(CFG, mo):
    procedural_button = mo.ui.run_button(label=f"▶️  Learn procedures from the two logs with {CFG.llm_model} (2 model calls)")
    procedural_button
    return (procedural_button,)


@app.cell
def _(
    ATTEMPT_LOGS,
    InMemoryStore,
    MODEL,
    PROCEDURE_RULE,
    Procedure,
    create_memory_manager,
    mo,
    procedural_button,
    solve,
    ui,
):
    mo.stop(not procedural_button.value, mo.md("*Click above to run it.*"))

    procedure_store = InMemoryStore()
    procedure_manager = create_memory_manager(MODEL, schemas=[Procedure], enable_updates=False, instructions=PROCEDURE_RULE)
    with mo.status.spinner(title="Reading the logs…"):
        for logged_task, attempt_log in ATTEMPT_LOGS.items():
            extracted = procedure_manager.invoke({"messages": [{"role": "user", "content": attempt_log}]})
            if extracted:
                procedure_store.put(("procedures",), logged_task, extracted[0].content.model_dump())

    mo.vstack([
        ui.table([{"task": stored.key, "approach_that_worked": stored.value["approach_that_worked"][:70],
                   "avoid": len(stored.value["avoid"])} for stored in procedure_store.search(("procedures",))],
                 title="What the model wrote down"),
        ui.table([solve(procedure_store, task) for task in ["find shipment depot", "expense filing", "reset a scanner"]],
                 title="Second time: attempts counted, not assumed"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The eval: does the second attempt cost less?

    Those attempt counts came out of `solve()`, which tried approaches until
    one worked and counted them. That matters more than the numbers. **If you
    assume the saving instead of counting it, you no longer have an eval.** A
    procedural-memory demo that hardcodes "1 step with, 4 without" will still
    show a saving on the day the retrieval breaks.

    Run a task twice. Measure **steps, tokens, or wall-clock**, whichever you
    can count. If attempt two is not cheaper, the procedure was not learned,
    or it was not retrieved.

    > Look at what the third row costs. It had no procedure, so it worked
    > through every approach it had, and the one that worked was the last one
    > it tried. The saving is real, and it is *bounded by how many wrong turns
    > there were to skip*. On a task with two plausible approaches,
    > procedural memory buys you almost nothing. Check that before you build
    > a memory system for one.

    **The failure mode is a wrong procedure learned confidently.** A bad
    procedure is worse than none, because the agent retrieves it instead of
    thinking. So the second test is: *when the procedure no longer works,
    does the agent notice?* Systems that trust their own memory
    unconditionally fail this every time, and nothing reports it.

    LangMem has a second form of procedural memory. `create_prompt_optimizer`
    rewrites the agent's **system prompt** from feedback on past
    conversations, so the how-to lives in the instructions. It is the right
    tool when the lesson is a rule for every task. This notebook uses a record
    keyed by task because the eval has to see which approach was retrieved,
    and a rewritten prompt does not tell you that.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 4: Episodic memory, checked against the log

    Episodic memory is a record of events: what happened, and when. Its main
    value is **explanation**, not recall. An agent that can say why it did
    something can be audited.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S13_Three_Kinds_of_Memory_task4")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The conversation below is the assistant routing a ticket. It made two
    tool calls. It searched the runbook, then routed the ticket. Then its
    reply **said it had checked the connection pool**. It had not, and no
    tool did. A model narrating its work can fill in the step the runbook
    says comes next.

    The next cell writes the episode **from the observed events**: the tool
    calls in the message list, with their arguments and what came back. No
    model is involved.
    """)
    return


@app.cell
def _(ui):
    TRAJECTORY = [
        {"role": "user", "content": "TKT-4471: Atlas dashboards timing out since 09:00. Who should take it?"},
        {"role": "assistant", "content": "", "tool_calls": [{"id": "c1", "type": "function", "function": {
            "name": "search_runbook", "arguments": '{"query": "Atlas timeout"}'}}]},
        {"role": "tool", "tool_call_id": "c1", "content": "Atlas runbook: first check the Ledger connection pool."},
        {"role": "assistant", "content": "", "tool_calls": [{"id": "c2", "type": "function", "function": {
            "name": "route_ticket", "arguments": '{"ticket": "TKT-4471", "team": "Data Platform"}'}}]},
        {"role": "tool", "tool_call_id": "c2", "content": "routed TKT-4471 -> Data Platform"},
        {"role": "assistant", "content": "I checked the Ledger connection pool and it was exhausted, "
                                         "so I routed TKT-4471 to Data Platform."},
    ]

    def observed_calls(messages: list) -> list[dict]:
        """The log: every tool call that happened, with what it returned. No model involved."""
        results = {message["tool_call_id"]: message["content"] for message in messages if message["role"] == "tool"}
        return [{"tool": call["function"]["name"], "arguments": call["function"]["arguments"], "returned": results.get(call["id"], "")}
                for message in messages if message["role"] == "assistant" for call in message.get("tool_calls", [])]

    ui.table(observed_calls(TRAJECTORY), title="The episode, written from observed events")
    return TRAJECTORY, observed_calls


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now the other way: ask LangMem to record the same conversation as an
    `Episode`. Then run the eval, which is the point of the task. **Every
    observation the episode states has to be in something a tool
    returned.** The check below is deliberately plain. If the episode says
    the pool was checked, or that it was exhausted, some tool in the log must
    have checked it. Otherwise the episode records something nobody
    observed.
    """)
    return


@app.cell
def _(CFG, mo):
    episodic_button = mo.ui.run_button(label=f"▶️  Let {CFG.llm_model} write the episode (1 model call)")
    episodic_button
    return (episodic_button,)


@app.cell
def _(
    Episode,
    MODEL,
    TRAJECTORY,
    create_memory_manager,
    episodic_button,
    mo,
    observed_calls,
    ui,
):
    mo.stop(not episodic_button.value, mo.md("*Click above to run it.*"))
    import re

    episode_manager = create_memory_manager(
        MODEL, schemas=[Episode], enable_updates=False,
        instructions="Record what the agent did in this conversation as an episode.",
    )
    with mo.status.spinner(title="Writing the episode…"):
        written_episodes = episode_manager.invoke({"messages": TRAJECTORY})
    mo.stop(not written_episodes, mo.md("*The model wrote no episode this time. Press again.*"))
    model_episode = written_episodes[0].content

    episode_calls = observed_calls(TRAJECTORY)
    account = " ".join(model_episode.model_dump().values()).lower()
    says_checked = re.search(r"checked\b[^.]*connection pool", account) is not None
    says_exhausted = "exhausted" in account
    a_tool_checked = any("pool" in call["tool"] for call in episode_calls)
    TRUTHFULNESS = {
        "says it checked the pool": says_checked,
        "says the pool was exhausted": says_exhausted,
        "a tool checked the pool": a_tool_checked,
        "passed": a_tool_checked or not (says_checked or says_exhausted),
    }
    mo.vstack([
        ui.table([{"field": name, "the model's account": value} for name, value in model_episode.model_dump().items()],
                 title="The episode, written by the model"),
        ui.table([TRUTHFULNESS], title=f"Truthfulness against the log — tools that ran: {[call['tool'] for call in episode_calls]}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The eval: can it explain, and is the explanation true?

    The eval has two halves.

    1. Ask it to explain a decision it made. Did it produce a record?
    2. **Check the record against what actually happened.** An episodic
       memory written by the model is the model's account of itself. A
       system that records a plausible story instead of the real one is worse
       than no memory at all. It is an audit trail that lies.

    On the model above, the episode recorded the check nobody made in every
    run measured while writing this: five of five, thinking on and off.
    Sometimes it is in the `action` (*"Checked the Ledger connection pool and
    routed TKT-4471 to Data Platform"*). Sometimes it is only in the
    `reasoning` (*"…checking Ledger connection pool which was exhausted"*).
    That is why the test reads every field. LangMem did exactly what it was
    asked. It summarised the conversation faithfully, including the part
    that was not true.

    On a larger hosted model the test sometimes passes: the episode stops at
    *"found that the first step is to check the pool"* and claims nothing
    more. If yours passed, press the button again. A pass that depends on
    the model's mood is the reason the test exists, not a reason to drop it.

    **Write episodic entries from observed events**, not from the model's
    summary of them. Log the tool call that happened, not the model's
    description of the tool call. Let the model write the *reasoning* field
    if you want it, and label it as the model's.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #2

    Pick the test that would catch your memory failing. If it is procedural:
    what will you count — tool calls, model calls, turns, seconds — to show
    attempt two is cheaper, and how many wrong turns are there to skip? If it
    is episodic: where is the log of observed events you would compare an
    explanation against? Does it exist yet, or would you be relying on the
    model's account of itself?

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 5: What actually goes wrong, and the leakage test

    | Failure | Which memory | How it looks | The test |
    | --- | --- | --- | --- |
    | Stale fact | semantic | Confidently out of date | Change a fact, ask again |
    | Wrong fact retrieved | semantic | Plausible and unrelated | Ask about a near-neighbour subject |
    | Bad procedure | procedural | Repeats a mistake efficiently | Break the procedure, see if it notices |
    | Unbounded growth | all | Slow, then expensive, then wrong | Measure recall quality at 10 vs 1,000 entries |
    | Fabricated history | episodic | An audit trail that lies | Compare records against real logs |
    | Cross-user leakage | all | **A user sees another user's memory** | Two users, same question |

    Look at the last one. If your memory is keyed by anything less specific
    than the user, two people asking the same question can get each other's
    context. In a regulated firm that can be a reportable incident.
    """)
    return


@app.cell(hide_code=True)
def _(ui):
    ui.diagram("S13_Three_Kinds_of_Memory_task5")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    LangMem has two memory **tools** an agent calls mid-conversation:

    - `manage_memory` creates, updates or deletes an entry
    - `search_memory` looks one up

    Both take the namespace as a template, and `{langgraph_user_id}` is
    filled from the config of each call. The test below calls the tools
    directly, with no model, exactly as an agent would. It runs once with the
    user in the namespace and once without.
    """)
    return


@app.cell
def _(
    InMemoryStore,
    as_user,
    create_manage_memory_tool,
    create_search_memory_tool,
    ui,
):
    def leakage_test(namespace: tuple) -> dict:
        """Two users store a fact each, then ask the same question. Neither may see the other's."""
        store = InMemoryStore()
        manage = create_manage_memory_tool(namespace=namespace, store=store)
        search = create_search_memory_tool(namespace=namespace, store=store)
        manage.invoke({"action": "create", "content": "Tomás: PO approval limit is $50k; escalate above it to Finance."}, config=as_user("tomas"))
        manage.invoke({"action": "create", "content": "Kwame: PO approval limit is $250k (Procurement lead)."}, config=as_user("kwame"))
        kwame_sees = search.invoke({"query": "what is my PO approval limit"}, config=as_user("kwame"))
        tomas_sees = search.invoke({"query": "what is my PO approval limit"}, config=as_user("tomas"))
        return {"namespace": str(namespace), "Kwame sees Tomás's limit": "Tomás" in kwame_sees,
                "Tomás sees Kwame's limit": "Kwame" in tomas_sees,
                "passed": "Tomás" not in kwame_sees and "Kwame" not in tomas_sees}

    ui.table([leakage_test(("memories",)), leakage_test(("memories", "{langgraph_user_id}"))],
             title="The leakage test: two users, same question")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One tuple element is the whole difference. The first namespace looks fine
    in a demo with one user. Look at which limit Tomás
    would have been told: the larger one, which belongs to someone else.

    > Test it explicitly. Two users, same question, assert the answers do not
    > contain each other's facts. It takes ten minutes.

    > **🏢 In the enterprise:** the user id in the namespace has to come from
    > your identity provider (the authenticated session), never from
    > something the model or the user typed. A namespace built from a name in
    > the prompt is one prompt injection away from reading somebody else's
    > drawer. "The user" may also not be fine-grained enough. If two business
    > units must not share context, put the tenant in the namespace too:
    > `("memories", "{tenant}", "{user}")`.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #3

    Does your app have more than one user? Write down the namespace your
    memory would be keyed by, and where each part of it comes from. Then the
    before/after: memory can make answers *worse*, because a wrong fact
    retrieved confidently displaces correct reasoning. Which of the cases in
    your eval harness would you expect memory to move, and in which
    direction?

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ By the End of the Sesh

    The code you saw at the start, now that every line of it has been
    unrolled (the schemas, `ATTEMPT_LOGS`, `TRAJECTORY` and `observed_calls`
    are in the cells above it):

    ```python
    mo.stop(not sesh_button.value, mo.md("*Click above to build it.*"))

    sesh_store = InMemoryStore()

    # Semantic: one live profile per user, updated in place.
    sesh_profile = create_memory_store_manager(
        MODEL, schemas=[UserProfile], enable_inserts=False,
        namespace=("profile", "{langgraph_user_id}"), store=sesh_store,
    )
    sesh_profile.invoke({"messages": [
        {"role": "user", "content": "I'm on the Revenue Systems team. Keep answers under 100 words."},
        {"role": "assistant", "content": "Noted."},
        {"role": "user", "content": "Update: I moved to Data Platform in June."},
    ]}, config=as_user("tomas"))

    # Procedural: what worked, learned from a log of attempts, keyed by the task.
    sesh_learn = create_memory_manager(MODEL, schemas=[Procedure], enable_updates=False, instructions=PROCEDURE_RULE)
    sesh_learned = sesh_learn.invoke({"messages": [{"role": "user", "content": ATTEMPT_LOGS["find shipment depot"]}]})
    if sesh_learned:
        sesh_store.put(("procedures",), "find shipment depot", sesh_learned[0].content.model_dump())

    # Episodic: written from the tool calls that happened, not from the model.
    sesh_store.put(("episodes", "tomas"), "TKT-4471", {"calls": observed_calls(TRAJECTORY)})

    ui.table(
        [{"namespace": "/".join(sesh_item.namespace), "key": sesh_item.key, "value": str(sesh_item.value)[:110]}
         for sesh_namespace in [("profile", "tomas"), ("procedures",), ("episodes", "tomas")]
         for sesh_item in sesh_store.search(sesh_namespace)],
        title="One store, three kinds of memory",
    )
    ```

    - `InMemoryStore`, namespaces and keys are Task 1: a key is unique in its
      namespace, and the user belongs in the namespace.
    - `UserProfile` with `enable_inserts=False` is Task 2: supersede on
      write, and the staleness test that tells you it worked.
    - The `Procedure` record keyed by task is Task 3, and `solve()` is the
      count that says whether it saved anything.
    - The episode built from `observed_calls` is Task 4. The block above
      never asks the model what it did, on purpose.
    - This block has no tests. Tasks 2 to 5 are those tests, and they are
      what you take to your own app.

    ---
    ## 🏭 What we Built vs. What's in Production

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | The store | `InMemoryStore`, gone when the kernel restarts | `SqliteStore` for one process, `PostgresStore` for many — the same `put`/`get`/`search` calls |
    | Search | No index: `search` returns the namespace, unranked | An `index=` with an embedding model once a namespace outgrows a profile, and a recall test re-run at 10, 100 and 1,000 entries |
    | Semantic memory | A profile schema that supersedes on write | Validity windows where the history matters, and a history you can query as-of a date |
    | Procedural memory | A record per task, and an attempt count | Real token and latency accounting per task, and a check that a retrieved procedure still works |
    | Episodic memory | Built from the message list's tool calls | Built from the trace your agent already emits, with a request id that ties it to the audit log |
    | Extraction | Inline, on every conversation | In the background after the conversation ends (LangMem's `ReflectionExecutor`), so the user does not wait for it |
    | Consolidation | None | A pass that summarises and prunes on a schedule, with a recall test before and after, because this is where memory systems get worse unnoticed |
    | Isolation | `{langgraph_user_id}` from a config dict | The user and tenant from the authenticated session, and the leakage test in CI |

    ---
    ## 👋 Conclusion

    We built the three kinds of memory on one store, and each came with the
    test that catches it failing:

    - **Semantic** memory went stale the moment a fact changed, even with a
      framework doing the extraction. A schema with one record per user fixed
      it.
    - **Procedural** memory saved attempts on the tasks with wrong turns to
      skip, and we counted them.
    - **Episodic** memory written by the model recorded a check that never
      happened. The log of tool calls did not.
    - One element of a namespace tuple was the difference between a memory
      per user and a memory everyone shares.

    The memory plan for Ryan's assistant, filled in:

    - a profile per user for the facts people keep repeating, superseded on
      write
    - procedures keyed by task, with the saving counted
    - episodes from the tool log
    - the user from the session in every namespace
    - four tests that run with everything else

    LangMem extracted and stored every memory here in a few lines. None of
    those lines tell you whether what it stored is current, true, or yours.
    That is what the tests are for, so put them in your eval harness!

    Now build 🏗️, ship 🚢, and share 📤
    [this week's challenge](../challenge/README.md).

    ---
    ## 📖 Official Documentation

    | Tool | Used here for | Docs |
    | --- | --- | --- |
    | LangMem | the three kinds of memory, and which LangMem primitive serves each | [langchain-ai.github.io/langmem — core concepts](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) |
    | LangMem memory managers | `create_memory_manager`, `create_memory_store_manager`, schemas, `enable_inserts` | [langchain-ai.github.io/langmem — memory API reference](https://langchain-ai.github.io/langmem/reference/memory/) |
    | LangMem memory tools | `create_manage_memory_tool`, `create_search_memory_tool`, namespace templates | [langchain-ai.github.io/langmem — tools API reference](https://langchain-ai.github.io/langmem/reference/tools/) |
    | LangMem prompt optimization | `create_prompt_optimizer`, procedural memory as a rewritten system prompt | [langchain-ai.github.io/langmem — prompt optimization](https://langchain-ai.github.io/langmem/guides/optimize_memory_prompt/) |
    | LangGraph store | `InMemoryStore`, namespaces, `put` / `get` / `search`, `index=` | [docs.langchain.com — LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory) |
    | LangChain OpenAI | `ChatOpenAI`, the model through any OpenAI-compatible endpoint | [docs.langchain.com — ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai) |
    | Pydantic | the `UserProfile`, `Procedure` and `Episode` schemas | [pydantic.dev — models](https://pydantic.dev/docs/validation/latest/concepts/models/) |
    """)
    return


if __name__ == "__main__":
    app.run()
