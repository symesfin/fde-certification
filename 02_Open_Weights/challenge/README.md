<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Technical Challenge 2</h1>
  <p><strong>Generate the data you are not allowed to have yet — and say what it can prove.</strong></p>
</div>

---

## Overview

> **Read first:** [`use_case/CHARTER.md`](../../use_case/CHARTER.md) and your
> five golden examples in [`use_case/evals/`](../../use_case/evals/). This
> challenge generates *from* them. If they are still templates, finish TC1.

Your real data is probably still behind an approval, a privacy review, or a
network path that does not exist from your laptop. That block routinely lasts
weeks, and it lands before you have anything built that would justify
expediting it.

This week you remove the block. You will generate a synthetic dataset from the
five examples you wrote by hand, throw most of it away on purpose, and write
the one document that stops the survivors from being misused:

> **"What can this data prove, and what can it not?"**

The generation is a prompt and a loop. **The datasheet is the assignment.**

> 💡 **You already know enough to be dangerous.** Session 3 gave you every
> sampler a model uses and a model of your own to run them on. Session 4 gave
> you the loop: axes, generation, dedupe, validation, leak check, datasheet.
> This is where you run it on your own problem.

<table>
  <tr>
    <td width="120"><strong>Outcome</strong></td>
    <td>A synthetic dataset covering your use case's real variation, the honest counts behind it, and a datasheet that says what it is allowed to prove.</td>
  </tr>
  <tr>
    <td><strong>Tools</strong></td>
    <td>LiteLLM, pydantic, numpy, and a model — hosted or local.</td>
  </tr>
  <tr>
    <td><strong>Due</strong></td>
    <td>End of the week. Post your repo link in the Maven Community.</td>
  </tr>
  <tr>
    <td><strong>Before you start</strong></td>
    <td>TC1 finished: a charter with no template text left, and five hand-written golden examples. Session 4's first cell refuses to run without them.</td>
  </tr>
</table>

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

## 📖 Official documentation

Everything this challenge uses, from the people who maintain it.

