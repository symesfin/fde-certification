<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Week 4 — Evals</h1>
  <p><strong>📊 Evals and the path to PoC</strong></p>
</div>

---

## 🎯 What you'll be able to do

Report a number about your system that someone outside your team has a reason
to believe — and know when that number is lying to you.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S7 | [`Practical_Evals`](./sessions/S7_Practical_Evals.py) | **DeepEval, installed and run first** on your own goldens; then the harness it is made of in forty lines, four scorers that need no model, an LLM judge and the check that decides whether to believe it, two loops — one that makes the eval better rung by rung (down to failures generated from your own goldens and the interval on the result), one that uses it to make the app better (a basic prompt against an elaborate one, every scorer side by side) — and the framework's metric running inside your harness with the number in the Head of Claims' units. Told through a claims-operations analyst whose Head of Claims will not fund a score, only an overturn rate, a leakage figure, and an interval. | Coming soon | Coming soon |
| S8 | [`Agent_Evals_via_Simulation`](./sessions/S8_Agent_Evals_via_Simulation.py) | **The agent, drawn, then built in five parts** — a claims assistant with four tools, one of which writes. **DeepEval's agent metrics first** — end-to-end, trajectory, component — on one claim and two agents, one of which gets the right answer without checking. Then the blend, with a table of who wrote what and why: scenarios with a goal and a secret (yours — three by hand, ten composed from atoms, loaded from a file); the simulator loop from `helpers.simulation` (a library, built in the companion notebook); a verifier that reads the ledger (yours — a framework cannot see your state); `TaskCompletionMetric` as one column (the framework's judge); and a capability report with a saved, fingerprinted baseline and a `compare` with a tolerance (yours — the gate). The same agent with its tools unwired barely moves the average, collapses every tool capability, and still looks fine to the framework's judge. | Coming soon | Coming soon |
| S8b | [`Agent_Simulation_From_Scratch`](./sessions/S8b_Agent_Simulation_From_Scratch.py) | **Self-study: every line S8 imports.** Scenarios composed from targets × capabilities × personas; the loop and the trajectory it records; verify what you can, judge what you cannot (with DeepEval's `TaskCompletionMetric` prompts read beside your judge); the harness tested on five agents you know are broken — the lying one passes every text check; a model user, five runs, and `pass^k`. Each task ends with the framework's version of that piece and what it leaves out, and the Conclusion maps every function to `helpers/simulation.py`. | — | — |

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC4 — The harness, a saved baseline, and a five-minute demo**](./challenge/README.md) | Coming soon |

---

## 📖 Overview

Everything you have built so far *seems* to work. Somebody has tried it, the
answers looked right, and that is where most AI projects inside a company stay
— because nobody can say, with a number, whether the next change made it
better or worse. This week is about producing that number, and about knowing
exactly how far to trust it.

**Session 7 is about scoring a single answer.** It opens with the
framework: your golden examples go into DeepEval as a dataset, six named
metrics come back in a minute, and the question is what that framework
decided for you. Then you write the measuring instrument yourself — a list
of test cases, a handful of functions that compare an answer to the expected
one, and a report — in about forty lines, and test it before trusting it by
feeding it a system that echoes the question back and one that cheats by
knowing the answer. You use a model as a grader for the things a function
cannot check, read the framework's own grader prompts beside yours, and run
the check almost everyone skips: separation on known-bad and known-good, and
agreement with a person. Then two loops. The first makes the *eval* better,
one rung at a time — exact match, token overlap, required fields, the judge,
failures you generate from your own goldens because your goldens do not
contain a reversed claim until you put one there, and the interval that says
whether a five-point change is real. The second uses the eval to make the
*app* better: a basic prompt against an elaborate one, every scorer side by
side, and the sentence *change X, to move Y, because the business measures
Z*. The session ends with the framework's metric running inside your own
harness, a saved baseline, the number translated into the units a Head of
Claims measures, and a three-row answer to "framework or my own?" for MVP,
PoC and production.

**Session 8 is about scoring a conversation**, and it is the same ladder as
Session 7 — framework first, then the blend, then the gate — on an agent.
The claims assistant now has tools and talks to claimants. It is drawn
first, then built in five parts so you can see what each eval can observe:
three read-only tools, one tool that writes to a ledger, the schemas the
model sees, the system prompt (every rule in it is a scenario waiting to be
written), and the loop that records every tool call. DeepEval's agent
metrics run at three levels — did the final answer do the job, were the
right tools called, were they called with the right arguments — on one
claim and two agents, one of which gets the right answer without checking
anything. Then the blend, with a table of who wrote what and why: the
scenarios are yours, because they are your product's requirements (three
by hand, ten composed from atoms and loaded from a file); the simulator
loop is a library, `helpers.simulation`; the verifier is yours, because it
reads the ledger and no framework can see your state; the framework's
`TaskCompletionMetric` is one column; and the gate — a saved, fingerprinted
baseline and a `compare` with a tolerance — is yours, because the decision
to ship cannot live in a library default. The same agent with its tools
unwired barely moves the average, collapses every tool-dependent
capability, and still looks fine to the framework's judge, which is the
whole argument in one table. A person still reads the worst transcript
before anything reaches a claimant.

