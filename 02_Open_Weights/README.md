<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Week 2 — Open Weights</h1>
  <p><strong>🏋️ Why open weights matter, and what that means for FDEs</strong></p>
</div>

---

## 🎯 What you'll be able to do

Write every sampler a modern LLM uses in numpy, run a real model on your own
laptop with them, and generate a synthetic dataset for a use case whose real data
you cannot touch yet — knowing exactly what that data can and cannot prove.

> ⚠️ **Prerequisite:** TC1 finished. Session 4 reads your five golden examples
> from `use_case/evals/golden.jsonl` and refuses to run while they are still
> the template. Session 3 has no such gate — Tasks 1–6 need nothing at all.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S3 | [`Local_Inference_Fundamentals`](./sessions/S3_Local_Inference_Fundamentals.py) | Every sampler a language model uses, written by hand in numpy — then a real model on your own laptop running with them, timed against your hosted provider. Told through one worker: an incident-response analyst at a regulated firm whose Security, Legal and Procurement teams each have a rule, and every sampler is a step in satisfying them. | [Recording!](https://us02web.zoom.us/rec/share/32K8POoLKNXyfORuqNLCs4LdfFP75e1LqBLzmN5GeRuOGo0dBDdXF6nNZQ-BaMXH.vXKjWl1HSUGnXr2T) <br> passcode: `$V+*3m@g` | Coming soon |
| S4 | [`Synthetic_Data_Generation`](./sessions/S4_Synthetic_Data_Generation.py) | A generator that turns five hand-written examples into a dataset, a de-duplicator and validator that throw most of it away, a leak check, and the datasheet that says what the survivors can prove. The same analyst, one week on: she cannot touch the incident database until a request clears, so she generates stand-in records while Security asks what leaked, Legal rules held incidents out, and Procurement's gateway rate-limits the run. | [Recording!](https://us02web.zoom.us/rec/share/yUo7IkNCgwnrQhtr46eg4pW0pGV3lApIIjNggqQ1BP_KWotUNfAiwZAfqhiSVhzX.6-qFXps_PDjEpUfj) <br> passcode: `E5mY7h+9` | Coming soon |

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC2 — Generate synthetic data for your use case**](./challenge/README.md) | Coming soon |

---

## 📖 Overview

When you use an AI model through a company like OpenAI or Anthropic, you send
text and get text back. What happens in between is hidden. This week opens the
box, and then uses what is inside to solve a problem almost every enterprise
project has: **you are not allowed to touch the real data yet.**

**Session 3 is about what a model actually does.** Underneath, a language model
does one thing: given some text, it produces a score for every word that could
come next. Everything you think of as the model's "personality" — how creative
it is, how repetitive, how often it goes off the rails — is decided *after*
that, by a few lines of ordinary code that pick one word from those scores.
That code is called *sampling*, and settings like "temperature" are knobs on
it. You will write those few lines yourself, watch them change the output, and
then download a small model to your own laptop and run it with them. Doing this
once makes every "temperature = 0.7" you see for the rest of your career mean
something specific.

Why does it matter that the model runs on *your* machine? Because a hosted
service hides those scores from you, and several things you will want later —
making a model *unable* to produce malformed output, or training it on your
own data — need access to them. "Open weights" means a model whose insides you
can download and reach into. This session is where you find out what that
buys.

**Session 4 is about the data you cannot have.** Your real records are usually
behind an approval, a privacy review, or a network you cannot reach from your
laptop, and the wait routinely lasts weeks. So you generate stand-in data
instead: start from the five examples you wrote by hand in Week 1, ask a model
for hundreds more that vary in ways you choose, and then — this is the part
people skip — throw most of them away. Duplicates go. Anything that does not
fit your schema goes. Anything that might leak a real name or a real customer
goes. What survives is useful precisely because you know what it *cannot*
prove, and you write that down in a one-page datasheet so nobody, including
you in six weeks, mistakes it for real data.

**The challenge** is the second session on your own problem: your axes of
variation, your generated dataset, your datasheet, and a conversation with
someone who sees the real inputs every day about whether your fake ones look
right.

If you take one idea from this week: **a number you generated is not evidence
until you have said what it cannot show.** Sampling settings are measured, not
copied from a blog post. Synthetic data proves your pipeline runs, and nothing
about how it performs on the real thing.

---

## 🔀 Priya's path, and where yours diverges

Every decision in the notebooks is one Priya made for *her* setup — a
regulated firm, customer identifiers in the data, a Legal team that needs
drafts regenerated, no access to the real records yet. The reasoning
transfers; the answers may not. This is the map. The notebooks carry the same
forks next to each decision.

