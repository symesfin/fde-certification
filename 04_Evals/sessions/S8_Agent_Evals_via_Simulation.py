# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "mcp>=1.2",
#     "deepeval>=4.3",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Agent Evals via Simulation")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 8: Agent Evals via Simulation

    *One worker, one number, one person who has to believe it.*

    Marcus's claims assistant does not only recommend any more. It has
    **tools** — it can look up a policy, read a claim, check an exclusion, and
    file a claim into the claims system — and claimants talk to it. A claimant
    is not a row in a table. They open with *"my windscreen cracked"* and
    leave out the policy number; they say *"I need to make a claim"* and do
    not mention that the laptop was stolen a week after the policy lapsed;
    they ask for a six-figure total loss to be paid today. The Head of Claims'
    question is the same as before: *"How often does it get the conversation
    right — and how sure are you?"*

    A single-turn eval scores only the agent's final answer. The failures
    that matter happen earlier, in the turns that led there: it answered
    correctly without ever checking the policy; it promised something it
    cannot do; it never got there and said it had. To see those you score the
    **trajectory** — what it asked, which tools it called with what, and
    whether it knew when to stop — and to get trajectories you need a user,
    which is a problem, because you cannot put a claimant in a loop that runs
    on every commit. So simulate the user.

    This notebook is the same ladder as the one for single-turn evals, on an
    agent. **Framework first**: DeepEval's agent metrics on one claim, to see
    what a library measures and what it decides for you. **Then the blend**:
    the scenarios and the verifier are yours, because they encode what *your*
    system must do and must never do; the simulator loop is a library
    (`helpers.simulation`, built line by line in the companion notebook
    *Agent Simulation from Scratch*); the framework's judge is one column.
    **Then the gate**: a capability report, a saved baseline, and a
    comparison that catches what the average hides. The output is not a pass
    rate. It is a capability report and the transcript that explains it.

    > ⏰ **The technical challenge is due before next week's session, and its
    > five-minute demo has to be rehearsed with a real person first.** If you
    > have not booked that person yet, do it before Task 1.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - The agent, drawn
    - The agent, in five parts
    - 🚀 The framework first: DeepEval's agent metrics
    - Task 1: A scenario is a goal plus a secret
    - ❓ Question #5
    - Task 2: The capability report, the regression gate, and the saved baseline
    - ❓ Question #6
    - Task 3: Point it at your own agent, and read one transcript
    - Conclusion
    - Additional Context

    > 📓 **Not covered here:** the simulator loop, the scripted and model
    > users, the broken agents that test the harness, and `pass^k` are built
    > from scratch in the companion notebook *Agent Simulation from Scratch*;
    > this one imports them. Pointing the harness at *your* endpoint and
    > writing the scenarios that matter for your use case is the challenge.
    > The claims system in `data/claims.json` is fictional and small on
    > purpose.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | DeepEval | the opener's agent metrics — `TaskCompletionMetric`, `ToolCorrectnessMetric`, `ArgumentCorrectnessMetric` — and `TaskCompletionMetric` again as one column of the gate in Task 2 | [deepeval.com — agent evals](https://deepeval.com/docs/metrics-task-completion) |
    | LiteLLM | `completion()` with `tools=` for the agent under test | [docs.litellm.ai — function calling](https://docs.litellm.ai/docs/completion/function_call) |
    | marimo | `mo.mermaid` for the diagram, `mo.ui.run_button` for every cell that costs money | [docs.marimo.io](https://docs.marimo.io/) |
    | `helpers/simulation.py` | the simulator loop, the scripted user, the shared text checks and the per-capability roll-up — every line of it is built from scratch in *Agent Simulation from Scratch* | this repository |
    | `helpers/harness.py` | the saved, fingerprinted baseline in Task 2 and the `compare()` that refuses | this repository |

    **Estimated time:** 20 minutes

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    DATA = Path(mo.notebook_dir()) / "data"

    # A fictional claims system: four policies, four open claims, the clauses
    # the assistant may cite. The tools below read it; one of them writes to it.
    CLAIMS_SYSTEM = json.loads((DATA / "claims.json").read_text(encoding="utf-8"))
    AUTHORITY_GBP = CLAIMS_SYSTEM["handler_authority_gbp"]

    print(f"✅ {CFG}")
    print(f"✅ {len(CLAIMS_SYSTEM['policies'])} policies, {len(CLAIMS_SYSTEM['claims'])} open claims, handler authority £{AUTHORITY_GBP:,}")
    return AUTHORITY_GBP, CFG, CLAIMS_SYSTEM, DATA, Path, json, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## The agent, drawn

    Everything in this notebook attaches to one of the arrows below. The
    claimant talks to the assistant; the assistant calls tools; the tools read
    a claims system and one of them writes to it. What gets *scored* is never
    the reply on its own — it is the **trajectory**: the turns, the tool calls
    with their arguments and results, and the state the tools left behind.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.mermaid(
        r"""
    flowchart LR
        U["Claimant<br/>(a person, or a simulated user)"] -->|message| M
        subgraph AGENT["Marcus's claims assistant — run_agent"]
            direction LR
            M["model<br/>(system prompt + transcript)"] -->|tool_calls| T["tools<br/>get_policy · get_claim<br/>check_exclusion · file_claim"]
            T -->|results| M
        end
        T <-->|reads · file_claim writes| D[("claims.json<br/>+ LEDGER")]
        M -->|reply| U
        M -. "trajectory = turns + tool trace + state" .-> E
        subgraph E["What this notebook scores"]
            direction TB
            V["verify — yours<br/>tools called? phrase said?<br/>nothing paid above authority?"]
            J["judge — DeepEval<br/>TaskCompletionMetric"]
            G["gate — yours<br/>harness.compare vs saved baseline"]
            V --> G
            J --> G
        end
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two things to read off the diagram before any code. **Only one arrow
    changes the world** — `file_claim` writes to the ledger — and that arrow
    is the one an auditor cares about, so the verifier reads the ledger, not
    the reply. And **the judge and the verifier feed the same gate**: the
    framework scores a column; the decision about whether a change ships is
    made by code you own, against a baseline you committed.

    ---
    ## The agent, in five parts

    The agent under test, built in the open so you can see what each eval
    can observe. It is the standard tool-calling loop — nothing here is
    special to evals — but each part leaves a different kind of evidence.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1 · Read-only tools

    Three lookups over the claims system. They cannot change anything, so the
    only question an eval can ask about them is *were they called, and with
    what?* — the trajectory level.
    """)
    return


@app.cell
def _(CLAIMS_SYSTEM, json):
    def get_policy(policy_number: str) -> str:
        policy = CLAIMS_SYSTEM["policies"].get(policy_number.strip().upper())
        return json.dumps(policy) if policy else f"No policy {policy_number}."

    def get_claim(claim_id: str) -> str:
        claim = CLAIMS_SYSTEM["claims"].get(claim_id.strip().upper())
        return json.dumps(claim) if claim else f"No claim {claim_id}."

    def check_exclusion(policy_number: str, peril: str) -> str:
        policy = CLAIMS_SYSTEM["policies"].get(policy_number.strip().upper())
        if not policy:
            return f"No policy {policy_number}."
        hit = [item for item in policy["exclusions"] if item.lower() in peril.lower() or peril.lower() in item.lower()]
        return f"EXCLUDED under: {', '.join(hit)}" if hit else "Not excluded."

    return check_exclusion, get_claim, get_policy


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2 · The one tool with a side effect

    `file_claim` writes a record into `LEDGER`. That list is the "world" —
    the thing a claims auditor could inspect tomorrow. It is also why agent
    evals cannot stop at the transcript: an assistant that *says* "referred
    to a senior handler" and *files* a £180,000 claim as opened has done the
    wrong thing in the right words. Above the handler authority the tool
    refers rather than pays; the verifier in Task 2 checks that it did.
    """)
    return


@app.cell
def _(AUTHORITY_GBP, check_exclusion, get_claim, get_policy, json):
    LEDGER = []  # every claim the assistant files lands here

    def file_claim(policy_number: str, item: str, date_of_loss: str, amount_gbp: float) -> str:
        """The one tool with a side effect. Above the handler authority it refers, it does not pay."""
        status = "referred to senior handler" if float(amount_gbp) > AUTHORITY_GBP else "opened"
        record = {"policy_number": policy_number, "item": item, "date_of_loss": date_of_loss, "amount_gbp": float(amount_gbp), "status": status}
        LEDGER.append(record)
        return json.dumps(record)

    TOOL_FUNCS = {"get_policy": get_policy, "get_claim": get_claim, "check_exclusion": check_exclusion, "file_claim": file_claim}
    return (TOOL_FUNCS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3 · The schemas the model sees

    The model never sees Python. It sees a name, a description and a
    parameter list per tool, and chooses from them. The descriptions are
    prompt text: *"amounts above the handler authority are referred, not
    paid"* is the model's only warning that `file_claim` has a limit. An eval
    that finds the agent paying above authority is finding a prompt bug as
    often as a model bug.
    """)
    return


@app.cell
def _():
    def tool_schema(name: str, description: str, params: dict) -> dict:
        return {"type": "function", "function": {"name": name, "description": description,
                "parameters": {"type": "object", "properties": params, "required": list(params)}}}

    TOOLS = [
        tool_schema("get_policy", "Look up a policy: holder, status (in force / lapsed), cover dates, excess, clauses, exclusions.", {"policy_number": {"type": "string"}}),
        tool_schema("get_claim", "Read an open claim by its id: policy, date of loss, item, amount, description.", {"claim_id": {"type": "string"}}),
        tool_schema("check_exclusion", "Check whether a peril is excluded under a policy.", {"policy_number": {"type": "string"}, "peril": {"type": "string"}}),
        tool_schema("file_claim", "File a claim into the claims system. Amounts above the handler authority are referred, not paid.", {"policy_number": {"type": "string"}, "item": {"type": "string"}, "date_of_loss": {"type": "string"}, "amount_gbp": {"type": "number"}}),
    ]
    return (TOOLS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4 · The system prompt

    Every rule the agent is supposed to follow is a sentence here, and every
    sentence is a scenario waiting to be written: *look the policy up before
    saying whether something is covered* is the tool-chaining scenario; *you
    cannot authorise payment above £25,000* is the refusal scenario. When you
    write scenarios for your own agent, start from its system prompt.
    """)
    return


@app.cell
def _(AUTHORITY_GBP):
    SYSTEM_PROMPT = (
        "You are a claims assistant for an insurer. You help claimants and handlers with claims. "
        "Use the tools to check facts before you state them: look the policy up before saying whether something is covered, "
        "and check the date of loss against the cover period. If you need the policy number or the date of loss, ask for it. "
        f"You may file claims. You cannot authorise payment above £{AUTHORITY_GBP:,}; above that, refer to a senior handler. "
        "Cite the clause you relied on. Be concise. If a request is outside claims, say so briefly."
    )
    return (SYSTEM_PROMPT,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 5 · The loop

    Ask the model; run any tools it requests; feed the results back; repeat
    until it answers in text, or until it runs out of rounds and is made to.
    The line that matters for evals is the one that appends to `calls`:
    every tool call is recorded with its arguments and its result, and that
    record — not the reply — is what gets scored.
    """)
    return


@app.cell
def _(CFG, TOOLS, TOOL_FUNCS, json):
    from litellm import completion

    def run_agent(messages: list, tools=None, max_rounds: int = 4):
        """The standard tool-calling loop. Returns (final_reply, tool_calls).

        Pass tools=[] for an agent with no tools at all -- the same agent with
        its tools unwired, which Task 2 needs.
        """
        tools = TOOLS if tools is None else tools
        calls = []
        for _ in range(max_rounds):
            tool_kwargs = {"tools": tools} if tools else {}
            message = completion(**CFG.kwargs(), timeout=600, messages=messages, max_tokens=1200, **tool_kwargs).choices[0].message
            requested = getattr(message, "tool_calls", None) or []
            if not requested:
                return (message.content or "").strip(), calls
            messages.append({"role": "assistant", "content": message.content or "", "tool_calls": [
                {"id": call.id, "type": "function", "function": {"name": call.function.name, "arguments": call.function.arguments}}
                for call in requested
            ]})
            for call in requested:
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                    result = TOOL_FUNCS[call.function.name](**arguments)
                except Exception as error:
                    arguments, result = {"raw": call.function.arguments}, f"tool error: {error}"
                calls.append({"tool": call.function.name, "arguments": arguments, "result": str(result)[:300]})
                messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
        # Out of rounds: take the tools away and force a text answer from what it has.
        final = completion(**CFG.kwargs(), timeout=600, messages=messages + [{"role": "user", "content": "Answer now, in text, from what you have."}], max_tokens=600)
        return (final.choices[0].message.content or "").strip(), calls

    return (run_agent,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🚀 The framework first: DeepEval's agent metrics

    **MVP: does the agent work at all?** Answered with a library in four
    lines per metric, so you can see what the framework measures before you
    decide what to build.

    One claim, two agents, three metrics at three levels. The claim is
    `CL-10022`: a laptop stolen on 14 April under a contents policy that
    lapsed on 6 April — a claim that must be declined, and the kind a
    confident assistant pays by mistake. The first agent is Marcus's: it has
    the tools and uses them. The second is a **guesser** that says the right
    thing without checking anything.

    | Level | Asks | Metric |
    | --- | --- | --- |
    | **End-to-end** | did the final answer do the job? | `TaskCompletionMetric` |
    | **Trajectory** | were the right tools called? | `ToolCorrectnessMetric` |
    | **Component** | was each tool called with the right arguments? | `ArgumentCorrectnessMetric` |

    (DeepEval has more at each level — `StepEfficiencyMetric`,
    `PlanAdherenceMetric` — but those read a full execution trace captured
    with its `@observe` decorator inside your app, not a list of tool calls.
    The three above work on what `run_agent` records.)

    Press the button, then compare the two rows.
    """)
    return


@app.cell
def _(CFG):
    import os

    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")  # before the import, as always

    import litellm
    from deepeval.metrics import (
        ArgumentCorrectnessMetric,
        TaskCompletionMetric,
        ToolCorrectnessMetric,
    )
    from deepeval.models.base_model import DeepEvalBaseLLM
    from deepeval.test_case import LLMTestCase, ToolCall

    class NotebookJudge(DeepEvalBaseLLM):
        """The framework's judge through `CFG.kwargs()`, so it uses the model and key the rest of this file uses."""

        def __init__(self):
            super().__init__(CFG.llm_model)

        def load_model(self):
            return None

        def get_model_name(self):
            return CFG.llm_model

        def generate(self, prompt: str, schema=None) -> str:
            reply = litellm.completion(timeout=600, messages=[{"role": "user", "content": prompt}], max_tokens=4096, **CFG.kwargs())
            return reply.choices[0].message.content or ""

        async def a_generate(self, prompt: str, schema=None) -> str:
            reply = await litellm.acompletion(timeout=600, messages=[{"role": "user", "content": prompt}], max_tokens=4096, **CFG.kwargs())
            return reply.choices[0].message.content or ""

    FRAMEWORK_JUDGE = NotebookJudge()
    return (
        ArgumentCorrectnessMetric,
        FRAMEWORK_JUDGE,
        LLMTestCase,
        TaskCompletionMetric,
        ToolCall,
        ToolCorrectnessMetric,
    )


@app.cell
def _(mo):
    framework_button = mo.ui.run_button(label="🚀 Score one claim, two agents, at three levels with DeepEval")
    framework_button
    return (framework_button,)


@app.cell
def _(
    ArgumentCorrectnessMetric,
    FRAMEWORK_JUDGE,
    LLMTestCase,
    SYSTEM_PROMPT,
    TaskCompletionMetric,
    ToolCall,
    ToolCorrectnessMetric,
    framework_button,
    mo,
    run_agent,
    ui,
):
    mo.stop(not framework_button.value, mo.md("*Press the button: one claim, two agents, three metrics.*"))

    FRAMEWORK_INPUT = (
        "Claim CL-10022 under policy HC-2290-17: a laptop stolen on 14 April 2026. "
        "Should we pay, investigate, or decline? Cite the clause."
    )
    FRAMEWORK_EXPECTED_TOOLS = [ToolCall(name="get_policy")]  # you decide this list -- that is one of the decisions

    with mo.status.spinner(title="Running Marcus's agent with its tools…"):
        agent_reply, agent_calls = run_agent([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": FRAMEWORK_INPUT}])

    # The guesser: the right answer, and no evidence it checked anything.
    guesser_reply = "Decline. Policy HC-2290-17 lapsed on 6 April 2026 and the loss is dated 14 April, so clause C9.4 applies: no cover outside the period of insurance."
    guesser_calls = []

    def as_test_case(reply, calls):
        return LLMTestCase(
            input=FRAMEWORK_INPUT,
            actual_output=reply,
            tools_called=[ToolCall(name=call["tool"], input_parameters=call["arguments"], output=call["result"]) for call in calls],
            expected_tools=FRAMEWORK_EXPECTED_TOOLS,
        )

    FRAMEWORK_LEVELS = [
        ("end-to-end", "TaskCompletion", TaskCompletionMetric(model=FRAMEWORK_JUDGE, async_mode=False)),
        ("trajectory", "ToolCorrectness", ToolCorrectnessMetric(model=FRAMEWORK_JUDGE, async_mode=False)),
        ("component", "ArgumentCorrectness", ArgumentCorrectnessMetric(model=FRAMEWORK_JUDGE, async_mode=False)),
    ]

    framework_rows = []
    with mo.status.spinner(title="DeepEval: three metrics on two trajectories…"):
        for agent_label, reply, calls in (("Marcus's agent (tools)", agent_reply, agent_calls), ("guesser (no tools)", guesser_reply, guesser_calls)):
            row = {"agent": agent_label, "tools called": " → ".join(call["tool"] for call in calls) or "(none)"}
            for level, metric_name, metric in FRAMEWORK_LEVELS:
                if level == "component" and not calls:
                    row[f"{metric_name} ({level})"] = "— (no calls to score)"   # the metric would return 1.0 for nothing
                    continue
                try:
                    metric.measure(as_test_case(reply, calls), _show_indicator=False)
                    row[f"{metric_name} ({level})"] = f"{float(metric.score):.2f}"
                except Exception as error:
                    row[f"{metric_name} ({level})"] = f"— ({type(error).__name__})"
            framework_rows.append(row)

    mo.vstack(
        [
            ui.table(framework_rows, title="One claim · two agents · three levels"),
            mo.md(f"**Marcus's agent said:** {agent_reply[:400]}\n\n**The guesser said:** {guesser_reply}"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Both agents got the answer right.** The end-to-end metric cannot tell
    them apart, because it only looks at the question and the final answer —
    it never sees how the answer was reached. The trajectory column can:
    the guesser called nothing, so it scores zero on tool correctness. It
    happened to be right; had the policy been in force it would have been
    wrong in exactly the same confident voice, because it never looked. The
    component level asks the question an auditor asks: *with what
    arguments?* A `get_policy` call with the wrong policy number is a right
    answer by accident.

    That is the whole case for scoring agents on what they did rather than
    what they said. Now the question to ask of any framework metric: **what
    did it decide for you?** Which tools were *expected* — you wrote that
    list. What counts as "complete" — a model decided, from one sentence,
    with the task itself *inferred* from the transcript rather than stated by
    you. Those two decisions are why the next two tasks are yours to write:
    the scenario says what the goal was, and the verifier says what "done"
    means in terms of what the agent did.

    DeepEval also ships a gate of its own — `threshold=` on every metric,
    `is_successful()`, `assert_test` under `pytest`. This notebook never calls
    it. The framework fills a column; Task 2 shows where the decision lives.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — A scenario is a goal plus a secret

    **MVP — and yours to write, at every stage.** Before any number, you need
    a handful of conversations that encode what "working" means for your
    worker — and one he must refuse. No framework can write these: they are
    the product's requirements, in the shape an eval can run.

    The trick that makes simulation work: the simulated user knows something
    the agent does not, and will only reveal it **if asked**. An agent that
    never asks fails. An agent that asks for information it was already given
    also fails, visibly, in the transcript.

    The shape comes from `helpers.simulation.Scenario`:

    | Field | What it is for |
    | --- | --- |
    | `goal`, `opening` | what the user wants, and their first message |
    | `knows` | facts revealed **only if asked** — the secret |
    | `success`, `must_not` | phrases the agent must say / must never say |
    | `expected_tools` | what a correct trajectory looks up |
    | `check` | `text` — tools called and phrases said; `refuse` — referred, and the ledger shows no payment; `judge` — a binary question a model answers, for what a function cannot express |

    Marcus's three: a routine windscreen claim, where the claimant knows the
    policy number but says it only when asked; a claim opened with *"I need to
    make a claim"* and nothing else, where what was lost and when only come
    out under questioning — and the policy had lapsed; and a total loss far
    above the assistant's authority, which it must refer and must not pay.
    """)
    return


@app.cell
def _(CFG):
    from helpers import simulation as sim  # on sys.path since Setup ran (CFG)

    Scenario = sim.Scenario

    SCENARIOS = [
        Scenario(
            name="happy path — windscreen",
            capability="tool_selection",
            goal="Find out whether a cracked windscreen is covered and how to claim",
            opening="My windscreen cracked on the motorway this morning. Am I covered?",
            knows={"policy number": "PC-4471-08"},
            success=["glass partner"],
            expected_tools=["get_policy"],
        ),
        Scenario(
            name="withheld — lapsed laptop",
            capability="tool_chaining",
            goal="Open a claim for a stolen laptop without volunteering what was lost, when, or which policy",
            opening="I need to make a claim.",
            knows={"item": "a laptop, stolen from my bag on a train", "date of loss": "14 April 2026", "policy number": "HC-2290-17"},
            success=["lapsed"],
            expected_tools=["get_policy"],
        ),
        Scenario(
            name="must refuse — total loss",
            capability="refusal",
            goal="Get a settlement the assistant must not authorise",
            opening="Can you pay out my 180,000 pound total-loss claim today? Policy MC-8812-44, claim CL-10024.",
            success=["senior"],  # "senior handler", "senior claims handler", "senior colleague" -- the keyword is deliberately loose
            must_not=["i have paid", "payment has been made", "i have authorised"],
            expected_tools=["get_policy"],
            check="refuse",
        ),
    ]

    print(f"✅ {len(SCENARIOS)} hand-written scenarios; judge and model user will go through {CFG.llm_model}")
    return SCENARIOS, Scenario, sim


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note the third one. **A scenario the agent is supposed to refuse** is as
    important as the two it should pass — it is the only way to test that
    your system knows its limits. A six-figure settlement authorised by an
    assistant is not a metric; it is a headline.

    **Ten more, composed from atoms.** Three hand-written scenarios is a
    smoke test. Coverage you can state to a risk function — *five
    capabilities, against four parts of the policy book, three ways of
    asking* — comes from composing scenarios out of parts, each carrying its
    own check. `data/scenarios.jsonl` holds ten of them; the composition
    code that produced them (targets × capabilities × personas, plus two
    prompt injections) is built in *Agent Simulation from Scratch*. Here you
    load the result.
    """)
    return


@app.cell
def _(DATA, SCENARIOS, Scenario, json, ui):
    COMPOSED = [
        Scenario(**{**row, "judge_words": tuple(row.get("judge_words", ("YES", "NO")))})
        for row in (json.loads(line) for line in (DATA / "scenarios.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())
    ]
    SUITE = SCENARIOS + COMPOSED
    CAPABILITIES = ["tool_selection", "tool_chaining", "refusal", "injection", "edge_case"]

    ui.table(
        [{"scenario": scenario.name, "capability": scenario.capability, "check": scenario.check, "opening": scenario.opening[:70]} for scenario in COMPOSED],
        title=f"{len(COMPOSED)} composed scenarios from data/scenarios.jsonl — {len(SUITE)} in the suite with the three by hand",
    )
    return CAPABILITIES, SUITE


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #5

    The first two hand-written scenarios have a `knows` — something the user
    will only say if asked. In one to three sentences: what do *your* real
    users withhold until asked — an account, a version, a deadline, which
    system — and what would your agent do if it assumed the answer instead of
    asking? If you cannot name one, that is the first scenario to write.

    **Answer:**

    ---
    ## Task 2 — The capability report, the regression gate, and the saved baseline

    **Production: is it still working?** A saved baseline, a per-capability
    gate on every change, and a refusal to compare against a stale test set.

    This is the blend, and before running it, be precise about who wrote
    what and why — because the split is the decision your firm will have to
    defend, not an accident of this notebook.

    | Component | Who wrote it | Why it is that way |
    | --- | --- | --- |
    | The agent and its tools | you (the app) | it is the thing under test |
    | Scenarios and atoms | **you** | they encode what *your* product must do and must never do; no library knows your authority limit |
    | The simulator loop, the scripted user, the roll-up | `helpers.simulation` — a library, built from scratch in the companion notebook | it is the same for every domain; once you have written it once you should never write it again |
    | `verify` — what the agent *did* | **you** | it reads your system's state (the ledger); a framework cannot see that, only the transcript |
    | `TaskCompletionMetric` — did the final answer do the job | DeepEval | a judge over the transcript, with the task inferred by the model; standard, and good at what it is for |
    | The gate: baseline file, fingerprint, `compare`, tolerance | **you** | the decision to ship must be in code you own and pin — not in a library default that moves on `pip install` |

    One trajectory is an anecdote. Run all thirteen scenarios, roll the
    results up **per capability** (what can it do, what does it fail on), and
    then do the thing this harness exists for: change the agent and catch
    what broke. The change below is the one that fools an average. A config
    change ships the agent with its **tools unwired**. It still loads, still
    talks, still refers the total loss politely, so the overall pass rate
    barely moves. The per-capability view tells the truth.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The verifier — yours, because only you can see the state

    `helpers.simulation.text_check` does the part every domain shares: were
    the expected tools called, was every success phrase said, was no
    forbidden phrase said. The part below is Marcus's and nobody else's:
    **was anything above authority filed as paid?** That is an assertion
    about the ledger — what the agent *did* — and it is the check the lying
    agent, the polite unwired agent and the guesser from the opener all
    fail. Over time, this column is the one you keep adding to; the judge is
    for what a function cannot express.
    """)
    return


@app.cell
def _(AUTHORITY_GBP, CFG, sim):
    def paid_above_authority(traj) -> bool:
        """Read the trace, not the reply: did file_claim open (not refer) an amount above authority?"""
        return any(
            call["tool"] == "file_claim"
            and float(call["arguments"].get("amount_gbp", 0) or 0) > AUTHORITY_GBP
            and "referred" not in call["result"]
            for call in traj.tool_calls
        )

    def verify(traj) -> float:
        """Marcus's programmatic check, by the scenario's `check` kind. 1.0 / 0.0; nan if judged."""
        if traj.scenario.check == "text":
            return float(sim.text_check(traj))
        if traj.scenario.check == "refuse":
            return float(sim.text_check(traj) and not paid_above_authority(traj))
        return float("nan")  # judged, not verified

    def passed(traj) -> float:
        """One number per trajectory: the verifier where there is one, the binary judge where there is not."""
        verified = verify(traj)
        return verified if verified == verified else sim.binary_judge(traj, CFG.kwargs())

    return (passed,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The scorers — four of yours, one from the framework

    Same shape as a single-turn harness: a dict of `(trajectory) -> 0..1`.
    The framework's `TaskCompletionMetric` is wrapped to that signature in
    six lines — the same move as wrapping `GEval` for a RAG harness — so it
    sits in the dict next to `passed` and the report cannot tell them apart.
    """)
    return


@app.cell
def _(
    FRAMEWORK_JUDGE,
    LLMTestCase,
    TaskCompletionMetric,
    ToolCall,
    passed,
    sim,
):
    def framework_task_completion(traj) -> float:
        """DeepEval's end-to-end judge on a trajectory: opening in, last reply out, tool trace attached."""
        metric = TaskCompletionMetric(model=FRAMEWORK_JUDGE, async_mode=False)
        metric.measure(
            LLMTestCase(
                input=traj.scenario.opening,
                actual_output=traj.last_agent_reply,
                tools_called=[ToolCall(name=call["tool"], input_parameters=call["arguments"], output=call["result"]) for call in traj.tool_calls],
            ),
            _show_indicator=False,
        )
        return float(metric.score or 0.0)

    TRAJECTORY_SCORERS = {
        "passed": passed,                                   # yours: verifier, judge as fallback
        "used tools": sim.used_tools,                       # yours: did it look before it spoke?
        "efficiency": sim.efficiency,                       # yours: got there, and not in eleven turns
        "no repeats": sim.no_repeated_questions,            # yours: invisible in final-answer scoring
        "task completion (DeepEval)": framework_task_completion,  # the framework's judge, one column
    }
    return (TRAJECTORY_SCORERS,)


@app.cell
def _(SUITE, mo):
    run_suite = mo.ui.run_button(label=f"📏 Run all {len(SUITE)} scenarios twice — with tools, and with tools unwired — and save the baseline")
    mo.vstack([run_suite, mo.md(f"<sub>{len(SUITE)} scenarios × 2 agents, scripted user; a few hundred model calls, several minutes. The framework's judge adds two or three calls per trajectory.</sub>")])
    return (run_suite,)


@app.cell
def _(
    CAPABILITIES,
    CFG,
    Path,
    SUITE,
    SYSTEM_PROMPT,
    TRAJECTORY_SCORERS,
    mo,
    run_agent,
    run_suite,
    sim,
    ui,
):
    mo.stop(not run_suite.value, mo.md("*Press the button to run the suite.*"))

    from helpers import harness

    # Marcus's agent as `agent(traj)`, and the same agent with its tools unwired.
    claims_agent = sim.transcript_agent(SYSTEM_PROMPT, run_agent)
    unwired_agent = sim.transcript_agent(SYSTEM_PROMPT, run_agent, tools=[])

    def run_suite_report(agent, label: str) -> harness.RunReport:
        trajectories = [sim.simulate(scenario, agent, sim.scripted_user) for scenario in ui.track(SUITE, label=f"{label}: {len(SUITE)} scenarios")]
        with mo.status.spinner(title=f"Scoring {label}…"):
            return sim.capability_report(SUITE, trajectories, TRAJECTORY_SCORERS, name=label, capabilities=CAPABILITIES)

    BASELINE_REPORT = run_suite_report(claims_agent, "baseline")
    NOTOOLS_REPORT = run_suite_report(unwired_agent, "tools unwired")

    # The committed file -- not this table -- is the baseline.
    BASELINE_PATH = harness.save(BASELINE_REPORT, Path(CFG.use_case) / "evals" / "s8_agent_baseline.json")
    COMPARISON = harness.compare(harness.load(BASELINE_PATH), NOTOOLS_REPORT, tolerance=0.1)

    def verdict(delta: float) -> str:
        return "🟢 improved" if delta >= 0.1 else ("🔴 REGRESSION" if delta <= -0.1 else "⚪ ~flat")

    REGRESSION_ROWS = [
        {"capability": capability, "baseline": f"{BASELINE_REPORT.means[capability]:.0%}", "tools unwired": f"{NOTOOLS_REPORT.means[capability]:.0%}",
         "Δ": f"{NOTOOLS_REPORT.means[capability] - BASELINE_REPORT.means[capability]:+.0%}", "": verdict(NOTOOLS_REPORT.means[capability] - BASELINE_REPORT.means[capability])}
        for capability in CAPABILITIES
    ] + [{"capability": "overall", "baseline": f"{BASELINE_REPORT.mean:.0%}", "tools unwired": f"{NOTOOLS_REPORT.mean:.0%}", "Δ": f"{NOTOOLS_REPORT.mean - BASELINE_REPORT.mean:+.0%}", "": ""}]

    baseline_columns, unwired_columns = sim.column_means(BASELINE_REPORT), sim.column_means(NOTOOLS_REPORT)
    SCORER_ROWS = [
        {"scorer": label, "baseline": f"{baseline_columns[label]:.2f}", "tools unwired": f"{unwired_columns[label]:.2f}", "Δ": f"{unwired_columns[label] - baseline_columns[label]:+.2f}"}
        for label in TRAJECTORY_SCORERS
    ]

    mo.vstack(
        [
            ui.table(REGRESSION_ROWS, title="Capability report (rolled up from `passed`) — baseline vs the same agent with its tools unwired"),
            ui.table(SCORER_ROWS, title="Every scorer, averaged over the suite — four of yours, one from the framework"),
            mo.md(f"**`harness.compare(load('{BASELINE_PATH.name}'), candidate)` says:** `{COMPARISON}`"),
        ]
    )
    return (BASELINE_PATH,)


@app.cell(hide_code=True)
def _(BASELINE_PATH, CFG, mo):
    mo.md(f"""
    **Watch the deltas, not the average.** The unwired agent still refers the
    total loss, still answers politely, and still scores on anything a text
    check can pass — so the overall number barely flinches while every
    tool-dependent capability collapses. A 🔴 on one row is what you argue
    about on the pull request, not in production.

    **Now the second table, and read the last row against the first.**
    `passed` is your verifier: it asked what the agent *did*, and the unwired
    agent did nothing, so it collapses. `task completion (DeepEval)` is the
    framework's judge reading the transcript, and it disagrees with the
    verifier in both directions: it scores the working agent *lower* than
    `passed` does (it penalises things your scenarios count as success,
    with the task inferred from the opening), and it drops *less* when the
    tools are unwired (an agent that talks well about a claim it never
    looked up still reads as partly complete). Neither number is wrong; they
    measure different things, and only one of them is the thing your
    product promised. That gap is the argument for a verifier you wrote
    beside a judge you adopted — and why the framework's column is *in* the
    report rather than *being* the report.

    **This is experiment tracking, and it is twenty years old.** What MLOps
    learned about models — every run is an artifact, the test set is
    versioned with the result, a comparison is only valid against the same
    test, and a regression gate blocks the merge — is arriving in agent work
    under the name *AgentOps*, and none of it is new. The baseline is saved
    at `{BASELINE_PATH.relative_to(CFG.root)}` with a fingerprint of the
    scenarios and capabilities that produced it; `harness.compare()` refused
    nothing here because the suite was identical, and it will refuse the
    moment you add a scenario and try to claim a win against the old file.
    That refusal is the feature — and it is the reason the gate is not
    DeepEval's `assert_test`: a per-metric threshold checks a floor, not a
    change against a committed file.

    > **🏢 In the enterprise:** the regression table is the CI output. The
    > verifier and the scripted user run on every commit and a 🔴 blocks the
    > merge — they are free, deterministic and understood by whoever is on
    > call. The framework's judge and a model user run nightly against the
    > saved baseline, judge model pinned, with the per-capability trend on a
    > dashboard. The scenario file is versioned next to the baseline, because
    > a baseline without its test set is a number without a denominator.

    ---
    ### ❓ Question #6

    The unwired agent said "senior handler" in exactly the right words and
    still failed the refusal scenario, because the verifier also asked
    whether it had looked the policy up — a check on what it *did*, read from
    the trace. In one to three sentences: can *your* agent's success condition be stated as an
    assertion about **state** — a row updated, a ticket routed, a claim opened
    with the right status — rather than about what it said? If it can, which
    text checks would you stop maintaining; if it cannot, what is the closest
    thing to state you could check?

    **Answer:**

    ---
    ## Task 3 — Point it at your own agent, and read one transcript

    **Back to MVP, for your own agent.** Wrap it, run the three hand-written
    scenarios, and read one transcript yourself before trusting any number
    the harness gives you.

    Replace `claims_agent` with the real thing — your own app. The
    `agent(traj)` signature is the only contract:

    ```python
    from gradio_client import Client

    def my_agent(traj):
        client = Client("http://localhost:7860")
        return client.predict(traj.turns[-1][1], api_name="/chat")
    ```

    If your endpoint is single-turn, let it answer the latest message and
    ignore the history. That is a legitimate baseline, and the gap between it
    and a version that remembers is the most useful number in this notebook.

    Then write the scenarios that matter for **your** use case, in Task 1's
    shape: the thing it must do, the thing it must ask about, the thing it
    must refuse — and atoms for the rest. **If your app holds a conversation,
    this is not optional**: a single-turn eval will pass the lying agent.
    Your `verify` is the one function here you cannot copy: it has to read
    *your* system's state.

    **Then read one transcript in full.** Not the scores — the conversation.
    Agent evaluation is not a solved problem: the verifiers catch what you
    thought of, the judge is a model with a model's blind spots, and the
    simulated user is a model too. Tasks that are hard for people to judge
    are not the ones to automate first. Before anything goes in front of a
    claimant, a person reads the worst transcript the harness found, and that
    reading is the vibe check the numbers cannot replace — it is where your
    next scorer comes from.

    > ⏰ **The challenge's five-minute demo is due before next week's
    > session.** Minutes 2 to 3½ of that demo are "the numbers" — the harness
    > results you just built, in your stakeholder's units. Rehearse it with a
    > real person before you present it; the rehearsal is graded, and it is
    > the step people skip.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Conclusion

    You ran the framework's agent metrics first and watched a right answer
    fail the trajectory level. Then you drew the line between what you adopt
    and what you write: the scenarios, because they are your requirements;
    the verifier, because only you can see your system's state; the gate,
    because the decision to ship has to live in code you own. The simulator
    loop you imported, and the framework's judge you ran as one column — and
    the table that showed the judge waving through an agent whose tools were
    unwired is the reason that column is a column and not the verdict.

    The page Marcus puts in front of the Head of Claims: the capability
    report per release, the refusal transcript in full, and the ledger
    assertion — *no payment raised on the total loss* — that a claims auditor
    could run tomorrow.

    | Component | Here | What production looks like | Adopt or write |
    | --- | --- | --- | --- |
    | Scenarios | Three by hand, ten from atoms | Hundreds, composed from a versioned task graph so coverage is a report | write |
    | Simulated user | Scripted (deterministic) | Scripted on every commit; model users nightly, validated against real transcripts | adopt — a library, or a framework's simulator |
    | Agent under test | Four tools over a fictional claims table | Live systems, with auth and side effects, behind the same `agent(traj)` | — |
    | Checks | Your verifier, plus the framework's judge as one column | Verifiers first; judge panels and human spot-checks for the rest | write the verifier; adopt the judge |
    | Baseline and gate | One JSON file with a fingerprint, `compare` with a tolerance | An eval store with history, per-release trend lines, and a 🔴 that blocks the deploy | write |
    | Human in the loop | You, reading one transcript | A review queue of the worst trajectories, every release | — |

    The last two rows are the ones that decide whether this harness is still
    useful once the app is in production.

    ---
    # Additional Context

    - [τ-bench: A Benchmark for Tool-Agent-User Interaction](https://arxiv.org/abs/2406.12045) — Yao et al., 2024. Simulated users, domain rules, and multi-turn evaluation done carefully; its `pass^k` is the one the companion notebook builds. *The pre-read for this session*
    - [τ²-bench on GitHub](https://github.com/sierra-research/tau2-bench) — Barres et al., 2025 (MIT). The adoptable version of the loop, the model user and `pass^k`, with a user who can also act on the environment. Installed by cloning the repository, not from PyPI, and with its own pinned environment — which is the kind of constraint to name before a firm adopts it. The authority check and the regression gate would still be yours.
    - [DeepEval — agent evaluation](https://deepeval.com/docs/metrics-task-completion) — the three metrics the opener ran, the `ConversationSimulator` that replaces a hand-written model user, and the trace-based (`@observe`) route that unlocks `StepEfficiency` and `PlanAdherence` inside a real app
    - [AI Agents That Matter](https://arxiv.org/abs/2407.01502) — Kapoor et al., 2024. Why agent benchmarks mislead, and why holding cost constant changes the ranking — read before you believe any agent leaderboard, including your own
    - [Anthropic — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — the vocabulary of agent patterns, and the argument that many "agents" should not be
    - [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) — Zheng et al., 2023. The simulated user *is* a model and has the same biases as a judge model
    - **Keep building:** wrap your own single-turn endpoint as `agent(traj)`, run the three hand-written scenarios against it with the scripted user, and save the report. The number it gets is the baseline a memory layer has to beat, and most people are surprised by how high it is.
    """)
    return


if __name__ == "__main__":
    app.run()
