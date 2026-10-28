# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "numpy>=2.0",
#     "deepeval>=4.3",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Practical Evals")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 7: Practical Evals

    *One worker, one number, one person who has to believe it.*

    Marcus is a claims-operations analyst at a mid-size property and casualty
    insurer. He has built an assistant for claims handlers: it reads a new
    claim and recommends **pay, investigate, or decline**, with the policy
    clause it relied on. It works, as far as he can tell. The person who
    decides whether it goes further is the Head of Claims, who measures three
    things and has for twenty years — **cycle time, leakage, and the overturn
    rate on appeal** — and who was shown a vendor's demo last year that
    *"scored 94%"* and then paid a claim on a policy that had lapsed.

    His brief to Marcus was one sentence: *"Don't tell me a score. Tell me
    what it does to leakage and overturns, and how sure you are."*

    | What he measures | What the harness has to produce, in his units |
    | --- | --- |
    | **Overturn rate** — decisions reversed on appeal | Agreement with adjudicated decisions, on claims nobody picked (Tasks 2, 3, 6) |
    | **Leakage** — money paid that should not have been | The rate of wrong *pay* recommendations, times the average claim (Tasks 3, 5) |
    | **Cycle time** — days from notification to decision | Handler minutes saved, discounted by the override rate — from the override log, not from this harness |
    | **"How sure are you?"** | An interval, not a decimal (Task 5) |
    | **"Why would I trust a model grading a model?"** | A judge you checked before you believed it (Task 4) |

    **Where Marcus's ground truth comes from.** He did not label a single
    claim. Forty thousand claims from the last two years sit in the claims
    system, each with the handler's decision, the clause cited, and — for the
    appealed ones — whether it was upheld. Whether a decision was upheld or
    overturned on appeal *is* the ground-truth label, and nobody wrote it by
    hand. That is **back-testing**: run the system over inputs from the past
    and compare against what actually happened. Ask *"what did we do last
    year, and did it work?"* before you ask anyone to label anything. Cycle
    time comes from a second record the handlers already keep: when one
    disagrees with a recommendation they **override** it, with a reason, and
    minutes saved only count on claims nobody overrode. Those reasons are
    also the list of failures his next scorers should catch.

    This notebook is Marcus building that answer: the framework first, then
    the harness it is made of, a judge and the check that decides whether to
    believe it, the two loops that make the eval better and then the app
    better, and the page the Head of Claims can act on.

    > ⏰ **The technical challenge is due before next week's session, and its
    > demo has to be rehearsed with a real person first.** That person's
    > calendar is the slow part.

    > **📚 Go deeper** sections are collapsed throughout. The main path reads
    > in about 35 minutes; the accordions and the Bonus Tasks are the detail
    > for when you build your own.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - Task 1: The framework first — DeepEval
    - Task 2: The harness
    - ❓ Question #1
    - Task 3: Deterministic metrics
    - ❓ Question #2
    - Task 4: LLM as a judge — and the check before you believe it
    - ❓ Question #3
    - Task 5: Run the evals — improve the eval, then improve the app
    - ❓ Question #4
    - Task 6: The framework in your harness, and Marcus's page
    - Conclusion
    - Additional Context
    - Bonus Tasks

    > 📓 **Not covered here:** pointing the harness at *your* endpoint and
    > hand-scoring twenty of your own outputs. Both are the challenge.
    > Marcus's claims are described, not shipped; everything below runs on
    > your own golden examples.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | DeepEval | Task 1 and Task 6: `LLMTestCase`, the RAG metrics, `GEval`, a fifteen-line custom judge model; its judge prompts are read aloud in Task 4 | [deepeval.com — metrics](https://deepeval.com/docs/metrics-introduction) |
    | LiteLLM | `completion()` — the two prompts under test in Task 5 and every judge call in this file | [docs.litellm.ai](https://docs.litellm.ai/) |
    | numpy | the bootstrap interval in Task 5 | [numpy.org/doc](https://numpy.org/doc/stable/) |
    | SummEval | 480 human-rated summaries, used by the Bonus calibration task | [github.com/Yale-LILY/SummEval](https://github.com/Yale-LILY/SummEval) |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    "It seems better" is not a claim anyone can act on. An eval turns it into
    a number that is comparable across changes and survives the meeting you
    are not in.

    > **Evals are the shared language between business and technology.** The
    > number a VP uses to decide whether to fund the next quarter is the one
    > you use to decide whether to merge — and the translation is the work.
    > *"0.83 agreement"* is Marcus's number. *"Overturns fall from 6% to about
    > 4%, and we are 95% sure it is below 5%"* is the Head of Claims'. Same
    > measurement. Every task below ends by making that translation.

    **Estimated time:** 35 minutes on the main path; longer with the 📚 sections and the Bonus

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import json
    import sys
    from pathlib import Path

    import numpy as np

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    EVALS = CFG.use_case / "evals"
    GOLDEN = EVALS / "golden.jsonl"
    DATA = Path(mo.notebook_dir()) / "data"

    def read_jsonl(path):
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    # Human-rated summaries, for the Bonus calibration task. Yours are loaded below.
    ARTICLES = {
        article["id"]: article["text"] for article in read_jsonl(DATA / "articles.jsonl")
    }
    JUDGED = read_jsonl(DATA / "judgments.jsonl")

    print(f"✅ {CFG}")
    return ARTICLES, CFG, EVALS, GOLDEN, JUDGED, json, np, read_jsonl, ui


@app.cell
def _(GOLDEN, mo, read_jsonl):
    golden_rows = read_jsonl(GOLDEN) if GOLDEN.exists() else []

    mo.stop(
        not golden_rows or any("REPLACE ME" in seed.get("input", "") for seed in golden_rows),
        mo.md(r"""
        ### ⚠️ Your golden examples are still the template

        This session runs on your own examples in `use_case/evals/golden.jsonl`.
        Without them there is nothing of yours to score.

        Go finish [`use_case/evals/`](../../use_case/evals/).
        """),
    )

    # Assigned only once the gate has passed, so that in a plain Jupyter kernel
    # (where mo.stop is an ordinary exception) nothing downstream can run on the
    # template by accident -- it fails with NameError instead, which is honest.
    SEEDS = golden_rows
    mo.md(f"✅ {len(SEEDS)} golden examples — your ground truth.")
    return (SEEDS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — The framework first: DeepEval

    **MVP: does it work at all?** Before you fund any eval work you need a
    first number, and a framework gives you one in an afternoon. This task
    takes it — and shows what you accept by taking it.

    Your golden examples go in as a dataset, two systems run over them, named
    metrics come back as numbers between 0 and 1 with a pass mark. Then the
    same framework scores three answers to one retrieval question with the
    four metrics every RAG paper quotes, faithfulness scored two ways. One
    button, two tables.

    Read the second table slowly. Three of the four RAG metrics score the
    retrieved passages, not the answer, so they give the same number for all
    three answers. Only faithfulness scores the answer, and it uses a
    definition of "faithful" you have not seen yet — Task 4 reads it. Keep one
    question in mind: *what did it decide for me?*
    """)
    return


@app.cell
def _(CFG):
    import os

    # Before the import, not after: the library phones home by default, and a
    # firm's eval library sending usage events to a vendor is a procurement
    # question, not a default. One line, and the 🏢 callout in Task 6 says why.
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

    import litellm
    from deepeval.dataset import EvaluationDataset, Golden
    from deepeval.metrics import (
        AnswerRelevancyMetric,
        ContextualPrecisionMetric,
        ContextualRecallMetric,
        ContextualRelevancyMetric,
        FaithfulnessMetric,
        GEval,
    )
    from deepeval.models.base_model import DeepEvalBaseLLM
    from deepeval.test_case import LLMTestCase, SingleTurnParams

    class NotebookJudge(DeepEvalBaseLLM):
        """The framework's judge, made of the same call as every other call in this notebook.

        DeepEval ships its own model wrappers, but each guesses which key to
        send from the environment, and a .env with more than one provider key
        in it (an OpenAI key for embeddings, an Anthropic key for chat) makes
        that guess wrong. Fifteen lines through `CFG.kwargs()` and the judge
        uses exactly the model, endpoint and key the rest of this file uses.
        It returns the model's text; the framework parses the JSON itself.
        """

        def __init__(self):
            super().__init__(CFG.llm_model)

        def load_model(self):
            return None

        def get_model_name(self):
            return CFG.llm_model

        def generate(self, prompt: str, schema=None) -> str:
            reply = litellm.completion(
                timeout=600, messages=[{"role": "user", "content": prompt}], max_tokens=4096, **CFG.kwargs()
            )
            return reply.choices[0].message.content or ""

        async def a_generate(self, prompt: str, schema=None) -> str:
            reply = await litellm.acompletion(
                timeout=600, messages=[{"role": "user", "content": prompt}], max_tokens=4096, **CFG.kwargs()
            )
            return reply.choices[0].message.content or ""

    # One judge for every framework metric in this notebook. Note what this
    # means: the model that answers and the model that grades are the same
    # model, unless you choose otherwise -- one of the decisions named below.
    FRAMEWORK_JUDGE = NotebookJudge()
    return (
        AnswerRelevancyMetric,
        ContextualPrecisionMetric,
        ContextualRecallMetric,
        ContextualRelevancyMetric,
        EvaluationDataset,
        FRAMEWORK_JUDGE,
        FaithfulnessMetric,
        GEval,
        Golden,
        LLMTestCase,
        SingleTurnParams,
    )


@app.cell
def _(mo):
    framework_button = mo.ui.run_button(label="🚀 Score the goldens and a RAG answer with DeepEval")
    framework_button
    return (framework_button,)


@app.cell
def _(
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    EvaluationDataset,
    FRAMEWORK_JUDGE,
    FaithfulnessMetric,
    GEval,
    Golden,
    LLMTestCase,
    SEEDS,
    SingleTurnParams,
    framework_button,
    mo,
    ui,
):
    mo.stop(not framework_button.value, mo.md("*Press the button: one dataset, two systems, seven metric columns.*"))

    # ---- Half one: your goldens, two systems, two answer-level metrics -------
    FRAMEWORK_DATASET = EvaluationDataset(
        goldens=[Golden(input=seed["input"], expected_output=seed["output"]) for seed in SEEDS]
    )
    answer_key = {seed["input"]: seed["output"] for seed in SEEDS}
    FRAMEWORK_SYSTEMS = {"echo the input": lambda text: text, "oracle (cheats)": lambda text: answer_key[text]}

    correctness_metric = GEval(
        name="Correctness",
        criteria="Does the actual output convey the same substance as the expected output? Wording and length do not matter; a missing or contradicted fact does.",
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        model=FRAMEWORK_JUDGE,
    )
    relevancy_metric = AnswerRelevancyMetric(model=FRAMEWORK_JUDGE)

    goldens_rows = []
    with mo.status.spinner(title="DeepEval: scoring the goldens for two systems…"):
        for system_label, system_fn in FRAMEWORK_SYSTEMS.items():
            per_metric = {"Correctness": [], "AnswerRelevancy": []}
            for golden in FRAMEWORK_DATASET.goldens:
                test_case = LLMTestCase(
                    input=golden.input,
                    actual_output=system_fn(golden.input),
                    expected_output=golden.expected_output,
                )
                correctness_metric.measure(test_case)
                relevancy_metric.measure(test_case)
                per_metric["Correctness"].append(correctness_metric.score or 0.0)
                per_metric["AnswerRelevancy"].append(relevancy_metric.score or 0.0)
            goldens_rows.append(
                {
                    "system": system_label,
                    "n": len(FRAMEWORK_DATASET.goldens),
                    "Correctness (GEval)": f"{sum(per_metric['Correctness']) / len(per_metric['Correctness']):.2f}",
                    "AnswerRelevancy": f"{sum(per_metric['AnswerRelevancy']) / len(per_metric['AnswerRelevancy']):.2f}",
                    "pass ≥ 0.5": f"{sum(score >= 0.5 for score in per_metric['Correctness'])}/{len(per_metric['Correctness'])}",
                }
            )

    # ---- Half two: one retrieval question, three answers, four RAG metrics --
    RAG_CONTEXT = [
        "Sev-1 incidents require paging the on-call engineer immediately.",
        "The incident commander must be notified within 15 minutes of a sev-1.",
    ]
    RAG_QUESTION = "What is the escalation path for a sev-1 incident?"
    RAG_EXPECTED = "Page the on-call engineer immediately, then notify the incident commander within 15 minutes."
    RAG_ANSWERS = [
        ("grounded", "Page the on-call engineer, then notify the incident commander within 15 minutes."),
        ("one detail wrong", "Page the on-call engineer, then notify the incident commander within 2 hours."),
        ("invented", "Page the on-call engineer, then file a ticket and wait for the weekly review board to triage it."),
    ]
    # Two faithfulness columns on purpose. The default marks a claim "no" only
    # when it CONTRADICTS the context; a claim the context never mentions is
    # "borderline" and counts as faithful. The strict flag counts it against.
    RAG_METRICS = {
        "Faithfulness": FaithfulnessMetric(model=FRAMEWORK_JUDGE),
        "Faithfulness (strict)": FaithfulnessMetric(model=FRAMEWORK_JUDGE, penalize_ambiguous_claims=True),
        "ContextualPrecision": ContextualPrecisionMetric(model=FRAMEWORK_JUDGE),
        "ContextualRecall": ContextualRecallMetric(model=FRAMEWORK_JUDGE),
        "ContextualRelevancy": ContextualRelevancyMetric(model=FRAMEWORK_JUDGE),
    }

    rag_rows = []
    with mo.status.spinner(title="DeepEval: four RAG metrics on three answers…"):
        for answer_label, answer_text in RAG_ANSWERS:
            rag_case = LLMTestCase(
                input=RAG_QUESTION,
                actual_output=answer_text,
                expected_output=RAG_EXPECTED,
                retrieval_context=RAG_CONTEXT,
            )
            rag_row = {"answer": answer_label}
            for metric_name, metric in RAG_METRICS.items():
                metric.measure(rag_case)
                rag_row[metric_name] = f"{(metric.score or 0.0):.2f}"
            rag_rows.append(rag_row)

    mo.vstack(
        [
            ui.table(goldens_rows, title="Your goldens · two systems · two answer-level metrics"),
            ui.table(rag_rows, title=f"'{RAG_QUESTION}' · three answers · the four RAG metrics, faithfulness twice"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One cell, and it works. Now the question: **what did it decide for
    you?** Each row is a decision the framework made silently, and the task
    where you make it on purpose.

    | The framework decided… | …and here you decide it |
    | --- | --- |
    | the default faithfulness column counts a claim as faithful unless the context *contradicts* it, so an invented procedure the context never mentions can score high; only the strict column counts unmentioned claims against the answer | Task 4, where you read the verdict prompt that says so; Task 5, where you build the failures that would catch it |
    | three of the four RAG metrics scored the context, not the answer | Task 2's harness, where every scorer takes `(actual, case)` and you know what each reads |
    | a case "passes" when its score is at least 0.5 — the framework's default, which nobody chose for your data | Task 3, where the oracle *must* score 1.0 or the scorer is wrong |
    | the judge is the same model that answered, and nothing checked it against a human | Task 4, where you check yours before you believe it |
    | the failures in your goldens are whatever your goldens happen to contain | Task 5, generating the ones you need, labelled by construction |
    | a 0.78 is a number — no interval, no "how sure" | Task 5, the bootstrap, and the five-point improvement you cannot see |
    | it sent usage telemetry to the vendor until one line turned it off | the 🏢 callout in Task 6 |

    None of these defaults are wrong. They are *defaults*, and the page Marcus
    hands the Head of Claims has to say which were kept and why. The rest of
    this notebook is that page, one decision at a time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 2 — The harness

    **MVP to PoC.** The framework answered "does it work at all". To tell the
    Head of Claims *how well, on claims nobody picked*, you need a loop whose
    every line you can defend, because the number it produces is the one that
    gets funded or killed.

    An eval harness is a loop that runs your system over cases and scores each
    output, plus a function that averages the scores. The code below is all of
    it; dashboards, frameworks and tracing are conveniences built on top.
    Build it small enough to read, because you will be arguing about its
    output for weeks.
    """)
    return


@app.cell
def _():
    from dataclasses import dataclass, field

    @dataclass
    class Result:
        """One case, one score, and enough context to argue about it."""

        case: dict
        actual: str
        scores: dict = field(default_factory=dict)

        @property
        def passed(self) -> bool:
            # 0.5 is the same default the framework used in Task 1. Chosen on
            # purpose here, for now; your challenge decides the real threshold.
            return all(score >= 0.5 for score in self.scores.values())

    def run_eval(cases, system, scorers: dict) -> list[Result]:
        """Run `system` over every case and score it every way.

        `system` is any callable input -> output. Keeping it that loose is what
        lets the same harness score a prompt, a RAG pipeline, an agent, and a
        fine-tuned model -- which is what every later comparison rests on.
        """
        results = []
        for case in cases:
            actual = system(case["input"])
            scores = {name: fn(actual, case) for name, fn in scorers.items()}
            results.append(Result(case=case, actual=actual, scores=scores))
        return results

    def report(results: list[Result]) -> dict:
        """Aggregate. One row per scorer, plus the pass rate."""
        if not results:
            return {}
        names = results[0].scores.keys()
        out = {
            name: sum(result.scores[name] for result in results) / len(results)
            for name in names
        }
        out["pass rate"] = sum(result.passed for result in results) / len(results)
        out["n"] = len(results)
        return out

    return report, run_eval


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `cases` is your goldens. `system` is whatever you are testing. `scorers`
    is a dict of functions, each `(actual, case) -> 0..1`. That one signature
    is the design: a string comparison, an LLM judge and a framework metric
    all take `(actual, case)` and return a number from 0 to 1, so you can add
    or replace a scorer without changing the loop or the report.

    > **The taxonomy comes before the scorers.** Marcus read fifty of the
    > assistant's recommendations before writing a line of this and wrote one
    > sentence per failure: *wrong policy version; recommended pay without
    > checking the policy was in force; missed a named exclusion; got the
    > excess wrong.* Counting them told him which scorers to write. A scorer
    > that does not trace to a failure you have seen is one you invented
    > because it was easy to compute.

    ---
    ### ❓ Question #1

    Marcus's ground truth is the claims system and the appeals team. In one to
    three sentences: where at your company does the already-judged work live
    for *your* use case — fifty outputs a human has already called right or
    wrong — and who did the judging? If you cannot name a system and a role,
    that is the finding, and the challenge's first step is where you go
    looking.

    **Answer:**

    ---
    ## Task 3 — Deterministic metrics

    **Production from day one.** These scorers cost nothing per run, so they
    are the only ones that can gate every commit; write them first, and they
    are the gate you keep when the judge is too expensive to run on every
    change.

    Start with the scorers that need no model. They are free, instant,
    deterministic, and they catch more than people expect.
    """)
    return


@app.cell
def _():
    import re

    def tokenize(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", str(text).lower())

    def exact_match(actual: str, case: dict) -> float:
        """The strictest scorer. Right for IDs, categories, and routing."""
        return float(
            str(actual).strip().lower() == str(case["output"]).strip().lower()
        )

    def token_f1(actual: str, case: dict) -> float:
        """Overlap between predicted and expected tokens. Forgiving of phrasing."""
        from collections import Counter

        predicted, expected = Counter(tokenize(actual)), Counter(tokenize(case["output"]))
        common = sum((predicted & expected).values())
        if not common:
            return 0.0
        precision, recall = common / sum(predicted.values()), common / sum(expected.values())
        return 2 * precision * recall / (precision + recall)

    def contains_required(actual: str, case: dict) -> float:
        """Did the output mention everything it had to?

        The most underrated scorer in enterprise work. "Did the answer cite the
        policy number" is a real acceptance criterion and it is a substring check.
        """
        required = case.get("must_include", [])
        if not required:
            return 1.0
        text = str(actual).lower()
        return sum(str(phrase).lower() in text for phrase in required) / len(required)

    def declines(actual: str, case: dict) -> float:
        """Did it refuse when it should have?

        Only scored on cases marked `should_decline`. A system that never declines
        is not confident, it is uncalibrated.
        """
        if not case.get("should_decline"):
            return 1.0
        signals = (
            "i don't know",
            "i do not know",
            "cannot",
            "can't",
            "unsure",
            "escalate",
            "not enough information",
            "unable",
        )
        return float(any(signal in str(actual).lower() for signal in signals))

    return contains_required, declines, exact_match, re, token_f1


@app.cell
def _(
    SEEDS,
    contains_required,
    declines,
    exact_match,
    report,
    run_eval,
    token_f1,
    ui,
):
    SCORERS = {
        "exact": exact_match,
        "f1": token_f1,
        "required": contains_required,
        "declines": declines,
    }

    # A deliberately terrible baseline: echo the input back.
    baseline_results = run_eval(SEEDS, lambda x: x, SCORERS)

    # A cheating "perfect" system, to prove the harness can see a difference.
    answer_by_input = {seed["input"]: seed["output"] for seed in SEEDS}
    oracle_results = run_eval(SEEDS, lambda x: answer_by_input[x], SCORERS)

    ui.table(
        [
            {
                "system": "echo the input",
                **{
                    key: f"{value:.2f}" if isinstance(value, float) else value
                    for key, value in report(baseline_results).items()
                },
            },
            {
                "system": "oracle (cheats)",
                **{
                    key: f"{value:.2f}" if isinstance(value, float) else value
                    for key, value in report(oracle_results).items()
                },
            },
        ],
        title="Sanity check: can the harness tell these apart?",
    )
    return SCORERS, answer_by_input


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Always run the two dumb baselines first

    **Echo** (return the input unchanged) is the worst system you can build;
    **oracle** (return the expected output) is the best. Every real system
    should land between them. If yours does not beat echo, something is broken
    upstream of the model. If the oracle does not score 1.0, **your scorer is
    wrong** — better to learn that now than when a fine-tune "fails" for
    reasons that were never about the model.

    In Marcus's units: *"does the decision match the adjudicated one"* is
    exact match; *"was the policy in force on the date of loss"* is a date
    comparison; *"is the cited clause in this policy's wording"* is a lookup.
    None of the three needs a model, and the second — was the policy in
    force? — is the check that would have caught the vendor's lapsed-policy
    payout.

    > **🏢 In the enterprise:** these scorers cost nothing per run, so they can
    > run on every commit — the only kind of scorer that catches a regression
    > before a user does. The judge in Task 4 costs a model call per case;
    > teams that put it in the commit gate watch it get disabled within a
    > month, and then have no gate at all.

    ---
    ### ❓ Question #2

    Think of the failure you most worry about in your own system. In one to
    three sentences: which of your failure modes could a function catch with
    no model at all, and what would the *oracle* answer be for one of them —
    the output that must score 1.0 on that scorer, or the scorer is wrong?

    **Answer:**

    ---
    ## Task 4 — LLM as a judge, and the check before you believe it

    **PoC.** A judge is what lets you measure things no function can — but a
    funding decision made on an unchecked judge is the vendor's 94% again. The
    check against known-bad, known-good and a person is the deliverable, not
    the judge.

    Some things cannot be scored programmatically — is this summary faithful,
    is this tone right. For those, use a model, carefully. A judge is a scorer
    with a rubric. Building one is easy. **Knowing whether to believe it is the
    actual work**, and it is the step nearly everyone skips.
    """)
    return


@app.cell
def _(CFG, json):
    from litellm import completion

    JUDGE_PROMPT = """You are scoring one answer against a reference.

    Question:
    {input}

    Reference answer (written by a domain expert):
    {expected}

    Answer to score:
    {actual}

    Score 0 to 1 on whether the answer conveys the same substance as the reference.
    Differences in wording, length, or style do not matter. Missing or contradicting
    a fact does.

    Reply with JSON only: {{"score": <0-1>, "why": "<one sentence>"}}"""

    def ask_judge(prompt: str) -> dict:
        """One judge call. Returns the parsed JSON, or an empty dict."""
        reply = (
            completion(
                **CFG.kwargs(),
                timeout=600,
                messages=[{"role": "user", "content": prompt}],
            )
            .choices[0]
            .message.content
        )
        try:
            start, end = reply.index("{"), reply.rindex("}") + 1
            return json.loads(reply[start:end])
        except (ValueError, KeyError, TypeError):
            return {}

    def judge(actual: str, case: dict) -> float:
        """Score one answer with a model. Returns 0-1."""
        parsed = ask_judge(
            JUDGE_PROMPT.format(
                input=case["input"], expected=case["output"], actual=actual
            )
        )
        try:
            return float(parsed["score"])
        except (KeyError, TypeError, ValueError):
            return (
                0.0  # an unparseable judge is a failed judgement, not a pass
            )

    return ask_judge, completion, judge


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    That is a judge: a prompt, a parse, a number. Now look at what the
    framework's `FaithfulnessMetric` ran in Task 1. It ships its prompts as
    plain text files inside the package, so you can read them.
    """)
    return


@app.cell
def _(mo):
    import importlib.resources as resources

    # Three prompts, run in sequence per answer: pull the claims out of the
    # answer, give each claim a verdict against the context, write the reason.
    # The score is the fraction of claims with a "yes". Read them: it is the
    # judge above, split into steps.
    FAITHFULNESS_TEMPLATES = {}
    for template_name in ("generate_claims", "generate_verdicts", "generate_reason"):
        try:
            FAITHFULNESS_TEMPLATES[template_name] = (
                resources.files("deepeval.metrics.faithfulness.templates").joinpath(f"{template_name}.txt").read_text(encoding="utf-8")
            )
        except (ModuleNotFoundError, FileNotFoundError, TypeError):
            FAITHFULNESS_TEMPLATES[template_name] = "(deepeval is not installed in this environment)"

    mo.accordion(
        {
            f"DeepEval · FaithfulnessMetric · `{template_name}.txt` ({len(template_text):,} characters)": mo.md(f"```text\n{template_text[:2500]}{'…' if len(template_text) > 2500 else ''}\n```")
            for template_name, template_text in FAITHFULNESS_TEMPLATES.items()
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Under the hood it is prompts.** Three of them instead of one — extract
    the claims, judge each one, write the reason — longer and more careful
    than the short judge above, and the same thing in kind: a model reading
    text and returning a judgement. It does not add the one thing that would
    let you believe the number. That is next.

    ### Check the judge before you believe it

    A judge's score is a model's opinion. Before it goes on anyone's page, two
    checks, and they are different questions:

    - **Separation** — does the judge give known-bad outputs a lower score
      than known-good ones? Task 3's echo outputs are known-bad and its oracle
      outputs are known-good, so you already have both.
    - **Agreement** — does it score the way *a person* would? That needs
      outputs a human already scored. The challenge has you hand-score twenty
      of your own; if `use_case/evals/human_scores.jsonl` exists, the cell
      below uses it. The Bonus runs the same check on 480 published ratings.

    A judge can pass the first and fail the second. That is the common case,
    and it is why "I checked it on a good answer and a bad answer" is not the
    whole check.
    """)
    return


@app.cell
def _(SEEDS, mo):
    run_check = mo.ui.run_button(label=f"Check the judge: separation on {2 * len(SEEDS)} outputs, agreement if you have hand scores")
    run_check
    return (run_check,)


@app.cell
def _(EVALS, SEEDS, answer_by_input, judge, mo, np, read_jsonl, run_check, ui):
    mo.stop(not run_check.value, mo.md("*Press the button to check the judge.*"))

    # Separation: the judge over the two systems the harness already proved apart.
    with mo.status.spinner(title="Judging the echo and oracle outputs…"):
        echo_judged = [judge(seed["input"], seed) for seed in SEEDS]
        oracle_judged = [judge(answer_by_input[seed["input"]], seed) for seed in SEEDS]

    SEPARATION = [
        {"outputs": "echo (known bad)", "judge mean": f"{np.mean(echo_judged):.2f}", "judge min–max": f"{min(echo_judged):.2f}–{max(echo_judged):.2f}"},
        {"outputs": "oracle (known good)", "judge mean": f"{np.mean(oracle_judged):.2f}", "judge min–max": f"{min(oracle_judged):.2f}–{max(oracle_judged):.2f}"},
    ]

    # Agreement: only if you have hand scores. Each line: {"input", "output", "actual", "human": 0..1}
    HUMAN_SCORES_PATH = EVALS / "human_scores.jsonl"
    if HUMAN_SCORES_PATH.exists():
        human_rows = read_jsonl(HUMAN_SCORES_PATH)
        with mo.status.spinner(title=f"Judging {len(human_rows)} hand-scored outputs…"):
            judged_rows = [
                {"human": float(row["human"]), "judge": judge(row["actual"], {"input": row["input"], "output": row["output"]})}
                for row in human_rows
            ]
        humans = np.array([row["human"] for row in judged_rows])
        judged = np.array([row["judge"] for row in judged_rows])
        AGREEMENT = mo.md(
            f"**Agreement on {len(judged_rows)} hand-scored outputs:** correlation "
            f"**{np.corrcoef(humans, judged)[0, 1]:.2f}**, within 0.25 of the human score "
            f"**{np.mean(np.abs(humans - judged) <= 0.25):.0%}** of the time."
        )
    else:
        AGREEMENT = mo.md(
            "*No `use_case/evals/human_scores.jsonl` yet — agreement is the half you cannot "
            "run without a person. The challenge's first step produces that file; the Bonus "
            "task runs this half on 480 published ratings so you can see what the result looks like.*"
        )

    mo.vstack([ui.table(SEPARATION, title="Separation: the judge on known-bad and known-good"), AGREEMENT])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If the two means in that table are close, the judge is not measuring what
    you think, and nothing downstream is worth reading. If they are far apart,
    you have half a reason to believe it; the other half is a person.

    > **🏢 In the enterprise:** a judge you checked is checked against one
    > model version. The day the vendor upgrades the model behind your
    > endpoint, every number the judge produces changes and nothing in your
    > dashboard says why. Pin the judge model and store the check's result
    > next to the pin, so a model change re-runs the check before anything
    > else. `helpers/judge.py` makes that structural: `score()` raises until
    > `calibrate()` has passed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "📚 Go deeper: what to do when the judge fails the check": mo.md(r"""
    It usually does the first time. In order of what actually works:

    1. **Narrow the question.** "Is this good?" cannot be scored. "Does this
       state anything the reference does not support?" can — ask only about
       the thing you mean and exclude style.
    2. **Give the rubric examples** of a bad, a middling and a good answer.
    3. **Ask for a decision, not a score.** Binary pass/fail is far more
       reliable than a float, and you can average the decisions.
    4. **Use a different model for judging than for answering.** A model
       grading its own output is generous about its own habits.
    5. **Check whether the dimension is judgeable at all.** If two people at
       your firm would not agree on it, neither will you and the judge — the
       Bonus task shows this on published data, where humans agree on factual
       consistency four times in five and on coherence barely above chance.
       Score the objective thing; report the subjective one as a signal.
    """)
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #3

    Marcus has two things a judge could score: *"does the recommendation rest
    on a clause that supports it?"* (two senior handlers agree almost every
    time) and *"is the explanation good enough for the claimant's letter?"*
    (the same two handlers argue). In one to three sentences: which dimension
    of "correct" for *your* use case would two people at your firm disagree
    on — and should you score it at all, or record it as a signal and score
    something objective instead?

    **Answer:**

    ---
    ## Task 5 — Run the evals: improve the eval, then improve the app

    **PoC: the number against data you did not choose, with an interval.**
    Loop A makes sure the eval can see the failures that matter — the ones
    your natural data barely contains. Loop B is how you say *"change X moved
    Y, because Z"* to the person who funds the next quarter, and how sure you
    are.

    Two loops, and teams usually run only the second. **Loop A** makes the
    *eval* better: each step catches something the previous scorer let
    through. **Loop B** uses the eval to make the *app* better: change one
    thing, see which column moves, and say why that matters.

    ### Loop A — the scorer ladder

    Take your goldens' correct answers and break them in four named ways —
    change a number, reverse a claim, add a sentence the reference does not
    support, swap a name for one from a different golden. Each broken answer
    is **wrong, and you know exactly how**, which is a labelled test case that
    cost nothing. Then score the broken answers with every scorer you have
    and see which ones notice.
    """)
    return


@app.cell
def _(EVALS, SEEDS, json, np, re):
    UNSUPPORTED = (
        " This is expected to be reviewed again within the month.",
        " No further action is required on the account.",
        " A supervisor has already approved this in principle.",
        " The figure is lower than it was last year.",
    )
    NAME_PATTERN = re.compile(r"\b[A-Z][a-z]{2,}(?: [A-Z][a-z]{2,})*\b")

    def corrupt(answer: str, kind: str, pool_names: list[str], rng) -> str | None:
        """Break a correct answer in one known way. None if that way does not apply.

        Each mirrors a real failure mode. The point is not that a model would
        make exactly this mistake -- it is that you know precisely what is
        wrong, so you know what a working detector must catch.
        """
        if kind == "number":
            nums = re.findall(r"\b\d[\d,\.]*\b", answer)
            if not nums:
                return None
            target = nums[int(rng.integers(len(nums)))]
            return answer.replace(target, str(int(rng.integers(2, 99))) if "." not in target else "9.9", 1)
        if kind == "negate":
            for phrase, negated in ((" was ", " was not "), (" is ", " is not "), (" will ", " will not "), (" should ", " should not "), (" can ", " cannot ")):
                if phrase in answer:
                    return answer.replace(phrase, negated, 1)
            return None
        if kind == "unsupported":
            return answer.rstrip() + UNSUPPORTED[int(rng.integers(len(UNSUPPORTED)))]
        if kind == "entity":
            present = NAME_PATTERN.findall(answer)
            others = [name for name in pool_names if name not in present]
            if not present or not others:
                return None
            old = present[int(rng.integers(len(present)))]
            return answer.replace(old, others[int(rng.integers(len(others)))], 1)
        raise ValueError(kind)

    CORRUPTIONS = ("number", "negate", "unsupported", "entity")
    corruption_rng = np.random.default_rng(7)
    golden_names = sorted({name for seed in SEEDS for name in NAME_PATTERN.findall(seed["output"])})

    SYNTHETIC = []
    for seed in SEEDS:
        for failure_kind in CORRUPTIONS:
            broken = corrupt(seed["output"], failure_kind, golden_names, corruption_rng)
            if broken and broken != seed["output"]:
                SYNTHETIC.append({**seed, "actual": broken, "label": "wrong", "failure": failure_kind})

    # This file is the challenge's deliverable: your generated failures, labelled.
    # Written once; once you start growing it yourself, this cell leaves it alone.
    SYNTHETIC_PATH = EVALS / "synthetic.jsonl"
    if not SYNTHETIC_PATH.exists():
        SYNTHETIC_PATH.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in SYNTHETIC) + "\n", encoding="utf-8")
        written_note = f"→ wrote {SYNTHETIC_PATH.name}"
    else:
        written_note = f"({SYNTHETIC_PATH.name} already exists — not overwritten)"

    print(f"✅ {len(SYNTHETIC)} labelled wrong answers from {len(SEEDS)} correct ones {written_note}")
    for failure_mode in CORRUPTIONS:
        print(f"   {failure_mode:12} {sum(1 for row in SYNTHETIC if row['failure'] == failure_mode):>4}")
    return CORRUPTIONS, SYNTHETIC


@app.cell
def _(SEEDS, mo):
    run_ladder = mo.ui.run_button(label=f"Score the broken answers with every scorer (about {4 * len(SEEDS)} judge calls)")
    run_ladder
    return (run_ladder,)


@app.cell
def _(CORRUPTIONS, SCORERS, SYNTHETIC, judge, mo, np, run_ladder, ui):
    mo.stop(not run_ladder.value, mo.md("*Press the button to climb the ladder.*"))

    LADDER_SCORERS = {**SCORERS, "judge": judge}

    with mo.status.spinner(title="Scoring every broken answer, five ways…"):
        ladder_scores = {
            (row["failure"], name): fn(row["actual"], row)
            for row in SYNTHETIC
            for name, fn in LADDER_SCORERS.items()
        }

    # Every row is a WRONG answer, so every cell should be low. A high cell is
    # a scorer that was fooled by that kind of failure.
    LADDER = [
        {
            "failure": failure_kind,
            "n": sum(1 for row in SYNTHETIC if row["failure"] == failure_kind),
            **{
                name: f"{np.mean([score for (kind, scorer), score in ladder_scores.items() if kind == failure_kind and scorer == name]):.2f}"
                for name in LADDER_SCORERS
            },
        }
        for failure_kind in CORRUPTIONS
        if any(row["failure"] == failure_kind for row in SYNTHETIC)
    ]
    ui.table(LADDER, title="Every answer here is wrong — a high score is a scorer that did not notice")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read it across. `exact` catches everything, because anything but the
    reference is a miss — and it would also fail a correct answer in different
    words, which is why it is not the headline. `f1` barely moves: a reversed
    claim shares almost every token with the original, so a scorer that
    rewards overlap rewards the wrong answer. `required` passes an answer that
    still mentions the clause and is wrong about everything else. The judge is
    the first scorer that reads for meaning — and look at its `unsupported`
    cell: an added sentence the reference never mentions can sail through,
    because "conveys the same substance" does not say "and nothing more". The
    same definition problem as the framework's faithfulness, in your own
    prompt; the fix is one line in the rubric, and the ladder is how you found
    out you needed it.

    **Each rung fixes the one below it.** Exact match → token overlap for
    phrasing → required fields for completeness → a judge for meaning → the
    failures you generated, because your goldens do not contain a reversed
    claim until you put one there. Marcus's corruptions write themselves from
    his failure list — move the date of loss past the lapse, for one. In his
    real data only one claim in two hundred is on a lapsed policy, so a
    natural sample would contain almost none; he generated two hundred.

    > **The events you most want to detect are the ones your natural data
    > barely contains**, and collecting more natural data preserves the ratio.
    > A corruption you introduced arrives with its label attached. The file
    > this cell wrote, `use_case/evals/synthetic.jsonl`, is the challenge's
    > generated-failures deliverable; grow it from your own failure list.

    ### The last rung: is the difference real?

    Every number above is a mean over a handful of cases. Before you compare
    two of them, you need to know how much a mean on *n* cases moves on its own.
    """)
    return