| Decision | What Priya chose, and why | What flips it |
| --- | --- | --- |
| **Hosted API or local weights** | Local — Security's *"nothing in that table leaves the network"* is a constraint, not a preference; the latency and cost numbers are supporting evidence | **Your data may leave the network** (public, synthetic, Legal-cleared): the hosted model's quality ceiling is a real advantage and self-hosting is a cost to justify. **You need only Security, not Control**: a private endpoint to a hosted model inside your cloud tenancy is the cheaper, legitimate answer |
| **Which local model** | A 350M model on her laptop — prototyping, and it is the model the recorded trace came from | **16 GB laptop / Apple Silicon**: a 4–8B instruction-tuned model. **Consumer GPU**: a quantised 20–30B. **Download blocked**: the question becomes which internal registry, and that is an `ecosystem.md` line first |
| **Greedy or sampled** | Both — greedy for the extracted fields, sampled (with a logged seed) for the narrative, because a regulator asks about each differently | **All extraction** (categories, ids): greedy is the whole answer. **All prose** (a drafting assistant): sampled everywhere, and the seed stands in for greedy's free reproducibility |
| **Top-k or top-p** | Top-p — one rule Legal approves once for incidents the model is sure and unsure about | A **single, uniform prompt shape** where confidence barely varies: a fixed `k` is simpler and nobody will notice the difference |
| **What to log** | Model version, settings and seed on the same line as every request — Legal's seven years | **No regulatory retention**: log it anyway, for a week; it is what makes "the output changed" answerable, and it costs nothing |
| **Where the training data comes from** | Generated from a description and five hand-written examples — she has no real records and could not use them if she did | **You have an approved masked export**: use it to *check* the synthetic set's distribution, not as the seeds. **Your firm allows local development on real data**: generate anyway for anything you will share |
| **How hard to dedupe** | Threshold 0.7 on character 4-grams — strict enough to catch the same outage reworded | **Short, formulaic inputs** (tickets, log lines): raise it or you delete legitimate near-twins. **Long free text**: lower it; paraphrases of one scenario are the failure |
| **What the datasheet claims** | Prototyping data: it proves the pipeline runs and the schema holds, and says in writing what it cannot validate | **Backtested from real outcomes**: then and only then can it support a production number — and the datasheet says so with the source |

The habit to copy is not any row. It is that every row has a **condition** in
it — the fact about Priya's setup that made the answer come out that way — so
that when your fact is different, you know which way to go.

---

## 🔑 Required accounts, keys, and setup

**S3** needs no model to complete Tasks 1–6 — they run on a recorded logits trace
committed to this repo. Task 7 downloads a 0.7 GB model; Task 9 makes **one**
call to your hosted provider. **S4** needs a model for every generation call, and
reads your five golden examples from Week 1.

```bash
uv sync --group local        # torch (CPU wheels) + transformers, ~one-time
make nb F=02_Open_Weights/sessions/S3_Local_Inference_Fundamentals.py
```

> **`uv sync` is exact and will remove this group again.** A later plain
> `uv sync` uninstalls `torch` and `transformers`, and Task 7 then fails with
> `ModuleNotFoundError` on a machine where it worked yesterday. `make setup`
> keeps the group if it is installed; otherwise re-run `uv sync --group local`,
> or use `uv sync --inexact`.

The `local` group is opt-in so Weeks 1 and 3 stay a light install.

**A Hugging Face account is optional.** The S3 model is a public download and
needs no token. Make one only if your firm's network requires you to authenticate
through a mirror — and if it blocks the Hub outright, see the fallback below.

### Running a model yourself

Session 3 defaults to a **350M-parameter model, 0.7 GB, on CPU** — for one
reason: it is the model the committed logits trace was recorded with, so what
you dissect in Tasks 1–6 is exactly what you run in Task 7. It is a
prototyping choice, not a recommendation. **An FDE should know what a laptop
can actually run in 2026, and it is a lot more than 350M.** Sizes below are
the download at the quantisation most people run (roughly 4-bit where a GGUF
is the normal route; `float16` for the small ones); check the model card.