| Tool | What you use it for here | Docs |
| --- | --- | --- |
| LiteLLM | the generation call, whichever provider is behind it | [docs.litellm.ai](https://docs.litellm.ai/) |
| pydantic | the schema from your charter, as the validator | [pydantic.dev/docs](https://pydantic.dev/docs/validation/latest/get-started/) |
| Hugging Face Hub | model cards and licences, if you generate locally | [huggingface.co/docs/hub](https://huggingface.co/docs/hub/index) |
| Ollama | an OpenAI-compatible local server, for Step 5 | [docs.ollama.com](https://docs.ollama.com/) |

---

## Setting Expectations

**Budget four to six hours**, spread across the week. Generation runs take
minutes each and you will run several; reading fifty rows properly takes longer
than you think.

| Step | What it is | Rough time |
| :---: | --- | --- |
| 1 | Name your variation axes | 45 min |
| 2 | Generate, dedupe, validate | 1 hr, mostly waiting |
| 3 | Leak check, then read fifty rows | 45 min |
| 4 | Write the datasheet | 45 min |
| 5 | Run it on a model you own *(optional)* | 30 min |
| 6 | Show it to someone who knows the real data | 30 min, plus their calendar |
| 7 | Share: bring it to work | 30 min |

> **Send the Step 6 message today.** The person who knows what the real inputs
> look like is the only one who can tell you whether your fake ones are
> plausible, and they are not waiting for you.

---

## What you are building

| File | Role |
| --- | --- |
| Your axes, in your repo | The coverage decision. A dict; the thinking is the deliverable |
| `use_case/data/synthetic_v1.jsonl` | The dataset. **Gitignored.** Weeks 3, 4 and 8 all read it |
| `use_case/data/DATASHEET.md` | What the data can and cannot prove. **Committed** |
| `CLAUDE.md` | The instructions Claude Code reads before it touches anything |

> Session 4's loop is packaged as `helpers/sdg.py`. `generate()` returns an
> `SDGReport` carrying every count this challenge asks for, plus
> `failed_combos`, so a dead axis point cannot vanish into a single "errors"
> number. Use it or match it — the counts are what is graded, not the loop.

`CLAUDE.md` puts Claude Code into **instructor mode** for this directory: it
will explain, debug, and review, and it will decline to write your axes or your
datasheet. That is deliberate. The axes look like a config dict, so it feels
harmless to have them filled in. They are the dataset's coverage, and a person
who did not choose them cannot say what their data misses.

---

## Step 1 — Name your variation axes

Not "generate 200 more like these" — that gives you 200 paraphrases of five
things, and it will hide every failure your system has.

Name the dimensions along which **your** inputs actually vary. Session 4 gave
you four keys — persona, length, difficulty, quality — with values written for
one worker's incident records. The keys travel; the values do not. Replace at
least two with axes specific to your domain, and treat her values as a worked
example of *how specific* a value has to be, not as a template. If you cannot
name a domain-specific axis, you do not yet understand the variation, and
that is worth discovering now rather than in front of a user.

**One axis value is mandatory: an input where the right answer is to decline.**
A dataset with no declines cannot tell you whether your system is calibrated or
just confident, and you will not find that out until it matters.

> **Ask your agent to argue with your axes**, not to write them. A good prompt:
> *"Here are my four axes. Which two could be collapsed into one, and what
> variation in my real inputs does none of them capture?"*

### ✅ Deliverables

1. **Your axes, committed in your repo** — a dict or a table, with a one-line
   reason per axis saying what real variation it covers.
2. **The `Variation axes` table in `use_case/data/DATASHEET.md`** filled in
   from the same list. The two must match.

---

## Step 2 — Generate, dedupe, validate

In that order, and report the number that survives all three.

The honest size of your dataset is not how many rows you generated. It is how
many were structurally distinct *and* passed your schema. That number is
usually much smaller than the first one, and quoting the first is how teams end
up believing they tested something they did not.

Three settings decide what you get, and the notebooks gave you the arithmetic
for all three:

| Setting | What it decides | Where you measured it |
| --- | --- | --- |
| Temperature | How much of the tail is live per token | S3 Task 3 — the 95%-mass count |
| Top-p, not top-k | Whether the candidate set adapts to the model's confidence across different prompts | S3 Task 5 — the candidate-set table |
| Dedupe threshold | What counts as "the same row twice" | S4 Task 4 — the *what got dropped* table |

Run every combination, not the sample the session used. Then watch the
counters: an unparseable line means the model wrote badly; a **dead combination**
means a point in your axis space produced nothing, and your coverage is smaller
than you think.

**Optional, strongly recommended:** run the same generation against a
**larger** local model than Session 3's 350M default, and note where its
temperature ceiling sits by comparison. Write both ceilings, with the model
names and the hardware, in `use_case/decisions.md`.

### ✅ Deliverables

1. **Four counts in the datasheet:** generated, after dedupe, schema-valid, and
   dead combinations. Not one "errors" number.
2. **The settings you used** — temperature, top-p, dedupe threshold — recorded
   next to the counts, so someone can reproduce the run.
3. **One row in `use_case/decisions.md`** for the dedupe threshold: what you
   chose, what you rejected, and what in the dropped table would change your
   mind.

---

## Step 3 — Do the leak check, then read fifty rows yourself

The automated check finds names, companies, and identifiers. It cannot find a
distinctive scenario, an unusual document structure, or a category that only
one team or one account in your company would ever produce.

**Read fifty rows before you commit anything.** Against these four:

- [ ] No real names, companies, or identifiers survived.
- [ ] No distinctive internal formats — reference schemes, code layouts.
- [ ] Rare categories were *generated*, not copied. A category with one real
      instance is identifying even with the name changed.
- [ ] Nothing here would embarrass you in a public repo.

The strongest protection is procedural: **generate from the schema and a
written description, not from real records.** You lose a little fidelity and
you remove the leak path entirely. For prototyping data, that trade is almost
always right.

### ✅ Deliverables

1. **The `Leakage check` section of the datasheet**, every box ticked by a
   person, not a script.
2. **What you removed, and why** — one line per row you deleted after reading.
   If you removed nothing, say what you looked for.

---

## Step 4 — Write the datasheet

[`use_case/data/DATASHEET.md`](../../use_case/data/DATASHEET.md). The data is
gitignored; this file is not. It is the artifact a colleague, an auditor, or you
in six weeks will read instead of the data.

The section that matters is **"What it cannot validate"**, and it should be
uncomfortable to write. Synthetic data cannot tell you about real distribution,
real frequency, or failure modes you did not think to generate. Say so in your
own words, specifically, about your own data.

Start from the distinction Session 4 opened with: is this **prototyping** data
(inputs that look like yours, no labels anyone verified) or **backtesting**
data (inputs with the output you would accept)? Whichever it is, the datasheet
says so, and the "cannot validate" section follows from the answer.

> Six weeks from now you will have forgotten how this data was made. The
> datasheet is what stops you — or a colleague, or an auditor — from believing
> it proves something it does not.

**Two more lines, and they are the ones that get read later.**

The first is about the data's *other* leak — Session 4's Task 6 called it the
inward one. Say in the datasheet whether your five goldens are **disjoint from
anything the system was, or will be, tuned on**. If your goldens were written
from the same production edge cases you later feed into a prompt, a retriever
or a fine-tune, then the eval set and the training set share a source and the
score measures self-consistency rather than correctness. Three answers are
allowed — *yes, disjoint* / *no, and here is the overlap* / *unknown, and here
is who would know* — and the third is a finding, not a failure.

The second is the row Session 3 built toward. In
[`use_case/decisions.md`](../../use_case/decisions.md), write **the
model/endpoint decision** — hosted, gateway or local, and which model — the
way Priya had to write it for her manager: every number in the row tagged
*measured* (a wall-clock you timed, a token count the provider reported) or
*looked up* (a price per token, a benchmark score), and every reason tagged
*constraint* (Security says the data does not leave; Legal needs it
regenerable) or *preference* (it writes nicer prose). Six weeks from now, in
Week 8, you will be asked to replace this model and keep the harness green —
and this row is what tells you which of today's reasons still hold.

### ✅ Deliverables

1. **Every section of `DATASHEET.md` filled in**, no template comments left.
2. **"What it cannot validate"** names at least three specific things about
   *your* data, not the generic three.
3. **"What it must never be compared against"** names where real ground truth
   lives, if any exists — even if you cannot reach it yet.
4. **The goldens-provenance line** — disjoint / overlapping / unknown, and
   with whom the answer sits.
5. **The model/endpoint row in `use_case/decisions.md`**, every number marked
   *measured* or *looked up*, every reason marked *constraint* or
   *preference*. One row; the tags are the deliverable.

---

## Step 5 — Run it on a model you own *(optional, strongly recommended)*

Session 3 ran a model on your laptop through `transformers`. Your application
talks to a model through an HTTP endpoint. The gap between those two is a local
server, and closing it is the point of this step.

Install [Ollama](https://docs.ollama.com/), pull a small model, and point your
`.env` at it. Then re-run **your Week 1 application** against it. Nothing in the
app's code should change — that is what the provider indirection was for. If
the diff is more than two lines in `.env`, you have a vendor dependency you did
not know about, and better to find it now.

### ✅ Deliverables

1. **The diff**, in your repo: what changed to move the app onto a local model.
2. **One line in `use_case/ecosystem.md`**: whether a local model is a
   plausible deployment path at your firm, and what would have to be true.
3. **If the weight download was blocked**, that is the finding instead. Record
   it in `use_case/ecosystem.md`; a network that blocks Hugging Face shapes
   Weeks 8 and 9 more than any technical decision you will make.

---

## 🧯 If it's blocked

### "Everything I generate looks the same"

Your axes are not orthogonal, or the model is anchoring on your seed examples.
Show it fewer seeds, and make the axis values more extreme — "a rambling wall
of text" produces more variation than "slightly longer". Then check the
temperature: at the 95%-mass count you measured in S3, is enough of the tail
live for the model to vary the *substance*?

### "Most of it fails validation"

Good, that is the schema working. Check whether the failures are the model's
fault or whether your schema is stricter than your real inputs — the second
case is a real finding about your problem, and it belongs in the datasheet.

### "I can't reach a model at all"

Session 3's Tasks 1–6 still run — they use the recorded logits trace, which
needs nothing. You lose the generation loop in Task 7.

For this challenge you do need a model somewhere: a local download, your API
key, or your firm's endpoint. If all three are blocked, say so in
`use_case/ecosystem.md` and **hand-write twenty rows instead.** Twenty rows you
wrote yourself beat two hundred you cannot produce, and Week 4 only needs
dozens for backtesting anyway.

Being fully blocked is not a bad outcome for this course — it is the single
most useful thing you can learn about your own firm in Week 2, and Week 9 is
where you do something about it.

### "The dedupe pass dropped rows that were different"

Character n-gram Jaccard will miss "floor 3" vs "floor three" and will catch
two rows that share a long boilerplate prefix. That is expected: lower the
threshold, or strip the boilerplate before shingling. Embeddings would catch
the first case, and they arrive with retrieval — this week the n-gram version
is deliberate, because it makes the upgrade legible.

---

## 👥 Step 6 — Show it to someone who knows the real data

You have generated data that *looks* like your inputs. The only person who can
tell you whether it does is someone who sees the real ones every day — the
person from your charter, a teammate on the queue, whoever owns the system your
data would come from.

**Show them twenty rows and the datasheet, and write down what they said.** Not
a summary of what you think they meant — what they actually said, in their
words.

The bar is deliberately low on ceremony and high on it being real. A ten-minute
screen-share counts. A document you send with three questions counts. What
does not count is imagining how it would go.

**Ask three things, in this order:**

1. *"Which of these would never actually happen?"* — before you tell them
   what you were trying to cover.
2. *"What comes in that is not here at all?"*
3. *"If this were public, what would worry you?"*

The second answer is usually a variation axis you did not have, and that is the
most valuable thing you will learn this week.

> **Your agent will help you structure this and will not invent it.** Ask it how
> to run the session, how to turn messy notes into three clear findings, or how
> to tighten the write-up. It will decline to write the feedback itself, because
> it was not in the room.

### ✅ Deliverables

1. **A row in [`use_case/stakeholders.md`](../../use_case/stakeholders.md)** —
   who you showed it to by role, what you asked, what you learned, and the
   follow-up.
2. **A line in [`use_case/decisions.md`](../../use_case/decisions.md)** naming
   one thing their feedback changed — an axis you added, a value you cut, a row
   you removed. If nothing changed, write that and say why.
3. **The three answers**, in your own words, in your repo.

---

## 📤 Step 7 — Share: bring it to work

This week's pattern is *generate the data you cannot have yet, and be exact
about what it proves*. Somewhere at your company there is a project stalled on
data access, a privacy review, or a vendor's sample set nobody trusts. This
step is where you write down which one, and what this week's work would be
worth applied to it.

### ✅ Deliverables

1. **Which project at work this is for**, one line under `## Bring it to
   work` in your README. *"The fraud team cannot prototype against real
   transactions until the DPIA clears"* names one; *"data access"* does not.
2. **What you would swap** — three lines under the same heading, one each for
   the **data** (what you would seed from, and whether you would generate from
   records or from a description), the **model or endpoint** (which one, and
   whether the data may leave the network), and the **access or approval** you
   would need to ask for. This is what turns the notebook into the version
   your team could run.
3. **Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)**,
   and comments on at least two other students' submissions after the deadline.

---

## What this challenge deposits for later

| What you write | Where it lives | When it comes back |
| --- | --- | --- |
| The synthetic dataset | `use_case/data/synthetic_v1.jsonl` | **Week 3** builds retrieval over it. **Week 4** scores against your goldens, not this. **Week 8** fine-tunes on it. |
| The datasheet | `use_case/data/DATASHEET.md` | **Week 4**, when a number needs defending. **Week 10**, when an auditor-shaped reader asks where the data came from. |
| The temperature ceiling and dedupe threshold | `use_case/decisions.md` | **Week 8** — a fine-tuned model has to be sampled somehow, and this is the baseline. |
| A blocked download, or a working local model | `use_case/ecosystem.md` | **Week 9**, which extends this file with the full deployment checklist. |
| The three swap lines | Your README, `## Bring it to work` | **Week 10** — the final report's "what it would take to run" section. |

---

## Your Final Submission

Please include the following in your final submission:

1. **A public link to your repo**, containing:
   1. **A five-minute-or-less Loom video** walking through your axes, the four
      counts, and the "cannot validate" section of your datasheet.
   2. **A written document addressing each deliverable above** — the axes with
      reasons, the counts and settings, what you removed after reading, the
      Step 6 answers, and the swap lines.
   3. **All relevant code**, committed and pushed. **Never the data.**
2. **Your `use_case/` directory updated** — `data/DATASHEET.md` with no template
   text left, and the new rows in `decisions.md`, `stakeholders.md`,
   and `ecosystem.md`.

### How to submit

1. **Post your repo link** in
   [our community on Maven](https://bit.ly/fde1-maven-community). That is where
   every technical challenge is submitted.
2. **Push your `use_case/` updates to that repo** before you post, so the link
   shows the current state of your project rather than last week's.
3. **After the deadline, comment on at least two other students' submissions.**
   Read their datasheet, and leave something specific — an axis they missed, or
   a claim in "what it can validate" you would push back on.

> **Never commit real data, and never commit the synthetic data either.**
> `use_case/data/` is gitignored except the datasheet, for exactly this reason.
> Do not post screenshots of internal infrastructure, hostnames, or anything
> your firm would consider confidential.

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

## Where this goes next

| Week | What it adds to this data |
| --- | --- |
| 3 | Retrieval — your endpoint answers from a corpus, and this is the first corpus it has. |
| 4 | Evals — the goldens are the bar, this data is the traffic, and the datasheet says which is which. |
| 6 | Guardrails — the `top_k` mask you wrote becomes a grammar the model cannot escape. |
| 8 | Fine-tuning — this is the training set, and open weights are what you train. |
| 9 | Infrastructure — the blocked download and the licence on your model both land in the deployment checklist. |
| 10 | Production — the final report, with the swap lines you started this week as its "what it would take to run" section. |

Everything after this week assumes you have data you can show people, and a
document that says what it is.