@app.cell
def _(np):
    def bootstrap_ci(
        scores, n_resamples: int = 5000, level: float = 0.95, seed: int = 0
    ):
        """Confidence interval for a mean, by resampling.

        Sample the results you have, with replacement, thousands of times. The
        spread of those means is how much your number would move if you had
        collected a different set of the same size. No distribution assumed --
        which matters, because eval scores are rarely normal.
        """
        rng = np.random.default_rng(seed)
        arr = np.asarray(scores, dtype=float)
        means = arr[
            rng.integers(0, len(arr), size=(n_resamples, len(arr)))
        ].mean(axis=1)
        lo, hi = np.percentile(
            means, [(1 - level) / 2 * 100, (1 + level) / 2 * 100]
        )
        return float(arr.mean()), float(lo), float(hi)

    def difference_ci(scores_a, scores_b, n_resamples: int = 5000, seed: int = 0):
        """CI for the difference between two systems on the SAME cases.

        Paired, deliberately: resample the cases, not the two systems
        independently. Ignoring the pairing throws away the fact that both
        systems found the same cases hard, and widens the interval for no reason.
        """
        rng = np.random.default_rng(seed)
        scores_a, scores_b = np.asarray(scores_a, dtype=float), np.asarray(scores_b, dtype=float)
        idx = rng.integers(0, len(scores_a), size=(n_resamples, len(scores_a)))
        diffs = scores_a[idx].mean(axis=1) - scores_b[idx].mean(axis=1)
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        return float(scores_a.mean() - scores_b.mean()), float(lo), float(hi)

    return bootstrap_ci, difference_ci


