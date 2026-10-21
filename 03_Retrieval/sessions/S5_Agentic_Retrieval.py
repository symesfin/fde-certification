# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "mcp>=1.2",  # not imported here: litellm imports it when tools= is passed, and the sandbox asks for it on the first call without this line
#     "rank-bm25>=0.2.2",
#     "pandas>=2.2",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 5: Agentic Retrieval — DCI over an LLM Wiki vs. Agentic RAG

    *One worker, one decision, one person who has to sign it.*

    Nadia is a second-line support engineer on the service desk of a regional
    broadband and mobile operator. A ticket comes in, and the answer is never
    in the ticket: it is in a runbook, a tariff page, the glossary that says
    what `LOS 0x21` means, or spread across two of them. She is building an
    assistant that finds that answer, and her manager will sign off on one
    page: *how often it is right, what it costs per question, how long a
    ticket waits, and what would change her mind.*

    The knowledge base already exists — seven pages of runbooks, tariffs,
    codes and data-handling rules, kept as Markdown by Knowledge Operations.
    The decision this session makes is not *which model*; it is *what sits
    between the model and those pages*. Either a retriever selects chunks on
    the model's behalf and the model can search again, or the model is handed
    the pages themselves — an index, a search, a read — and investigates. Same
    model, same corpus, same questions, same loop, same scoring. Only the
    corpus interface changes, and the page her manager signs is built from
    what that changes.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - Task 1: Build the two corpus interfaces
    - ❓ Question #1
    - Task 2: Use one agent loop for both approaches
    - ❓ Question #2
    - Task 3: Evaluate outcomes and behaviour
    - ❓ Question #3
    - Task 4: Inspect the difference
    - ❓ Question #4
    - Conclusion
    - Additional Context
    - Bonus Tasks

    > 📓 **Not covered here:** dense retrieval and reranking. The retriever on
    > the RAG side is BM25 on purpose — local, inspectable, and no embedding
    > endpoint to approve — and swapping it for a dense or hybrid retriever
    > changes the retriever, not the experiment. The Bonus Tasks show where
    > that swap goes. Nadia's real tickets are described, not shipped: the
    > corpus below is her operator's knowledge base, written so that each
    > question has a reviewed answer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | LiteLLM | `completion()` with `tools=` — the function-calling loop both approaches share | [docs.litellm.ai — function calling](https://docs.litellm.ai/docs/completion/function_call) |
    | rank-bm25 | the chunk index on the Agentic RAG side, forty lines of lexical search | [github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25) |
    | pandas | the results table and the per-approach summary | [pandas.pydata.org/docs](https://pandas.pydata.org/docs/) |
    | marimo | the run buttons and the rendered tables | [docs.marimo.io](https://docs.marimo.io/) |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Operational definitions

    Three terms, used precisely for the rest of this notebook:

    - **LLM Wiki** — Markdown pages with stable names, headings, and a
      navigational index page. A course term, not a protocol. Nadia's seven
      pages already have this shape, which is the only reason the second
      approach is available to her at all.
    - **Direct Corpus Interaction (DCI)** — the agent lists, searches and reads
      those pages directly. No chunk retriever selects context on its behalf.
    - **Agentic RAG** — the agent can run several chunk searches and
      reformulate between searches, but it only ever sees ranked chunks.

    The comparison holds the model, the corpus, the questions, the loop and the
    scoring constant. **Only the tools change.** That is what makes the result
    a finding about the interface rather than about the orchestration.

    **Estimated time:** 30–40 minutes

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import json
    import re
    import sys
    import time
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    import litellm
    from litellm.exceptions import UnsupportedParamsError

    CFG = nb.bootstrap()
    DATA = Path(mo.notebook_dir()) / "data"
    CORPUS_DIR = DATA / "corpus"
    WIKI_INDEX = (DATA / "wiki" / "index.md").read_text(encoding="utf-8")
    PAGES = {page.name: page.read_text(encoding="utf-8") for page in sorted(CORPUS_DIR.iterdir()) if page.suffix in {".md", ".txt", ".csv"}}
    CASES = [json.loads(line) for line in (DATA / "eval_cases.jsonl").read_text(encoding="utf-8").splitlines() if line]

    SAMPLER = {"temperature": 0}  # deterministic where the provider allows it

    def ask_model(messages, tools):
        """One chat turn with tools offered. Every model call in this notebook goes through here."""
        kwargs = dict(messages=messages, tools=tools, **CFG.kwargs())  # tool_choice defaults to "auto"; some gateways reject it sent explicitly
        try:
            return litellm.completion(timeout=600, **SAMPLER, **kwargs).choices[0].message
        except UnsupportedParamsError:
            SAMPLER.clear()  # some providers accept only their default temperature; run at it from now on
            return litellm.completion(timeout=600, **kwargs).choices[0].message

    print(f"✅ {CFG.root.name}   model: {CFG}   {len(PAGES)} pages · {len(CASES)} eval cases")
    return CASES, CFG, PAGES, WIKI_INDEX, ask_model, json, re, time, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — Build the two corpus interfaces

    **Agentic RAG receives ranked chunks.** Each page is split at its `##`
    headings, BM25 indexes the sections, and the one tool the agent has
    returns the top-k sections for a query. It can search again, but it
    cannot list files or ask for a whole page.

    **DCI receives navigation primitives.** `list_pages` returns the wiki
    index; `grep_wiki` returns matching lines with page and line number;
    `read_page` returns a complete page by its stable name. The agent — not a
    retriever — decides what to inspect next.

    Both sit over the same seven files. Nothing is embedded, nothing is
    downloaded, and every tool result is a string a person can read.

    **Every retriever has a cap, and this one is visible.** `search_chunks`
    returns at most eight sections and at most 1,000 characters of each.
    That is not a bug to fix; it is the budget every chunk retriever has
    somewhere, usually hidden in a config file. Here it is in the function,
    so when a question's answer sits past character 1,000 of a long section
    you will see exactly what the RAG agent could and could not see.
    """)
    return


@app.cell
def _(PAGES, WIKI_INDEX, re, ui):
    from rank_bm25 import BM25Okapi

    TOKEN = re.compile(r"[a-z0-9£$%]+")

    def tokenize(text):
        return TOKEN.findall(text.lower())

    chunks = []
    for page_name, page_text in PAGES.items():
        sections = re.split(r"(?=^## )", page_text, flags=re.M)
        for section_index, section in enumerate(block for block in sections if block.strip()):
            chunks.append({"id": f"{page_name}#s{section_index}", "page": page_name, "text": section.strip()})
    bm25 = BM25Okapi([tokenize(chunk["text"]) for chunk in chunks])

    def search_chunks(query: str, k: int = 4) -> str:
        scores = bm25.get_scores(tokenize(query))
        order = sorted(range(len(chunks)), key=lambda index: scores[index], reverse=True)[: max(1, min(k, 8))]
        return "\n\n---\n\n".join(f"[{chunks[index]['id']}]\n{chunks[index]['text'][:1000]}" for index in order)

    def list_pages() -> str:
        return WIKI_INDEX

    def grep_wiki(pattern: str) -> str:
        try:
            rx = re.compile(pattern, re.I)
        except re.error:
            rx = re.compile(re.escape(pattern), re.I)
        hits = []
        for page, text in PAGES.items():
            for number, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    hits.append(f"{page}:{number}: {line}")
        return "\n".join(hits[:40]) or "(no matches)"

    def read_page(page: str) -> str:
        if page not in PAGES:
            return f"(unknown page: {page})"
        return PAGES[page][:12000]

    RAG_FUNCS = {"search_chunks": search_chunks}
    DCI_FUNCS = {"list_pages": list_pages, "grep_wiki": grep_wiki, "read_page": read_page}

    def schema(name, description, properties, required=()):
        return {"type": "function", "function": {"name": name, "description": description,
                "parameters": {"type": "object", "properties": properties, "required": list(required)}}}

    RAG_TOOLS = [schema("search_chunks", "Search ranked corpus chunks. Search again with a new query when evidence is incomplete.",
                        {"query": {"type": "string"}, "k": {"type": "integer"}}, ["query"])]
    DCI_TOOLS = [
        schema("list_pages", "Read the wiki index and page map.", {}),
        schema("grep_wiki", "Search exact text or a regular expression across wiki pages with line provenance.", {"pattern": {"type": "string"}}, ["pattern"]),
        schema("read_page", "Read a complete wiki source page by stable name.", {"page": {"type": "string", "enum": sorted(PAGES)}}, ["page"]),
    ]

    ui.table(
        [{"page": name, "sections": sum(1 for chunk in chunks if chunk["page"] == name), "characters": len(text)} for name, text in PAGES.items()],
        title=f"RAG index: {len(chunks)} sections · DCI pages: {len(PAGES)}",
    )
    return DCI_FUNCS, DCI_TOOLS, RAG_FUNCS, RAG_TOOLS, grep_wiki, search_chunks


@app.cell
def _(grep_wiki, mo, search_chunks):
    def tool_box(title: str, text: str):
        """A tool result as the agent receives it: a string, wrapped so it stays readable."""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return mo.vstack(
            [
                mo.md(f"**{title}**"),
                mo.Html(
                    f'<pre style="white-space:pre-wrap; word-break:break-word; font-size:0.85em; '
                    f'padding:0.75em; border-radius:6px; background:rgba(127,127,127,0.08)">{escaped}</pre>'
                ),
            ]
        )

    mo.vstack(
        [
            tool_box("`search_chunks('LOS 0x21', k=2)` — what the RAG agent sees", search_chunks("LOS 0x21", k=2)[:900]),
            tool_box("`grep_wiki('LOS 0x21')` — what the DCI agent sees", grep_wiki("LOS 0x21")[:900]),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🏢 In the enterprise:** both interfaces here see every page, because
    > the notebook has one user. At work the corpus interface is where
    > authorisation lives — `list_pages`, `grep_wiki` and `read_page` must
    > enforce the *caller's* permissions, not the service account's, and a
    > chunk retriever has to filter by the same rule before ranking, not
    > after. Nadia's data-handling page says a record under legal hold may not
    > be processed by any automated tool; that is a filter on the corpus
    > interface, and it is the same filter whichever approach wins.

    ### ❓ Question #1

    Each eval case below labels the page and the answer terms *before* either
    approach runs. The chunker also made a choice for you — a section ends at
    the next `##` heading. For the ten questions you will label on your own
    corpus: which ones need exact text (a code, a figure, a product name),
    which need two pages, and does your corpus have the headings and stable
    page names that make the second approach possible at all?

    **Answer:**

    ---
    ## Task 2 — Use one agent loop for both approaches

    The loop logs every tool call and the number of characters it returned.
    Keeping the loop identical prevents us from crediting the interface for
    behaviour caused by different orchestration. The system prompt is the
    same for both: investigate before answering, cite page names, say when
    the evidence is incomplete.

    `max_turns=6` is a budget, not a tuning knob — both approaches can loop
    badly, and a loop that cannot stop is a cost with no upper bound.
    """)
    return


@app.cell
def _(ask_model, json, time):
    SYSTEM = (
        "Answer Northline Broadband questions only from tool evidence. Investigate before answering. "
        "Cite page names. If evidence is incomplete, say so."
    )

    def run_agent(question, tools, funcs, max_turns=6):
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
        trace, chars = [], 0
        started = time.perf_counter()
        for _ in range(max_turns):
            msg = ask_model(messages, tools)
            calls = msg.tool_calls or []
            if not calls:
                return {"answer": (msg.content or "").strip(), "trace": trace, "evidence_chars": chars,
                        "latency_s": time.perf_counter() - started, "stopped": "answer"}
            shaped = [{"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}} for call in calls]
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": shaped})
            for call in shaped:
                name = call["function"]["name"]
                try:
                    args = json.loads(call["function"]["arguments"] or "{}")
                    if name not in funcs:
                        raise KeyError(f"unknown tool {name}")
                    result = str(funcs[name](**args))
                except Exception as exc:
                    result = f"(tool error: {type(exc).__name__}: {exc})"
                chars += len(result)
                trace.append({"tool": name, "args": args, "chars": len(result)})
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
        return {"answer": "(max turns reached)", "trace": trace, "evidence_chars": chars,
                "latency_s": time.perf_counter() - started, "stopped": "max_turns"}

    return (run_agent,)


@app.cell
def _(CASES, CFG, mo):
    FIRST_CASE = next(case for case in CASES if case["id"] == "vocabulary")
    first_button = mo.ui.run_button(label=f"▶️  Run one question both ways with {CFG.llm_model}")
    mo.vstack([first_button, mo.md(f"<sub>*{FIRST_CASE['question']}* — up to six model calls per approach.</sub>")])
    return FIRST_CASE, first_button


@app.cell
def _(
    DCI_FUNCS,
    DCI_TOOLS,
    FIRST_CASE,
    RAG_FUNCS,
    RAG_TOOLS,
    first_button,
    mo,
    run_agent,
):
    def show_result(label: str, result: dict):
        trace = " → ".join(f"{step['tool']}({', '.join(str(value) for value in step['args'].values())[:40]})" for step in result["trace"]) or "(no tool calls)"
        return mo.md(
            f"**{label}** · {len(result['trace'])} calls · {result['evidence_chars']:,} evidence chars · "
            f"{result['latency_s']:.1f} s · stopped: `{result['stopped']}`\n\n`{trace}`\n\n> {result['answer']}"
        )

    if first_button.value:
        with mo.status.spinner(title="Running both approaches…"):
            FIRST_RAG = run_agent(FIRST_CASE["question"], RAG_TOOLS, RAG_FUNCS)
            FIRST_DCI = run_agent(FIRST_CASE["question"], DCI_TOOLS, DCI_FUNCS)
        FIRST_PANEL = mo.vstack([mo.md(f"### {FIRST_CASE['question']}"), show_result("Agentic RAG", FIRST_RAG), show_result("DCI Wiki", FIRST_DCI)])
    else:
        FIRST_RAG, FIRST_DCI = None, None
        FIRST_PANEL = mo.callout(mo.md("Press the button to run the first eval case through both tool sets."), kind="info")

    FIRST_PANEL
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the two traces before the two answers. The question was written
    without a single word the tariffs page uses — no `£45`, no `tariff`, no
    `minimum term` — so the ranked search has nothing to rank on and the RAG
    agent has to guess a reformulation. The DCI agent does not search for
    words; it reads the index, sees a page called tariffs, and reads it.
    The answer may end up the same. The *trace* is what an auditor can
    reconstruct, what a reviewer can replay, and what a cost line is built
    from — and the two traces are not the same even when the answers are.

    ### ❓ Question #2

    Both runs produce a trace: the tool, its arguments, the characters
    returned, the latency. Your endpoint will have to name its sources in
    every answer. Which parts of *this* trace would you keep in the response
    so that someone who was not in the room can see why the answer says what
    it says — and which approach makes that easier to do?

    **Answer:**

    ---
    ## Task 3 — Evaluate outcomes and behaviour

    The answer check is deliberately plain: the reviewed terms must appear in
    the answer. It is not a semantic metric, but it is deterministic and easy
    to audit — and on a corpus you wrote the answer key for, plain is enough
    to see a difference. Citations, calls, evidence volume and latency are
    tracked separately, so a correct answer cannot hide a wasteful
    trajectory.

    **Six questions, chosen so that each column has somewhere to move.**
    Each case carries a prediction — `favours` — written before any run, so
    the table below is predicted against observed, not a leaderboard.

    | id | shape | favours | the mechanism |
    | --- | --- | --- | --- |
    | `exact` | an acronym | either | exact text; one call each way |
    | `vocabulary` | none of the page's words in the question | DCI | ranking has nothing to rank on; the index names the page |
    | `deep_section` | the answer past character 1,000 of a long section | DCI | the retriever's cap hides it; `read_page` does not |
    | `which_pages` | "which pages mention X" | DCI | top-k cannot answer that; one `grep` returns every line with provenance — and it is *cheaper* |
    | `broad_churn` | split between the metrics CSV and the field guide | RAG | ranking returns both at fixed cost; DCI reads whole pages |
    | `broad_incident` | three pages, no single section | RAG | same shape |
    | `decline` | a question the corpus cannot answer | either | retrieval always returns a top-k; saying "no" is the loop's job, and `must_decline` scores the refusal |

    Seven cases, two approaches, up to six turns each. Press once; it takes a
    few minutes.
    """)
    return


@app.cell
def _(CASES, mo):
    eval_button = mo.ui.run_button(label=f"📊  Run all {len(CASES)} cases × 2 approaches")  # the decline case counts too
    eval_button
    return (eval_button,)


@app.cell
def _(
    CASES,
    DCI_FUNCS,
    DCI_TOOLS,
    RAG_FUNCS,
    RAG_TOOLS,
    eval_button,
    mo,
    run_agent,
):
    import pandas as pd

    DECLINE_MARKERS = ("not ", "no ", "cannot", "can't", "unavailable", "does not", "doesn't", "isn't", "only covers", "no data")

    def score(case, result):
        answer = result["answer"].lower()
        if case.get("must_decline"):
            # Retrieval always returns a top-k. Declining is the loop's job, so the
            # pass mark here is "it refused" -- said so, and invented no figure.
            passed = any(marker in answer for marker in DECLINE_MARKERS) and not any(term.lower() in answer for term in case["expected_terms"])
        else:
            passed = all(term.lower() in answer for term in case["expected_terms"])
        return {
            "pass": passed,
            "cited_expected_page": any(page.lower() in answer for page in case["expected_pages"]),
            "calls": len(result["trace"]),
            "evidence_chars": result["evidence_chars"],
            "latency_s": round(result["latency_s"], 2),
            "stopped": result["stopped"],
        }

    rows, details = [], {}
    if eval_button.value:
        with mo.status.spinner(title="Running every case through both approaches…"):
            for eval_case in CASES:
                for eval_approach, eval_tools, eval_funcs in [("Agentic RAG", RAG_TOOLS, RAG_FUNCS), ("DCI Wiki", DCI_TOOLS, DCI_FUNCS)]:
                    eval_result = run_agent(eval_case["question"], eval_tools, eval_funcs)
                    details[(eval_case["id"], eval_approach)] = eval_result
                    rows.append({"id": eval_case["id"], "approach": eval_approach, "favours": eval_case.get("favours", "either"), **score(eval_case, eval_result)})

    results = pd.DataFrame(rows)
    results if rows else mo.callout(mo.md("Press the button above to fill this table."), kind="info")
    return details, results, score


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🏢 In the enterprise:** `pass` is a keyword check and `latency_s` is
    > one laptop on one afternoon. The page Nadia's manager signs needs the
    > same four columns measured on the ten questions her users actually ask,
    > with the model pinned, and re-run every time the prompt, the tools or
    > the corpus change. A result that is not re-run is a result that was
    > true once. Keep the harness; the numbers are disposable.

    ### ❓ Question #3

    A correct answer can hide a wasteful trajectory. For each approach, look
    at `calls`, `evidence_chars` and `latency_s` next to `pass`. Your endpoint
    has a latency budget and a token budget per question. Which column would
    push you over first on your corpus, and what is the one change to the
    tools — not the model — that would bring it back?

    **Answer:**

    ---
    ## Task 4 — Inspect the difference

    There is no universal winner, and the two tables below are the honest way
    to say so: the per-approach averages first, then every case side by side
    with its prediction, so you can see *which column moved on which shape of
    question* rather than two numbers that hide the mechanism.

    **How each column is computed** — all of it is in `score()` in Task 3,
    and none of it involves a model judging a model:

    | Column | What it checks | Where it comes from |
    | --- | --- | --- |
    | **pass** | every string in the case's `expected_terms` appears in the answer, case-insensitive — `all(term in answer.lower() for term in expected_terms)` | `eval_cases.jsonl`, written before any run |
    | **cited** | any name in the case's `expected_pages` appears in the answer text | same file |
    | **calls** | the length of the trace — how many tool calls the loop made before the model answered | `run_agent` |
    | **chars** | the total characters every tool result returned, the nearest thing to tokens-read without a tokenizer | `run_agent` |
    | **favours** | the approach the question was written to reward, and why | same file, decided before the run |
    | **pass**, when `must_decline` is set | the answer contains a refusal ("not", "no data", "cannot"…) **and** none of the listed terms — it said no and invented nothing | the `decline` case |

    So a ❌ means *the reviewed words were not in the answer*, which is not
    the same as *the answer was wrong*. When a row surprises you, read the
    answer and the trace at the bottom of this task before trusting the mark:
    a plain keyword check is auditable precisely because it is this dumb, and
    the first time it disagrees with you it is usually the label that needs
    fixing. That is also the first thing the challenge asks you to do on your
    own corpus.

    - Agentic RAG is economical when a query maps cleanly to a few sections —
      `broad_churn`, `broad_incident` — because ranking returns the best
      sections at a fixed cost whatever the corpus size.
    - DCI earns its extra navigation when the words in the question are not
      the words on the page (`vocabulary`), when the answer sits past the
      retriever's cap (`deep_section`), or when the question is "which pages
      mention X" (`which_pages`) — which, on a service desk, is most of the
      hard tickets.
    - DCI also gives the model broader raw access. In production, page
      listing and reads must enforce the caller's permissions.
    - Both approaches can loop badly. Bound turns, record traces, and test
      incomplete evidence.
    - Neither interface can say "nothing matched" — a ranked search returns
      its top-k and a grep returns its hits. `decline` tests whether the
      *loop* says so. Your endpoint will need the same behaviour, and a
      labelled question to prove it.
    """)
    return


@app.cell
def _(mo, results):
    if len(results):
        summary = results.groupby("approach").agg(
            pass_rate=("pass", "mean"), citation_rate=("cited_expected_page", "mean"),
            avg_calls=("calls", "mean"), avg_evidence_chars=("evidence_chars", "mean"),
            avg_latency_s=("latency_s", "mean"),
        )
        SUMMARY_PANEL = summary
    else:
        summary = None
        SUMMARY_PANEL = mo.callout(mo.md("Run Task 3 first."), kind="info")

    SUMMARY_PANEL
    return


@app.cell
def _(mo, results, ui):
    if len(results):
        SIDE_BY_SIDE = []
        for case_id in results["id"].unique():
            rag_row = results[(results["id"] == case_id) & (results["approach"] == "Agentic RAG")].iloc[0]
            dci_row = results[(results["id"] == case_id) & (results["approach"] == "DCI Wiki")].iloc[0]
            SIDE_BY_SIDE.append({
                "case": case_id,
                "favours": rag_row["favours"],
                "RAG pass": "✅" if rag_row["pass"] else "❌",
                "DCI pass": "✅" if dci_row["pass"] else "❌",
                "RAG calls": int(rag_row["calls"]),
                "DCI calls": int(dci_row["calls"]),
                "RAG chars": f"{int(rag_row['evidence_chars']):,}",
                "DCI chars": f"{int(dci_row['evidence_chars']):,}",
            })
        SIDE_PANEL = ui.table(SIDE_BY_SIDE, title="Predicted against observed — which column moved on which shape of question")
    else:
        SIDE_BY_SIDE = []
        SIDE_PANEL = mo.md("")

    SIDE_PANEL
    return


@app.cell
def _(CASES, details, mo):
    TRACE_BLOCKS = []
    for trace_case in CASES:
        if (trace_case["id"], "Agentic RAG") not in details:
            continue
        block = [f"### `{trace_case['id']}` — {trace_case['question']}\n\n<sub>favours **{trace_case.get('favours', 'either')}** · {trace_case.get('why', '')}</sub>"]
        for approach_name in ("Agentic RAG", "DCI Wiki"):
            trace_result = details[(trace_case["id"], approach_name)]
            trace_text = " → ".join(step["tool"] for step in trace_result["trace"]) or "(none)"
            block.append(f"**{approach_name}** · `{trace_text}`\n\n> {trace_result['answer']}")
        TRACE_BLOCKS.append("\n\n".join(block))

    mo.md("\n\n---\n\n".join(TRACE_BLOCKS)) if TRACE_BLOCKS else mo.md("")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🔀 If your corpus is not a wiki:** DCI needs stable page names,
    > headings, and an index someone maintains. A SharePoint of PDFs has none
    > of those, and the honest first move is to *make* the wiki — convert,
    > name, index — before comparing anything. If nobody will own that index,
    > the comparison is already decided, and the page should say so.

    ### ❓ Question #4

    `read_page` returns up to 12,000 characters of whichever page the model
    names, and `list_pages` shows it every page there is. Nadia's
    data-handling page bars any automated tool from a record under legal
    hold. For *your* corpus: what does per-user authorisation look like on
    `list`, `search` and `read`, which of the two approaches can you actually
    get approved, and what would change your mind?

    **Answer:**

    ---
    # Conclusion

    You gave one agent two ways to investigate the same seven pages and held
    everything else constant. The RAG side saw ranked sections and could
    search again; the DCI side saw an index, a grep and whole pages and
    decided for itself. The scoring is plain on purpose, and the four columns
    next to it — citations, calls, evidence volume, latency — are what turn a
    pass rate into a page someone can sign.

    The retrieval row on Nadia's page, filled in: *DCI over the wiki for the
    service desk, because the hard tickets are exact codes and two-page
    procedures; Agentic RAG held in reserve for the day the corpus stops
    being a wiki; the interface enforces the caller's permissions and the
    legal-hold filter before it enforces anything else; what would change
    her mind is a corpus change — pages without stable names — not a model
    change.*

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Retriever | Local BM25 over `##` sections | Dense or hybrid retrieval with reranking, an index that is rebuilt when a page changes, and a record of which index version answered |
    | Corpus interface | Every page visible to the one user in the room | Per-user authorisation on `list`, `search` and `read`, enforced in the tool, with the legal-hold filter applied before ranking |
    | The wiki | Seven hand-maintained Markdown pages and one index | Generated navigation, link validation, an owner per page, and a freshness date the agent can see |
    | Answer check | Reviewed terms must appear in the answer | Human-calibrated semantic and citation judgement, on the ten questions users actually ask |
    | Agent loop | In-process tools, six turns, a timing | Timeouts and rate limits per tool, a trace per run kept as an artifact, and a budget the loop cannot exceed |
    | The decision | One run, one afternoon | Re-run on every prompt, tool or corpus change, with the result that is not re-run treated as stale |

    The decision is conditional: **choose the cheapest interface that passes
    your reviewed questions, then write down what kind of corpus change would
    make you reconsider.**

    ---
    # Additional Context

    - [LiteLLM — function calling](https://docs.litellm.ai/docs/completion/function_call) — the tool-call shape both loops use, and how to make it work against your own endpoint
    - [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — Yao et al., 2022. The loop in Task 2 is a ReAct loop with a budget; §3 is enough
    - [Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG](https://arxiv.org/abs/2501.09136) — where the RAG side of this notebook sits among the loops a model can drive
    - [BM25: The Probabilistic Relevance Framework](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) — the forty lines behind `rank_bm25`; §3 for the intuition
    - [Anthropic — Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) — the cheapest improvement to a chunk retriever, and a reason a section-level chunk often beats a fixed-size one
    - [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — the case for simple loops with good tools over orchestration, which is the design choice this session holds constant
    - [Model Context Protocol](https://modelcontextprotocol.io/) — the standard shape `list`, `search` and `read` take when the corpus interface becomes a service other teams call
    - **Keep building:** add one question from your own project that needs exact text and one that needs evidence from two pages, label the pages and the terms *before* running either approach, and see which column moves.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Bonus Tasks

    Optional. The first is worth doing tonight; the rest are meaningfully
    harder.

    ## Your own two questions

    Add one question that requires exact text and one that requires evidence
    from two pages. Label the pages and the answer terms before running
    either approach — that order is the discipline the challenge grades.
    """)
    return


@app.cell
def _(mo):
    MY_CASES = [
        # {"id": "mine_exact", "question": "…", "expected_terms": ["…"], "expected_pages": ["northline_glossary.md"]},
        # {"id": "mine_two_pages", "question": "…", "expected_terms": ["…", "…"], "expected_pages": ["…", "…"]},
    ]

    my_button = mo.ui.run_button(label=f"Run my {len(MY_CASES)} case(s)", disabled=not MY_CASES)
    my_button
    return MY_CASES, my_button


@app.cell
def _(
    DCI_FUNCS,
    DCI_TOOLS,
    MY_CASES,
    RAG_FUNCS,
    RAG_TOOLS,
    mo,
    my_button,
    run_agent,
    score,
    ui,
):
    if my_button.value and MY_CASES:
        MY_ROWS = [
            {"id": my_case["id"], "approach": approach, **score(my_case, run_agent(my_case["question"], tools, funcs))}
            for my_case in MY_CASES
            for approach, tools, funcs in [("Agentic RAG", RAG_TOOLS, RAG_FUNCS), ("DCI Wiki", DCI_TOOLS, DCI_FUNCS)]
        ]
        MY_PANEL = ui.table(MY_ROWS, title="Your cases")
    else:
        MY_ROWS = []
        MY_PANEL = mo.md("<sub>Fill in `MY_CASES`, then press the button.</sub>")

    MY_PANEL
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Harder

    - **Swap the retriever, keep the experiment.** Replace `BM25Okapi` with a
      dense index — `litellm.embedding(**CFG.embed_kwargs(), input=[...])`
      over the same sections, cosine for scoring — and re-run Task 3. The
      only cell that changes is `search_chunks`. If the pass rate moves, you
      learned something about the retriever; if the DCI column moves, you
      have a bug.
    - **Make the interface enforce permissions.** Give `read_page` and
      `grep_wiki` a `caller` argument and a page-level allow-list; mark one
      page as held under `LH-0088`. Confirm the agent reports incomplete
      evidence rather than an answer when the page it needs is barred.
    - **Bound the cost, not the turns.** Replace `max_turns` with a budget in
      evidence characters and stop the loop when it is spent. Which approach
      hits the budget first on the cross-page case?
    - **Break the wiki.** Rename one page without updating the index, re-run
      the DCI side, and watch what the trace does. That is the freshness
      failure the production table names, and it is cheaper to see here.
    """)
    return


if __name__ == "__main__":
    app.run()