**Session 8b is the from-scratch build of what Session 8 imports**, for
self-study: the atoms and the composition, the loop and the trajectory,
verify-or-judge with the framework's prompts read beside yours, five broken
agents that test the harness (none of which a framework ships), and a model
user run five times for `pass^k`. Each task says why that piece is built
rather than adopted, and ends with the framework's version and what it
leaves out.

**The challenge** is the harness for your own app: a test set (your goldens
plus the failures you generated), your scorers and a judge, both dumb
baselines, a saved run with its interval that Weeks 5 through 8 are measured
against, and conclusions a stakeholder can act on. Then a five-minute demo
that leads with the number, rehearsed with a real person before you present
it live in Week 5 — and the challenge is due before that session, so the
rehearsal is the first thing to schedule, not the last.

If you take one idea from this week: **a number without a baseline, an
interval, and a check against a human is not evidence.** It is a decoration,
and the person who eventually notices will not be you.

---

## 🔑 Required accounts, keys, and setup

Both sessions need a model and nothing else. **S7 reads your golden
examples** — if `use_case/evals/golden.jsonl` is still the template, the
session stops at Setup and tells you so. **S8 reads a fictional claims
system** in `sessions/data/claims.json`; nothing in it is real.

```bash
make nb F=04_Evals/sessions/S7_Practical_Evals.py
```

**On Windows, or anywhere `--sandbox` is blocked**, open them from the root
environment instead — one command per notebook, no `make`, no sandbox prompt,
and no new executable for an Application Control policy to block:

```powershell
uv run python scripts/nb.py 04_Evals\sessions\S7_Practical_Evals.py
uv run python scripts/nb.py 04_Evals\sessions\S8_Agent_Evals_via_Simulation.py
uv run python scripts/nb.py 04_Evals\sessions\S8b_Agent_Simulation_From_Scratch.py
```