@app.cell
def _(bootstrap_ci, difference_ci, np, ui):
    # Two systems that genuinely differ by five points, measured on eval sets of
    # different sizes. Same true difference every time -- only n changes.
    simulation_rng = np.random.default_rng(3)

    size_rows = []
    for case_count in (5, 10, 20, 50, 200, 1000):
        old_scores = (simulation_rng.random(case_count) < 0.83).astype(float)
        new_scores = (simulation_rng.random(case_count) < 0.88).astype(float)
        new_mean, mean_low, mean_high = bootstrap_ci(new_scores)
        difference, difference_low, difference_high = difference_ci(new_scores, old_scores)
        size_rows.append(
            {
                "eval cases": case_count,
                "new system": f"{new_mean:.2f}",
                "95% CI": f"[{mean_low:.2f}, {mean_high:.2f}]",
                "difference": f"{difference:+.3f}",
                "CI on the difference": f"[{difference_low:+.2f}, {difference_high:+.2f}]",
                "real?": "no — spans 0" if difference_low <= 0 <= difference_high else "yes",
            }
        )

    ui.table(
        size_rows, title="The same true 5-point improvement, at six eval-set sizes"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The improvement is real in every row. You cannot see it in most of them.**
    Below a couple of hundred cases the interval on the difference includes
    zero — and at fifty it can show a real gain as a loss. **Report the
    interval, not just the mean.** *"0.88, 95% CI [0.79, 0.95]"* is a sentence
    an executive can act on and an engineer can check; *"0.88"* invites a
    comparison the data does not support. It is also the answer to *"how sure
    are you?"* — the one question a mean cannot answer.

    > **Rule of thumb, not a law:** a 5-point difference needs a few hundred
    > cases; a 20-point difference, a few dozen. Five goldens catch a broken
    > system; they cannot compare two working ones.

    ### Loop B — use the eval to improve the app

    Now the loop teams actually run. Two versions of the system under test —
    the same model, a **basic prompt** that just passes the question through,
    and an **elaborate prompt** that says what a good answer contains and
    shows one worked example from your own goldens — scored by every scorer
    you have, side by side. The columns that move tell you what the change
    bought; the interval tells you whether to believe it.
    """)
    return


@app.cell
def _(CFG, SEEDS, completion):
    BASIC_PROMPT = "{question}"

    # The elaborate prompt is generic on purpose: it works on any goldens. It says
    # what a good answer must contain, and shows ONE of your own goldens as the
    # worked example -- never the one being asked, or the oracle would leak in.
    ELABORATE_PROMPT = """Answer the question below for a colleague who will act on your answer.

    A good answer: states the decision or fact directly in the first sentence; includes every
    specific the question depends on (names, numbers, dates, references); says "I don't know"
    or "escalate" if the question cannot be answered from what you have, rather than guessing.

    Here is one example of a question and the answer a domain expert gave:
    Q: {example_q}
    A: {example_a}

    Now answer this one in the same style.
    Q: {question}
    A:"""

    def answer_with(prompt_template: str):
        """A system under test: one prompt template around the same model."""

        def system(question: str) -> str:
            example = next(seed for seed in SEEDS if seed["input"] != question) if len(SEEDS) > 1 else SEEDS[0]
            prompt = prompt_template.format(question=question, example_q=example["input"], example_a=example["output"])
            reply = completion(**CFG.kwargs(), timeout=600, messages=[{"role": "user", "content": prompt}])
            return (reply.choices[0].message.content or "").strip()

        return system

    return BASIC_PROMPT, ELABORATE_PROMPT, answer_with


@app.cell
def _(SEEDS, mo):
    run_prompts = mo.ui.run_button(label=f"Run both prompts over the goldens and score them (about {4 * len(SEEDS)} model calls)")
    run_prompts
    return (run_prompts,)


@app.cell
def _(
    BASIC_PROMPT,
    ELABORATE_PROMPT,
    SCORERS,
    SEEDS,
    answer_with,
    difference_ci,
    judge,
    mo,
    np,
    run_eval,
    run_prompts,
    ui,
):
    mo.stop(not run_prompts.value, mo.md("*Press the button to compare the two prompts.*"))

    PROMPT_SCORERS = {**SCORERS, "judge": judge}
    with mo.status.spinner(title="Running both prompts, then scoring…"):
        BASIC_RESULTS = run_eval(SEEDS, answer_with(BASIC_PROMPT), PROMPT_SCORERS)
        ELABORATE_RESULTS = run_eval(SEEDS, answer_with(ELABORATE_PROMPT), PROMPT_SCORERS)

    def column(results, name):
        return [result.scores[name] for result in results]

    PROMPT_ROWS = []
    for scorer_name in PROMPT_SCORERS:
        gap, gap_low, gap_high = difference_ci(column(ELABORATE_RESULTS, scorer_name), column(BASIC_RESULTS, scorer_name))
        PROMPT_ROWS.append(
            {
                "scorer": scorer_name,
                "basic prompt": f"{np.mean(column(BASIC_RESULTS, scorer_name)):.2f}",
                "elaborate prompt": f"{np.mean(column(ELABORATE_RESULTS, scorer_name)):.2f}",
                "difference": f"{gap:+.2f}",
                "95% CI on the difference": f"[{gap_low:+.2f}, {gap_high:+.2f}]",
                "real on this many cases?": "yes" if gap_low > 0 or gap_high < 0 else "no — spans 0",
            }
        )

    mo.vstack(
        [
            ui.table(PROMPT_ROWS, title=f"One change to the app, every scorer, n={len(SEEDS)}"),
            ui.table(
                [{"question": result.case["input"][:60], "basic": basic.actual[:80], "elaborate": result.actual[:80]} for basic, result in zip(BASIC_RESULTS, ELABORATE_RESULTS)][:4],
                title="The first four answers, side by side",
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the columns, not the row. `exact` probably did not move — two
    different prompts rarely produce the reference word for word. `required`
    and the judge are where an instruction like *"include every specific"*
    shows up. The last column is the honest part: on a handful of goldens
    most intervals include zero. That does not mean the prompt did nothing; it
    means you have too few cases to tell — which is what the generated
    failures and a growing golden set are for.

    And read the *levels*, not only the differences. If both prompts sit low
    on `required` and the judge, the prompt was never the limiting component:
    a system that has not been given the policy wording cannot cite clause
    4.2, however well you ask. The eval has just told you which component to
    change next — retrieval, not wording — which is the whole point of
    running it before you spend a week on prompts.

    **Change X, to move Y, because Z.** This is the sentence you take to your
    stakeholder, and the harness is what lets you say it before anyone asks:

    | Change this component (X) | This column moves (Y) | Because the business measures (Z) |
    | --- | --- | --- |
    | Prompt asks for the policy clause by name | `required` ↑ | Overturn rate on appeal — a recommendation with its clause survives review |
    | Add the "was the policy in force on the date of loss" check before answering | wrong-pay rate on the generated lapsed-policy set ↓ | Leakage — the vendor's failure, in pounds |
    | Instruct it to say "escalate" when the claim is outside the clause | `declines` ↑ | Overturns, and the claims that reach a regulator |


    ---
    ### ❓ Question #4

    Loop B showed a change whose effect you could or could not see on your
    goldens. In one to three sentences: pick one component of *your* system
    you would change next — the prompt, the retriever, the model — name the
    column you expect to move, and the business number that column translates
    to. Then say how many cases you would need before the interval could show
    a five-point change, and what Loop A lets you do about it.

    **Answer:**

    ---
    ## Task 6 — The framework in your harness, and Marcus's page

    **Production: is it still working, and against what?** A saved baseline
    with a fingerprint is what every later run is compared to and what a
    regression is measured against; the translation into the Head of Claims'
    units is what keeps the harness funded long enough to run.

    Two things are left: the framework's metric has to run *inside* your
    harness — one run, one report, model-free scorers and the framework's
    judge in the same table, saved so a later run can compare against it —
    and the number has to come out in the Head of Claims' units.
    """)
    return


