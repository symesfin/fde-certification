<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Technical Challenge 4</h1>
  <p><strong>The harness — a number you can defend, saved as a run, and a five-minute demo that leads with it.</strong></p>
</div>

---

## Overview

> **Read first:** [`use_case/CHARTER.md`](../../use_case/CHARTER.md). The
> harness scores the endpoint you shipped in Week 3 against the goldens you
> wrote in Week 1 and the questions you labelled in Week 3. If any of those is
> still the template, finish that week.

Until now every claim about your app has been *"it seems better."* This week
turns that into a number — one with a denominator, an interval, a baseline it
is measured against, and a saved run that the next four weeks are held to.
Then you put the number in front of a real person and find out whether they
can act on it.

**This is the week your app becomes measurable.** Week 3 gave you a thing a
person could use. This one gives you the instrument that says whether the next
change helped — and the question this week asks is not *what did it score*, it
is:

> **"What would it take to convince you that number is wrong?"**

The harness is a few files. **The test set, the baselines and the interval
are the assignment** — and the conclusions you can defend from them.

> 💡 **You already know enough to be dangerous.** Session 7 had you run the
> framework, write the harness it is made of, score with functions before
> models, check a judge before believing it, generate the failures your
> goldens did not contain, put an interval on the result, and compare two
> prompts on every scorer. Session 8 had you simulate a user, score the whole
> conversation, catch an agent that said the right words without checking,
> and see why one run is a sample of one. This is where you point all of it at
> your own endpoint.
>
> ⏰ **This challenge is due before Week 5's session, and Step 7's demo needs
> a real person's calendar.** Book that person first.

<table>
  <tr>
    <td width="120"><strong>Outcome</strong></td>
    <td>A test set you prepared, an eval harness in your repo that runs on demand — model-free scorers, a judge with its separation shown, both dumb baselines, generated failures, scenarios if your app holds a conversation — and a saved baseline run at <code>use_case/evals/baseline.json</code> that Weeks 5–8 are measured against, with conclusions a stakeholder can act on. Plus a five-minute demo that leads with the number.</td>
  </tr>
  <tr>
    <td><strong>Tools</strong></td>
    <td>Python, LiteLLM (the judge and the simulated user), <code>helpers/harness.py</code> and <code>helpers/judge.py</code> from this repo, Gradio, Docker. DeepEval for the standard metrics and as the judge if you prefer <code>GEval</code> to a hand prompt — checked like any other.</td>
  </tr>
  <tr>
    <td><strong>Due</strong></td>
    <td>End of the week. Post your repo link in the Maven Community. <strong>The demo is presented live in Week 5.</strong></td>
  </tr>
  <tr>
    <td><strong>Before you start</strong></td>
    <td>TC1's <code>use_case/evals/golden.jsonl</code>, TC3's <code>use_case/evals/retrieval.jsonl</code>, and TC3's endpoint running — the harness needs something to score.</td>
  </tr>
</table>

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
| 6 | What right-in-different-words and right-words-without-checking answers look like for your agent, and which of your checks would tell them apart | S8 |
| 7 | Which `pass^k` you would put in an SLA, and how many repeats per scenario you can afford on every commit versus nightly | S8 |
| 8 | Whether your success condition can be stated as an assertion about state rather than about text — and what that would let you stop scoring | S8 |

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

## 📖 Official documentation

Everything this challenge uses, from the people who maintain it.