| Tier | Models (examples) | Download | What runs it |
| --- | --- | --- | --- |
| **Any laptop CPU** | **`LiquidAI/LFM2.5-350M`** (the default), `Qwen/Qwen3-1.7B` | 0.7 – 4 GB | Any machine in the cohort. Seconds per sentence on CPU |
| **A 16 GB laptop / Apple Silicon** | `google/gemma-4-E4B-it`, `Qwen/Qwen3-4B`, `Qwen/Qwen3-8B` | 3 – 8 GB quantised | Most of the cohort. This is the tier to prototype a *real* assistant on — instruction-tuned, follows a system prompt, calls tools |
| **A consumer GPU, or 32–64 GB of unified memory** | `Qwen/Qwen3.6-27B`, `openai/gpt-oss-20b` | 12 – 20 GB quantised | A gaming card or a well-specced Mac. Frontier-adjacent quality, entirely offline |
| **Needs real hardware** | `openai/gpt-oss-120b`, Qwen3 235B-A22B | 60 GB + | A workstation GPU or a small server — the size a platform team provisions, not a laptop |
| **Server-class** | Kimi K2, DeepSeek-V4 | hundreds of GB | Multi-GPU nodes. This is what a firm's gateway serves, and what you compare against in Task 9 |

Changing the model is one string in the notebook. None of your sampler code
knows which model it is running against, which is the point — and the tier
you can run is itself a finding for `use_case/ecosystem.md`, because it decides
whether "run it locally" means your laptop, a shared box, or a request to the
platform team.

> **Check the licence before any of these go to work.** "Open weights" describes
> what you can download, not what you may do with it — the default here is under
> a custom licence, not Apache-2.0. Week 9 has a task on this.

### About the CPU pin

torch is pinned to the **CPU wheel index**, and that covers everyone: it ships
wheels for Linux (x86_64, aarch64), Windows (amd64, arm64), and macOS arm64.

> **Apple Silicon keeps MPS.** The macOS wheel in that index is the same build
> PyPI serves — PyTorch does not publish a separate CPU-only Mac wheel. You give
> up nothing.

This week's model is 350M parameters and generates faster than you can read on
any laptop CPU, so a GPU buys you nothing here. **Week 8 is where that changes.**

If you want your GPU now, one line in `pyproject.toml`:

| Hardware | Change the index URL to | Notes |
| --- | --- | --- |
| **NVIDIA**, Windows or Linux | `.../whl/cu130` or `.../whl/cu126` | Both carry torch 2.13 on both platforms |
| **AMD**, Linux | `.../whl/rocm7.0` | **Linux only** — no official Windows ROCm wheels exist. Also pinned to torch 2.10, so it will not share this lockfile; use a separate environment |
| **Apple Silicon** | nothing | MPS is already there |

Two traps worth knowing: `cu129` has **no Windows wheels**, and `cu128` is stuck
at torch 2.11.

### 🧯 If the download is blocked

Tasks 1–6 run entirely on a **recorded logits trace** committed to this repo —
same model, real numbers, no network. You lose only the generation loop.

**And that blockage is itself a finding.** Write it in `use_case/ecosystem.md`:
a network that blocks Hugging Face shapes Weeks 8 and 9 more than any technical
decision you will make, and the answer is usually an internal model registry
somebody already runs. See
[`sessions/data/README.md`](./sessions/data/README.md) for what the trace can
and cannot do.

### Before the sessions

- **Pull the model the day before** — `uv sync --group local`, open S3 and
  press *Download and load* in Task 7 once. It is 0.7 GB and the one thing that
  cannot be hurried in the room; after that the notebook finds the cached
  weights and loads them without the button. If you have a 16 GB laptop or
  Apple Silicon, also pull one model from the next tier of the table above —
  you will want it in the second hour.
- **Play with temperature on something you already use.** Any chat interface
  with a temperature control: push it to 0, then to 1.5, on the same prompt,
  three times each. Form an opinion before Session 3 shows you the arithmetic.
- **Re-read your five goldens.** If they are thin, Session 4 will make that
  obvious in a way that is useful rather than embarrassing.
- **Write down three ways a real input could be weird.** Not the happy path —
  the malformed one, the ambiguous one, the one where the right answer is "I do
  not know." These become your variation axes, and thinking of them cold is
  much harder than thinking of them now.

---

---

## 📚 Recommended reading

Two of these close gaps the challenge assumes and the sessions only gesture at;
the rest are the canonical texts behind the two sessions.

- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) — Gebru et al. **The challenge grades your datasheet, and this is the genre.** Appendix A has worked examples; ten minutes there changes Step 4 from a description into an assessment
- [Ollama — quickstart](https://docs.ollama.com/) — **Step 5 of the challenge re-points your app at a local server**, and Session 3 ran the model through `transformers` rather than a server. This is the gap between the two
- [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) — the nucleus-sampling paper. Read it *after* S3; you will have written the algorithm by then
- [Hugging Face: how to generate](https://huggingface.co/blog/how-to-generate) — the same samplers, in library form, for comparison
- [Self-Instruct](https://arxiv.org/abs/2212.10560) — Wang et al. Seed examples → generated instructions → filtering. S4 is a small version of this pipeline
- [Textbooks Are All You Need](https://arxiv.org/abs/2306.11644) — synthetic data as a first-class training input, not a fallback
- [The False Promise of Imitating Proprietary LLMs](https://arxiv.org/abs/2305.15717) — the counterweight to both sessions: synthetic data from a strong model teaches style faster than substance
- [QLoRA](https://arxiv.org/abs/2305.14314) — §2 only, for quantisation: how a model that should not fit in your memory fits in your memory

**Pre-reads, from the session briefs** — ten minutes each, before the session they belong to:

- [State of Open Source on Hugging Face: Spring 2026](https://huggingface.co/blog/huggingface/state-of-os-hf-spring-2026) — before S3. What the open-weight landscape looks like this year, so the model table in S3 reads as a choice rather than a list
- [Designing synthetic datasets for the real world (Simula)](https://research.google/blog/designing-synthetic-datasets-for-the-real-world-mechanism-design-and-reasoning-from-first-principles/) — before S4. Coverage, difficulty and quality as separate dials, which is what S4's axes are by hand
- [How to Build Privacy-Preserving Evaluation Benchmarks with Synthetic Data](https://developer.nvidia.com/blog/how-to-build-privacy-preserving-evaluation-benchmarks-with-synthetic-data/) — before S4. The whole S4 pipeline in a regulated domain, with tooling

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A synthetic dataset generated from your own golden examples across variation
axes you named, deduplicated and validated, with a datasheet that says what it
can and cannot prove.

Eight questions are asked inside the notebooks as you work through them. *They
are not submitted and not graded* — they are how you work out what the challenge
is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | Whether a "should decline" axis value wants a higher or lower temperature than a routine one, and what the 95%-mass count says about it | S3 |
| 2 | Why a fixed `k` is the wrong tool for a batch run whose prompts differ in how confident the model is | S3 |
| 3 | Why the temperature ceiling you measured is nearly worthless to Legal on its own, and what two other things must sit beside it before a colleague or a regulator can reproduce the draft | S3 |
| 4 | In the written answer to "why not the hosted model?", which numbers are measured and which looked up, which requirements the hosted option fails outright regardless of numbers, and how you mark a constraint apart from a preference | S3 |
| 5 | One axis specific to your domain, and the failure it would expose that paraphrases cannot | S4 |
| 6 | Whether you would raise or lower the dedupe threshold for your data, and what you would look at to decide | S4 |
| 7 | One thing in your seeds the regex leak check cannot see that would still identify your firm | S4 |
| 8 | Whether `synthetic_v1.jsonl` is prototyping or backtesting data, and the datasheet claim that follows | S4 |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-7`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] Axes in your repo: at least two specific to your domain, one that covers inputs the system should **decline**
- [ ] `use_case/data/synthetic_v1.jsonl` written (gitignored — the datasheet says how many rows)
- [ ] Generated / after-dedupe / schema-valid counts reported, plus dead axis combinations
- [ ] Leak check run **and** fifty rows read by you, with what you removed
- [ ] `use_case/data/DATASHEET.md` filled in, including what the data cannot validate **and whether the goldens are disjoint from anything the system was tuned on**
- [ ] **The model/endpoint row in `use_case/decisions.md`** — every number tagged *measured* or *looked up*, and constraints marked apart from preferences

### 📤 Share

- [ ] **A demo to a real user, with their feedback recorded in your own words** — graded, and the one people skip
- [ ] **What you would swap to run this at work** — data, model or endpoint, and the approval you would need — three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## 📊 What the notebooks measure

Notebooks ship without outputs, so this is where the numbers live for anyone
reading on GitHub.

**Top-p adapts where top-k cannot.** The same `k` that is right for a confident
prediction is wrong for an uncertain one. S3 measures the candidate-set size at
each recorded position and the two diverge immediately — which is the entire
argument for nucleus sampling, made with numbers rather than assertion.

**Greedy is a lookup, not a draw.** Ten runs, one distinct answer, no seed
involved. That determinism is exactly what extraction work wants and exactly what
makes greedy prose read like an early chatbot.

**T=1.8 breaks a 350M model inside a dozen tokens**, usually into other
languages. Finding a model's usable ceiling takes about a minute; most teams
copy a temperature from a blog post instead.

**Local vs hosted, timed on the same prompt.** S3 runs both and reports
wall-clock and token counts. The quality gap is large and expected — the local
model is 2–3 orders of magnitude smaller. The findings that survive are
structural: no network floor, no per-token meter, and nobody can deprecate the
model your Week 4 evals were measured against. *(Cost per token is a lookup, not
a measurement, and the notebook says so.)*

**Deduplication is where synthetic data quality actually lives.** S4's char-4-gram
Jaccard pass at threshold 0.7 shows how much of a naively generated set is
near-duplicate — and its separate counters for unparseable rows versus dead
combinations exist because averaging them hides a coverage hole.

### Terms you'll meet

You do not need to know any of these in advance. This is what each one means
in one sentence, and where it comes up. Every term from every week is also
collected, alphabetically, in the repository's [`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it bites |
| --- | --- | --- |
| **Token** | The unit a model reads and writes — usually a word piece; 30 tokens is roughly 20 words | S3 intro, and every count in Task 9 |
| **Vocabulary** | The fixed list of every token a model knows, and the only things it can ever output | S3 Task 1 |
| **Forward pass** | One run of the network over the input, producing a score for every vocabulary token at the next position | S3 Task 1, and Task 7's generation loop |
| **Logit** | The raw score for each candidate next token, before it is turned into a probability | S3 Task 1 |
| **Softmax** | The step that turns logits into probabilities that sum to one | S3 Task 1 |
| **Sampling** | Choosing one token from those probabilities — the only place randomness enters | S3 Tasks 2–6 |
| **Seed** | The number that makes a random choice repeatable | S3 Task 6; Legal's requirement |
| **Open weights** | A model whose parameters you can download and run yourself | S3 Task 7 onward |
| **KV cache** | The per-request memory that lets token 200 cost one forward pass instead of two hundred; it is what you provision alongside the weights | S3, the hardware section |
| **Batching** | Serving several requests through one forward pass, multiplying the cache by requests in flight | S3, the hardware section |
| **Prompt caching** | A hosted provider keeping a processed prompt *prefix* and charging far less to reuse it | S3 Task 9 |
| **Prototyping vs backtesting data** | Generated to exercise a pipeline, versus drawn from real outcomes and able to support a production number | S4 Task 1, and the datasheet |
| **Variation axes** | The dimensions along which real inputs differ, which you generate across on purpose | S4 Task 2 |
| **Character n-gram Jaccard** | Overlap between two texts' sets of 4-character shingles — a model-free near-duplicate detector | S4 Task 4 |
| **Leak (outward)** | A distinctive string from your seeds surviving into data you will share | S4 Task 6 |
| **Leak (inward)** | Your evaluation set drawn from the same data the system was tuned on, so the score measures self-consistency | S4 Task 6 |
| **Datasheet** | The document that says where a dataset came from and what it cannot validate | S4 Task 7 |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions rarely use the words a
syllabus uses, and that costs people interviews. This week is advertised as
**inference engineering** — also **model serving**.

Roles here name vLLM, SGLang, quantisation and KV-cache management. The sampler
you wrote by hand is what all of them are optimising.

### Where the industry is headed

Small models are getting good faster than large
models are getting cheap, so "we cannot send this data anywhere" is
decreasingly a reason to abandon a project and increasingly a reason to pick a
different model. Control is being added at the sampler — constrained decoding,
grammar-based generation, structured output all mask logits before the sampler
runs, which is exactly the surface Session 3 hands you. And the open-weights
argument is now operational rather than ideological: a vendor can deprecate a
model, change its behaviour without a deploy of yours, or retire it on a
schedule that is not yours. You cannot be surprised by a model you host.

On the data side, synthetic data has stopped being a fallback — it is a
deliberate stage in most serious training pipelines, because it is the only
way to get coverage of cases that are rare in the wild but expensive when they
happen. Provenance is becoming a compliance question, and the teams that find
that cheap are the ones already writing datasheets.

**Back to Week 1** — your five golden examples are the seeds, and your pydantic
schema is the validator that throws most of the generated rows away.

**Forward to Week 3** — you build retrieval over the data you generate here.

**Forward to Week 4** — the prototyping/backtesting distinction becomes the
difference between a demo and a number you can defend. Your goldens are the
bar; this data is the traffic.

**Forward to Week 6** — `top_k` becomes constrained decoding.

**Forward to Week 8** — this data is what you fine-tune on, and open weights are
what you fine-tune. The temperature ceiling and latency baseline you wrote into
`use_case/decisions.md` are what the fine-tuned model is measured against.

**Forward to Week 9** — a blocked model download, and the licence on whatever you
picked, both land in `use_case/ecosystem.md`.

**Forward to Week 10** — the three "what you would swap" lines from Step 7
are the first of the final report's list of what it would take to run for real.