@app.cell
def _(mo):
    run_baseline = mo.ui.run_button(label="📏  Run four systems through the harness with the framework's judge, and save the baseline")
    mo.vstack(
        [
            run_baseline,
            mo.md(
                "<sub>Your goldens; echo, the basic prompt, the elaborate prompt, and the oracle; "
                "the four model-free scorers plus DeepEval's `GEval` correctness as a fifth, through "
                "`helpers.harness` so the run is saved with a fingerprint. The elaborate prompt's run "
                "is the baseline that gets saved. Roughly five model calls per golden: one answer and "
                "two judge calls per prompt, plus the framework's judge on echo and oracle.</sub>"
            ),
        ]
    )
    return (run_baseline,)


@app.cell
def _(
    BASIC_PROMPT,
    CFG,
    ELABORATE_PROMPT,
    FRAMEWORK_JUDGE,
    GEval,
    LLMTestCase,
    SEEDS,
    SingleTurnParams,
    answer_with,
    contains_required,
    declines,
    exact_match,
    mo,
    run_baseline,
    token_f1,
    ui,
):
    mo.stop(not run_baseline.value, mo.md("*Press the button to run.*"))

    import sys as sys_for_harness

    sys_for_harness.path.insert(0, str(CFG.root))
    from helpers import harness

    # A framework metric wrapped as a harness scorer: (actual, case) -> 0..1.
    # This is the whole integration. Anything with that signature can sit in
    # the same dict as exact_match, and the report cannot tell them apart.
    baseline_correctness = GEval(
        name="Correctness",
        criteria="Does the actual output convey the same substance as the expected output? Wording and length do not matter; a missing or contradicted fact does.",
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        model=FRAMEWORK_JUDGE,
    )

    def framework_correctness(actual: str, case: dict) -> float:
        baseline_correctness.measure(
            LLMTestCase(input=case["input"], actual_output=actual, expected_output=case["output"])
        )
        return float(baseline_correctness.score or 0.0)

    BASELINE_SCORERS = {
        "exact": exact_match,
        "f1": token_f1,
        "required": contains_required,
        "declines": declines,
        "correctness (GEval)": framework_correctness,
    }

    baseline_answer_key = {seed["input"]: seed["output"] for seed in SEEDS}
    # Echo and oracle bracket the range; the two prompts are the real systems.
    BASELINE_SYSTEMS = {
        "echo": lambda text: text,
        "basic prompt": answer_with(BASIC_PROMPT),
        "elaborate prompt": answer_with(ELABORATE_PROMPT),
        "oracle": lambda text: baseline_answer_key[text],
    }
    BASELINE_REPORTS = {}
    for baseline_name, baseline_system in BASELINE_SYSTEMS.items():
        with mo.status.spinner(title=f"Harness: {baseline_name}…"):
            BASELINE_REPORTS[baseline_name] = harness.run(SEEDS, baseline_system, BASELINE_SCORERS, name=baseline_name)

    # The elaborate prompt is the system you would actually ship, so its run is the
    # baseline -- a real number with a real interval, not the oracle's 1.0.
    BASELINE_REPORT = BASELINE_REPORTS["elaborate prompt"]
    BASELINE_PATH = harness.save(BASELINE_REPORT, CFG.use_case / "evals" / "s7_baseline.json")

    ui.table(
        [
            {"system": report.name, "n": report.n, **{label: f"{value:.2f}" for label, value in report.means.items()}}
            for report in BASELINE_REPORTS.values()
        ],
        title="One harness, four systems, five scorers — four you wrote, one from the framework",
    )
    return BASELINE_PATH, BASELINE_REPORT