The script installs the `week4` group into `.venv` (`uv sync --inexact
--group week4`, which leaves other weeks' groups in place) and starts marimo
through Python. Same notebooks, same pins; the reasoning is in
[`00_Prerequisites/5_Your_Notebooks`](../00_Prerequisites/5_Your_Notebooks/README.md#two-ways-to-run-a-notebook).

**Both sessions run DeepEval** (`deepeval>=4.3`, in each notebook's header
and in the `week4` dependency group — `make setup-week W=4` if you open them
without `--sandbox`). Three things the notebooks do that the documentation
does not mention: `DEEPEVAL_TELEMETRY_OPT_OUT=YES` before the import, because
the library sends usage events to the vendor by default; a fifteen-line
judge class of its own instead of the shipped `LiteLLMModel`, because the
shipped wrapper guesses which API key to send from the environment and
guesses wrong when `.env` holds both an OpenAI key (embeddings) and an
Anthropic key (chat); and an explicit token budget on the judge so its JSON
is not truncated. Every judge call goes through `CFG.kwargs()` exactly like
the rest of the notebook, so an Anthropic, OpenAI or gateway setup works
unchanged. It writes a `.deepeval/` cache folder in the working directory,
which is gitignored.

**What reaches the network, for a managed laptop.** On the main path of both
notebooks the only outbound traffic is to your model provider through
`CFG.kwargs()` — the same endpoint every other week uses. DeepEval's PyPI
version check is opt-in (`DEEPEVAL_UPDATE_WARNING_OPT_IN`) and never runs;
its telemetry is opted out before import; the calibration data, the
claims system and the composed scenarios are files in `sessions/data/`.
Nothing in Week 4 reaches GitHub or any other host. (τ²-bench, named in
S8's reading list as the adoptable version of the simulator, is installed
by cloning its repository — which is exactly the kind of constraint to
write down in `use_case/ecosystem.md` before a firm adopts it.)

### Before the sessions

- **Score twenty of your own outputs by hand** — pass or fail, and *why*.
  Genuinely by hand, before a model has an opinion. This is the calibration
  set for the challenge and the single highest-value hour this week.
- **Read one of your own real conversations end to end** — a support thread,
  an email chain. Notice how much of the work is the back-and-forth. That is
  what final-answer scoring cannot see, and it is the case S8 builds.
- **Have your Week 3 endpoint runnable.** The challenge points the harness at
  it, and that only works if it starts.

### The calibration dataset

**30 news articles and 480 machine-written summaries, each rated by three human
experts** on consistency, relevance, coherence, and fluency — from
[SummEval](https://github.com/Yale-LILY/SummEval), MIT licensed, committed to
[`sessions/data/`](./sessions/data/README.md).

It is here because checking a judge for agreement requires human judgement
to check against, and that is the thing teams never have. S7's main path
uses it only if you have no hand scores of your own yet; the Bonus
calibration task uses all of it. Regenerate with:

```bash
uv run --with pyarrow python scripts/make_eval_dataset.py
```

---

## 📚 Recommended reading

The first two are the method behind the challenge's test set and judge check
— read fifty traces, hand-score twenty, measure agreement. The rest are the
canonical texts behind the two sessions.

- [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) — Hamel Husain. **The trace pass the challenge's Step 1 asks for** — read fifty traces, write one sentence per failure, group and count — is this post's method, and it is the most practical thing written on evals
- [Eugene Yan — LLM Evaluators](https://eugeneyan.com/writing/llm-evaluators/) — **how to measure agreement between your judge and your own hand scores** — Cohen's kappa, and why raw agreement flatters a lopsided label set. The challenge's Step 3, with the arithmetic
- [Judging LLM-as-a-Judge (MT-Bench)](https://arxiv.org/abs/2306.05685) — where the judge's failure modes were catalogued: position bias, verbosity bias, self-preference. S7's Task 4 check exists because of this paper
- [AI Agents That Matter](https://arxiv.org/abs/2407.01502) — why agent benchmarks mislead when cost is not held constant. Read before you believe any leaderboard, including your own
- [τ-bench](https://arxiv.org/abs/2406.12045) — simulated users, domain rules, and multi-turn evaluation done carefully; the `pass^k` S8b computes comes from here
- [τ²-Bench](https://arxiv.org/abs/2506.07982) — the dual-control successor, and the argument for a user who can also act; the adoptable version of the loop, the model user and `pass^k` that S8b builds — cloned from GitHub rather than installed from PyPI, with its own pinned environment
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — the vocabulary of agent patterns; read before Session 8
- [DeepEval — metrics](https://deepeval.com/docs/metrics-introduction) — the framework S7 runs; the metrics reference and the `GEval` page, for when you want the standard RAG scorers without writing them — and the prompts S7's Task 4 reads from the package; the agent metrics S8's opener runs are on the same site
- [Ragas](https://docs.ragas.io/) — the other widely used framework, same ideas with a different API; know the name for when a colleague's pipeline uses it

**Pre-reads, from the session briefs** — ten minutes each, before the session they belong to:

- [In Defense of AI Evals, for Everyone](https://www.sh-reya.com/blog/in-defense-ai-evals/) — Shreya Shankar. Before S7: why systematic measurement is the tool teams without deep domain expertise cannot do without
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — Anthropic. Before S7: single-turn versus multi-turn, code graders versus model graders versus people, and designing around real failure modes
- [Judging LLM-as-a-Judge (MT-Bench)](https://arxiv.org/abs/2306.05685) — before S7, and listed above
- [τ-bench](https://arxiv.org/abs/2406.12045) — before S8, and listed above

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

An eval harness in your repo that scores your Week 3 endpoint against a test
set you prepared — your goldens and the failures you generated — with the
baselines and the interval that make its number one you can defend, a saved
baseline run that later weeks have to beat, and conclusions a stakeholder
can act on.

Eight questions are asked inside the notebooks as you work through them. *They
are not submitted and not graded* — they are how you work out what the challenge
is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | Where at your company the already-judged work lives — fifty outputs a human has already called right or wrong — and who judged them | S7 |
| 2 | Which of your failure modes a function can catch with no model, and what your oracle answer would be for one of them | S7 |
| 3 | Which dimension of "correct" two people at your firm would disagree on — and whether you should score it at all | S7 |
| 4 | Which component of your system you would change next, the scorer column you expect to move, the business number it translates to — and how many cases the interval needs before it could show it | S7 |
| 5 | What your real users withhold until asked, and what your agent would do if it assumed the answer instead of asking | S8 |
| 6 | Whether your success condition can be stated as an assertion about state rather than about text — and what that would let you stop scoring | S8 |
| 7 | What right-in-different-words and right-words-without-checking answers look like for your agent, and which of your checks would tell them apart | S8b (self-study) |
| 8 | Which `pass^k` you would put in an SLA, and how many repeats per scenario you can afford on every commit versus nightly | S8b (self-study) |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-7`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **A test set you prepared** — `use_case/evals/golden.jsonl` grown past the Week 1 seeds, plus **`use_case/evals/synthetic.jsonl`**: generated failures with their labels and the count of naturally occurring ones for comparison. `use_case/evals/failures.md` — one sentence per failure you saw in fifty real traces, ranked — is how you know which failures to generate
- [ ] **An eval harness relevant to your problem** — at least three model-free scorers that each trace to a line in `failures.md`, **echo and oracle** run with the oracle scoring 1.0, and one LLM judge (your own prompt, or DeepEval's `GEval`) with its separation shown on echo and oracle. Checking its agreement against twenty outputs you hand-scored is recommended, not graded; if you skip it, say so in the decision row
- [ ] **If your app holds a conversation: multi-turn scenarios**, one a refusal, in `use_case/evals/scenarios.py`, repeated with the spread reported if the user is a model. A single-turn eval passes an agent that says the right words without checking anything. Optional for a single-turn endpoint
- [ ] **`use_case/evals/baseline.json` committed**, with a confidence interval on the headline number, and `harness.compare()` of the file against itself reporting PASS
- [ ] **Conclusions** — `use_case/decisions.md` has the eval decision: the headline number with its interval, what it does not cover, what you rejected, and what would change your mind
- [ ] It still runs in Docker

### 📤 Share

- [ ] **A five-minute demo, rehearsed with a real person before Week 5, with their questions recorded in your own words** — graded, and the one people skip
- [ ] **What you would swap to run this at work** — data, model or endpoint, and the approval you would need — three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## 📊 What the notebooks measure

Notebooks ship without outputs, so this is where the numbers live for anyone
reading on GitHub.

### Session 7 — the framework first, then the harness it is made of

**The framework is run first, not described.** Task 1 puts the goldens
through DeepEval — two systems, `GEval` correctness and answer relevancy —
and three answers to one retrieval question through the four RAG metrics
(faithfulness, contextual precision, recall and relevancy). Measured with
`anthropic/claude-sonnet-5` as the judge:

| Answer | Faithfulness (default), run 1 → run 2 | Faithfulness (strict) | Contextual precision | Contextual recall | Contextual relevancy |
| --- | ---: | ---: | ---: | ---: | ---: |
| grounded in the context | **1.00 → 1.00** | 0.50 | 1.00 | 1.00 | 1.00 |
| one detail wrong (2 hours instead of 15 minutes) | **0.50 → 0.50** | 0.50 | 1.00 | 1.00 | 1.00 |
| invented procedure | **1.00 → 0.67** | 0.25 | 1.00 | 1.00 | 1.00 |

Three things in that table are the lesson, and none is a bug. The three
right-hand columns are identical because they score the *retrieved context*
against the question and the expected answer, and the context was the same
for all three answers. The invented procedure scored **1.00** on
faithfulness the first time because DeepEval's shipped verdict prompt marks
a claim "no" only when it *contradicts* the context; a claim the context
never mentions is "borderline" and counts as faithful unless
`penalize_ambiguous_claims=True`. The metric named faithfulness measures *not
contradicted*, not *grounded*. And the strict column is not simply "the
right setting": it drops the *grounded* answer to 0.50, because "page the
on-call engineer" without the word "immediately" was marked borderline too.
The run-to-run change (1.00 → 0.67, same judge, same inputs) is the judge's
own variance, and it is why the interval in Task 5 exists.

On the goldens (eight claims recommendations, same judge), the oracle scored
**1.00** on `GEval` correctness and the echo **0.00–0.05** across two runs —
and the echo scored **0.97–0.98** on answer relevancy, because a question is
perfectly relevant to itself. A metric with a reassuring name gave the worst
possible system a good mark.

**Four scorers that cost nothing to run.** `exact_match`, `token_f1`,
`contains_required`, and `declines` need no model, no key, and no latency.
Task 3 runs echo and oracle through them: the oracle row must be 1.00
everywhere or the scorer is wrong, and the echo's `declines` of **0.88** on
eight goldens is the row to read — seven of eight are questions a system
*should* answer, so "never decline" scores 0.88 on a scorer whose name sounds
like safety.

**Under the hood it is prompts.** Task 4 reads `FaithfulnessMetric`'s three
prompt templates straight from the installed package — claims out, verdicts
back, a reason — and puts them beside the short judge the student wrote.
Same thing in kind; more machinery; no more trust. Then the check:
separation on the echo and oracle outputs (no new data), and agreement
against `use_case/evals/human_scores.jsonl` if you have hand-scored twenty of
your own. Measured: the judge scored every echo output **0.00** and every
oracle output **1.00**; against twenty hand-scored outputs it reached
correlation **0.98**, within 0.25 of the human score 100% of the time.

**Loop A — the scorer ladder** (Task 5). Your goldens' correct answers,
broken four named ways — a changed number, a reversed claim, an unsupported
sentence, a swapped name — and scored by every scorer. Every row is a wrong
answer, so every cell should be low; a high cell is a scorer that was
fooled. Measured on eight claims goldens (**29 labelled wrong answers**: 8
number, 5 negate, 8 unsupported, 8 entity):

| failure | exact | f1 | required | declines | judge |
| --- | ---: | ---: | ---: | ---: | ---: |
| number | 0.00 | 0.96 | 1.00 | 1.00 | 0.50 |
| negate | 0.00 | 0.99 | 1.00 | 1.00 | 0.40 |
| unsupported | 0.00 | 0.90 | 1.00 | 1.00 | **1.00** |
| entity | 0.00 | 0.97 | 0.67 | 1.00 | 0.10 |

`f1` stays above 0.9 on every failure because a wrong answer shares almost
every token with the right one; `required` passes anything that still
mentions the clause; the judge catches swapped names and reversed claims and
is fooled completely by an *added* sentence — the same "not contradicted"
gap as the framework's faithfulness, in the student's own rubric. The file
this writes, `use_case/evals/synthetic.jsonl`, is the challenge's
generated-failures deliverable.

**A five-point improvement is invisible on a small eval set.** The last rung
bootstraps an interval and shows the same true difference at six eval-set
sizes. Measured (true improvement +0.05, one draw per size):

| eval cases | difference | CI on the difference | real? |
| ---: | ---: | --- | --- |
| 5 | +0.000 | [+0.00, +0.00] | no — spans 0 |
| 10 | −0.100 | [−0.40, +0.20] | no — spans 0 |
| 20 | +0.050 | [−0.10, +0.25] | no — spans 0 |
| 50 | −0.020 | [−0.16, +0.12] | no — spans 0 |
| 200 | +0.070 | [+0.01, +0.13] | yes |
| 1000 | +0.072 | [+0.04, +0.10] | yes |

Fifty cases can show a five-point *improvement* as a two-point regression and
the interval is honest about it; the sign only becomes trustworthy around 200.
TC8 asks you to beat the numbers you save this week, so knowing when a
difference is noise is not optional.

**Loop B — use the eval to improve the app.** The same model behind a basic
prompt (the question, nothing else) and an elaborate one (what a good answer
contains, plus one of your own goldens as a worked example), every scorer
side by side with the interval on each difference. Measured, n=8:

| scorer | basic | elaborate | difference | 95% CI | real? |
| --- | ---: | ---: | ---: | --- | --- |
| exact | 0.00 | 0.00 | +0.00 | — | no |
| f1 | 0.12 | 0.21 | +0.10 | [+0.06, +0.13] | yes |
| required | 0.25 | 0.35 | +0.10 | [−0.12, +0.31] | no — spans 0 |
| declines | 1.00 | 1.00 | +0.00 | — | no |
| judge | 0.24 | 0.43 | +0.19 | [+0.09, +0.29] | yes |

The elaborate prompt moved `f1` and the judge with intervals that clear
zero, and `required` moved by the same amount without clearing it — eight
cases. But read the levels: both prompts sit low on `required` and the
judge, because a prompt-only system has never been given the policy wording
and cannot cite clause 4.2 however well it is asked. The eval has named the
next component to change — retrieval, not wording — which is the X → Y → Z
sentence the task ends on.

**The framework's metric runs inside your harness, not instead of it.** Task
6 wraps `GEval` as a fifth scorer beside the four string scorers and runs
four systems through `helpers.harness.run` — echo, the basic prompt, the
elaborate prompt, and the oracle — then saves the **elaborate prompt's** run
as `use_case/evals/s7_baseline.json`: the first fingerprinted baseline, a
real number rather than the oracle's 1.0, and the file TC8's "beat your Week
4 numbers" is checked against. The echo and oracle rows bracket the range
(oracle 1.00 everywhere or the scorer is wrong; echo `declines` 0.88 because
only one golden in eight should decline); the two prompt rows are the
systems. Measured on the eight goldens:

| system | exact | f1 | required | declines | correctness (GEval) |
| --- | ---: | ---: | ---: | ---: | ---: |
| echo | 0.00 | 0.22 | 0.00 | 0.88 | 0.00 |
| basic prompt | 0.00 | 0.12 | 0.29 | 0.88 | 0.20 |
| elaborate prompt | 0.00 | 0.20 | 0.33 | 1.00 | 0.24 |
| oracle | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

The framework's judge agrees with the hand judge about the ordering and is
harsher on both prompts; both sit near the floor for the same reason Loop B
found. (A second run put the prompts' GEval at 0.18 and 0.20 — the judge's
own variance, a few points either way.)

**Marcus's page is arithmetic, not prose.** The last cell turns the harness
output into the Head of Claims' units — agreement with its interval as an
overturn rate, the wrong-pay rate times claims times the average claim as
leakage in pounds — with the three business numbers as editable inputs. The
overturn row is the framework's correctness score for the elaborate prompt
on the goldens with its bootstrap interval — measured: agreement **24%** on
n=8, so an overturn rate of about **76%**, 95% CI **[59%, 91%]**, which is
the page telling the truth about a prompt-only system that has no policy
text; leakage is 1.5% wrong-pay × 20,000 claims × £1,800 ≈ **£540,000 a
year** with the three business numbers as editable inputs. It closes with the
three-row answer to "framework or my own?": **adopt** it whole at MVP,
**blend** at PoC (its metrics and CI plumbing, your scorers for the criteria
that decide the product, its judge checked like yours), **own the gate** in
production. The reasoning is in the Bonus.

**Adopting a framework has a cost you can see before you pay it.** DeepEval
installs cleanly (no LangChain, no torch) but phones home by default, its
model wrappers pick an API key by guessing, and its judge is whichever model
you hand it — the one that answered, unless you decide otherwise. S7 names
each of those as a decision in Task 1's table and sets each one explicitly.

**Bonus: the judge against 480 human ratings.** The Bonus calibration task
keeps the long version of Task 4's check. Three human experts rated each
summary, and the dataset ships the *mean* of three ratings, so unanimity is
bracketed rather than measured:

| Dimension | Agreed at least | At most |
| --- | --- | --- |
| consistency | **80%** | 83% |
| fluency | **67%** | 72% |
| coherence | **6%** | 32% |
| relevance | **4%** | 35% |

Three annotators answering **at random** produce a whole-number mean **33%**
of the time, so coherence and relevance sit on their own chance floor — *a
metric that would read the same if the thing it measures were absent is not
a signal*. Consistency's lower bound sits above coherence's upper bound, so
the ordering is proved, not assumed. Then the hand-written prompt and
DeepEval's `GEval` score the same 24 stratified summaries against the human
mean. Measured, one run, same judge model for both:

| judge | correlation with humans | within 1 point | scored bad (≤ 2) at | scored good (≥ 4.5) at | unparseable |
| --- | --- | --- | --- | --- | --- |
| hand-written prompt (Task 4) | **0.88** | 92% | 2.08 | 5.00 | 0 |
| DeepEval `GEval` | **0.84** | 75% | 2.77 | 4.97 | 0 |

Both separate bad from good; the twelve-line prompt agrees with the humans
more closely than the framework's, and the framework is gentler on the bad
summaries. Neither row existed until the cell ran: the framework ships its
judge exactly as unchecked as yours was. What it buys is convenience, not
trust.

### Session 8 — three levels, who wrote what, and a gate that watches the deltas

**The framework's agent metrics, first.** One claim — a laptop stolen eight
days after the contents policy lapsed — and two agents: Marcus's, with four
tools over a fictional claims system, and a guesser that says the right
thing without calling anything. Three DeepEval metrics at three levels,
measured with `anthropic/claude-sonnet-5` as agent and judge:

| Level | Metric | Marcus's agent (`get_claim → get_policy → check_exclusion`) | Guesser (no calls) |
| --- | --- | ---: | ---: |
| end-to-end | `TaskCompletionMetric` | 0.95 | 0.90 |
| trajectory | `ToolCorrectnessMetric` | 1.00 | **0.00** |
| component | `ArgumentCorrectnessMetric` | 1.00 | — (no calls to score) |

Both agents said "decline" and both were right; the end-to-end metric gave
them 0.95 and 0.90. The trajectory level is where they separate, and the
component level asks *with what arguments*. (`StepEfficiencyMetric` was
dropped from the opener: it needs DeepEval's `@observe` execution trace and
returns 0.00 for everything when given only a tool list — the notebook says
so, and points at the trace route.) That is the case for scoring agents on
what they did rather than what they said. DeepEval also ships a gate —
`threshold=`, `is_successful()`, `assert_test` — and the notebook never
calls it; the next section is where the decision lives.

**The blend, and who wrote what.** Task 2 opens with the table the session
is built around, because the split is a decision a firm has to defend:

| Component | Who wrote it | Why |
| --- | --- | --- |
| Scenarios and atoms | you | they encode what *your* product must do and never do; no library knows your authority limit |
| The simulator loop, scripted user, roll-up | `helpers.simulation` — a library, built line by line in S8b | the same for every domain; write it once, read it once, import it after |
| `verify` — what the agent *did* | you | it reads the ledger; a framework sees only the transcript |
| `TaskCompletionMetric` | DeepEval | a judge over the transcript with the task inferred by the model — standard, and one column |
| Baseline file, fingerprint, `compare`, tolerance | you | the decision to ship lives in code you own and pin, not in a default that moves on `pip install` |

**Watch the deltas, not the average.** Task 2 runs all thirteen scenarios
— Marcus's three by hand plus ten composed from atoms and shipped as
`sessions/data/scenarios.jsonl` — against Marcus's agent and against the
same agent with its tools unwired, rolls `passed` up per capability, saves
the baseline through `helpers.harness` with a fingerprint of the scenario
set, and compares. The unwired agent still refers the total loss politely
and still answers in words a text check can pass. Measured, thirteen
scenarios, scripted user:

| capability | baseline | tools unwired | Δ | |
| --- | ---: | ---: | ---: | --- |
| tool_selection | 100% | 0% | −100% | 🔴 |
| tool_chaining | 67% | 0% | −67% | 🔴 |
| refusal | 100% | 0% | −100% | 🔴 |
| injection | 100% | 100% | +0% | ⚪ |
| edge_case | 100% | 50% | −50% | 🔴 |
| **overall** | **93%** | **30%** | **−63%** | |

`injection` is the row to explain: an agent with no tools cannot be tricked
into filing anything, so the injected instruction has nothing to act on.
`edge_case` at 50% unwired is the binary judge being generous to a polite
recovery with no lookup behind it. The 67% baseline row is one failed
chaining scenario out of three — read that transcript. And
`harness.compare()` says `REGRESSION baseline → tools unwired` with the
per-capability deltas, which is the sentence a CI gate prints. The saved
file, `use_case/evals/s8_agent_baseline.json`, is what `harness.compare()`
refuses to cross the moment the scenario set changes — which is experiment
tracking, twenty years old, arriving in agent work under the name AgentOps.

**The second table is the argument for the verifier.** Every scorer
averaged over the suite, baseline against unwired — four of yours and the
framework's `task completion (DeepEval)` beside them. Measured:

| scorer | baseline | tools unwired | Δ |
| --- | ---: | ---: | ---: |
| `passed` (your verifier, judge as fallback) | 0.92 | 0.23 | −0.69 |
| `used tools` | 0.92 | 0.00 | −0.92 |
| `efficiency` | 0.96 | 0.46 | −0.50 |
| `no repeats` | 1.00 | 1.00 | +0.00 |
| `task completion (DeepEval)` | 0.67 | 0.22 | −0.45 |

The framework's judge disagrees with the verifier in both directions: it
scores the working agent lower (0.67 against 0.92 — it penalises things
the scenarios count as success, with the task inferred from the opening),
and it drops less when the tools are unwired (−0.45 against −0.69 — an
agent that talks well about a claim it never looked up still reads as
partly complete). Neither is wrong; they measure different things, and only
`passed` measures what the product promised. That is why the framework's
column is *in* the report rather than *being* the report.

### Session 8b — the from-scratch build, for self-study

**Scenarios composed from atoms.** Four targets in the claims world (a lapsed
policy, a named exclusion, the excess, the authority limit) × five
capabilities (tool selection, tool chaining, refusal, injection, edge case)
× three personas (terse, precise, confused) → **ten composed scenarios** from
a dozen lines, each carrying its own check — `text`, `refuse`, or `judge` —
plus Marcus's three by hand. Add a target and every capability gets a new
test for free. These ten are the ones S8 loads from `data/scenarios.jsonl`.
(Seeded with `crc32`, not `hash()` — Python salts `hash()` per process, and
a suite whose targets change between runs changes its fingerprint, which
makes every baseline comparison refuse.)

**Five agents through the same scenarios**, scripted user, and the tables
are the lesson — measured, and identical on every run because nothing in
them calls a model. The useless agent scores zero and the user gives up. The
oracle looks things up and says the right words: 1.00 across. **The lying
agent says exactly the right words without calling a single tool** —
`reached goal (text)` 1.00 on every row, `used tools` and `passed` 0.00 on
every row, because the verifier asked what it did (including on the refusal
scenario: saying "senior handler" without having looked the policy up is
not a refusal, it is a guess). The repetitive agent passes and is caught
only by `no repeats` (0.00) and `efficiency` (0.67). And the agent that is
right *in its own words* has `used tools` 1.00 and `reached goal (text)`
0.00 — the keyword check failed a correct agent, which is the scorer's
failure, not the agent's. No framework ships a lying agent; the five are
the cheapest test of an eval you will write.

**One run is a sample of one.** The same scenario with a model-driven user,
five times, gives a distribution — and the number to report from it is
`pass^k`, the chance that *k* consecutive attempts all succeed:

| You say | `pass^5` really is |
| --- | ---: |
| "90% success" | ~0.59 |
| "80% success" | ~0.33 |
| "70% success" | ~0.17 |

An agent that passes 80% of the time fails two users in three within their
first five tasks. That is the number to put in an SLA, and it is why the
repeats are not optional. Measured on the withheld-laptop scenario with a
model user: **5 of 5 runs passed**, turns taken [2, 2, 2, 3, 3], `pass^5` =
1.00 — identical outcomes, different conversations (in one the simulated
claimant pushed back on being asked five things at once, and the agent
adapted). A property of this agent and this scenario, not a guarantee.

**Each task ends with the framework's version** — `ConversationalGolden`
for storage (nothing composes), `ConversationSimulator` for the loop and
the model user (single-turn callback, stopping decided by its controller),
`TaskCompletionMetric` for the judge (nothing for the state verifier),
nothing for the broken agents, `flaky=` instead of `pass^k` (a retry, not a
measurement) — and the Conclusion maps every function to
`helpers/simulation.py`, with an adopt-or-write column.

### The eval dashboard

These notebooks are `.py` files, which means they deploy:

```bash
uv run marimo run 04_Evals/sessions/S7_Practical_Evals.py --headless -p 8080
```

Read-only, source hidden, live scores. Point a colleague at the URL. **That is
how an eval becomes a shared language** rather than a thing engineers talk
about among themselves — and in Week 10 the same file becomes your production
observability console.

### Terms you'll meet

You do not need to know any of these in advance. This is what each one means
in one sentence, and where it comes up. Every term from every week is also
collected, alphabetically, in the repository's [`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it bites |
| --- | --- | --- |
| **Ground truth** | The answer a human judged correct, recorded before the system ran | S7 intro, and Question #1 |
| **Deterministic scorer** | A function comparing output to expected with no model involved | S7 Task 3 |
| **Exact match / F1** | Two ways of scoring partial correctness, and they disagree | S7 Task 3, and the ladder in Task 5 |
| **LLM-as-judge** | Using a model to score outputs a function cannot score | S7 Task 4 |
| **Separation and agreement** | The two halves of checking a judge — does it rank known-bad below known-good, and does it score the way a person would | S7 Task 4, the step everyone skips |
| **Chance floor** | What a metric would read if the thing it measures were absent; a number sitting on it is not a signal | S7 Bonus 1 |
| **Bootstrap interval** | Resample your results thousands of times to see how much the number would move with a different sample of the same size | S7 Task 5 |
| **Faithfulness** | What fraction of an answer's claims the retrieved context actually supports — in DeepEval's default, *does not contradict* | S7 Task 1, where DeepEval computes it |
| **Contextual precision / recall** | Of the chunks retrieved, how many were needed (precision); of the chunks needed, how many were retrieved (recall) — the retrieval half of a RAG score | S7 Task 1 |
| **G-Eval** | A judge that writes its own evaluation steps from a one-sentence criterion, then scores with them; DeepEval's rubric judge | S7 Tasks 1 and 6, S7 Bonus 1 |
| **Trajectory** | The full sequence of turns, tool calls with their arguments, and results — not just the final output | The premise of S8, drawn at the top; S8b Task 2 records it |
| **End-to-end / trajectory / component** | The three levels an agent can be scored at: the final answer, the path of tool calls, each call's arguments | S8's opener |
| **Scenario** | A goal plus information the user has but will not volunteer unless asked, with its own success check | S8 Task 1; composed from atoms in S8b Task 1 |
| **Simulated user** | A model playing a person with a goal, talking to your system so the test can run without a human | S8b Tasks 2 and 5; `helpers.simulation` |
| **Verifier** | A programmatic success check — tools called, fact stated, state changed — used wherever the outcome is checkable, before any judge | S8 Task 2 (the ledger check); S8b Task 3 |
| **Harness validation** | Testing the test — feeding it agents you know are broken and checking it notices | S8b Task 4 |
| **`pass^k`** | The chance that *k* consecutive attempts all succeed; what a user experiences, rather than a rate | S8b Task 5 |
| **Capability report** | Pass rate per capability rather than overall — the artifact a stakeholder reads, and the baseline a change is compared against | S8 Task 2 |
| **Regression** | A change that improves one thing and quietly breaks another — the reason the harness exists at all | Every later week |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions rarely use the words a
syllabus uses, and that costs people interviews. This week is advertised as
**eval harness development** — also **error analysis**.

This is the skill most consistently named outright, and often the one a posting
leads with. "Evaluation frameworks" in a job description means the thing you
built here.

**Back to Week 1** — your hand-written goldens are what your own system is
scored against, what the generated failures are made from, and what the two
prompts in S7's Loop B are compared on.

**Back to Week 2** — the prototyping/backtesting distinction is what makes some
of your synthetic data usable here and some of it not.

**Back to Week 3** — your retrieval endpoint is the first system to score, and
the ten questions you labelled are already the retrieval half of the harness.

**Forward to Week 5** — the five-minute demo goes live, and the critique goes
after the number. The decision row you wrote this week is the defence.

**Forward to Week 6** — every guardrail is re-run through `run.py`, and the
vulnerability you find in your own app becomes a permanent case.

**Forward to Week 7** — three memory tests join your scenarios, and "how much
does remembering the conversation buy" gets a measured answer.

**Forward to Week 8** — **the harness is the referee.** TC8 is "replace your
closed model with a fine-tuned open one and pass the same harness." That
sentence only means something because `use_case/evals/baseline.json` exists,
and `harness.compare()` refuses to compare runs on different cases.

**Forward to Week 10** — a sampled version of this harness runs on live
traffic, and the three "what you would swap" lines from Step 8 join the
final report's list of what it would take to run for real.

### Where the industry is headed

**Evaluation is becoming the moat.** Model quality is converging and getting
cheaper; what does not commoditise is knowing whether a system works on your
data, for your users, against your bar. Teams with a harness ship changes with
confidence; teams without one ship changes with hope, and eventually stop
shipping.

**Judges are improving faster than trust in them.** Model-based evaluation
keeps getting more accurate, and the calibration step keeps being skipped.
Expect the gap between "we have evals" and "we have evals we have checked" to
be a real quality differentiator between teams for some time.

**Simulation is becoming standard for agent development**, for the same reason
integration tests became standard: manual testing does not survive contact
with a release cadence. The unsolved operational problem is non-determinism —
a simulated user is a model, so the same scenario produces different
conversations on different runs, and the current answer is running each one
several times and reporting the distribution. More expensive, and considerably
more honest, than a single number.

**Online evaluation is the frontier.** Running the harness against a sample of
live traffic — continuously, not at release — is what catches silent quality
regression, and almost nobody does it. It is the one metric a monitoring
platform will not give you for free, and the one that catches the failure that
kills a product quietly.