| Tool | What you use it for here | Docs |
| --- | --- | --- |
| LiteLLM | the judge call and the simulated user — a *different* model from the one being scored | [docs.litellm.ai](https://docs.litellm.ai/) |
| `helpers/harness.py` | `run`, `save`, `load`, `compare`, `gate` — the run as an artifact with a fingerprint | [`helpers/harness.py`](../../helpers/harness.py) |
| `helpers/judge.py` | `Judge` — `score()` raises until `calibrate()` has passed | [`helpers/judge.py`](../../helpers/judge.py) |
| Gradio | the endpoint under test, and the `@app.api feedback` route from Session 7 if you add one | [gradio.app/docs](https://www.gradio.app/docs) |
| DeepEval | `GEval` as the judge in Step 3 if you prefer it to a hand prompt, and the RAG metrics over your retrieved context if Step 2's scorers do not cover it — calibrated exactly like a hand-written judge | [deepeval.com — metrics](https://deepeval.com/docs/metrics-introduction) |
| τ²-bench | a reward function that has survived public scrutiny, to check your scorer against | [github.com/sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench) |

---

## Setting Expectations

**Budget six to eight hours**, spread across the week — and the week is
short: the challenge is due before Week 5's session. The trace pass is slow
and decides everything after it; the scorers and the baselines are an
evening; the scenarios, if you need them, are mostly waiting for a model
user.

| Step | What it is | Rough time |
| :---: | --- | --- |
| 7 | **Book the demo rehearsal** with a real person — do this first; the rest can wait, their calendar cannot | 5 min today, 1 hr later |
| 1 | Read fifty traces, write the taxonomy; hand-score twenty if you will check agreement | 1–2 hrs |
| 2 | Model-free scorers, echo and oracle | 1–2 hrs |
| 3 | Check the judge — separation required, agreement recommended | 30 min, plus a few dozen model calls |
| 4 | Generate the failures you do not have | 45 min — Session 7's Task 5 writes the first version for you |
| 5 | Scenarios, one a refusal, with repeats — *if your app holds a conversation* | 1–2 hrs, mostly waiting |
| 6 | The baseline: interval, saved run, decision row | 45 min |
| 8 | Share: bring it to work | 30 min |

> **Do Step 1 before anything else.** Every scorer you write should trace back
> to a line in `failures.md`; a scorer written before the taxonomy is one you
> invented because it was easy to compute. And the person who watches your
> demo in Week 5 will ask the question your rehearsal partner asked first.

---

## What you are building

| File | Role |
| --- | --- |
| `use_case/evals/failures.md` | What goes wrong, ranked, with counts. **Every scorer traces back to a line here** |
| `use_case/evals/human_scores.jsonl` | Twenty outputs you scored by hand — pass or fail, and why. The judge is checked against these |
| `use_case/evals/harness.py` | Your scorers, `run_eval`, `report`, `bootstrap_ci` — the Session 7 code, over your cases |
| `use_case/evals/synthetic.jsonl` | The failures you generated, each with its label and the failure mode it exercises |
| `use_case/evals/scenarios.py` | Three multi-turn scenarios — goal, secret, success, `must_not` |
| `use_case/evals/run.py` | Points the harness at your endpoint and prints the report. **`python use_case/evals/run.py` is the whole interface** |
| `use_case/evals/baseline.json` | The run itself, saved with `helpers.harness.save`. **Weeks 5–8 are measured against this file** |
| `use_case/decisions.md` | The eval row: the headline number, what it does not cover, what would change your mind |
| `CLAUDE.md` | The instructions Claude Code reads before it touches anything |

> **What is already written for you, and what is not.** `helpers/harness.py`
> turns a run into an artifact — `run`, `save`, `load`, `compare` — and
> `compare()` refuses when the case set behind two runs differs, which is the
> feature Week 8 relies on. `helpers/judge.py` is a judge whose `score()`
> raises until `calibrate()` has passed. Use both for plumbing. **The scorers,
> the rubric, the twenty hand scores, the scenarios and the refusal case are
> yours** — they are the written-down definition of "correct" for your
> problem, and nothing in `helpers/` knows what that is.

`CLAUDE.md` puts Claude Code into **instructor mode** for this directory: it
will explain, debug, and review, and it will decline to write your scorers,
your rubric, your hand scores or your scenarios. That is deliberate. A scorer
looks like a utility function, so it feels harmless to have it written. It is
the whole assignment.

---

## Step 1 — Read fifty traces, write the taxonomy, hand-score twenty

Session 7 opened with the claim that ground truth already exists at your
company — in work a human already did and already judged. This step is where
you go and find it.

**Read fifty real traces** from your endpoint, or from the process it
replaces. One sentence per failure. Then group the sentences and count them.
That is `use_case/evals/failures.md`: what goes wrong, ranked by how often, with
the count next to each line. Session 7's claims analyst got four sentences
from his fifty — the wrong policy wording, a lapsed policy, a missed exclusion,
the wrong excess — and the second one became a scorer with no model in it.
It takes an afternoon and it decides which scorers
are worth writing — a scorer that does not trace back to a line in this file is
one you wrote because it was easy to compute.

Then **score twenty outputs by hand.** Pass or fail, and *why*, before any
model has an opinion. This is the calibration set for Step 3 and it is the
single highest-value hour this week. It also tends to reveal that your own
criteria are less consistent than you assumed — which is the real lesson, and
worth a line in `failures.md`.

```json
{"input": "...", "actual": "...", "pass": true, "why": "one sentence — what made it pass or fail"}
```

> **Session 7's Bonus stratified-sample point applies to you.** A random twenty from
> a system that is right 90% of the time gives you eighteen passes and two
> fails, and tells you almost nothing about whether a judge catches a bad one.
> Pick your twenty so that at least a third are failures — from `failures.md`,
> which is why it comes first.

### ✅ Deliverables

1. **`use_case/evals/failures.md`** — the taxonomy, ranked, with counts, and
   one line saying how many of the fifty traces were failures at all.
2. **`use_case/evals/human_scores.jsonl`** — twenty lines, at least a third of
   them fails, each with a `why`.

---

## Step 2 — Model-free scorers, echo and oracle

**At least three scorers that need no model**, in `use_case/evals/harness.py`,
each with a comment naming the `failures.md` line it catches. Exact match,
token F1, required substrings, decline detection, a parse check, an allowed
set, a length cap, whether the named sources exist — whichever fit *your*
output. Session 7's four run unchanged if your output is text; if it is JSON,
the scorer that checks it parses is the one that catches most of your failures
and it is six lines.

Model-free scorers are free, instant and deterministic, and they catch more
than people expect. Write every one that a line in the taxonomy permits before
you write a single judge prompt.

Then **run both dumb baselines** through the same `run_eval`:

| Baseline | What it does | What it proves |
| --- | --- | --- |
| **Echo** | returns the input | If your endpoint does not beat this, something is broken upstream |
| **Oracle** | returns the golden output | **If this does not score 1.0 on every scorer, the scorer is wrong** — and you have just saved yourself Week 8 |

The oracle is not a formality. Session 7's `contains_required` and Session 8's
keyword success check both look correct and both fail an answer that is right
in different words. The oracle catches the first kind. Step 5 catches the
second.

### ✅ Deliverables

1. **Three or more model-free scorers** in `harness.py`, each commented with
   the `failures.md` line it covers.
2. **The echo / oracle / your-endpoint table** in your README — one row per
   system, one column per scorer — with the oracle at 1.0 on every column.

---

## Step 3 — Check the judge: separation required, agreement recommended

For the lines in `failures.md` a function cannot catch — is this grounded, does
it answer the question that was asked, did it hedge where it should have
committed — you need a judge. **A judge is a scorer you are not allowed to
trust until it has proved itself**, and proving it means two tests, not one:

| Test | Question | How |
| --- | --- | --- |
| **Separation** | Does it score known-bad below known-good? | `helpers.judge.Judge(CFG).calibrate(goldens)` — scores each golden output and an obviously wrong answer, and passes only if the two separate. A DeepEval `GEval` metric counts as "the judge" too; wrap `metric.measure()` as a scorer and put it through the same two tests |
| **Agreement** | Does it score the way *a human* would? | Run it over Step 1's twenty hand scores. Count how often it agrees with your pass/fail. Compare that to the chance floor Session 7 computed — a judge that agrees with you 60% of the time on a two-way call is guessing |

Separation is required and costs nothing new — the echo and oracle outputs
from Step 2 are known-bad and known-good. **Agreement is recommended, not
graded**, because it needs the twenty hand scores and the week is short; but
it is the half your reported number actually depends on, and if you skip
it, say so in the decision row. If the judge fails either test, **say so, do
not use it, and score only what your functions can score** — a number from
an unchecked judge is worse than no number, because it stops the
conversation.

Three things Session 7 showed you that decide whether this passes:

- **Use a different model to judge than the one being scored.** `Judge(CFG,
  model=...)` exists for this, and on the framework side the judge model is
  whatever you pass to the metric — Session 7's fifteen-line `NotebookJudge`
  is the pattern, with a different model name. A model grading its own output is generous
  about its own habits — and a framework's judge defaults to the model that
  answered unless you set it.
- **Narrow the question.** One checkable property per rubric, with an example
  of a 0 and a 1. A rubric that asks for "quality" gets 0.9 for everything.
- **Check whether the dimension is judgeable at all.** Session 7's Bonus
  calibration task showed trained annotators agreeing with each other no more
  often than chance on some dimensions. If two people at your firm would not agree on it,
  neither will you and the judge — score something objective instead, and
  write down that you stopped.

### ✅ Deliverables

1. **The rubric**, in `harness.py`, for one named line of `failures.md` — a
   hand-written prompt or a `GEval` criterion, either is fine; both go
   through the same two tests.
2. **The separation numbers** in your README — the judge's mean on the echo
   outputs and on the oracle outputs — and, if you ran it, the agreement rate
   against your twenty with the chance floor next to it.
3. **One line saying whether you used it.** *"Separation 0.1 / 0.9, agreement
   0.85 on 20 — used"*, *"Separation 0.2 / 0.9, agreement not checked — used
   for the judge column only, not the headline"*, or *"Agreement 0.60 — not
   used; scored grounding with `contains_required` instead."* Any of the three
   is a good result, well recorded.

---

## Step 4 — Generate the failures you do not have

Step 1 probably told you that most of your traces are fine. That is good news
for your users and bad news for your eval: a random sample that contains one
or two failures cannot measure a detector, because there is nothing to detect.

**Take outputs you consider correct and break them in named ways** — Session
7's four kinds, or your own: a changed number, a reversed claim, a swapped
entity, an unsupported addition, a dropped source, a decline where an answer
was required. Each one is a labelled test case, and **the label was free,
because you know what you broke.** Write them to `use_case/evals/synthetic.jsonl`
with the failure mode on every line, and run every scorer from Steps 2 and 3
over them.

**Report two counts side by side**: how many failures your fifty real traces
contained, and how many you generated. If the first number is small, say so —
it is the reason the second exists, and a reviewer who sees only the generated
set will assume your system fails more than it does.

> **Make at least a few of them hard.** Swap a name for a plausible one rather
> than an absurd one; change a number by 10% rather than an order of
> magnitude. The gap between your detector's accuracy on the easy corruptions
> and the hard ones is how much the synthetic set was flattering you.

### ✅ Deliverables

1. **`use_case/evals/synthetic.jsonl`** — each line an input, the corrupted
   output, the original, and the failure mode.
2. **The detection table** in your README — per failure mode, what fraction
   each scorer caught — with the natural count and the generated count above
   it.

---

## Step 5 — Scenarios, one a refusal, with repeats *(if your app holds a conversation)*

> **Optional for a single-turn endpoint; not optional for anything that holds
> a conversation.** Session 8's lying agent said exactly the right words
> without calling a single tool and passed every text check. If your app
> talks to people across turns, or calls tools, a single-turn eval will pass
> that agent too, and this step is where you catch it. If your endpoint
> answers one question and stops, skip to Step 6 and say so in the decision
> row.

Session 8 showed conversations that all ended with the right answer and
were all failures. To see those you score the **trajectory**, and a
trajectory needs a user, so you simulate one.

**Write three scenarios** in `use_case/evals/scenarios.py`, each a goal plus
something the user knows and will not volunteer until asked — Session 8's
`Scenario` shape, with `knows`, `success` and `must_not`. The windscreen, the
stolen laptop and the total loss in that file are one insurer's three; yours
are the same shape with your own values:

1. **The thing it must do** — your most common real request.
2. **The thing it must ask about** — the user withholds something essential,
   so you find out whether your agent asks or assumes.
3. **The thing it must refuse.** Every system has one. Deciding what yours is
   is a judgement about your domain and your risk, and it is the case that keeps
   you employed.

Run them with the scripted user first, then with a model user. **If the user
is a model, run each scenario at least three times and report the spread** —
turns taken, `reached goal`, and `pass^k` — because one run of a
non-deterministic user is a sample of one. Session 8's table is the shape:
three scenarios × three to five repeats, minutes and a few cents.

> **Your system does not have to be multi-turn to be scored this way.** If
> what you have is a single-turn endpoint, wrap it as `agent(traj)` and let it
> answer the latest message and ignore the history. That is a legitimate
> baseline, not a cheat, and it produces the most useful number in the
> section: *how much does remembering the conversation actually buy?* Plenty
> of scenarios are won without it, and finding out which is exactly the kind of
> thing that stops you building a memory layer in Week 7 that you did not need.

Two checks before you believe any of it, both from Session 8:

- **Test the simulated user against an oracle agent.** A user that cannot be
  satisfied by a correct answer is broken and will fail everything you point
  it at.
- **Test the success check against a paraphrasing agent.** Session 8's
  `user_is_satisfied` was a keyword match, and an agent that answered every
  scenario correctly in its own words scored zero — and the oracle did not
  reveal it, because the oracle was written from the keyword. If your success
  check is a string match, decide now what it does with a right answer in
  different words.

### ✅ Deliverables

1. **`use_case/evals/scenarios.py`** — three scenarios, one a refusal, with
   `must_not` filled in on all three.
2. **The trajectory table** in your README — per scenario, per repeat, every
   trajectory scorer, turns, and how it ended — with `pass^k` underneath.
3. **One transcript, read in full**, and one sentence on what you found in it
   that no scorer would have caught. That sentence is your next scorer.

---

## Step 6 — The baseline: interval, saved run, decision row

Everything above produces numbers. This step turns one of them into **the
number** — the one Weeks 5 through 8 are held to — and makes it beatable in a
way you can detect.

**Pick the headline scorer.** One, from Step 2 or a Step 3 judge that passed
both halves. It should be the one that traces to the top line of `failures.md`.

**Put an interval on it.** Session 7's `bootstrap_ci` is eight lines. *"0.88,
95% CI [0.79, 0.95]"* is a claim; *"0.88"* invites a comparison your data does
not support. Session 7's Task 5 also showed you what size eval set a
five-point improvement needs before the interval clears zero — if yours is
smaller, say so in the decision row, because it means Week 8 cannot show a
small win no matter how real it is.

**Save the run, not the number:**

```python
from helpers import harness
report = harness.run(cases, my_endpoint, SCORERS, name="week4-baseline")
harness.save(report, "use_case/evals/baseline.json")
print(harness.compare(harness.load("use_case/evals/baseline.json"), report))
```

The last line must report PASS — proof the artifact loads and compares. A
number typed into prose cannot be compared by anything and stops being true
the moment you add a golden example; the saved run carries a fingerprint of
the cases and scorers behind it, so `compare()` will **refuse** rather than let
you claim a win that came from changing the suite. That refusal is the
feature, and Week 8 depends on it.

Then the row in [`use_case/decisions.md`](../../use_case/decisions.md):

| Field | What it means |
| --- | --- |
| **Decision** | The headline scorer, its value and its interval, on how many cases |
| **What you rejected** | The scorers you did not make the headline — and the judge, if it failed calibration |
| **Why** | Which `failures.md` line it covers, and what it does not cover — *"40 back-tested cases from last quarter; says nothing about volume spikes"* |
| **What would change your mind** | The condition under which you would swap the headline — a judge that passes agreement, a slice that carries all the failures, an interval that finally clears zero |

### ✅ Deliverables

1. **`use_case/evals/baseline.json`**, committed, and the `compare()` PASS
   line in your README. If a framework metric is one of your scorers, it is
   in that run like any other scorer, wrapped as `(actual, case) -> 0..1`;
   Session 7's Task 6 shows the wrapper.
2. **The headline number with its interval**, in the decision row, with
   the case count and what it does not cover.
3. **`python use_case/evals/run.py`** producing the report from a clean
   checkout — this is what Week 6 runs after every guardrail and Week 8 runs
   against the fine-tuned model.

---

## 🧯 If it's blocked

### "My judge scores everything 0.9"

It is agreeing rather than judging. Narrow the question to one checkable
property, give it examples of a 0 and a 1, or ask for a binary decision and
average the decisions. Session 7's rubric does the last of these.

### "My judge disagrees with me and I cannot fix it"

Check whether the thing you are asking about is objective. On dimensions where
trained annotators agree with each other no more often than chance, a judge
that matches you that often is performing at human level. Score the objective
properties and treat the rest as signals — and write in the decision row that
you stopped.

### "My scores are all 1.0"

Your cases are too easy, and they are too easy because you wrote them from
what your system already does. Step 4 exists for this: add the case that
worries you, and the corruptions that exercise it.

### "My improvement is tiny and I cannot tell if it is real"

Bootstrap it. If the interval on the difference includes zero, the honest
report is "we cannot tell yet" — a legitimate result, and a much better look
than a claim that falls over when someone adds ten cases.

### "I don't have ground truth"

You almost certainly do — Session 7's opening pages and Question #1. Look for work that was already
done and already judged by a human: closed tickets, approved drafts, reviewed
summaries. Fifty of those is Step 1.

### "The simulated user never gets satisfied"

Test it against the oracle agent first. A simulator that cannot be satisfied by
a correct answer is broken and will fail everything you point it at.

### "My agent is right and scores zero"

Look at how success is detected before you look at the agent. If it is a
keyword check, an agent that answers correctly in different words fails it —
and the oracle does not reveal that, because the oracle was written from the
keyword. That is a broken scorer, not a broken agent.

### "`compare()` refuses"

It is supposed to. The case set or the scorer names changed since the baseline
was saved. Either re-run the baseline against the current suite, or pass
`require_same_cases=False` because you grew the suite on purpose — but do not
report the two numbers as though one beat the other.

---

## 👥 Step 7 — The five-minute demo, rehearsed with a real person

The demo is presented live in Week 5, to stakeholder-style critique. Before
that, **run it once for someone real** — the person from your charter, or the
person who would fund the seat — and write down what they asked.

Five minutes, and the minutes are not negotiable:

| Minute | What |
| --- | --- |
| 0–1 | **The problem.** One person, one workflow, what it costs today. No architecture. |
| 1–2 | **The demo.** The thing running. Not slides of the thing running. |
| 2–3.5 | **The numbers.** Step 6's headline with its interval, on what data, and what it does not prove — in the units the person in the room already measures, the way Session 7 turned agreement into an overturn rate. |
| 3.5–5 | **What is next**, and what you need from whom. |

What earns a good critique: lead with the problem, not the stack — nobody funds
a vector database. **Show one failure** — a demo with no failures is a demo
nobody believes, and volunteering it is what makes the successes credible.
Say what the number does not cover. Name the person you spoke to — every
`stakeholders.md` row since Week 1 is where this starts paying.

What gets picked apart: scores with no baseline, a judge nobody calibrated,
"it works well" without a denominator, the happy path only, and an eval set
you wrote *after* building the thing, scored against data you also chose.

**Ask your rehearsal audience three things, in this order:**

1. *"What would you do differently on Monday if this number is right?"* — if
   the answer is "nothing", the number is not the one they need.
2. *"What would it take to convince you it is wrong?"* — the question this
   whole week asks, from the other side.
3. *"What did you expect to see that you didn't?"*

> **Your agent will help you tighten this and will not invent it.** Ask it to
> time the sections, to cut the stack slide, or to turn messy notes into three
> findings. It will decline to write the feedback itself, because it was not
> in the room.

### ✅ Deliverables

1. **A row in [`use_case/stakeholders.md`](../../use_case/stakeholders.md)** —
   who you rehearsed with by role, what you asked, what you learned, and the
   follow-up.
2. **A line in [`use_case/decisions.md`](../../use_case/decisions.md)** naming
   one thing their questions changed — a scorer added, the headline swapped,
   a failure you now show. If nothing changed, write that and say why.
3. **The demo, timed**, ready for Week 5.

---

## 📤 Step 8 — Share: bring it to work

This week's pattern is *score before you believe, calibrate before you score,
and save the run so the next change is measured against it*. Somewhere at your
company there is a model, a vendor tool or a process whose quality nobody has
measured — it "works" because nobody wrote down what working means. This step
is where you write down which one, and what this week's harness would be
worth applied to it.

### ✅ Deliverables

1. **Which model, vendor tool or process at work this harness is for**, one
   line under `## Bring it to work` in your README. *"The summarisation
   vendor's output is spot-checked by whoever has time, and nobody knows the
   failure rate"* names one; *"AI quality"* does not.
2. **What you would swap** — three lines under the same heading, one each for
   the **data** (which fifty traces at work, and who already judged them), the
   **model or endpoint** (which model judges, and whether the traces may leave
   the network), and the **access or approval** you would need to ask for —
   with the judge calls per `run.py` next to it, marked *measured*, because
   that is what decides whether it runs on every commit or nightly. This is
   what turns the harness into the version your team could run.
3. **Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)**,
   and comments on at least two other students' submissions after the deadline.

---

## What this challenge deposits for later

| What you write | Where it lives | When it comes back |
| --- | --- | --- |
| The saved baseline run | `use_case/evals/baseline.json` | **Week 6** re-runs it after every guardrail. **Week 8** — `harness.compare()` against the fine-tuned model is the pass/fail. **Week 9** gates the deploy on it. **Week 10** runs a sampled version on live traffic. |
| The harness and `run.py` | `use_case/evals/` | Every later week's "did this break anything" is `python use_case/evals/run.py`. |
| The failure taxonomy | `use_case/evals/failures.md` | **Week 6** — the winning attack becomes a new line. **Week 7** — the memory tests trace to it. |
| The scenarios and trajectory scorers, if you built them | `use_case/evals/scenarios.py` | **Week 6** — injection regression testing is trajectory scoring. **Week 7** — validating a loop is the same discipline. Both show the shape if you skipped Step 5. |
| The generated failures | `use_case/evals/synthetic.jsonl` | **Week 6** — the test set for whether a guardrail catches anything. |
| The eval decision | `use_case/decisions.md` | **Week 5**, out loud, when the critique goes after the number. |
| The five-minute demo | Your head, timed | **Week 5**, live. |
| The three swap lines | Your README, `## Bring it to work` | **Week 10** — the final report's "what it would take to run" section. |

---

## Your Final Submission

Please include the following in your final submission:

1. **A public link to your repo**, containing:
   1. **A five-minute-or-less Loom video** — the demo itself, as rehearsed,
      leading with the problem and showing one failure.
   2. **A written document addressing each deliverable above** — the
      taxonomy and hand scores, the scorer/baseline table with the oracle at
      1.0, both calibration halves and whether you used the judge, the
      detection table with natural and generated counts, the trajectory table
      with `pass^k`, the headline number with its interval and the `compare()`
      PASS, the decision row, the Step 7 answers, and the swap lines.
   3. **All relevant code**, committed and pushed — `use_case/evals/` runs
      from a clean checkout. **Never the data.**
2. **Your `use_case/` directory updated** — `evals/` with `baseline.json`
   committed, and the new rows in `decisions.md` and `stakeholders.md`.

### How to submit

1. **Post your repo link** in
   [our community on Maven](https://bit.ly/fde1-maven-community). That is where
   every technical challenge is submitted.
2. **Push your `use_case/` updates to that repo** before you post, so the link
   shows the current state of your project rather than last week's.
3. **After the deadline, comment on at least two other students' submissions.**
   Read their decision row and their calibration numbers, and leave something
   specific — a scorer their oracle would not have caught, a dimension you
   think is not judgeable, a condition in "what would change your mind" you
   would push on.

> **Never commit real company data.** `use_case/data/` is gitignored for this
> reason, and the fifty traces you read in Step 1 stay where you found them —
> `failures.md` carries the counts, not the traces. `human_scores.jsonl` and
> `synthetic.jsonl` are built from your synthetic data or anonymised inputs.
> Do not post screenshots of internal infrastructure, hostnames, or anything
> your firm would consider confidential.

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
| 6 | What right-in-different-words and right-words-without-checking answers look like for your agent, and which of your checks would tell them apart | S8 |
| 7 | Which `pass^k` you would put in an SLA, and how many repeats per scenario you can afford on every commit versus nightly | S8 |
| 8 | Whether your success condition can be stated as an assertion about state rather than about text — and what that would let you stop scoring | S8 |

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

## Where this goes next

| Week | What it adds to this harness |
| --- | --- |
| 5 | Tools, skills, MCP — the demo goes live, and the critique goes after the number. |
| 6 | Guardrails — every guardrail is re-run through `run.py`; the winning attack becomes a permanent case and a new line in `failures.md`. |
| 7 | Memory — three memory tests join the scenarios, and "how much does remembering buy" gets its answer. |
| 8 | Fine-tuning — `harness.compare(baseline, finetuned)` is the pass/fail. The baseline you saved this week is the bar. |
| 9 | Infrastructure — the harness gates the deploy. |
| 10 | Production — a sampled version runs on live traffic, and every week's swap lines become the final report's "what it would take to run" section. |

Everything after this week assumes your app has a number, an interval, and a
saved run to be measured against.