@app.cell(hide_code=True)
def _(BASELINE_PATH, CFG, mo):
    mo.md(f"""
    **The oracle must score 1.0 on the framework's metric too.** If it does
    not, the framework's judge is wrong for your data, and you found out on a
    system you built to be perfect rather than on a prompt that "failed". The
    echo row is the floor. The two prompts are the real systems, and they sit
    between the bounds — read where each column lands, and whether the
    framework's judge agrees with yours about which prompt is better.

    The elaborate prompt's run is saved at `{BASELINE_PATH.relative_to(CFG.root)}`
    with a fingerprint of the cases and scorers that produced it. That file,
    not the table, is the baseline. If a later run uses different goldens or
    scorers, `harness.compare` refuses to compare the two — on purpose,
    because 0.94 on twelve cases is not a win over 0.91 on sixty. The same
    one line, `harness.save(...)`, on your own app's run is the challenge's
    `baseline.json`, which later weeks have to beat.

    > **🏢 In the enterprise:** notice what it took to run the framework here —
    > a telemetry opt-out before the import, a fifteen-line judge class because
    > the shipped wrappers guess which key to send, an explicit token budget so
    > the judge's JSON is not truncated, and a judge model that is the one
    > that answered unless you say otherwise. None of that is in the metric's
    > documentation. A framework is a dependency like any other; raise the
    > telemetry line with procurement before the install, not after.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Marcus's page, in the Head of Claims' units

    Everything above produced rates between 0 and 1. The Head of Claims
    measures overturns, leakage and cycle time, and he asked how sure Marcus
    is. The cell below is the translation — the same arithmetic you will do
    for your own stakeholder, with your own numbers in the three boxes.
    """)
    return


