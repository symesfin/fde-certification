# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "numpy>=2.0",
#     "torch>=2.6",
#     "transformers>=5.0",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Local Inference Fundamentals")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 3: Local Inference Fundamentals

    *One worker, one problem, three departments in the way.*

    Priya is an operations analyst on the incident-response team at a regulated
    financial firm. Every incident ends with a post-incident report, and she
    writes the first draft of each one by hand from the incident database. She
    wants a model to write that draft. Three departments have an opinion:

    | Who | What they said | What it means for the build |
    | --- | --- | --- |
    | **Information Security** | Incident records contain customer identifiers and internal hostnames. *"Nothing in that table leaves the network."* | No hosted API. The model has to run where the data is |
    | **Legal** | Reports go into the regulatory filing. *"If a regulator asks why a sentence says what it says, you need to be able to regenerate it."* | Every draft has to be reproducible — which model, which settings, which seed — and kept for seven years |
    | **Procurement** | *"Only models on the approved list, and read the licence before you download anything."* | The model, and its licence, are a decision someone signs off |

    **What "local inference" means, and what this session is for.** *Inference*
    is running a trained model to get an output — as opposed to training it.
    *Local* means the model's weights are loaded on hardware you control — your
    laptop, a server inside your network — so the input never travels to a
    vendor's API and the model's raw output is yours to inspect. The goal of
    this session is that you can **explain what a model actually produces
    before it produces text, choose and defend the settings that turn that
    into words, run a model yourself, and argue the local-versus-hosted
    decision with measured numbers** rather than opinions.

    This notebook is Priya's week. Every sampler a modern LLM uses — greedy,
    temperature, top-k, top-p — in about twenty-five lines of numpy, then a
    real 350M model on her own machine generating with the samplers she wrote,
    timed against the hosted provider she is not allowed to use. The point is
    the vector underneath: running the weights yourself is what gives you the
    logits, and the logits are where the reproducibility Legal wants and the
    guardrails Security wants actually live. Each decision Priya makes ends
    with the condition under which yours would be different — her three
    departments are one firm's; the reasoning is the transferable part.

    > **You need a model for Task 7 onward** — `uv sync --group local` and a
    > 0.7 GB download. **Tasks 1–6 need nothing at all**: they run on real logits
    > committed to this repo. If your network blocks Hugging Face, you are in
    > Priya's position exactly, and that blockage is itself a deployment finding.

    **Eight words you will meet, in the order you meet them.** None needs to be
    known in advance; each is explained where it first appears, and the
    repository's `GLOSSARY.md` collects these and every later week's.

    | Word | The one-sentence version |
    | --- | --- |
    | **Token** | The unit a model reads and writes — usually a word piece, sometimes a whole word or a single character; "the model wrote 30 tokens" is roughly 20 words |
    | **Vocabulary** | The fixed list of every token the model knows — tens of thousands of entries — and the only things it can ever output |
    | **Forward pass** | One run of the network over the input, producing a score for every token in the vocabulary at the next position |
    | **Open weights** | A model whose parameters you can download and run yourself — as opposed to one you can only reach through someone else's API |
    | **Logit** | The raw score the model gives each possible next token, before it is turned into a probability |
    | **Softmax** | The step that turns those scores into probabilities that add up to one |
    | **Sampling** | Choosing one token from those probabilities — the only place randomness enters |
    | **Seed** | The number that makes a random choice repeatable, which is what turns "the model said" into "the model will say again" |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - Task 1: Look at what a model actually produces
    - Task 2: Greedy
    - Task 3: Temperature
    - ❓ Question #1
    - Task 4: Top-k
    - Task 5: Top-p, or nucleus sampling
    - ❓ Question #2
    - Task 6: Put it together
    - Task 7: Run the model yourself
    - ❓ Question #3
    - Task 8: Where logits come from, and why it matters
    - Task 9: Run both, then argue
    - ❓ Question #4
    - Conclusion
    - Additional Context
    - Bonus Tasks

    > 📓 **Not covered here:** generating the synthetic incident records Priya
    > would prototype on, and deciding what that data can prove. Those are the
    > next session and the challenge.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | numpy | every sampler, written by hand | [numpy.org/doc](https://numpy.org/doc/stable/) |
    | PyTorch | the forward pass in Task 7 | [docs.pytorch.org](https://docs.pytorch.org/docs/stable/) |
    | Transformers | loading the model and its tokenizer | [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers/index) |
    | Hugging Face Hub | where the weights come from, and their licences | [huggingface.co/docs/hub](https://huggingface.co/docs/hub/index) |
    | LiteLLM | the hosted side of the Task 9 comparison | [docs.litellm.ai](https://docs.litellm.ai/) |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start with what Security's rule actually costs Priya, technically. A
    forward pass returns one vector per position: an unnormalised score for
    every token in the vocabulary. That is the model's entire output. Choosing
    a token from that vector is **sampling**, and it is ordinary code running
    after the network has finished.

    Through a hosted API Priya would reach that code through three or four
    keyword arguments and never see the vector — and the incident record would
    have left the building on the way. Running the weights herself, the record
    stays on her machine and the vector is a numpy array she can inspect, mask,
    reweight, or constrain before anything is chosen.

    That distinction decides what is available to her later. Constrained
    decoding — *the report must never contain a customer identifier* — and
    per-token probabilities — *how sure was the model about this sentence?* —
    require the vector, not the sampled string, and no amount of prompting
    reconstructs it. Security's constraint is also the door to the tools that
    satisfy Legal.

    **Estimated time:** 40–50 minutes

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import json
    import sys
    import time
    from pathlib import Path

    import numpy as np

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    DATA = Path(mo.notebook_dir()) / "data"

    TRACE = np.load(DATA / "logits_trace.npz")
    META = json.loads((DATA / "logits_trace_meta.json").read_text(encoding="utf-8"))
    LOGITS, TOKEN_IDS = TRACE["logits"], TRACE["token_ids"]
    VOCAB = META["vocab"]

    def token(i) -> str:
        return VOCAB[str(int(i))]

    print(f"✅ {LOGITS.shape[0]} recorded positions, top {LOGITS.shape[1]} each")
    print(f"✅ model: {META['model']}")
    print(f"✅ hosted model, for the Task 9 comparison: {CFG.llm_model}")
    return CFG, LOGITS, META, TOKEN_IDS, np, time, token, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — Look at what a model actually produces

    The recorded trace below was made with the same 350M model Priya can run
    on her laptop, on six short prompts. One of them is the opening of an
    incident report — *"The incident started when the database"* — and it is the
    one to keep an eye on.

    Pick a position. What comes back is a raw score — a **logit** — for each
    candidate token. Not a probability: unbounded, and it can be negative. This
    is the thing Legal will eventually ask Priya to explain: *why did the model
    write this word?* The answer starts here.
    """)
    return


@app.cell
def _(META, mo):
    position = mo.ui.slider(
        0, len(META["positions"]) - 1, value=0, label="Recorded position",
        full_width=True,
    )
    position
    return (position,)


@app.cell
def _(LOGITS, META, TOKEN_IDS, mo, position, token, ui):
    _position_meta = META["positions"][position.value]
    _position_logits, _position_ids = LOGITS[position.value], TOKEN_IDS[position.value]

    mo.vstack([
        mo.md(f"**Context so far:** `{_position_meta['context']}`"),
        ui.table(
            [{"rank": rank, "token": repr(token(token_id)), "logit": f"{logit:.3f}"}
             for rank, (token_id, logit) in enumerate(zip(_position_ids[:8], _position_logits[:8]))],
            title="Top 8 raw logits",
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To turn scores into probabilities we need them positive and summing to one.
    That is **softmax**: exponentiate, then normalise.

    The subtraction of the maximum before exponentiating is not part of the
    maths — it is there so `exp` does not overflow. Every real implementation
    does it, and it is the kind of detail that only shows up when you write the
    function yourself — which is also the kind of detail an auditor's
    *"show me how the number was produced"* turns up, so it is worth having
    written it once.
    """)
    return


@app.cell
def _(np):
    def softmax(logits: np.ndarray) -> np.ndarray:
        """Scores -> probabilities. Subtract the max for numerical stability."""
        shifted = logits - logits.max()
        exp = np.exp(shifted)
        return exp / exp.sum()

    return (softmax,)


@app.cell
def _(LOGITS, META, TOKEN_IDS, mo, position, softmax, token, ui):
    _position_logits, _position_ids = LOGITS[position.value], TOKEN_IDS[position.value]
    _position_probs = softmax(_position_logits)

    mo.vstack([
        ui.table(
            [{"token": repr(token(token_id)), "logit": f"{logit:.2f}", "probability": f"{prob:.4f}",
              "bar": "█" * max(int(prob * 60), 0)}
             for token_id, logit, prob in zip(_position_ids[:8], _position_logits[:8], _position_probs[:8])],
            title=f"Distribution — {META['positions'][position.value]['context'][-40:]!r}",
        ),
        mo.md(
            f"Top token holds **{_position_probs[0]:.1%}** of the mass; the top 10 hold "
            f"**{_position_probs[:10].sum():.1%}**. Everything below is the long tail."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 2 — Greedy

    The simplest possible decision: always take the highest score.

    Deterministic, and that is both its virtue and its problem. Legal's
    *"regenerate the sentence"* requirement is met for free: same record, same
    model, same draft, every time, with no seed to keep. Great for the parts
    of Priya's report that are extraction — the incident ID, the affected
    system, the timeline — where the same input must produce the same fields.
    Poor for the narrative section, because it produces repetitive, flattened
    text: greedy decoding is why early chatbots kept saying the same phrase,
    and why a greedy incident report reads like a form.

    > **🔀 Where your path diverges.** Priya splits her output in two — greedy
    > for the fields, sampled for the narrative — because a regulator will ask
    > about both and they fail differently. If **everything** your system
    > produces is extraction (a category, an id, a yes/no), greedy is the whole
    > answer and the rest of this session's samplers are for understanding,
    > not shipping. If **nothing** is extraction — a drafting assistant, a
    > summariser — you will sample everywhere, and the seed in Task 6 is what
    > stands in for greedy's free reproducibility.
    """)
    return


@app.cell
def _(np):
    def greedy(probs: np.ndarray) -> int:
        """Index of the most likely token. That's the whole algorithm."""
        return int(np.argmax(probs))

    return (greedy,)


@app.cell
def _(LOGITS, TOKEN_IDS, greedy, mo, position, softmax, token, ui):
    _probs = softmax(LOGITS[position.value])

    # greedy() returns a slot in the top-1000 slice; TOKEN_IDS maps that slot
    # back to the real vocabulary id that token() expects.
    _greedy_index = greedy(_probs)
    _greedy_token_id = TOKEN_IDS[position.value][_greedy_index]

    # Greedy on the same distribution, ten times. The point is that the column
    # never changes -- run-to-run identity is the property you are buying.
    _distinct_picks = {greedy(_probs) for _ in range(10)}

    mo.vstack([
        ui.table(
            [{
                "position": position.value,
                "greedy pick": f"`{token(_greedy_token_id)}`",
                "probability": f"{_probs[_greedy_index]:.1%}",
                "distinct picks over 10 runs": len(_distinct_picks),
            }],
            title="Greedy is a lookup, not a draw",
        ),
        mo.md(
            "Ten runs, one distinct answer. Nothing is being sampled — "
            "`argmax` is a lookup, so there is no seed to set and no run-to-run "
            "variation to chase. That is the whole appeal for the fields in "
            "Priya's report — and for Legal — and the whole problem for the "
            "narrative that should read like a person wrote it."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 3 — Temperature

    The one everybody uses and few can define — and the first setting Legal
    will ask Priya to justify, because it is the one that decides whether two
    runs of the same report agree.

    Temperature divides the logits **before** softmax. Because softmax is
    exponential, that division reshapes the distribution rather than scaling it:

    - `T < 1` — differences get amplified. The leader pulls further ahead. More
      confident, more repetitive.
    - `T = 1` — the model's own distribution, untouched.
    - `T > 1` — differences get compressed toward uniform. More surprising, and
      eventually incoherent.

    Watch the actual numbers move.
    """)
    return


@app.cell
def _(np, softmax):
    def apply_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
        """Divide the logits, then softmax. T -> 0 approaches greedy."""
        if temperature <= 0:
            out = np.zeros_like(logits)
            out[np.argmax(logits)] = 1.0
            return out
        return softmax(logits / temperature)

    return (apply_temperature,)


@app.cell
def _(mo):
    temperature = mo.ui.slider(
        0.1, 2.0, step=0.1, value=1.0, label="Temperature", full_width=True
    )
    temperature
    return (temperature,)


@app.cell
def _(
    LOGITS,
    TOKEN_IDS,
    apply_temperature,
    mo,
    position,
    temperature,
    token,
    ui,
):
    _position_logits, _position_ids = LOGITS[position.value], TOKEN_IDS[position.value]
    _probs_at_t1 = apply_temperature(_position_logits, 1.0)
    _probs_at_t = apply_temperature(_position_logits, temperature.value)

    _rows = [
        {"token": repr(token(token_id)), "at T=1.0": f"{prob_at_t1:.4f}",
         f"at T={temperature.value}": f"{prob_at_t:.4f}",
         "bar": "█" * max(int(prob_at_t * 60), 0)}
        for token_id, prob_at_t1, prob_at_t in zip(_position_ids[:8], _probs_at_t1[:8], _probs_at_t[:8])
    ]

    # How many tokens hold 95% of the mass -- one number for "how open is this?"
    _cumulative_mass = _probs_at_t.cumsum()
    _tokens_for_95pct = int((_cumulative_mass < 0.95).sum() + 1)

    # Near the top of the slider the 95% set approaches the 1,000 candidates the
    # trace stored, and past that point this count is an under-estimate -- the
    # tokens that would have extended it were never recorded. Say so rather than
    # print a number that quietly stops being true.
    _truncated = _tokens_for_95pct > 0.6 * len(_probs_at_t)

    mo.vstack([
        ui.table(_rows, title=f"Temperature {temperature.value}"),
        mo.md(
            f"**{_tokens_for_95pct}** tokens hold 95% of the probability mass at this "
            f"temperature (at T=1.0 it is **{int((_probs_at_t1.cumsum() < 0.95).sum() + 1)}**)."
            + (
                f"\n\n> ⚠️ That is {_tokens_for_95pct} of only **{len(_probs_at_t)}** recorded "
                f"candidates. At this temperature the real number is larger — the "
                f"rest of the tail was never saved. A recorded trace has an edge, "
                f"and you have found it."
                if _truncated
                else ""
            )
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    That last number is the useful intuition. Temperature does not add options —
    every token was always there. It changes **how much of the tail is live** —
    and, for Priya, how many different reports the same incident could produce.

    > **🏢 In the enterprise:** temperature is a per-endpoint setting, not a
    > per-developer preference, and Legal's requirement makes it a *record*.
    > Priya's extraction endpoint runs at `0` so the same incident produces the
    > same fields every time; her drafting endpoint runs higher, with a seed.
    > The choice it forces is *where that number lives* — in the request, or in
    > the endpoint's config — because when a regulator asks "why does the March
    > report say this", the first question is what the sampler was set to, and
    > that is only answerable if the setting and the seed were logged with the
    > request and retained with the report.

    ---
    ### ❓ Question #1

    Priya will prototype on synthetic incidents, generated one prompt per axis
    combination — and one of those axis values is *"an incident the system
    should decline to draft"* (under legal hold, say). For that value, argue
    whether you want a **higher or lower** temperature than for *"a routine
    incident"*, in one to three sentences — and say what the 95%-mass count you
    just watched tells you about what Legal is signing up for on either side.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 4 — Top-k

    Temperature alone has a failure mode: raise it enough and genuinely absurd
    tokens become reachable, because they still have some probability. In a
    regulatory filing, "absurd" is not a style problem — it is a sentence that
    asserts something the incident record does not support.

    Top-k cuts that off. Keep the k best, discard the rest, renormalise.
    """)
    return


@app.cell
def _(np):
    def top_k(probs: np.ndarray, k: int) -> np.ndarray:
        """Zero everything outside the k most likely, then renormalise."""
        if k <= 0 or k >= len(probs):
            return probs
        cut = np.partition(probs, -k)[-k]
        kept = np.where(probs >= cut, probs, 0.0)
        return kept / kept.sum()

    return (top_k,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Simple, and its weakness is that `k` is fixed while the model's confidence is
    not.

    After "The capital of France is", the model is nearly certain — one token
    deserves the mass. After "She opened the door and found", a hundred
    continuations are reasonable. The same `k` is too permissive in the first
    case and too restrictive in the second. Priya's incidents are the same:
    *"The incident started when the database"* has a handful of plausible next
    words; the paragraph explaining what the on-call engineer tried has dozens.

    ---
    ## Task 5 — Top-p, or nucleus sampling

    The fix: instead of a fixed count, keep however many tokens are needed to
    reach a fixed *probability mass*.

    The candidate set now grows and shrinks with the model's own confidence,
    which is why this is the default nearly everywhere — and why it is the
    setting Priya can defend to Legal as *one rule for every report* rather
    than a number tuned per incident.
    """)
    return


@app.cell
def _(np):
    def top_p(probs: np.ndarray, p: float) -> np.ndarray:
        """Keep the smallest set of tokens whose mass reaches p. Renormalise."""
        order = np.argsort(-probs)
        cumulative = probs[order].cumsum()
        # +1 so we include the token that crosses the threshold.
        n_keep = int(np.searchsorted(cumulative, p) + 1)
        kept = np.zeros_like(probs)
        kept[order[:n_keep]] = probs[order[:n_keep]]
        return kept / kept.sum()

    return (top_p,)


@app.cell
def _(mo):
    top_p_value = mo.ui.slider(0.1, 1.0, step=0.05, value=0.9, label="top-p", full_width=True)
    top_k_value = mo.ui.slider(1, 100, value=50, label="top-k", full_width=True)
    mo.vstack([top_p_value, top_k_value])
    return top_k_value, top_p_value


@app.cell
def _(
    LOGITS,
    META,
    apply_temperature,
    mo,
    top_k,
    top_k_value,
    top_p,
    top_p_value,
    ui,
):
    _rows = []
    for _prompt_index, _position_meta in enumerate(META["positions"]):
        if _position_meta["step"] != 0:            # first position of each prompt only
            continue
        _probs = apply_temperature(LOGITS[_prompt_index], 1.0)
        _rows.append({
            "prompt": _position_meta["prompt"][:38],
            "confidence (top token)": f"{_probs.max():.0%}",
            "live tokens @ top-p": int((top_p(_probs, top_p_value.value) > 0).sum()),
            "live tokens @ top-k": int((top_k(_probs, top_k_value.value) > 0).sum()),
        })

    mo.vstack([
        ui.table(_rows, title="Candidate-set size, per prompt"),
        mo.md(
            "**This is the whole argument for top-p.** Its column moves with the "
            "model's confidence; top-k's does not. A confident position gets a "
            "narrow set, an open-ended one gets a wide set, from the same setting."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(LOGITS, apply_temperature, top_k, top_k_value, top_p, top_p_value, ui):
    # Six rows show the effect; all 72 recorded positions show its shape. Sorted
    # by how confident the model was, so the x-axis is "certain on the left,
    # unsure on the right" and the two lines can be read against each other.
    _probs_all = [apply_temperature(LOGITS[_prompt_index], 1.0) for _prompt_index in range(LOGITS.shape[0])]
    _order = sorted(range(len(_probs_all)), key=lambda _prompt_index: -_probs_all[_prompt_index].max())

    ui.lines(
        {
            "top-p": [int((top_p(_probs_all[_prompt_index], top_p_value.value) > 0).sum()) for _prompt_index in _order],
            "top-k": [int((top_k(_probs_all[_prompt_index], top_k_value.value) > 0).sum()) for _prompt_index in _order],
        },
        x_label="recorded positions, most confident first",
        y_label="live candidates",
        title="One of these adapts to the model. The other is a number you picked.",
        log_y=True,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #2

    Priya's quarter has two hundred incidents to draft, in one batch run, with
    one sampler setting that Legal has approved for all of them — and the table
    above shows the model is nearly certain on some openings and wide open on
    others. In one to three sentences, explain why a fixed `k` is the wrong
    tool for that run, and what top-p does about it that she would otherwise
    have to tune by hand and re-justify per incident.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 6 — Put it together

    The real pipeline, in the order every inference server applies it:

    **logits → temperature → top-k → top-p → sample**

    Order matters. Temperature reshapes first; the filters then cut the reshaped
    distribution. Swap them and the same settings mean something different.

    > **🏢 In the enterprise:** Priya will rarely call this pipeline directly —
    > the firm's internal gateway or a serving stack such as vLLM applies it
    > for her, and not every gateway exposes every knob. Some pass only
    > `temperature` through; `top_k` and `top_p` are silently dropped. The
    > choice it forces: before she tunes a prompt against a setting, confirm
    > the endpoint she will actually deploy against honours it — otherwise the
    > behaviour Legal approved on her laptop is not the behaviour that ships,
    > and the record of the settings is a record of settings that were never
    > applied.
    """)
    return


@app.cell
def _(apply_temperature, np, top_k, top_p):
    def sample(logits, *, temperature=1.0, k=0, p=1.0, rng=None) -> int:
        """The full sampler, in the order a real inference server applies it."""
        probs = apply_temperature(logits, temperature)
        if k:
            probs = top_k(probs, k)
        if p < 1.0:
            probs = top_p(probs, p)
        rng = rng or np.random.default_rng()
        return int(rng.choice(len(probs), p=probs))

    return (sample,)


@app.cell
def _(
    LOGITS,
    META,
    TOKEN_IDS,
    mo,
    np,
    position,
    sample,
    temperature,
    token,
    top_k_value,
    top_p_value,
    ui,
):
    _position_logits, _position_ids = LOGITS[position.value], TOKEN_IDS[position.value]
    _random_generator = np.random.default_rng(0)

    _draws = [
        token(_position_ids[sample(_position_logits, temperature=temperature.value, k=top_k_value.value,
                          p=top_p_value.value, rng=_random_generator)])
        for _ in range(20)
    ]
    _unique = sorted(set(_draws), key=_draws.count, reverse=True)

    mo.vstack([
        mo.md(f"**Context:** `{META['positions'][position.value]['context']}`"),
        ui.table(
            [{"token": repr(t), "drawn": _draws.count(t), "of 20": "█" * _draws.count(t)}
             for t in _unique],
            title=f"20 draws at T={temperature.value}, k={top_k_value.value}, p={top_p_value.value}",
        ),
        mo.md(
            "Move the sliders and re-run. **Temperature 0.1 gives one token every "
            "time; temperature 2.0 gives twenty different ones.** That is the "
            "entire difference between the part of Priya's report that fills in "
            "fields and the part that would, at that setting, write fiction into "
            "a regulatory filing."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What the recorded trace cannot do

    Be clear about the limit. The trace follows the **greedy** path, so the
    moment you sample something other than the top token, the next recorded
    position no longer corresponds to your sequence.

    Everything above — how a distribution is shaped and filtered — is exact and
    real. **Free generation is not available from a recording**, because after
    one non-greedy choice the recorded path is no longer your path.

    So run the model — which is also the only way Priya gets to run anything,
    because Security's rule rules out the alternative.

    ---
    ## Task 7 — Run the model yourself

    A 350M-parameter model is a 0.7 GB download that runs on a laptop CPU. Get
    it, and every sampler you just wrote becomes a generation loop that never
    sends an incident record anywhere. This is Priya's whole architecture:
    the data does not move; the model moves to the data.

    ```bash
    uv sync --group local        # torch (CPU wheels) + transformers
    ```

    Then run the cell below. First run downloads the weights; after that it is
    cached and offline.
    """)
    return


@app.cell
def _(mo):
    import os
    from pathlib import Path as _Path

    LOCAL_MODEL = "LiquidAI/LFM2.5-350M"

    # The button exists for the first run only: a 0.7 GB download should never
    # fire just because a notebook was opened. Once the weights are in the
    # Hugging Face cache, loading is a few seconds and happens on its own.
    _hf_hub_cache = _Path(
        os.environ.get("HF_HUB_CACHE")
        or _Path(os.environ.get("HF_HOME", _Path.home() / ".cache" / "huggingface")) / "hub"
    )
    CACHED = (_hf_hub_cache / f"models--{LOCAL_MODEL.replace('/', '--')}" / "snapshots").is_dir()

    load = mo.ui.run_button(label=f"Download and load {LOCAL_MODEL} (~0.7 GB)")
    mo.vstack([
        mo.md(f"Model: `{LOCAL_MODEL}`"),
        mo.md("✅ Weights already cached on this machine — loading below, no button needed.")
        if CACHED else load,
    ])
    return CACHED, LOCAL_MODEL, load


@app.cell
def _(CACHED, LOCAL_MODEL, load, mo, ui):
    mo.stop(
        not (CACHED or load.value),
        mo.md("*Click above to download and load the model.*"),
    )

    # torch is bound to None up front. It is one of this cell's exports, so if
    # the import fails and we never bind it, the `return` below raises
    # UnboundLocalError -- burying the friendly message we just printed under a
    # traceback. That is the default state for anyone who skipped
    # `uv sync --group local`, which is exactly who the message is for.
    torch = TOK = MODEL = None
    LIVE = False

    try:
        # A spinner, because the first run downloads ~0.7 GB and prints nothing
        # until it succeeds or fails. On a managed laptop behind a proxy, an idle
        # cell and a blocked one look identical, and the difference matters: one
        # of them is a finding for use_case/ecosystem.md.
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        with ui.spinner(f"Fetching and loading {LOCAL_MODEL}…"):
            TOK = AutoTokenizer.from_pretrained(LOCAL_MODEL)
            MODEL = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL, dtype=torch.float32)
            MODEL.eval()
        LIVE = True
        print(f"✅ {sum(p.numel() for p in MODEL.parameters()) / 1e6:.0f}M parameters, "
              f"vocab {MODEL.config.vocab_size}")
    except ModuleNotFoundError:
        mo.output.replace(mo.md(
            "⚠️ **torch / transformers are not installed in this environment.** "
            "From the repo root run `uv sync --group local`, then re-run this cell. "
            "(Opened with `--sandbox`? The notebook's own header lists them, so a "
            "fresh sandbox build will fetch them.) Tasks 1–6 above already ran: "
            "they use the recorded trace, not the model."
        ))
    except Exception as exc:
        mo.output.replace(mo.md(
            f"⚠️ **Could not fetch the weights** — `{type(exc).__name__}: "
            f"{str(exc)[:160]}`.\n\nIf your network blocks Hugging Face, that is a "
            "finding for `use_case/ecosystem.md`, and the most common thing that "
            "happens to someone in Priya's position. Tasks 1–6 still ran on real "
            "logits; Task 9 needs this model and will wait."
        ))
    return LIVE, MODEL, TOK, torch


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now your own sampler, driving real generation. This is the loop every
    inference server runs — forward pass, take the last position's logits, sample
    one token, append, repeat. Notice the `seed` argument: with the model, the
    settings and the seed recorded, the draft is reproducible, and that is the
    sentence Priya gets to say to Legal.
    """)
    return


@app.cell
def _(
    LIVE,
    MODEL,
    TOK,
    mo,
    np,
    sample,
    temperature,
    top_k_value,
    top_p_value,
    torch,
):
    mo.stop(not LIVE, mo.md("*Load the model above to run this.*"))

    def generate(prompt: str, n_tokens: int = 30, *, seed: int = 0,
                 on_token=None, **sampler) -> str:
        """Your sampler, in the loop. Nothing here is a library call.

        `on_token` is called with the text so far after every step. Streaming is
        not a feature bolted on by a serving framework -- it is just this loop,
        handing you each token as it decides on it, and there is no other way for
        a model to produce text. Watching it happen is the point of this cell.
        """
        ids = TOK(prompt, return_tensors="pt").input_ids
        rng = np.random.default_rng(seed)
        for _ in range(n_tokens):
            with torch.no_grad():
                logits = MODEL(ids).logits[0, -1].float().numpy()
            nxt = sample(logits, rng=rng, **sampler)
            ids = torch.cat([ids, torch.tensor([[nxt]])], dim=1)
            if on_token is not None:
                on_token(TOK.decode(ids[0], skip_special_tokens=True))
        return TOK.decode(ids[0], skip_special_tokens=True)

    _prompt = "The incident started when the database"
    _settings = [
        ("greedy (T=0.01)", {"temperature": 0.01}),
        (
            f"T={temperature.value}, k={top_k_value.value}, p={top_p_value.value}",
            {"temperature": temperature.value, "k": top_k_value.value,
             "p": top_p_value.value},
        ),
        ("wild (T=1.8)", {"temperature": 1.8}),
    ]

    # Three 30-token generations on CPU take a while, and a blank cell for a
    # minute is a poor advertisement for a session about how generation works.
    # Repaint after every token, for every row, so the wait *is* the lesson.
    _rows = []
    for _label, _kwargs in _settings:
        _show_partial = lambda _partial_text, _label_now=_label: mo.output.replace(
            mo.vstack(
                [mo.md(f"**{_done_label}**\n\n> {_done_text}") for _done_label, _done_text in _rows]
                + [mo.md(f"**{_label_now}** *(generating…)*\n\n> {_partial_text}")]
            )
        )
        _rows.append((_label, generate(_prompt, on_token=_show_partial, **_kwargs)))

    mo.output.replace(
        mo.vstack([mo.md(f"**{_label}**\n\n> {_final_text}") for _label, _final_text in _rows])
    )
    return (generate,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Three settings, one model, one incident-report opening. The difference
    between them is entirely code you wrote — no library did the sampling.

    Read them in order. Greedy is coherent and flat, and it will produce the
    *identical* text every time you run it — the version Legal would approve
    without a seed. The middle setting is the one Priya would ship for the
    narrative, with the seed logged. And at T=1.8 the model comes apart —
    usually within a dozen tokens, often into other languages entirely,
    because compressing the distribution that far makes genuinely unrelated
    tokens reachable. In a filing, that is the run that ends the project.

    > **That collapse is the useful part.** You have just found this model's
    > upper bound, empirically, in about a minute. Most teams pick a temperature
    > by copying one from a blog post; Priya can write hers into the decision
    > log with the run that found it.

    ### Want a different model?

    Change `LOCAL_MODEL` above and re-run. Everything else works unchanged,
    because none of your sampler code knows which model it is running against —
    which is the point. Sizes and trade-offs for six alternatives are listed in
    the README beside this notebook, from 0.5 GB up to server-class.

    > **Before you take any of them to work, check the licence.** This is
    > Procurement's line, and it is right. "Open weights" describes what you can
    > download, not what you may do with it, and the model this session hands
    > you is under a custom licence rather than Apache-2.0. Whether a firm may
    > run it on regulatory work is a question for Legal, not for the download
    > page — and it is a much better question to ask before the model is in
    > the pipeline than after.

    > **🔀 Where your path diverges.** Priya prototypes on a 350M model because
    > it runs on the laptop Security lets her use and it is the model this
    > session's recorded trace came from, so what you saw in Tasks 1–6 is what
    > runs here. That is a *prototyping* choice, not a production one. With a
    > **16 GB laptop or Apple Silicon** you can run a 4–8B instruction-tuned
    > model today and should; with a **consumer GPU** a quantised 20–30B model
    > is realistic; the model Priya's firm actually serves will be bigger again,
    > sized by the arithmetic in the next section. If your firm **blocks the
    > download**, the question is not which model but which *registry* — the
    > internal mirror Procurement already approved — and that is a line for
    > `use_case/ecosystem.md` before it is a technical decision.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #3

    You have just found, empirically, the temperature at which this model comes
    apart, and Priya writes that number into `use_case/decisions.md`. In one to
    three sentences, explain why the number on its own is nearly worthless to
    Legal, and what two other things have to sit next to it in that row before
    a colleague — or a regulator, with a different model next quarter — can
    reproduce the draft it produced.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### The number that decides the hardware

    The sizes above are **downloads**. What you have to provision is
    downloads **plus the KV cache**. The *KV cache* is the memory a model keeps
    per request so that generating token 200 does not mean re-reading tokens
    1–199 from scratch — each new token costs one forward pass instead of two
    hundred — and *batching* is serving several requests through one forward
    pass at once, which multiplies that memory by the number of requests in
    flight. The cache is allocated per request, grows linearly with context
    length and batch size, and is not in any of those download figures. At
    long context it routinely exceeds the weights:

    ```python
    from helpers.sizing import from_config, estimate

    geo = from_config("~/.cache/huggingface/.../config.json", params=7e9)
    print(estimate(geo, context=4096,   batch=1))
    print(estimate(geo, context=131072, batch=8))
    ```

    Run it on a real config and watch the cache share climb from a few percent to
    most of the total. That is the arithmetic behind "it was fine on my laptop"
    turning into an OOM in staging, and it is also why **grouped-query
    attention** matters commercially rather than academically: the cache scales
    with the number of *key/value* heads, so a model with four KV heads per eight
    attention heads needs **half** the cache. Halving the memory per request is a
    different sentence to your infrastructure team than "it is a bit faster".

    `helpers/sizing.py` reads the geometry out of the model's own `config.json`
    rather than a number anyone typed from memory, because layer count and head
    geometry are exactly the details people misremember. For Priya this is the
    number that goes in the request to the platform team: Security said the
    model has to run inside the network, and *inside the network* has to have
    enough memory for it.

    ---
    ## Task 8 — Where logits come from, and why it matters

    Three ways to get them, in order of how much you control:

    | | **Tier A — a server** | **Tier B — your machine** | **Tier C — the recording** |
    | --- | --- | --- | --- |
    | What | vLLM, or your firm's gateway | Task 7, above | The committed trace |
    | Needs | a reachable URL | `uv sync --group local` + a download | numpy |
    | Gives you | Speed, concurrency, bigger models | Full generation, full logit access | Distributions only |
    | Fails when | The URL is unreachable or unapproved | Weight downloads are blocked | Never |
    | Data leaves your machine | Ask. The answer matters | No | No |

    Read the last row as Security would. Tier A is where Priya's report
    generator ends up — a model served inside the network, sized by the
    arithmetic above — and *"ask"* means asking the team that runs it whether
    the incident records ever leave the box, in writing. Tier B is where she
    prototypes. Tier C is what she is left with on the day the download is
    blocked.

    ### Three reasons to run local, and they are different reasons

    "Local" is not one thing, and the three reasons people give for it pull in
    different directions. Priya's departments each want a different one:

    | Reason | What it actually means | What satisfies it | Who is asking |
    | --- | --- | --- | --- |
    | **Speed** | No network in the latency, no rate limit, no queue | Weights on hardware near the caller — a laptop, an on-prem box, a GPU in your own cloud account | Whoever is waiting on the answer |
    | **Security** | The input never leaves a boundary you control | *Any* deployment inside that boundary — including a hosted model behind a **private endpoint** inside your cloud tenancy, where you never touch the weights | Security |
    | **Control** | You hold the weights: logits, versioning, the licence, the ability to fine-tune | Open weights, self-hosted. Nothing else gives you this | Legal (reproducibility), and later, you |

    The second row is the one to be honest about. A private endpoint to a
    hosted model — the shape many regulated firms already run — answers
    Security's question without answering Control's: the record stays in the
    tenancy, but there are no logits, the vendor can still deprecate the model,
    and the licence is theirs. It is a legitimate answer for a bank that wants
    a chat assistant over private data and does not need the vector. It is not
    an answer for Priya, because Legal's *"regenerate it"* and the guardrail
    Security will ask for next both need the weights. Say which of the three
    you are buying before you pick the setup, because the setup that satisfies
    one is often the one that rules out another.

    > **🔀 Where your path diverges.** Priya needs all three rows, which is why
    > only self-hosted open weights work for her. Read your own requirements
    > against the table before copying her answer. **Security only** — a chat
    > assistant over private documents, no need for the vector — and a private
    > endpoint to a hosted model inside your cloud tenancy is the cheaper,
    > faster, entirely legitimate answer; most regulated firms run exactly
    > this. **Speed only** — a latency-bound feature on public data — and a
    > small model on a GPU near the caller wins, hosted or not. **Control**
    > — constrained decoding, fine-tuning, a model that cannot be deprecated
    > under your evals — is the one that forces open weights, and it is the
    > one people claim they need before checking whether they do.

    **If Task 7 failed on the download**, that is a finding, not a failure, and
    it is the most common thing that happens to someone in Priya's position.
    Write it in `use_case/ecosystem.md`: a network that blocks Hugging Face
    shapes what you can fine-tune and where you can deploy more than any
    technical decision you will make, and the answer is usually an internal
    model registry somebody already runs — which is also Procurement's approved
    list, in a form you can `pip install` from.

    ---
    ## Task 9 — Run both, then argue

    Priya's manager will ask the obvious question: *"the hosted model is
    better, so why not just use that?"* You now have both paths wired up, so
    measure them rather than reasoning about them. Same prompt, your local
    350M model and whatever `LLM_MODEL` points at, with the clock running.

    Expect the hosted model to be better *and* the comparison to be unfair — a
    350M model on CPU against a hosted frontier model differs in parameter
    count, quantisation, hardware, and serving stack all at once. The
    transferable results are the ones that hold regardless of quality, and
    they are the ones Priya needs for the conversation with her manager: no
    network hop, no per-token meter, no rate limit, no incident record in
    someone else's logs, and a logit vector she can reach.

    *(The prompt below is a made-up opening with no customer data in it. That
    is the only kind of prompt Priya may send to a hosted model, and it is
    worth noticing that the comparison had to be designed around the rule.)*
    """)
    return


@app.cell
def _(mo):
    # One budget for both sides, so the wall-clock numbers stay comparable.
    # 80 tokens is a short paragraph -- enough to judge the prose -- and about
    # four seconds on a laptop CPU. Turn it down on a slow machine.
    budget = mo.ui.slider(30, 200, value=80, step=10, label="Tokens per side")
    run_compare = mo.ui.run_button(label="Send one prompt to both")
    mo.vstack([
        mo.md(
            "**⚠️ This calls your hosted provider once.** It costs a fraction of "
            "a cent and needs the model loaded in Task 7. The local side takes "
            "roughly the budget ÷ 20 seconds on CPU."
        ),
        budget,
        run_compare,
    ])
    return budget, run_compare


@app.cell
def _(CFG, LIVE, budget, generate, mo, run_compare, time):
    mo.stop(not run_compare.value, mo.md("*Click above to run the comparison.*"))
    mo.stop(
        not LIVE,
        mo.md("*Load the local model in Task 7 first — this compares the two.*"),
    )

    PROMPT = "The incident started when the database"
    _token_budget = budget.value

    _started_at = time.perf_counter()
    _local = generate(PROMPT, n_tokens=_token_budget, temperature=0.7, k=50, p=0.95)
    _local_s = time.perf_counter() - _started_at

    _sampler_note = ""
    try:
        from litellm import UnsupportedParamsError, completion

        # Streamed, so the wait is visible rather than a frozen cell -- and so
        # the comparison is honest: the local model above printed nothing until
        # every token was sampled, which is the same experience a user gets
        # from a service that does not stream.
        # The local model is a raw text continuer: it was handed the fragment
        # and kept writing. A hosted chat model is wrapped in a chat template,
        # so the same fragment sent as a user turn reads as a request for help
        # ("I'd be happy to help with this database incident...") and the two
        # outputs stop being comparable. The instruction below asks the chat
        # model to do what the base model does by default -- which is itself
        # the lesson: the hosted product has a conversation layer you cannot
        # remove, only steer.
        _hosted_call = dict(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Continue the user's text from exactly where it stops, "
                        "as the next words of the same passage. Do not answer, "
                        "comment, or restate it. Output only the continuation: "
                        "two or three sentences, then stop."
                    ),
                },
                {"role": "user", "content": PROMPT},
            ],
            max_tokens=_token_budget,
            temperature=0.7,
            stream=True,
            stream_options={"include_usage": True},
            **CFG.kwargs(),
        )
        _started_at = time.perf_counter()
        try:
            _stream = completion(timeout=600, **_hosted_call)
        except UnsupportedParamsError:
            # Some hosted models refuse a sampler setting outright -- the
            # Claude 5 family accepts only temperature=1, for instance. That
            # refusal is a finding, not a failure: you asked for the same
            # sampler as the local run and the provider said no. Run it on the
            # provider's own setting and say so in the output.
            _hosted_call.pop("temperature")
            _stream = completion(timeout=600, **_hosted_call)
            _sampler_note = " · provider rejected `temperature=0.7`; ran at its default"
        _hosted, _usage, _last_redraw_at = "", None, 0.0
        for _chunk in _stream:
            _usage = getattr(_chunk, "usage", None) or _usage
            if not _chunk.choices:
                continue
            _hosted += getattr(_chunk.choices[0].delta, "content", None) or ""
            _clock_now = time.perf_counter()
            if _clock_now - _last_redraw_at >= 0.08:
                mo.output.replace(mo.md(
                    f"**Local** · {_local_s:.2f}s\n\n> {' '.join(_local.split())}\n\n"
                    f"**Hosted** · {_clock_now - _started_at:.2f}s and counting\n\n"
                    f"> {' '.join((PROMPT + ' ' + _hosted).split())}"))
                _last_redraw_at = _clock_now
        _hosted_s = time.perf_counter() - _started_at
    except Exception as _error:
        _hosted_s = None
        _hosted = f"({type(_error).__name__}: {_error})"
        _usage = None
    else:
        # `generate()` returns prompt + continuation as one string; a chat API
        # returns only the continuation. Put the prompt back so the two lines
        # read the same way.
        _hosted = f"{PROMPT} {_hosted.lstrip()}"

    # Token counts are reported by the provider, so they are measured. The price
    # per token is not -- that is a lookup on a pricing page, and saying so is
    # the difference between a finding and a guess.
    _tokens = (
        f" · {_usage.prompt_tokens} in / {_usage.completion_tokens} out"
        if _usage else ""
    )

    def _tidy(text: str) -> tuple[str, bool]:
        """One paragraph, cut back to the last full sentence.

        The timings and token counts above were measured on the whole run; this
        only decides what is *shown*. A base model has no notion of "finished"
        -- it stops when the budget does, usually mid-word -- so without this
        every run ends on a ragged edge. Return whether anything was trimmed,
        so the display can say so rather than pretend the model stopped there.
        """
        flat = " ".join(text.split())
        cut = max(flat.rfind(". "), flat.rfind("! "), flat.rfind("? "), -1)
        if flat.endswith((".", "!", "?")):
            return flat, False
        if cut > len(PROMPT):
            return flat[: cut + 1], True
        return flat, False

    _local_shown, _local_cut = _tidy(_local)
    if _hosted_s:
        _hosted_shown, _hosted_cut = _tidy(_hosted)
    else:
        _hosted_shown, _hosted_cut = _hosted, False
    _trim_note = " · trimmed to the last full sentence for display"

    # Words shown next to tokens generated, because the two models do not share
    # a tokenizer: the same budget buys a different amount of English on each
    # side, and the header should make that visible rather than leave the reader
    # wondering why one passage is longer.
    def _words(text: str) -> int:
        return len(text.split()) - len(PROMPT.split())

    mo.vstack([
        mo.md(
            f"**Local — `LiquidAI/LFM2.5-350M`, CPU** · {_local_s:.2f}s · "
            f"{_token_budget} tokens generated · {_words(_local_shown)} words shown"
            + (_trim_note if _local_cut else "")
            + f"\n\n> {_local_shown}"
        ),
        mo.md(
            f"**Hosted — `{CFG.llm_model}`** · "
            + (f"{_hosted_s:.2f}s" if _hosted_s else "failed")
            + _tokens
            + (f" · {_words(_hosted_shown)} words shown" if _hosted_s else "")
            + _sampler_note
            + (_trim_note if _hosted_cut else "")
            + f"\n\n> {_hosted_shown}"
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Reading the two results

    Three things are on the screen above: two passages, two times, and two
    token counts. Take each on its own, because each says less than it seems
    to — and then the table that follows says what actually decides the choice.

    **The prose.** The hosted model is two to three orders of magnitude larger,
    so if it wrote the better passage that is the expected result, and the
    comparison is not designed to be fair on this axis. But look at what you
    got before you conclude anything. Continuing a sentence about a database
    incident is generic prose, and a small model has seen a million incident
    write-ups; on this task the visible gap is often a doubled word (*"the
    database database"*) and a flatter story, and nothing more. The hosted
    model's real advantages show up where this prompt cannot: it can be *told*
    things — stop after three sentences, answer in JSON, cite the record — and
    will mostly comply, where the local model cannot be told anything and runs
    until the budget does; and it is far stronger on facts, on long inputs, and
    on anything with structure to get wrong. The rest of the week puts both
    models in front of exactly that kind of work.

    **The times.** On a laptop the hosted side usually wins, and that is
    expected too: the local number is a Python loop you wrote, doing a forward
    pass per token on a CPU at ten to twenty tokens a second; the hosted number
    is a datacenter GPU behind a load balancer, plus a network round-trip. Put
    the same weights on a GPU you own and the order flips. So neither number
    says which is *faster*. What the hosted time contains that the local time
    does not is a network and a queue you do not control — and that is the
    figure that matters for the floor, below.

    **The counts.** Same token budget, different amount of text: the two models
    do not share a tokenizer, so eighty tokens buys a different amount of
    English on each side (the header's *words shown* makes it visible), and a
    side that ran into the cap mid-sentence lost its unfinished tail to the
    trim. Neither has anything to do with quality. And if the hosted line says
    *provider rejected `temperature=0.7`*, that is not noise: you wrote
    `temperature`, `top_k` and `top_p` yourself in Tasks 2–5 and applied all
    three to the local run; the hosted provider accepted none of them, or only
    one. A product exposes the sampler settings it chooses to; a component
    exposes all of them.

    ### What each side gives you, and what it costs

    | | Hosted model | Local model |
    | --- | --- | --- |
    | **Quality ceiling** | The highest available, and it keeps rising without you doing anything | Lower, and closing — but it moves only when *you* swap the weights |
    | **Speed on this laptop** | Faster today — someone else's GPU | Slower today — your CPU; a GPU you own flips it |
    | **Latency floor** | Network round-trip plus the provider's queue, outside your control | Your hardware, and nothing else; the P99 is a fact about a machine you own |
    | **Cost shape** | Per token, forever — scales with usage, and the sticker price has a discount structure you have to engineer around (below) | Fixed at provisioning; ten times the traffic costs the same until you run out of capacity |
    | **Control over sampling** | Whatever parameters the provider accepts this quarter | Everything — temperature, top-k, top-p, the seed, and the logits themselves, which is what constrained decoding and fine-tuning need |
    | **Steering by instruction** | Strong — a chat layer you can tell what to do | Weak to none at this size; you steer it with code, not words |
    | **Who runs it** | The provider: uptime, patches, scaling, incidents are theirs | You: a server to size, patch, monitor and keep up at 3 a.m. |
    | **Versioning** | The model behind the string can be deprecated or changed; your eval numbers were measured against the old one | You keep the weights; nothing changes until you change it |
    | **Where the data goes** | Leaves your network, under the provider's terms | Stays inside it |

    Read the rows as a pair of honest lists rather than a verdict. The hosted
    column wins on capability and on having nobody to page at night; the local
    column wins on control, predictability and on what the data touches. Which
    rows count depends entirely on who is asking.

    **What the comparison actually measured** is narrower than either column:

    | | What you measured | What you did **not** measure |
    | --- | --- | --- |
    | **Local** | Wall-clock on your CPU | — |
    | **Hosted** | Wall-clock including the network round-trip | **Cost.** LiteLLM reports token counts; the price per token is a number you look up on a pricing page, not something this notebook can measure |

    Be precise about that last cell. It is tempting to put a dollar figure in a
    table and call it a finding. Token counts are measured; **prices are looked
    up, and they change.** A table that mixes the two without saying which is
    which is how "our costs tripled" happens.

    > **🏢 In the enterprise:** the bill is the sum of exactly the token counts
    > this cell just printed, so the cheapest observability Priya will ever add
    > is logging `prompt_tokens` and `completion_tokens` per request, tagged
    > with the endpoint and the team, from the first day — and for the local
    > model, the same log carries the seed and the settings Legal asked for, so
    > one line per request satisfies both Finance and the regulator. The choice
    > it forces is whether cost is a number the platform team reads off an
    > invoice a month later, or a number she can break down by feature this
    > afternoon — and the second one is what gets a budget approved.

    ### What decides it for Priya

    Not the prose and not the stopwatch. Three rows of the table are structural
    — true regardless of which model wrote the nicer sentence or came back
    first — and they are what the infrastructure team and the CFO actually ask
    about:

    - **No network floor.** The local run's latency is bounded by hardware she
      owns, not by someone else's availability.
    - **No per-token meter.** Its cost is fixed at provisioning, which is a
      completely different budgeting conversation from a line item that scales
      with usage.
    - **Nothing can be deprecated out from under her.** The hosted model behind
      that string can change next quarter, and the eval numbers were measured
      against the old one.

    Add Security's row — **no incident record ever leaves the network** — and
    Legal's — **the draft can be regenerated from the log**, which needs the
    seed and the sampler the hosted provider would not accept — and Priya has
    the whole argument, none of it about quality. The hosted column's real
    strengths, capability and nobody-to-page, are the price she pays for it;
    the 🔀 block further down is where that trade reads the other way.

    ### Before you conclude the hosted side is expensive: the cache

    The per-token price is the sticker price, and almost nobody pays it on the
    part of the prompt that matters most. Every major hosted provider offers
    **prompt caching** — it keeps the processed form of a prompt *prefix* for a
    short while and charges far less to reuse it than to process it again — and
    the economics are lopsided enough to change architecture decisions:

    | | Roughly |
    | --- | --- |
    | Writing a prefix into the cache | **more** than an ordinary input token |
    | Reading it back | **an order of magnitude less** |
    | Break-even | **about one re-read** |

    Check your provider's current multipliers rather than these words — they move
    — but the shape does not. And the shape has consequences:

    - **A long system prompt is nearly free if it is stable and first.** Reused
      across every request, it is paid for once and read back at a fraction. The
      instinct to trim instructions to save money is usually optimising the
      cheapest tokens you have.
    - **Order decides whether you get the discount at all.** Caching works on a
      *prefix*. Put anything that varies — a timestamp, a user id, retrieved
      chunks — before the stable part and you have invalidated it on every
      request. Same tokens, same output, several times the bill. **This is the
      most common way an LLM invoice goes wrong**, and it is invisible in the
      code review that caused it.
    - **It changes the retrieval trade.** If a corpus is small and stable enough
      to sit in a cached prefix, "put it all in the context" stops being obviously
      wasteful and starts competing with a retrieval pipeline you would otherwise
      have to build, run, and keep in sync.

    None of this exists for the local model, and it does not need to: nothing is
    metered. That is the honest comparison — one side has a meter with a discount
    structure you have to engineer around, and the other has a machine. For
    Priya the cache is moot anyway: the stable prefix she would want to cache
    is the incident record, and that is the one thing Security will not let
    her send.

    > **🚢 Write the two latency numbers into `use_case/decisions.md`**, with the
    > hardware you measured them on. Replacing a closed model with a fine-tuned
    > open one has to argue the trade — this is the baseline that argument gets
    > made against, and for Priya it is the number the platform team will size
    > the internal server from.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What you can build with each

    The table above compared the two as things you *run*. Two more rows decide
    what you can *build*, and they are the ones the rest of the week depends on:

    | | Closed API | Open weights, self-hosted |
    | --- | --- | --- |
    | **Logit access** | No — you get text back | **Yes** — constrained decoding needs this |
    | **Weight access** | No | **Yes** — fine-tuning needs this |

    Both are "no" for a product by design: the provider's model is the thing
    being sold. Both are "yes" for a component because there is nothing in the
    way. Everything else — residency, versioning, cost shape, the latency
    floor, the ceiling — is in the comparison above, and the **data residency**
    row of it is the one Security already decided for Priya.

    **Guardrails.** The cheapest and most reliable one is *constrained
    decoding* — masking invalid tokens out of the distribution before sampling,
    so the model literally cannot emit malformed output. Now that you have
    written `top_k`, you can see how: it is the same masking operation with a
    different rule — *"never emit a token that continues a customer
    identifier"* is a rule of that shape. That technique is unavailable through
    an API that only returns text, which means Security's constraint is also
    what makes Security's other request possible.

    **Fine-tuning** replaces a closed model with an open one that must
    pass the same eval harness. That needs weights.

    The honest version of the argument is not "open weights are better". It is:
    **a closed API is a product, and open weights are a component.** Products are
    faster to start with. Components are what you build a system out of when the
    requirements are someone else's — and in Priya's case, three someone elses.

    > **🔀 Where your path diverges.** Priya's answer to her manager is decided
    > by the **data residency** row before any number is measured: Security's
    > rule is a constraint, and the latency and cost figures are supporting
    > evidence for a decision already made. If **your data may leave the
    > network** — public content, synthetic inputs, a use case Legal has
    > cleared — the same table reads the other way: the hosted model's
    > capability ceiling is a real advantage, its per-token meter is fine at
    > low volume, and self-hosting is a cost you would have to justify rather
    > than a requirement you inherit. Mark which rows are *constraints* and
    > which are *preferences* in your decision record; the next question asks
    > you to.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #4

    Priya has to answer her manager's *"why not the hosted model?"* in writing,
    and this cell just showed her a wall-clock time, two token counts, and a
    model name. In one to three sentences, say which numbers in that answer
    are *measured* and which are *looked up*, which of Security's and Legal's
    requirements the hosted option fails outright regardless of the numbers,
    and how you would mark all of that so a reader six weeks from now cannot
    mistake a constraint for a preference.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Conclusion

    You wrote every sampler an inference server uses, watched them reshape a
    real distribution, drove a real model with them, and then measured the
    local path against the hosted one — and learned that the numbers that
    survive the comparison are structural, not "which one wrote the nicer
    sentence." Priya's three departments turned out to be the argument for the
    week rather than obstacles to it: Security's *"the data stays"* is what
    puts the logits in her hands, Legal's *"regenerate it"* is a seed and a
    log line, and Procurement's *"read the licence"* is a question that has to
    be asked once, before anything ships.

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Softmax | `softmax` over 1,000 recorded logits | Fused CUDA kernels over the full vocabulary, per token, per request |
    | Throughput | One position at a time | Continuous batching across hundreds of concurrent requests |
    | Memory | Recomputing everything | KV caching, so each new token costs one forward pass rather than N; sized per request with the weights |
    | Samplers | Temperature, top-k, top-p | Those plus min-p, typical-p, repetition and presence penalties, DRY, grammar constraints |
    | Sampling | `rng.choice` | The same, plus speculative decoding to draft several tokens at once |
    | Settings | Sliders in a notebook | Per-endpoint config, logged with every request, so "the output changed" has an answer |
    | Cost | Two token counts printed once | Per-request token logging by endpoint and team, feeding a forecast rather than an invoice |
    | Reproducibility | A `seed` argument you passed by hand | Model version, settings and seed written to the same log line as the request, retained as long as the document they produced |
    | Data boundary | A prompt with nothing sensitive in it | A served model inside the network, with a written answer from the team that runs it about where the inputs go |

    ---
    # Additional Context

    - [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) — Holtzman et al., 2019. The paper that introduced nucleus sampling, and the one that explains *why* maximising likelihood produces boring, repetitive text. Read it now that you have written the algorithm
    - [Transformers — Generation strategies](https://huggingface.co/docs/transformers/en/generation_strategies) — every parameter you wrote from scratch in Tasks 2–5, as an API, plus the ones we skipped
    - [QLoRA](https://arxiv.org/abs/2305.14314) — Dettmers et al., 2023. Read §2 for quantisation, the answer to "how does a model that should not fit in my memory fit in my memory"
    - [The False Promise of Imitating Proprietary LLMs](https://arxiv.org/abs/2305.15717) — Gudibande et al., 2023. The counterweight to Task 9: small models trained on big-model output match style while failing on substance
    - [Artificial Analysis](https://artificialanalysis.ai/) — independent benchmarks of open and hosted models on speed, price and quality; where a 350M model sits relative to what you use daily
    - [State of Open Source on Hugging Face: Spring 2026](https://huggingface.co/blog/huggingface/state-of-os-hf-spring-2026) — the read-before-the-session piece: where the open-weight ecosystem is, who is releasing what, and why the model on Procurement's approved list next year may not come from the vendor it came from this year
    - **Keep building:** take the Task 9 comparison and turn it into a script that runs the same twenty prompts against your local model and your hosted one, and writes wall-clock, token counts, settings and seed to a file — the first row of the latency baseline any later model swap has to beat, and the first entry in the log Legal asked Priya for.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Bonus Tasks

    Optional. The first two are worth doing if you have the hour; the rest are
    meaningfully harder.

    ### Find your model's breaking point

    Pick one recorded position and sweep the temperature from 0.1 to 2.0. For
    each setting, draw 20 samples and note where the output stops being usable
    for your use case — for Priya, where a draft first asserts something the
    incident record does not contain.

    Write that number in `use_case/decisions.md`, with the model and the seed
    next to it. It is a real parameter you will ship, most teams pick it by
    superstition, and you will have measured it — and be able to show the run.

    ---
    ### Swap the model under your app

    If you can: install Ollama, point your `.env` at it, and re-run your
    own challenge app against a model on your own machine. The diff should be
    two lines in `.env` and nothing else — if it is more than that, you have a
    vendor dependency you did not know about, and better to find it now than
    in the meeting where Security asks which hosts the app talks to.

    ---
    ### Harder

    - **Implement min-p.** Keep tokens whose probability is at least `min_p ×
      max_probability`. It adapts to confidence like top-p but is cheaper — no
      sort. About four lines with what you have.
    - **Write a grammar mask.** Given a set of allowed token ids, zero everything
      else before sampling. You have just built the core of constrained decoding,
      well before you need it — and the mechanism behind *"the report may never
      contain a customer identifier"*, which is a rule you can now enforce in
      the sampler rather than hope for in the prompt.
    - **Measure the repetition.** Generate 200 tokens greedily along the trace's
      path and count distinct tokens; compare against sampling at T=0.8. The gap
      is why nobody ships greedy decoding for prose.
    """)
    return


if __name__ == "__main__":
    app.run()
