# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "numpy>=2.0",
#     "pydantic>=2",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Synthetic Data Generation")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 4: Synthetic Data Generation

    *One worker, one problem, three departments in the way.*

    Priya is an operations analyst on the incident-response team at a regulated
    financial firm. She wants a model to draft post-incident reports from the
    incident database, and she has already learned to run a model where the
    data is. Now she has a different block: **she is not allowed to touch the
    incident database yet.** The access request is open, it needs three
    signatures, and the first of them wants to see a working prototype before
    signing. She needs inputs that look like incident records, without having
    any.

    | Who | What they said | What it means for the build |
    | --- | --- | --- |
    | **Information Security** | *"You may not query that table until the request clears. And anything you generate from what you already have — I want to know what survived."* | Generate from a description and five hand-scrubbed examples, then prove nothing distinctive leaked (Task 6) |
    | **Legal** | *"Incidents under legal hold are not test data. Not paraphrased, not anonymised, not at all. And if a score ends up in a filing, I need to know where the data it was scored on came from."* | Legal-hold records are excluded by rule, not by regex; every dataset carries a datasheet (Tasks 1, 7) |
    | **Procurement** | *"The generator model goes through the gateway on the approved list. It is rate-limited, and the limit is per team, not per person."* | A batch loop that survives 429s and counts what it lost (Task 3) |

    This notebook is Priya's next week. A generator that turns her five
    hand-written incident examples into a few hundred, a deduplicator written
    from scratch, a schema validator that throws most of the output away, and
    a leak check before anything is committed. The output is
    `use_case/data/synthetic_v1.jsonl` and the datasheet that says what it can
    and cannot prove — the second is the part Legal will read. Each decision
    she makes ends with the condition under which yours would be different:
    her three departments are one firm's, and the reasoning is the part that
    transfers.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - Task 1: Two kinds of synthetic data
    - Task 2: Variation axes
    - ❓ Question #5
    - Task 3: Generate
    - Task 4: Deduplicate, from scratch
    - ❓ Question #6
    - Task 5: Validate against the schema
    - Task 6: What did I just leak?
    - ❓ Question #7
    - Task 7: Write the datasheet
    - ❓ Question #8
    - The library
    - Conclusion
    - Additional Context
    - Bonus Tasks

    > 📓 **Not covered here:** choosing the axes for *your* inputs, reading the
    > rows yourself, and writing the datasheet properly. Those are the challenge.
    > Priya's axes are a worked example, not a template — the point of the
    > session is that you will not be able to reuse them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | LiteLLM | the generation call, through whichever gateway Procurement approved | [docs.litellm.ai](https://docs.litellm.ai/) |
    | pydantic | the schema from your charter, as the validator in Task 5 | [pydantic.dev/docs](https://pydantic.dev/docs/validation/latest/get-started/) |
    | itertools | the cross-product of your axes in Task 3 | [docs.python.org — itertools](https://docs.python.org/3/library/itertools.html) |
    | DeepEval | the library version of this loop — its `Synthesizer` grows goldens from goldens, for after you have done it by hand | [deepeval.com — Synthesizer](https://deepeval.com/guides/guides-using-synthesizer) |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Priya's situation is the normal one. You probably cannot put your real data
    in a prototype yet — it needs an approval, or a DPIA, or a network path that
    does not exist from your laptop. Waiting for that is often a multi-week
    block, and it arrives before you have anything to show that would justify
    the request. The signature she needs *is the reason she cannot get the
    data that would earn the signature.*

    Generating stand-in data breaks the loop. The generation itself is a prompt
    and a loop; the work is in the constraints. A generated set inherits the
    distribution of whatever produced it, so it can demonstrate that her
    pipeline runs, that her schema holds, and that her evaluation harness
    scores — and it cannot tell her how the system performs on real incidents.
    Being precise about which of those you are claiming is the difference
    between a prototype that earns the signature and one that earns a false
    sense of confidence, and the second kind is the one that ends up in a
    slide.

    **What Priya has.** Five incidents she wrote up herself, from memory, with
    every hostname, customer and ticket number invented: a payment-gateway
    timeout, a certificate that expired on a Sunday, a batch job that ran
    twice, a phishing report that turned out to be real, and one invented
    outright to be under legal hold — where the accepted "report" is a refusal
    to draft. None of them is a real record. Each has the report she would
    have accepted. Those five are her seeds, and they are what this notebook
    needs from you in your own domain.

    **Estimated time:** 35–45 minutes

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    GOLDEN = CFG.use_case / "evals" / "golden.jsonl"
    print(f"✅ {CFG}")
    return CFG, GOLDEN, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### How hard should the five be?

    Everything generated below is grown from your five golden examples, so
    their shape decides the shape of the whole dataset. The mistake to avoid
    is five examples of the same difficulty. Five routine cases teach the
    generator that every input is routine, and the dataset will never contain
    the case that breaks your system; five hard cases teach it that nothing is
    ever simple, and the dataset will not contain the eighty percent of real
    traffic that is. **Write the five as a ladder, one rung each**, and let
    the generator fill in the gaps between rungs.

    | Rung | What the input looks like | What the accepted output has to do | Priya's example |
    | --- | --- | --- | --- |
    | **1 · Plain** | One event, one cause, one fix, every fact present, written by someone who knew what they were doing | Restate it in the house format without adding a single fact | A pool-exhaustion incident fully resolved by the on-call engineer, with the follow-up already named |
    | **2 · Detailed** | Several facts that have to be kept straight — numbers, times, two systems, a request from someone senior — all of them present | Keep every number, attribute the cause to a process rather than a person, carry the request to the right section | An expired certificate: cause is a missing deploy step from last month's migration, 112 clients affected, the CTO wants it in a committee pack |
    | **3 · Partial** | Second-hand, incomplete, or contradictory: a manager's forwarded ticket, no engineering notes, a theory nobody has checked | Say what is known, mark what is not, refuse to promote a guess to a cause | *"Is this an outage or not?"* — a blank dashboard, some users affected, a browser update suspected, nothing confirmed |
    | **4 · Judgement** | Nothing went wrong on paper, but the right follow-up requires knowing the history | Resist inflating it; put the one thing that matters in follow-up | A report forty minutes late because a vendor feed was late — for the second time this month |
    | **5 · Decline** | Something in the input means the system must not do its job | Refuse, say why, say who to ask — and repeat nothing from the record | A record under legal hold |

    The **detailed** rungs carry the most information per example, because
    the output has to *do* things — keep facts straight, assign cause, route a
    request — that a plain example never exercises. They are also the ones
    that take the longest to write, which is why people skip them. Write
    those first, while you have the patience. The **partial** and **decline**
    rungs are what stop the generator from producing a dataset in which every
    input has a clean answer; a system that has never seen one will invent a
    root cause the first time production hands it a ticket with none.

    Three tests for each one before you save it:

    - **Is every fact in the output traceable to the input?** If the accepted
      output knows something the input did not say, the example is teaching
      the system to hallucinate politely.
    - **Would two colleagues accept the same output?** If the rung is
      *judgement*, write down in the `why` field what the judgement was —
      that field is for you, and it is what the datasheet quotes later.
    - **Could a reader who knows the domain identify a real event?** Invent
      the names, the identifiers and the dates, and change one fact that
      would otherwise make the story recognisable.

    > **🔀 Where your path diverges.** Priya's ladder is five rungs because an
    > incident report has five sections and one of them can be refused. If
    > your output is a classification, the rungs are *obvious*, *borderline*,
    > *out of distribution* and *should abstain*; if it is an extraction, they
    > are *all fields present*, *some missing*, *conflicting values*, and
    > *the document is the wrong kind*. The ladder is the same idea in each
    > case: **easy, hard-but-complete, incomplete, judgement, refuse** — pick
    > the four or five your system will actually meet.
    """)
    return


@app.cell
def _(GOLDEN, mo):
    import json

    golden_text = GOLDEN.read_text(encoding="utf-8") if GOLDEN.exists() else ""
    SEEDS = [json.loads(line) for line in golden_text.splitlines() if line.strip()]

    mo.stop(
        not SEEDS or any("REPLACE ME" in seed.get("input", "") for seed in SEEDS),
        mo.md(r"""
        ### ⚠️ Your golden examples are still the template

        This session generates data **from your five hand-written examples**.
        Without them there is nothing to vary. Priya wrote hers from memory,
        with every name invented — that is the version Security can live with.

        Go back to
        [`use_case/evals/golden.jsonl`](../../use_case/evals/)
        and write them. Five, by hand — it takes about twenty minutes and it is
        the seed for everything generated below.
        """),
    )

    mo.md(f"✅ {len(SEEDS)} seed examples loaded.")
    return SEEDS, json


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — Two kinds of synthetic data

    "Synthetic data" names two different artifacts, produced differently and
    failing differently. Priya needs both this month, and Legal cares about
    them differently. Keep them in separate files.

    | | **For prototyping** | **For backtesting** |
    | --- | --- | --- |
    | What it is | Incident records that look like hers | Incident records *with the report she would accept* |
    | What it is for | Getting the pipeline running and the demo in front of the first signature | Measuring whether the drafts are any good |
    | Where labels come from | There are none | She writes or verifies them |
    | How much you need | Hundreds — coverage matters | Dozens — correctness matters |
    | Failure mode | Looks real, isn't representative | Labels are wrong, so the score is fiction |
    | Safe to share? | Usually — that is the point | Usually — but see Legal's rule below |
    | What Legal asks | "Did any of it come from a record you were not cleared to see?" | "Where did the labels come from, and can you show me the datasheet?" |

    You need both, and you make them differently. Prototyping data can be
    generated freely and never checked — nothing downstream depends on it being
    correct.

    **Backtesting data with unverified labels is worse than having none.** It
    produces a score, the score goes in a slide, the slide goes to the steering
    committee, and nobody re-derives it. An empty eval set at least reads as
    empty. This is the false confidence Legal's second question is aimed at:
    not that the number is wrong, but that nobody can say what it was
    measured on.

    **And one rule that is not a data-quality rule.** Incidents under legal
    hold are not test data of either kind — not paraphrased, not with the
    names changed, not at all. That exclusion happens *before* generation, by
    choosing seeds that were never under hold, and no filter later in this
    notebook can substitute for it. Priya's five seeds are ones she wrote from
    memory for exactly that reason.

    > **🔀 Where your path diverges.** Priya generates from a description and
    > five invented examples because she *cannot* touch the real records yet,
    > and because generating from a description removes the outward leak path
    > entirely. That is the default here and the right one for
    > anything you will share. It is not the only strategy. If the owning team
    > will give you a **masked export** and policy allows it in a dev
    > environment, use it to *check* your synthetic set's distribution — not
    > as the seeds, because rare scenarios survive masking and still identify a
    > customer. If your firm **allows development on real data locally**, you
    > can run this pipeline on it and share only the numbers — strongest for
    > the eval weeks, nothing to show a classmate. And if your domain has a
    > **public dataset in the same shape**, it is good for format fidelity and
    > wrong in distribution; say which.

    ---
    ## Task 2 — Variation axes

    The naive approach — "generate 200 more like these" — gives you 200
    paraphrases of five incidents. Superficially varied, structurally
    identical, and it will hide every failure Priya's drafter has.

    Instead, name the dimensions along which real incident records vary, and
    generate across them deliberately. This is the step that decides whether
    the dataset is worth anything, and it is also the step that forces the
    question most prototypes skip: **who actually files these, and what state
    are they in when they do?** Priya cannot write a persona into a prompt
    without knowing that. Neither can you. If you cannot fill in the first
    axis below for your own inputs, you have found the real block, and it is
    not the data-access request.

    Below are Priya's axes. Same four keys you will find in almost every
    enterprise text problem; her values, for incident records.
    """)
    return


@app.cell
def _():
    # Priya's axes, for incident records. Rewrite these for your use case --
    # the four KEYS vary in almost every enterprise text problem; the VALUES
    # are hers, and yours will be different.
    AXES = {
        "persona": [
            "a first-line support agent relaying a customer complaint",
            "an on-call engineer writing at 3 a.m., mid-incident",
            "a business manager who saw the outage but not the cause",
            "a security analyst using precise jargon and ticket references",
        ],
        "length": ["one terse line", "a normal paragraph", "a rambling wall of text"],
        "difficulty": [
            "completely routine -- a known failure with a known fix",
            "ambiguous -- could be an outage or a misconfiguration",
            "under legal hold -- the system should decline to draft anything",
        ],
        "quality": [
            "clean prose typed into the ticketing form",
            "typos and abbreviations pasted from the on-call chat",
            "pasted from an email chain with the thread still attached",
        ],
    }

    combination_count = 1
    for axis_values in AXES.values():
        combination_count *= len(axis_values)
    print(f"{len(AXES)} axes -> {combination_count} distinct combinations")
    return (AXES,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice the third value under `difficulty`. **A record the system should
    decline to draft** belongs in the dataset from the start — for Priya, one
    marked as under legal hold.

    That is not the same thing as Legal's rule in Task 1. Legal's rule keeps
    real held incidents *out of the seeds*. This axis puts *invented* held
    incidents *into the generated data*, so that the drafter is tested on
    whether it refuses them. A system that never says "I can't draft this" is
    not confident, it is uncalibrated, and you will not find that out unless
    your data contains cases where declining is the right answer. Most
    synthetic datasets contain none, which is why most systems built on them
    are confidently wrong at the worst moment — and in Priya's case the worst
    moment is a regulator reading a draft that should never have existed.

    ---
    ### ❓ Question #5

    The four axes above are Priya's, and they were chosen for incident
    records. Name **one axis specific to your domain** that her four miss,
    and in one to three sentences say which failure of your system it would
    expose that two hundred paraphrases of your five examples never could.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 3 — Generate

    One prompt per axis combination, seeded with your five examples so the
    output keeps their shape. Read the example prompt that prints below: the
    persona line is where Priya's understanding of her users either shows up
    or does not. A vague persona produces a vague record, and a vague record
    tests nothing.

    The call goes through the gateway Procurement approved, and that gateway
    has a rate limit shared across her team. Watch the two counters at the end
    of the run — they are different failures.

    > **🏢 In the enterprise:** this loop is a batch job, and it gets re-run —
    > when the schema changes, when a new axis is added, when a better
    > generator model appears on the approved list. The choice it forces is
    > whether each run is reproducible: the prompt template, the generator
    > model and version, the seeds it saw, and the sampler settings, written
    > down *with* the output. Legal asked Priya exactly this about the
    > drafter's output; the answer for the dataset is the same one. A dataset
    > whose provenance is "someone ran a notebook in March" cannot be
    > regenerated, cannot be audited, and cannot be trusted six weeks later —
    > and that is the version most teams have.
    """)
    return


@app.cell
def _(AXES, SEEDS, json, mo):
    import itertools

    def build_prompt(seeds, combo: dict, example_count: int = 3) -> str:
        """One generation prompt for one point in the axis space."""
        shown = "\n".join(json.dumps(seed, ensure_ascii=False) for seed in seeds[:3])
        described = "\n".join(f"- {axis}: {value}" for axis, value in combo.items())
        return (
            "Here are real examples of inputs to a system, with the outputs a "
            "domain expert accepted:\n\n"
            f"{shown}\n\n"
            f"Generate {example_count} NEW examples in the same JSON format, one per line.\n"
            "They must match this profile:\n"
            f"{described}\n\n"
            "Rules:\n"
            "- Invent all names, identifiers, and companies. Never reuse any "
            "from the examples.\n"
            "- Vary the substance, not just the wording.\n"
            "- If the profile says the system should decline, the output should "
            "say so plainly.\n"
            "- Output only JSON lines, nothing else."
        )

    COMBOS = [
        dict(zip(AXES, values))
        for values in itertools.product(*AXES.values())
    ]

    mo.md(
        f"**{len(COMBOS)} combinations.** Sampling a subset below — generating "
        f"all of them is the Activity.\n\n"
        f"Example prompt:\n\n```\n{build_prompt(SEEDS, COMBOS[0])}\n```"
    )
    return COMBOS, build_prompt


@app.cell
def _(COMBOS, mo):
    n_combos = mo.ui.slider(1, min(24, len(COMBOS)), value=6, label="Combinations to run")
    go = mo.ui.run_button(label="Generate")
    mo.vstack([n_combos, go])
    return go, n_combos


@app.cell
def _(CFG, COMBOS, SEEDS, build_prompt, go, json, mo, n_combos):
    mo.stop(not go.value, mo.md("*Click **Generate** above.*"))

    from litellm import completion

    RAW = []
    unparseable_lines = 0      # the model emitted a line that is not JSON
    dead_combos = 0            # the call itself failed — a whole axis point missing
    with mo.status.progress_bar(total=n_combos.value, title="Generating") as generation_bar:
        for combo in COMBOS[: n_combos.value]:
            try:
                # Explicit timeout. Inheriting the library default is how a
                # generation run hangs for forty minutes and returns nothing —
                # a retrieval concern, covered separately.
                reply = completion(
                    **CFG.kwargs(),
                    messages=[{"role": "user", "content": build_prompt(SEEDS, combo)}],
                    timeout=600,
                ).choices[0].message.content or ""
            except Exception:
                dead_combos += 1
                generation_bar.update()
                continue

            for reply_line in reply.splitlines():
                reply_line = reply_line.strip().strip("`")
                if reply_line.startswith("{"):
                    try:
                        RAW.append({**json.loads(reply_line), "_axes": combo})
                    except json.JSONDecodeError:
                        unparseable_lines += 1
            generation_bar.update()

    # These two are different failures and must not share a counter. An
    # unparseable line means the model wrote badly; a dead combo means a point
    # in your axis space produced nothing at all, so the coverage you think you
    # have is smaller than you think. Averaging them into one number hides the
    # second one entirely.
    print(f"✅ {len(RAW)} rows · {unparseable_lines} unparseable lines · {dead_combos} dead combos")
    if dead_combos:
        print(f"⚠️  {dead_combos} axis combinations returned nothing — your coverage has holes there.")
    return (RAW,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 4 — Deduplicate, from scratch

    Models repeat themselves. Ask for variety across 24 prompts and you will get
    the same three outages rewritten, and Priya's "500-row dataset" will have
    perhaps 80 distinct incidents in it. The first signature she needs is from
    someone who will ask how many *different* things the prototype has seen,
    and "500" is the wrong answer.

    We measure similarity with **character n-gram Jaccard** — the overlap between
    two texts' sets of character 4-grams. No embeddings, no
    model call, and it catches near-duplicates that exact matching misses:
    reordered clauses, changed names, different punctuation.
    """)
    return


@app.cell
def _():
    def shingles(text: str, ngram_size: int = 4) -> set[str]:
        """The set of character n-grams. Cheap, and surprisingly effective."""
        normalized = " ".join(text.lower().split())
        return {normalized[start : start + ngram_size] for start in range(max(len(normalized) - ngram_size + 1, 1))}

    def jaccard(first: set, second: set) -> float:
        if not first or not second:
            return 0.0
        return len(first & second) / len(first | second)

    def dedupe(rows: list[dict], threshold: float = 0.7, key: str = "input"):
        """Keep a row only if it is unlike everything kept so far."""
        kept, kept_shingles, dropped = [], [], []
        for row in rows:
            row_shingles = shingles(str(row.get(key, "")))
            twin = next(
                (index for index, other in enumerate(kept_shingles) if jaccard(row_shingles, other) >= threshold),
                None,
            )
            if twin is None:
                kept.append(row)
                kept_shingles.append(row_shingles)
            else:
                dropped.append((row, kept[twin]))
        return kept, dropped

    return dedupe, jaccard, shingles


@app.cell
def _(RAW, dedupe, mo, ui):
    KEPT, DROPPED = dedupe(RAW)

    dedupe_summary = ui.table(
        [{
            "generated": len(RAW),
            "kept": len(KEPT),
            "dropped as near-duplicate": len(DROPPED),
            "actual variety": f"{len(KEPT) / max(len(RAW), 1):.0%}",
        }],
        title="Deduplication",
    )

    dropped_examples = ui.table(
        [
            {"dropped": pair[0].get("input", "")[:70], "because it matched": pair[1].get("input", "")[:70]}
            for pair in DROPPED[:5]
        ] or [{"dropped": "(nothing was duplicated)", "because it matched": ""}],
        title="What got dropped",
    )

    mo.vstack([dedupe_summary, dropped_examples])
    return (KEPT,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    That percentage is the honest size of the dataset. Report **that** number,
    not the number of rows you generated — in the datasheet, and in the meeting.

    > Tuning the threshold is a real decision. Too high and you keep paraphrases;
    > too low and you throw away genuinely different examples that happen to
    > share vocabulary. Look at what gets dropped before trusting it — the table
    > above exists for that.

    > **🔀 Where your path diverges.** Priya's 0.7 is tuned for incident
    > narratives: a few hundred characters of free text, where two records
    > about the same outage reworded are the failure she is hunting. **Short,
    > formulaic inputs** — tickets with a template, log lines, form fields —
    > share most of their characters by construction, and 0.7 will delete
    > legitimate near-twins; raise it, or shingle on the free-text field only.
    > **Long documents** — contracts, reports — go the other way: paraphrases
    > of one scenario can sit well below 0.7, so lower it and read more of the
    > drop table. The measure is the same either way; the threshold is a fact
    > about your text, and the *what got dropped* table is how you find it.

    ---
    ### ❓ Question #6

    Describe one case from your own domain where two inputs would share most
    of their vocabulary but differ in substance — for Priya, two records about
    the same payment gateway, one a timeout and one a certificate expiry, both
    written by the same on-call engineer in the same words. In one to three
    sentences, say whether that case makes you want to **raise or lower** the
    0.7 threshold, and what in the *what got dropped* table you would look at
    to decide.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 5 — Validate against the schema

    Your `use_case/CHARTER.md` defines an input and an output. That is a pydantic
    model. Use it. Everything that fails validation gets thrown away.

    Expect to discard a large fraction here. A row that fails validation would
    have thrown at your endpoint instead, so the only question is whether you
    find out now or in a request handler — for Priya, in the request handler
    that Security is watching on the day of the demo.

    > **🏢 In the enterprise:** the model below and the one your API validates
    > requests against should be the *same object*, imported from one place —
    > not a copy. The choice it forces is where the schema lives: in a shared
    > module both the generator and the endpoint import, or in two files that
    > agree today. The second is how a dataset passes validation on Tuesday and
    > the endpoint rejects it on Thursday, after someone added a required field
    > to one of them.
    """)
    return


@app.cell
def _():
    from pydantic import BaseModel, ValidationError

    # Replace with YOUR model, from your charter.
    class Example(BaseModel):
        input: str
        output: str

    return Example, ValidationError


@app.cell
def _(Example, KEPT, ValidationError, ui):
    VALID, INVALID = [], []
    for kept_row in KEPT:
        try:
            Example(**{key: value for key, value in kept_row.items() if not key.startswith("_")})
            VALID.append(kept_row)
        except ValidationError as validation_error:
            INVALID.append((kept_row, validation_error.errors()[0]["msg"] if validation_error.errors() else "invalid"))

    ui.table(
        [{
            "after dedupe": len(KEPT),
            "schema-valid": len(VALID),
            "rejected": len(INVALID),
            "reason (first)": INVALID[0][1] if INVALID else "—",
        }],
        title="Validation",
    )
    return (VALID,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 6 — What did I just leak?

    The step people skip, and the one Security asked for by name — and there
    are **two leaks**, in opposite directions, and most teams check for at
    most one.

    **The outward leak** is the one Security means: you generated *from*
    examples, and anything distinctive in those examples can survive into the
    output — which you are about to commit to a repo. Priya invented every
    name in her seeds, so the check below should come back clean for her. It
    is still run, because "should" is not what Security asked for.

    **The inward leak** is the one that quietly ruins evals, and it is the one
    Legal's *"where did the data it was scored on come from"* is really about.
    Teams build their golden set from the real edge cases they saw in
    production — the sensible thing to do — and then tune the system on the
    same production data: it goes into the prompt as examples, into the
    retrieval corpus, or later into a fine-tune. Now the eval set and the
    training data share a source, and the score that comes out measures how
    well the system reproduces what it was shown, not whether it is correct.
    It looks like a high number. It is self-consistency. Priya is protected
    from this by accident — she has no production data to tune on yet — and
    the second check below makes the protection deliberate, so that it still
    holds the month the access request clears.
    """)
    return


@app.cell
def _(SEEDS, VALID, ui):
    import re

    def leak_check(seeds, generated) -> list[dict]:
        """Look for distinctive strings from the seeds surviving into the output."""
        blob = " ".join(str(row.get("input", "")) + str(row.get("output", "")) for row in generated).lower()
        findings = []

        # Capitalized multi-word phrases and any token with digits: the shapes
        # that carry names, companies, and identifiers.
        for seed in seeds:
            text = f"{seed.get('input', '')} {seed.get('output', '')}"
            candidates = set(re.findall(r"\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,})+\b", text))
            # Include hyphens so TKT-99213 is reported whole rather than as 99213.
            candidates |= set(re.findall(r"\b[\w-]*\d[\w-]*\b", text))
            for candidate in candidates:
                if len(candidate) > 3 and candidate.lower() in blob:
                    findings.append({"leaked from your seed": candidate, "risk": "appears in generated data"})
        return findings

    outward_findings = leak_check(SEEDS, VALID)
    ui.table(
        outward_findings or [{"leaked from your seed": "— nothing detected —", "risk": ""}],
        title="Leak check — outward",
    )
    return


@app.cell
def _(SEEDS, VALID, jaccard, shingles, ui):
    # The inward check reuses the dedupe measure: how many generated rows are
    # near-twins of a golden? For Priya the answer should be "the paraphrases
    # of her five seeds", and the point is to know the number before any of
    # this data is used to tune anything the goldens will later score.
    INWARD_THRESHOLD = 0.5
    golden_shingles = [shingles(str(golden.get("input", ""))) for golden in SEEDS]
    inward_twins = []
    for valid_row in VALID:
        row_shingles = shingles(str(valid_row.get("input", "")))
        best_match = max((jaccard(row_shingles, golden_set) for golden_set in golden_shingles), default=0.0)
        if best_match >= INWARD_THRESHOLD:
            inward_twins.append({"generated row": str(valid_row.get("input", ""))[:60], "jaccard vs nearest golden": round(best_match, 2)})

    ui.table(
        inward_twins[:12] or [{"generated row": "— no generated row is a near-twin of a golden —", "jaccard vs nearest golden": ""}],
        title=f"Leak check — inward: {len(inward_twins)} of {len(VALID)} rows within {INWARD_THRESHOLD} of a golden",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    That second table is the number for the datasheet's **inward** section:
    how many rows of the set you are about to tune on are near-copies of the
    set you will later score with. If it is not zero — and for anything
    generated *from* the goldens it will not be — those rows go in the
    prototyping file and never in anything a golden is scored against. The
    rule that survives the access request is simple to state: **the goldens
    are written first, from memory, and nothing derived from them is ever on
    the training side of the line.**

    > **🔀 Where your path diverges.** Priya's inward number is a formality
    > this month because there is no training data yet. Yours is not if any of
    > these is true: your goldens were written from **real production cases**
    > that also feed a prompt, a retriever or a fine-tune; you plan to **tune
    > on the synthetic set** in a later week; or someone else on the team owns
    > the training data and nobody has asked. In each case the datasheet line
    > is *overlapping* or *unknown*, and the fix is a held-out split with a
    > named owner — not a bigger regex.

    > **A clean automated check is not a clearance.** It catches names,
    > companies, and identifiers. It cannot catch a distinctive scenario, an
    > unusual document structure, or a rare category that only one customer of
    > yours has. Priya's "certificate that expired on a Sunday" is invented —
    > but if it had really happened once, to one client, the regex would pass
    > it and the client would recognise it.

    Read a sample yourself before committing, against these four:

    - [ ] No real names, companies, or identifiers survived.
    - [ ] No distinctive internal formats — ticket reference schemes, hostname
          conventions, the shape of the on-call rota.
    - [ ] Rare categories were *generated*, not copied. A category with one real
          instance is identifying even with the name changed.
    - [ ] Nothing here would embarrass you in front of the person who signs the
          access request.

    The strongest protection is procedural rather than technical: **generate from
    the schema and a written description, not from real records.** You lose a
    little fidelity and you remove the leak path entirely. For prototyping data,
    that trade is almost always right — and it is the only version of this
    notebook Priya is allowed to run this month, because she has no real
    records to generate from.

    > **🏢 In the enterprise:** a regex is not a data-loss-prevention control,
    > and "it is synthetic" is not a classification. Generated data still needs
    > a label — public, internal, confidential — and somebody who can sign off
    > on it leaving the boundary. Security's question to Priya was not "is it
    > clean" but "what survived" — a question about provenance, which a
    > classification label answers and a regex does not. The choice it forces
    > is whether you find out who the signer is now, with twenty rows and a
    > datasheet in hand, or later, when a shared repo already contains a
    > category only one of your customers has. Generating from a description
    > rather than from records is usually what makes the sign-off a formality.

    ---
    ### ❓ Question #7

    The regex check above came back clean, or nearly. Name **one thing in your
    own seed examples** that this check cannot see and that would still
    identify your firm, your customer, or your team to a reader who knows the
    domain — the way a real Sunday certificate expiry would identify Priya's —
    and in one to three sentences, say what you would do about it before
    committing.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 7 — Write the datasheet

    A dataset without a datasheet gets misused, and usually by you, in about six
    weeks, when you have forgotten what it can prove. For Priya it is also the
    document Legal asked for in Task 1: the answer to "where did this come
    from" for anything that later turns into a score.
    """)
    return


@app.cell
def _(RAW, VALID, mo):
    write = mo.ui.run_button(label="Write to use_case/data/")
    mo.md(
        f"{len(VALID)} valid rows from {len(RAW)} generated. {write}\n\n"
        "*The data is gitignored; the datasheet is not.*"
    )
    return (write,)


@app.cell
def _(CFG, VALID, json, mo, write):
    mo.stop(not write.value, mo.md("*Click above when you are happy with the data.*"))

    output_path = CFG.use_case / "data" / "synthetic_v1.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            json.dumps({key: value for key, value in row.items() if not key.startswith("_")}, ensure_ascii=False)
            for row in VALID
        )
        + "\n",
        encoding="utf-8",
    )

    mo.md(
        f"✅ Wrote {len(VALID)} rows to `{output_path.name}`.\n\n"
        "Now fill in `use_case/data/DATASHEET.md` — particularly **what this data "
        "cannot validate**, and the new **inward leakage** line: are the goldens "
        "disjoint from anything this system is tuned on? Those two sections are "
        "the ones that stop the data being misused, and the ones Priya's Legal "
        "team reads first."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🔀 Where your path diverges.** Priya's datasheet says *prototyping*,
    > because nothing in her file carries an output a human verified — and so
    > it can prove the pipeline runs and the schema holds, and no more. Yours
    > says *backtesting* only if the outputs were written or checked by the
    > person who judges them for real, and then it can support a number. The
    > honest middle is common: prototyping inputs with a *handful* of verified
    > rows set aside. Say which rows are which; a datasheet that blurs them is
    > how a demo score ends up in a steering-committee slide.

    ---
    ### ❓ Question #8

    Task 1 split synthetic data into two kinds. In one to three sentences, say
    which kind the file you just wrote is — **prototyping** or **backtesting**
    — and name one claim that therefore belongs in the datasheet's *"what it
    cannot validate"* section, specific to your data rather than the generic
    three. (Priya's is *"that the drafter handles incidents whose root cause
    was never found"* — none of her five seeds is one, so none of the
    generated rows can be.)

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## The library

    [DeepEval](https://deepeval.com/guides/guides-using-synthesizer) has a
    `Synthesizer` that does a more elaborate version of this loop. It can
    grow goldens from documents, from hand-written contexts, from scratch —
    or, closest to what you just did by hand, **from goldens you already
    have**:

    ```python
    from deepeval.synthesizer import Synthesizer
    from deepeval.synthesizer.config import EvolutionConfig, StylingConfig
    from deepeval.synthesizer.types import Evolution
    from deepeval.models import LiteLLMModel
    from deepeval.dataset import Golden

    seeds = [Golden(input=s["input"], expected_output=s["output"]) for s in SEEDS]

    synthesizer = Synthesizer(
        # Default is an OpenAI model called directly. Route it through the
        # same gateway as everything else instead -- the one Procurement approved.
        model=LiteLLMModel(model=CFG.llm_model, base_url=CFG.api_base),
        max_concurrent=4,                       # a rate-limited gateway, not a benchmark
        styling_config=StylingConfig(
            input_format="an on-call engineer's incident record, as typed under pressure",
            expected_output_format="a five-section post-incident report",
            task="draft the report a reviewer would accept from the record",
            scenario="a financial firm's operations team",
        ),
        evolution_config=EvolutionConfig(
            num_evolutions=1,
            evolutions={Evolution.CONSTRAINED: 0.4, Evolution.HYPOTHETICAL: 0.3,
                        Evolution.IN_BREADTH: 0.3},
        ),
    )
    grown = synthesizer.generate_goldens_from_goldens(goldens=seeds, max_goldens_per_golden=3)
    synthesizer.save_as(file_type="jsonl", directory=str(CFG.use_case / "data"))
    ```

    Two parts of that map directly onto what you built, and the mapping is
    the reason to have built it first:

    | You wrote | DeepEval calls it | What is different |
    | --- | --- | --- |
    | The axes in Task 2 — *who wrote it, how long, how hard, how messy* | **Evolutions** — `REASONING`, `MULTICONTEXT`, `CONCRETIZING`, `CONSTRAINED`, `COMPARATIVE`, `HYPOTHETICAL`, `IN_BREADTH` | Its axes are generic ways to make an input *harder*; yours are the ways *your* inputs actually vary. `IN_BREADTH` widens coverage; the other six add complexity, which is the rung ladder from the top of this notebook with the rungs chosen for you |
    | `dedupe()` in Task 4 and the schema check in Task 5 | **Filtration** — a critic model scores each synthetic input for self-containment and clarity, below 0.5 it retries, three times | It filters for *quality of the question*, not for near-duplicates of each other and not against your schema. You still run Tasks 4 and 5 on its output |
    | The `why` field in your goldens and the datasheet in Task 7 | `additional_metadata` on each golden carries the quality scores and the evolutions applied | Provenance of *how* a row was made, which is good — but nothing about where the seeds came from or what the set cannot validate. The datasheet is still yours to write |

    We did not use it, and the reason is worth knowing. Every evolution step
    and every filtration retry is a model call: five seeds × three goldens ×
    one evolution × a critic pass is forty-odd calls before you see a row,
    and the default `max_concurrent` of 100 against Priya's rate-limited
    gateway is a run that spends its first minute being told no. More
    importantly, the library hides the two decisions that determine whether
    the dataset is any good — **the axes** and **the dedupe threshold** — and
    picks a third for you, the complexity mix, as an `Evolution` distribution.
    Having set all three by hand once, you will set them in the library on
    purpose rather than by default.

    It is a good tool, and the right one when your goldens have **contexts**
    — retrieved passages, documents, the material an answer is supposed to be
    grounded in — because then `include_expected_output` writes outputs that
    are anchored to those contexts rather than invented, and the
    from-documents path can build the contexts for you. For Priya that is the
    month *after* the access request clears, not this one. It is the worked
    example for the bonus discussion at the end of the session, if there is
    time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Conclusion

    Priya turned five hand-written incidents into a dataset by naming what
    varies, generating across it, and then throwing most of the output away on
    purpose — near-duplicates, schema failures, anything that leaked — before
    writing down what the survivors can and cannot prove. The loop is small.
    The judgement is in the axes, the threshold, and the datasheet.

    What the three departments turned out to be asking for:

    | Department | The line | What answered it |
    | --- | --- | --- |
    | **Information Security** | "What survived?" | Seeds written from memory, the leak check, and a classification label rather than a regex |
    | **Legal** | "Not held records. And where did the score come from?" | Exclusion before generation; prototyping and backtesting kept apart; the datasheet |
    | **Procurement** | "Rate-limited, per team" | Two counters, so a throttled run reports its holes instead of hiding them |

    None of them stopped the prototype. Each of them changed what it had to
    write down.

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Coverage | Four axes, hand-written from what Priya knows about who files incidents | Axes derived from the real distribution once the access request clears, and revisited when the distribution moves |
    | Generation | A loop in a notebook, run once, through the approved gateway | A reproducible batch job: prompt template, generator model and version, seeds and sampler settings recorded with the output; retries on 429 with the dead combos re-queued |
    | Deduplication | Character n-gram Jaccard | MinHash + LSH, so dedupe is sub-quadratic over millions of rows |
    | Validation | A pydantic model copied into a cell | The same model the endpoint imports, from one shared module |
    | Leak check | A regex over the seeds | A DLP scan, a data classification, and a named person who signs off before anything leaves a boundary |
    | Exclusions | Held incidents kept out of the seeds by hand | A query against the hold register that the generator refuses to run without |
    | The dataset | One `synthetic_v1.jsonl` | Versioned datasets with lineage — which model, which prompt, which seed |
    | The datasheet | Markdown in your repo | The same, reviewed and signed off, because auditors ask — and because provenance is becoming a regulatory question |

    ---
    # Additional Context

    - [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) — Gebru et al. The origin of Task 7, and the most directly useful paper here for enterprise work: the questions it asks are the ones a reviewer will ask you. Appendix A has worked examples
    - [Self-Instruct](https://arxiv.org/abs/2212.10560) — Wang et al., 2022. Seed examples → generated instructions → filtering. This session is a small version of that pipeline, and reading it shows which parts were simplified
    - [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644) — Gunasekar et al., 2023. The strongest evidence that carefully generated data can beat much larger quantities of scraped data
    - [The False Promise of Imitating Proprietary LLMs](https://arxiv.org/abs/2305.15717) — the counterweight. Synthetic data from a strong model teaches style faster than substance, and naive evaluation will not tell you which you got
    - [DeepEval — using the Synthesizer](https://deepeval.com/guides/guides-using-synthesizer) — the library version of this loop, once you have set the axes and the threshold by hand. Read the *evolutions* section against the rung ladder at the top of this notebook: it is the same idea with the rungs chosen for you
    - [Designing synthetic datasets for the real world](https://research.google/blog/designing-synthetic-datasets-for-the-real-world-mechanism-design-and-reasoning-from-first-principles/) — Google Research, April 2026. Simula, and a *pre-read for this session*. Its claim is that coverage, difficulty and quality are separate dials you can set independently — which is what the axes in Task 2 are, by hand, and it builds the taxonomy from a description of the domain rather than from seeds, which is the Task 6 recommendation at scale
    - [How to Build Privacy-Preserving Evaluation Benchmarks with Synthetic Data](https://developer.nvidia.com/blog/how-to-build-privacy-preserving-evaluation-benchmarks-with-synthetic-data/) — NVIDIA, December 2025. The other *pre-read*: Priya's problem in healthcare, with tooling. Read it for the shape — generate, filter for quality, evaluate across difficulty levels — and notice that the difficulty levels are an axis
    - **Keep building:** turn Tasks 3–6 into a script that takes an axes file and a seeds file, writes the rows *and* a run manifest — model, prompt hash, settings, the four counts — next to them, and refuses to run if the manifest would overwrite one it cannot reproduce. Then add the one thing Priya's Legal team would ask for: a list of seed identifiers the run checked against the hold register before it started.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Bonus Tasks

    Optional. The first is worth doing if you have the hour; the rest are
    meaningfully harder.

    ### Generate the full axis space

    Run every combination, not the six you sampled — against a rate-limited
    gateway, this is where the dead-combo counter earns its keep. Then:

    1. Sort by axis and read one row from each. Do they actually differ, or did
       the model produce the same thing wearing different hats? Priya's usual
       finding: the "business manager" persona collapses into the "support
       agent" one, because she did not describe either well enough.
    2. Find the axis with the least real variation and improve its values.
    3. Add one axis specific to your domain that Priya's four miss.

    Then write `use_case/data/DATASHEET.md` properly. The **"what it cannot
    validate"** section is the one that matters, and it should be uncomfortable
    to write.

    ---
    ### Harder

    - **Measure coverage instead of asserting it.** Cluster your generated inputs
      and count how many clusters have only one member. Those singletons are the
      only genuinely novel rows you produced; everything else is a variation.
    - **Generate the labels separately from the inputs.** Have one call write the
      input and a second, without seeing the first's reasoning, write the output.
      Labels written by the same pass that wrote the question are suspiciously
      easy to answer.
    - **Poison your own dataset deliberately.** Insert twenty rows with wrong
      outputs and see whether your eval harness notices. If a bad label
      cannot be detected, your evals cannot be trusted either — and that is
      the false confidence Legal's second question exists to catch.
    - **Enforce the hold rule in code.** Give each seed an identifier, keep a
      tiny `hold_register.txt`, and make the generator refuse to start if any
      seed appears in it. Priya's exclusion is currently a habit; make it a
      check.
    """)
    return


if __name__ == "__main__":
    app.run()