@app.cell
def _(mo):
    claims_per_year = mo.ui.number(start=1000, stop=1_000_000, step=1000, value=20_000, label="claims per year")
    average_claim_gbp = mo.ui.number(start=100, stop=100_000, step=100, value=1_800, label="average claim, £ (placeholder — use yours)")
    wrong_pay_rate = mo.ui.number(start=0.0, stop=0.2, step=0.001, value=0.015, label="wrong-pay rate on the generated lapsed-policy set")
    mo.hstack([claims_per_year, average_claim_gbp, wrong_pay_rate], gap=1)
    return average_claim_gbp, claims_per_year, wrong_pay_rate


@app.cell
def _(
    BASELINE_REPORT,
    average_claim_gbp,
    bootstrap_ci,
    claims_per_year,
    mo,
    wrong_pay_rate,
):
    # Agreement -> overturns. The judge's correctness score on the goldens stands
    # in for agreement with adjudicated decisions (exact match is 0 for free text);
    # the bootstrap puts the interval on it. Overturn rate = 1 - agreement.
    agreement_scores = [result.scores.get("correctness (GEval)", 0.0) for result in BASELINE_REPORT.results]
    agreement, agreement_low, agreement_high = bootstrap_ci(agreement_scores)

    # Leakage -> pounds. Wrong-pay rate times claims times the average claim.
    leakage_gbp = wrong_pay_rate.value * claims_per_year.value * average_claim_gbp.value

    mo.md(
        f"""
    | He asked | The number, in his units |
    | --- | --- |
    | **Overturns?** | agreement {agreement:.0%} on n={BASELINE_REPORT.n}, so an overturn rate of about **{1 - agreement:.0%}**, 95% CI **[{1 - agreement_high:.0%}, {1 - agreement_low:.0%}]** |
    | **Leakage?** | {wrong_pay_rate.value:.1%} wrong-pay on the generated lapsed-policy set × {claims_per_year.value:,} claims × £{average_claim_gbp.value:,.0f} ≈ **£{leakage_gbp:,.0f} a year** |
    | **How sure?** | the interval above is on n={BASELINE_REPORT.n}; to see a five-point change it needs a few hundred cases |

    <sub>Agreement is the framework's correctness score for the elaborate prompt on your goldens — a real number from the saved baseline, which is why the interval is wide. If it is low, the page is telling the truth: a prompt-only system without the policy wording does not match adjudicated decisions, and the next component to change is retrieval. Swap in whichever column your own decision rests on, and change the three boxes to your own figures.</sub>
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    That table is the deliverable: three rows a person who has never heard of
    a bootstrap can act on, each traceable to a cell above, each with its own
    doubt attached. Changing a component of your system should move one of
    those rows, and the harness is how you know which one before anyone asks.

    ### Framework, or your own? It depends where you are

    You have now run the framework and written the whole thing yourself, so
    the comparison is on the table rather than in the abstract. The honest
    answer changes as the work moves:

    | Stage | The question | Use |
    | --- | --- | --- |
    | **MVP** — does it work at all? | your goldens, pass rate, eyeballs | **Adopt the framework whole.** Its defaults are fine for a yes/no, and it is an afternoon |
    | **PoC** — does it work well enough to fund? | back-tested history, a judge you checked, an interval | **Blend.** The framework for the standard metrics and the CI plumbing; your own scorers for the handful of criteria that decide the product; its judge checked exactly as you checked yours |
    | **Production** — is it still working? | live traffic, sampled, scored continuously | **Own the gate.** Model-free scorers on every commit, blocking merge; the framework's judge nightly on a sample, pinned and re-checked when the model changes |

    > The reasoning behind each row — what DeepEval added, what it did not,
    > and why the transition that matters is MVP to PoC — is in the **Bonus
    > Tasks** at the end of this notebook.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Conclusion

    You ran the framework first and got six numbers in a minute. Then you
    wrote the harness it is made of in forty lines and tested it before
    trusting it, built a judge and checked it before believing it, climbed
    the scorer ladder on failures you generated from your own goldens, put an
    interval on the difference between two prompts, and watched most of the
    gaps span zero on eight cases. The number was never the point. Knowing
    what would make it wrong is.

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Cases | A handful of golden examples | Thousands, sampled from live traffic and reviewed weekly |
    | Scorers | A dict of four functions | A registry, versioned, with each scorer's own regression tests |
    | Judge | One rubric, checked once | Multiple judges, model pinned, re-checked whenever the model changes |
    | Failures | Corruptions of your own goldens | A generator tuned so the synthetic failures are as hard as the real ones |
    | Intervals | A bootstrap on the whole set | Intervals per slice, so you can see which segment moved |
    | Framework | DeepEval's metrics, judged by the same model that answered | Pinned version, pinned judge model, telemetry off at install, its judge re-checked with yours |
    | Reporting | `report()` printing a dict | A dashboard with per-slice breakdowns and trend lines |
    | Cadence | Run when you remember | Model-free scorers on every commit, blocking merge; the judge nightly, on a sample |

    The last row is the one that decides whether the harness is still running in
    six months.

    ---
    # Additional Context

    - [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) — Hamel Husain. The most useful practical piece written on this topic; if you read one thing, this one
    - [Judging LLM-as-a-Judge (MT-Bench)](https://arxiv.org/abs/2306.05685) — Zheng et al., 2023. The paper that both established the technique and documented its biases — position, verbosity, self-preference. Task 4's check exists because of this paper
    - [Eugene Yan — LLM Evaluators](https://eugeneyan.com/writing/llm-evaluators/) — a thorough survey of what works, with attention to the failure cases
    - [AI Agents That Matter](https://arxiv.org/abs/2407.01502) — Kapoor et al., 2024. How benchmark numbers mislead when cost is not held constant — directly relevant to comparing your own configurations
    - [SummEval](https://github.com/Yale-LILY/SummEval) — Fabbri et al., 2021. Where the 480 rated summaries in `data/` come from, and the paper behind the agreement numbers in the Bonus calibration task
    - [DeepEval — metrics](https://deepeval.com/docs/metrics-introduction) — the framework this notebook ran; the metrics reference and the `GEval` page are where to look before writing a RAG scorer yourself, and the source of the prompts Task 4 read
    - [Ragas](https://docs.ragas.io/) — the other widely used framework, same ideas with a different API; worth knowing the name when a colleague's pipeline uses it
    - [In Defense of AI Evals, for Everyone](https://www.sh-reya.com/blog/in-defense-ai-evals/) — Shreya Shankar, 2025. A *pre-read for this session*: why systematic measurement is the tool teams without deep domain expertise cannot do without, and the answer to the colleague who says "just ship it and see"
    - [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Anthropic, 2026. The other *pre-read*: single-turn versus multi-turn, code graders versus model graders versus people, and how to design around real failure modes
    - **Keep building:** hand-score twenty of your own outputs into `use_case/evals/human_scores.jsonl`, press Task 4's button again, and read the agreement line — that is the half of the check this notebook could not do for you, and it is the challenge's first step.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Bonus Tasks

    Optional. The first is the long version of a check Task 4 ran short; the
    second is the reasoning behind Task 6's three-row table; the rest are the
    challenge's shape and some harder extensions.

    ### Bonus 1 — Calibrate against a published human-rated set

    Task 4's agreement check needs outputs a person already scored, and
    until you have hand-scored twenty of your own there is nothing to run it
    on. This session ships a stand-in: 480 machine-written summaries of 30
    news articles, each rated 1–5 by **three human experts** on four
    dimensions ([SummEval](https://github.com/Yale-LILY/SummEval), MIT). First,
    look at what the humans did.
    """)
    return


@app.cell
def _(JUDGED, ui):
    DIMENSIONS = ("consistency", "fluency", "relevance", "coherence")

    # Each score is the MEAN of three annotators, so unanimity can only be
    # bracketed: a mean of 1.0 or 5.0 is provably unanimous; a whole-number
    # mean (2.0) might be {2,2,2} or {1,2,3}.
    def agreement_bounds(dim: str) -> tuple[float, float]:
        vals = [row[dim] for row in JUDGED]
        at_least = sum(value in (1.0, 5.0) for value in vals) / len(vals)
        at_most = sum(abs(value - round(value)) < 1e-6 for value in vals) / len(vals)
        return at_least, at_most

    # What "the mean is whole" would score if the annotators were guessing.
    random_ratings = [(first, second, third) for first in range(1, 6) for second in range(1, 6) for third in range(1, 6)]
    CHANCE_FLOOR = sum((first + second + third) % 3 == 0 for first, second, third in random_ratings) / len(random_ratings)

    ui.table(
        [
            {
                "dimension": dimension,
                "agreed at least": f"{agreement_bounds(dimension)[0]:.0%}",
                "at most": f"{agreement_bounds(dimension)[1]:.0%}",
                "vs chance": f"{agreement_bounds(dimension)[1] / CHANCE_FLOOR:.1f}×",
                "mean score": f"{sum(row[dimension] for row in JUDGED) / len(JUDGED):.2f}",
            }
            for dimension in DIMENSIONS
        ],
        title=f"How often three experts agreed — bracketed (chance floor {CHANCE_FLOOR:.0%})",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three trained annotators agreed unanimously about **consistency** at
    least four times in five — close to a fact. On **coherence** they agreed
    at most a third of the time, which is barely above what three people
    answering at random would produce. A metric sitting on its own chance
    floor is not a weak signal; it is not a signal. **You cannot hold a judge
    to a standard humans do not meet**, so calibrate on the dimensions where
    agreement is high and report the subjective ones as signals.

    Now judge 24 stratified summaries for consistency two ways — the Task 4
    prompt, and the framework's `GEval` given the same criterion in one
    sentence — and compare both against the humans.
    """)
    return


@app.cell
def _(JUDGED, mo):
    SAMPLE_N = 24
    run_calibration = mo.ui.run_button(
        label=f"Judge {SAMPLE_N} human-rated summaries, two ways"
    )
    mo.md(
        f"About {SAMPLE_N * 3} model calls: one per summary for your judge, two or three per summary for the framework's. "
        f"Out of {len(JUDGED)} available. {run_calibration}"
    )
    return SAMPLE_N, run_calibration


@app.cell
def _(
    ARTICLES,
    FRAMEWORK_JUDGE,
    GEval,
    JUDGED,
    LLMTestCase,
    SAMPLE_N,
    SingleTurnParams,
    ask_judge,
    mo,
    np,
    run_calibration,
    ui,
):
    mo.stop(
        not run_calibration.value, mo.md("*Press the button to calibrate.*")
    )

    # The framework's judge, given the same criterion as CONSISTENCY_PROMPT in
    # one sentence. GEval expands that into evaluation steps itself and scores
    # 0-1; multiply by 4 and add 1 to put it on the humans' 1-5 scale.
    framework_consistency = GEval(
        name="Consistency",
        criteria="Does the actual output state anything the retrieval context (the article) does not support? Judge only factual support, not style, completeness or writing quality.",
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.RETRIEVAL_CONTEXT],
        model=FRAMEWORK_JUDGE,
    )

    calibration_rng = np.random.default_rng(0)
    # Stratified, deliberately: a random sample is 93% good summaries and tells
    # you almost nothing about whether the judge catches a bad one.
    bad_summaries = [row for row in JUDGED if row["consistency"] <= 2]
    good_summaries = [row for row in JUDGED if row["consistency"] >= 4.5]
    sampled_summaries = [
        bad_summaries[index] for index in calibration_rng.choice(len(bad_summaries), SAMPLE_N // 2, replace=False)
    ] + [
        good_summaries[index] for index in calibration_rng.choice(len(good_summaries), SAMPLE_N // 2, replace=False)
    ]

    CONSISTENCY_PROMPT = """Does this summary state anything the article does not support?

    ARTICLE:
    {article}

    SUMMARY:
    {summary}

    Score 1 to 5, where 5 means every claim is supported by the article and 1 means
    it contains clear fabrications. Judge only factual support -- not style, not
    completeness, not writing quality.

    Reply with JSON only: {{"score": <1-5>, "why": "<one sentence>"}}"""

    CALIBRATION = []
    for summary_row in ui.track(sampled_summaries, label="Judging sampled summaries"):
        verdict = ask_judge(
            CONSISTENCY_PROMPT.format(
                article=ARTICLES[summary_row["article_id"]][:3000],
                summary=summary_row["summary"],
            )
        )
        try:
            judge_score = float(verdict["score"])
        except (KeyError, TypeError, ValueError):
            judge_score = float("nan")
        framework_consistency.measure(
            LLMTestCase(
                input="Summarise the article.",
                actual_output=summary_row["summary"],
                retrieval_context=[ARTICLES[summary_row["article_id"]][:3000]],
            )
        )
        framework_score = 1 + 4 * framework_consistency.score if framework_consistency.score is not None else float("nan")
        CALIBRATION.append(
            {
                "human": summary_row["consistency"],
                "judge": judge_score,
                "framework": round(framework_score, 2),
                "summary": summary_row["summary"][:60],
            }
        )

    def calibration_summary(column: str) -> dict:
        """Agreement and separation for one judge column against the human mean."""
        pairs = [(entry["human"], entry[column]) for entry in CALIBRATION if entry[column] == entry[column]]
        humans = np.array([pair[0] for pair in pairs])
        scores = np.array([pair[1] for pair in pairs])
        correlation = float(np.corrcoef(humans, scores)[0, 1]) if len(pairs) > 2 else float("nan")
        return {
            "judge": {"judge": "yours (Task 4 prompt)", "framework": "DeepEval GEval"}[column],
            "correlation with humans": f"{correlation:.2f}",
            "within 1 point": f"{float(np.mean(np.abs(humans - scores) <= 1)):.0%}",
            "scored bad (≤2) at": f"{np.mean([entry[column] for entry in CALIBRATION if entry['human'] <= 2 and entry[column] == entry[column]]):.2f}",
            "scored good (≥4.5) at": f"{np.mean([entry[column] for entry in CALIBRATION if entry['human'] >= 4.5 and entry[column] == entry[column]]):.2f}",
            "unparseable": sum(entry[column] != entry[column] for entry in CALIBRATION),
        }

    CALIBRATION_SUMMARY = [calibration_summary("judge"), calibration_summary("framework")]

    mo.vstack(
        [
            ui.table(CALIBRATION[:10], title="Human, your judge, the framework's judge — first ten"),
            ui.table(CALIBRATION_SUMMARY, title="Two judges against the same 24 humans"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `GEval` takes a one-sentence criterion, has the model write its own
    evaluation steps, runs them, and maps the answer to 0–1 — two or three
    calls per summary, with a rubric the model wrote. More machinery; not
    more calibrated. Nothing in the framework compared it to a human, so its
    row is the first time anyone did. If the two rows land within a few
    points, the framework bought you convenience, not trust.

    ### Bonus 2 — The reasoning behind Task 6's table

    The transition that matters is **MVP to PoC**, and it is not technical: it
    is when you stop reporting "it looks good" and start reporting a number
    against data you did not choose. The vendor scored 94% on cases the vendor
    chose. Marcus's number comes from a quarter of adjudicated claims he did
    not select, as an overturn rate with an interval.

    > If you take one thing from this session: **the number has to come from
    > data you did not pick, and it has to come with an interval.**

    What DeepEval added: the standard RAG metrics without writing them, a
    rubric judge that writes its own steps, retries and schema parsing, a
    dataset object that takes the goldens a synthesizer grows, and a `pytest`
    entry point so the whole thing runs in CI. What it did not add: a
    threshold that means anything, a judge anyone checked, an interval, a
    human in the loop, or a view of *your* failure modes. Ragas (Apache 2.0)
    covers the same ground with a different API and heavier dependencies;
    the trade-offs are the same. Build your own for the handful of criteria
    that decide whether your product works, adopt the framework for the
    standard metrics and the CI plumbing, and check its judge exactly as you
    checked yours. You have read its prompts, so "I don't know what it
    measures" is no longer an excuse.

    ### Bonus 3 — Write the harness into `use_case/evals/`

    Turn this notebook into a file your later work imports:

    ```
    use_case/evals/
    ├── failures.md       # your taxonomy: what goes wrong, ranked, with counts
    ├── golden.jsonl      # hand-written, and growing
    ├── human_scores.jsonl  # twenty outputs you scored yourself — Task 4's agreement half
    ├── synthetic.jsonl   # the failures Task 5 generated, with their labels
    ├── harness.py        # run_eval, report, your scorers, bootstrap_ci
    ├── run.py            # point it at your system, print the report
    ├── baseline.json     # the run itself — commit this
    └── s7_baseline.json  # the elaborate prompt's run Task 6 saved, with the framework's judge as a fifth scorer
    ```

    Then run it against your own application and **save the run**, not the number:

    ```python
    from helpers import harness

    report = harness.run(SEEDS, my_system, SCORERS, name="baseline")
    harness.save(report, CFG.use_case / "evals" / "baseline.json")
    ```

    A saved run carries a **fingerprint of the cases and scorers that produced
    it**, so when a later run asks whether the fine-tuned open model beat this:

    ```python
    print(harness.compare(harness.load("baseline.json"), candidate))
    ```

    …it either gives you a per-scorer delta, or it refuses — because 0.94 on
    twelve cases is not a win over 0.91 on sixty. `helpers/judge.py` is the
    judge you built, packaged with the one rule kept structural:
    **`Judge.score()` raises until `calibrate()` has run and passed.**

    ### Deploy the dashboard

    This notebook is a `.py` file, so it is already deployable:

    ```bash
    uv run marimo run 04_Evals/sessions/S7_Practical_Evals.py --headless -p 8080
    ```

    Read-only, no source shown, live scores. Point a colleague at it.

    ---
    ### Harder

    - **Slice your results.** Overall pass rate hides everything. Score by input
      type, length, or source and you will usually find one segment carrying all
      the failures — that is where the next week of work is.
    - **Make your corruptions harder.** Change a number by 10% rather than an
      order of magnitude. Measure how much the judge's catch rate falls — that
      gap is how much your synthetic set was flattering you.
    - **Add a cost and latency column.** An eval that only measures quality will
      cheerfully recommend something four times slower and eight times dearer.
    - **Work out your minimum detectable effect.** Given the eval set you have,
      how large would an improvement need to be for you to see it? If the answer
      is larger than any improvement you expect, collect more cases before
      collecting more ideas.
    """)
    return


if __name__ == "__main__":
    app.run()
