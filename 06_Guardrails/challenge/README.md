<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Technical Challenge 6</h1>
  <p><strong>Exploit your own app, close the hole, make the attack a permanent test, and price every rung of the ladder.</strong></p>
</div>

---

## Overview

> **Read first:** [`use_case/CHARTER.md`](../../use_case/CHARTER.md). This
> challenge attacks the endpoint you shipped in Week 3 and scores the fix with
> the harness you built in Week 4. If either is still the template, finish
> that week first.

> **Scope.** Your own application, your own environment, as part of a
> certification you are enrolled in. Do not attack systems you do not own.

*"We have guardrails"* is not a measurement. This week every defence gets two numbers: what it stops, and how many real
users it refuses. You get the first by landing an attack on your own app
before you write a single defence. You get the second by running your golden
set through the defence afterwards.

**This is the week your app gets a security section.** Session 11 followed an
engineer whose help assistant leaked a code because a partner uploaded a page.
Session 12 followed him pricing every layer that would have stopped it, for two
readers: a security lead who wants everything, and an ops director who wants
nothing slower. Your write-up answers the question they both ask:

> **"Which rung, for which failure, at what price, and what are you accepting
> instead?"**

The exploit takes an afternoon. **The regression test and the ladder table are
the assignment.**

> 💡 **You already know enough to be dangerous.** In Session 11 you planted a
> canary, attacked by hand, searched hundreds of variants, and watched one
> document beat all of them. You defended and measured both ways, escaped a
> sandbox and poisoned a tool description. In Session 12 you built the rungs,
> measured every one, and drew the line between a guardrail and an evaluator.
> Now point all of it at your own endpoint!

<table>
  <tr>
    <td width="120"><strong>Outcome</strong></td>
    <td>A working exploit against your own app with its exact input recorded, the specific fix, the exploit wired into <code>use_case/evals/</code> as a case that runs with everything else, and the guardrail ladder in <code>use_case/decisions.md</code> with your numbers: cost, latency, leaks stopped, real answers withheld, and a line for every rung you are not shipping.</td>
  </tr>
  <tr>
    <td><strong>Tools</strong></td>
    <td>Python, LiteLLM, NeMo Guardrails, <code>helpers/harness.py</code> from this repo, your Week 3 endpoint, your Week 4 harness and golden set, Docker.</td>
  </tr>
  <tr>
    <td><strong>Due</strong></td>
    <td>End of the week. Post your repo link in the Maven Community.</td>
  </tr>
  <tr>
    <td><strong>Before you start</strong></td>
    <td>TC3's endpoint running. TC4's <code>use_case/evals/run.py</code> producing a report. <code>use_case/evals/golden.jsonl</code>, which is what false positives are measured against. And <strong><code>INJECTION_MODEL</code> / <code>INJECTION_API_BASE</code> set in <code>.env</code></strong> (see the week README's setup section): Steps 2 and 3 send attack-shaped prompts, and those go to a local model or a firm-approved gateway, never a public API.</td>
  </tr>
</table>

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A working exploit against your own application, the specific fix, and that
exploit kept as a permanent case in your eval harness. Then a guardrail ladder
priced in cost, latency and false positives, with a written line for every rung
you are *not* shipping.

Eight questions are asked inside the notebooks as you work through them. *They
are not submitted and not graded.* They are how you work out what the challenge
is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | What in your system prompt must never come out, or, if nothing, which behaviour you would put a canary on instead | S11 |
| 2 | Every place untrusted text enters your system, who can write there, and which entry you would poison first | S11 |
| 3 | Which defence *removes* the thing at risk instead of filtering for it, and what in your prompt could move out of the model's reach tomorrow | S11 |
| 4 | Which of the three legs (private data, untrusted content, a way out) your app has today, and which you could remove most cheaply | S11 |
| 5 | Which of your outputs is a closed set, and whether you can make anything outside it unreachable through logits or your provider's structured output | S12 |
| 6 | Which of your failures you can spell as a regex, and how many of your golden inputs Levels 1 and 2 wrongly block | S12 |
| 7 | Which sentence in your prompt is really a permission rule, which service should own the `if`, and who signs when the model is uncertain | S12 |
| 8 | At your requests per day and latency budget, whether your judge is a guardrail or an evaluator, and whether a user gets refused when it fires | S12 |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar, for example `#discuss-question-7`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **A canary in your system prompt** (or a behaviour canary if there is no secret), with the `leaked()` check that scores it
- [ ] **At least one working exploit**, with the exact input recorded. If the hand-written ones failed, the optimiser's budget and its rate
- [ ] **The other doors tried:** indirect injection if you retrieve anything, a poisoned tool description if you expose tools, a sandbox escape if you run model-written code. Each gets a result, or one line saying that door is closed and why
- [ ] **The specific fix**, and the winning attack wired into `use_case/evals/` as a scorer that runs it through your NeMo Guardrails config, so it runs with everything else
- [ ] **Before/after leak rate and false-positive count**, both from one pass of your attacks and your golden inputs through the same rails config, so they cannot drift
- [ ] **The ladder table in `use_case/decisions.md`:** every rung, ships or declines, cost and latency, real answers withheld, and what you are accepting instead
- [ ] It still runs in Docker

### 📤 Share

- [ ] **Shown to a real person:** what your app did *before* the fix, with what they asked recorded in your own words. This one is graded
- [ ] **What you would swap to run this at work:** data, model or endpoint, and the approval you would need, as three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## 📖 Official documentation

Everything this challenge uses, from the people who maintain it.

| Tool | What you use it for here | Docs |
| --- | --- | --- |
| NeMo Guardrails | your ladder as one config: `RailsConfig.from_path`, `LLMRails`, `generate` with only the input rails switched on, and `log.activated_rails` to see which rung stopped an input | [docs.nvidia.com — NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/latest/index.html) |
| `helpers/guardrails.py` | *Optional reference.* The same ladder in plain Python (`Ladder`, `evaluate()`, `as_scorer()`). Read it for the shape; the challenge is built on NeMo | [`helpers/guardrails.py`](../../helpers/guardrails.py) |
| NeMo Guardrails generation options | `options` to run the input rails alone, and the log that names the rung that stopped an input | [docs.nvidia.com — rails.llm.options](https://docs.nvidia.com/nemo/guardrails/guardrails-python-sdk/nemoguardrails/rails/llm/options) |
| `helpers/harness.py` | `run`, `compare`: re-running your Week 4 baseline after every guardrail | [`helpers/harness.py`](../../helpers/harness.py) |
| LiteLLM | the target app, the judge rung if you build one, and `tools=` for a poisoned description | [docs.litellm.ai](https://docs.litellm.ai/) |
| OWASP Top 10 for LLM Applications | the vocabulary of your write-up; LLM01 is prompt injection | [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/) |
| Docker | it still has to run in the container | [docs.docker.com](https://docs.docker.com/) |
| Ollama | the local model your attacks run against: `ollama pull qwen2.5:7b` | [ollama.com](https://ollama.com/) |

---

## Setting Expectations

**Budget six to eight hours**, spread across the week. Landing the attack is
either quick or slow, with little in between. The doors, the fix and the
ladder table are steady work.

| Step | What it is | Rough time |
| :---: | --- | --- |
| 1 | The canary, and the `leaked()` check | 20 min |
| 2 | Land an attack: by hand, then the optimiser | 1–2 hrs |
| 3 | The other doors that apply to your app | 1–2 hrs |
| 4 | Fix it, and make the fix permanent in the harness | 1 hr |
| 5 | Price the ladder, both numbers on every row | 1–2 hrs |
| 6 | Show a real person what it did before the fix | 30 min, plus their calendar |
| 7 | Share: bring it to work | 30 min |

> **Do Step 1 before anything else, and book the Step 6 conversation today.**
> The canary scores everything after it, and the Step 6 conversation depends
> on someone else's calendar.

---

## What you are building

| File | Role |
| --- | --- |
| Your system prompt | Carries the canary, or the app carries a behaviour canary |
| `use_case/evals/attacks.jsonl` | Every attack you tried, with the exact input and whether it worked. **The winners are your regression cases** |
| Your app's `guardrails/` directory | The ladder as NeMo config: `config.yml` and your `.co` files. The order the YAML lists the input flows in is the order the rungs run |
| `use_case/evals/harness.py` | Gains `blocks_injection`, a scorer that runs each winning attack through your rails and checks that a rung stopped it |
| `use_case/evals/run.py` | Still the whole interface; now runs the injection cases with everything else |
| `use_case/decisions.md` | The ladder table: every rung, ships or declines, cost/latency, real answers withheld, what you accept instead |
| `use_case/evals/failures.md` | Gains one line: the attack that worked, as a failure mode |
| `CLAUDE.md` | The instructions Claude Code reads before it touches anything |

> **What is already written for you, and what is not.** NeMo Guardrails is the
> plumbing. It runs your input rails in the order the YAML lists them and stops
> at the first block. It ships the rules and judge rungs ready to configure, and
> runs anything else as a custom action. **The attack, the fix, the rungs'
> contents and the table are yours.** You cannot defend a regex in a review if
> you did not write it, for a failure you did not find.
>
> Two rules are yours to keep, because NeMo does not enforce them:
>
> - **Fail closed.** A custom action that raises blocks the input (*"I'm
>   sorry, an internal error has occurred."*), and a judge whose model cannot
>   be reached raises `LLMCallException`. Both are right. Wrap either in a
>   `try`/`except` that lets the input through, and you have built a guardrail
>   that switches itself off during an outage.
> - **No coverage without false positives.** NeMo will tell you how many
>   attacks it stopped and never ask how many real users it refused. Every
>   number you report has the other one beside it.

`CLAUDE.md` puts Claude Code into **instructor mode** for this directory. It
will explain attack classes, debug your optimiser loop and review your fix
hard. It will decline to write the exploit for your app. That is deliberate:
iterating on an attack that does not work yet is what being attacked feels
like, and it is the skill.

---

## Step 1 — Put a canary in your system prompt

Pick a unique, greppable string, like `ACME-CANARY-9931`: anything you will not
confuse with real output. Then write `leaked(response) -> bool`, the check that
scores every attempt from here on.

The canary turns "did the attack work?" into a substring check, so you can
score hundreds of attempts automatically. It costs nothing.

**If there is nothing secret in your prompt**, that is the best position to be
in, and the decision record should say so. Pick a *behaviour* to canary
instead: an approval the app must never grant, a tool it must never call with
a given argument, a category output that must never become a paragraph. Then
`leaked()` asserts something about that behaviour. Session 11's engineer had a
string. Question #1 asked which you have.

### ✅ Deliverables

1. **The canary** in your system prompt (or the behaviour, named in
   `use_case/decisions.md`), and **`leaked()`** in `use_case/evals/harness.py`.

---

## Step 2 — Land an attack

> **Where the attacks go.** For Steps 2 and 3, run your app against the
> `INJECTION_*` endpoint from `.env`. Point its model config at
> `http://localhost:11434` (or your firm's approved gateway) for the duration,
> then switch back for Steps 4 and 5. Why: the hosted providers' policies
> prohibit this content with no carve-out for your own app, their enforcement
> is automated, and on your employer's Azure tenant it trips the jailbreak
> detectors and abuse monitoring by default. Week 1 made your app's model
> configuration, not code, so this is a `.env` edit. If it is not, that is a
> finding.

Hand-written first. Session 11's seven are a starting list. Write three of your
own that use what you know about *your* prompt. If those fail, run the
optimiser: the session searched 720 recombinations, and seven failed manual
attempts are not a security finding.

Record every attempt in `use_case/evals/attacks.jsonl`: the exact input, the
context if any, and whether the canary leaked. **Run each attack that matters
more than once.** One run of a non-deterministic attack is a sample of one, and
the review wants a rate.

```json
{"kind": "direct", "input": "...", "context": null, "runs": 8, "leaked": 2}
```

> **If you cannot land one**, report it properly: how many candidates you
> tried, which model, and what your app does that made it hard. "I tried a few
> things" is not a finding. The session's caveat applies too: a fragment
> optimiser that found nothing is weak evidence. Then attack a deliberately
> weakened copy of your app, so you have *something* to test a defence
> against, and say in the write-up that you did.

### ✅ Deliverables

1. **`use_case/evals/attacks.jsonl`**: every attempt, with runs and leak
   counts, and the winning inputs marked.
2. **The rate**, in your README: attempts, model, and how many leaked, for the
   hand-written set and, if you needed it, the optimiser's budget and rate.

---

## Step 3 — Try the other doors that apply to you

Hosted models are now trained against direct injection.
Session 11's reference run put it at 0 of 22, and one document at 10 of 12.
**Try every door your app actually has.** For each one it does not have, write
one line saying it is closed and why:

| Door | Try it if | What it looks like |
| --- | --- | --- |
| **Indirect**: the attack is in something your pipeline reads | Your app retrieves *anything* | One poisoned document in your corpus, a legitimate question, eight runs. Session 11's Task 3 on your data |
| **Tool description**: the attack is in a description the model follows | Your app exposes tools, an MCP server or a manifest, especially any you did not write | One poisoned description. Watch whether the secret leaves through a tool argument, where an output check never looks |
| **Sandbox escape**: the attack is code the model wrote | Your app executes model-written code | Break out of your own restricted namespace. If you cannot in an hour, ask what the process it runs in can reach |

**Before you pick a door, ask what the session's engineer asked first: *who
can write to what your app reads?*** Your list from Question #2 is the map. If
the answer for any source is "customers", "a supplier" or "the public", that
is your incident before it has happened. Try that door first.

> **Indirect injection is the one that matters in an enterprise.** Your users
> are colleagues, and they have easier ways to misbehave. Input-side guardrails
> never see indirect injection either, because nothing about the request looks
> unusual. If your app retrieves anything, this door is required.

### ✅ Deliverables

1. **Each door that applies, in `use_case/evals/attacks.jsonl`** with its
   rate. In your README, **one line per door that does not apply**, saying why
   it is closed.
2. **Your answer to *who can write to what it reads***: the list of sources,
   each with who can write there, in `use_case/ecosystem.md`.

---

## Step 4 — Fix it, and make the fix permanent

Close the specific hole. Walk Session 11's chain of reasoning: *which of the
three legs can you remove: private data the model can reach, untrusted content
it reads, or a way out?* Removing beats filtering every time:

- a secret that is no longer in the prompt cannot leak
- an output that is a closed set cannot become a paragraph
- an app that can only read cannot act

If you cannot remove a leg, wrap the untrusted content, check the output, and
measure. Those help, and they are not enough on their own.

Build the ladder as NeMo config in your app: a `guardrails/` directory with
`config.yml` and your `.co` files, the way Session 12 built Theo's. Add
`nemoguardrails` to your app's own dependencies
(`uv add "nemoguardrails>=0.24"`). `make setup-week W=6` installs it for the
notebooks only, and the Dockerfile's `uv export` does not see the week groups.
Without that line the image has no guardrails.

Then **add the winning attack to your harness** as code, not as a note in a
doc. The shape:

```python
from nemoguardrails import LLMRails, RailsConfig
from helpers import harness

rails = LLMRails(RailsConfig.from_path("guardrails"))

def blocks_injection(actual: str, case: dict) -> float:
    ...  # 1.0 if a rung stopped case["input"], else 0.0

report = harness.run(cases, my_system, {**SCORERS, "blocks_injection": blocks_injection})
```

To run the input rails alone, pass `rails.generate(...)` the option
`{"rails": {"input": True, "dialog": False, "output": False, "retrieval": False}}`
and ask for `{"log": {"activated_rails": True}}`. A rail in
`response.log.activated_rails` with `stop` set is the rung that blocked it.

The scorer has the Week 4 harness signature, so the attack becomes a scored
case that runs with everything else. Week 8's model swap gets checked against
it automatically. **This is the actual deliverable.** An attack you fixed but
did not add to the harness can come back: in Week 8 you replace the model,
and a new model can behave differently on the same attack.

### ✅ Deliverables

1. **The fix**, named in your README with the leg it removes. If it filters
   instead, say why removal was not available.
2. **The attack as a scored case**: `blocks_injection` in
   `use_case/evals/harness.py`, and `python use_case/evals/run.py` reporting
   it alongside the Week 4 scorers.
3. **One new line in `use_case/evals/failures.md`**: the attack that worked,
   as a failure mode with its count.

---

## Step 5 — Price the ladder, both numbers on every row

Session 12 built the rungs and measured all of them. Now do it for your app.
Both of the session's readers insisted on one rule: **every row has two
numbers**, what it stops and how many real inputs it refuses.

```python
# One pass, both sets, the same rails config — so the two numbers cannot drift
caught = [stopped_by(rails, attack) for attack in my_attacks]
refused = [stopped_by(rails, case["input"]) for case in golden]
# e.g. caught 6 of 7 attacks · refused 1 of 25 legitimate · 31 ms per call
#      (illustrative shape — your numbers come from your own attacks)
```

Coverage on its own is not a result, because a rung that blocks every request
scores 100%. Nothing in NeMo stops you reporting coverage alone, so run both
sets every time. Keep **which** legitimate inputs got refused and which rung
refused each (the log names it). You need that list to fix anything. For the
per-rung rows, build one rails object per rung with only its flow switched on,
and run both sets through each, as the session's measurement did.

Then fill in the table in [`use_case/decisions.md`](../../use_case/decisions.md),
one row per rung, including the rungs you are not shipping:

| Level | Ships? | Cost / latency | Catches | Real answers withheld | What you are accepting instead |
| --- | --- | --- | --- | --- | --- |
| 0 — Constrained decoding | | | | | |
| 1 — Rules | | | | | |
| 2 — Classifier | | | | | |
| 3 — LLM judge | *guardrail or evaluator?* | | | | |
| 4 — Policy layer | | | | | |
| 5 — Human | | | | | |

Three rows need a sentence each:

- **Level 0.** If you are behind a closed API, say so, and say whether the
  provider's structured output covers any of your outputs. That is a finding
  for `use_case/ecosystem.md`, not a gap in your work.
- **Level 3.** Do the arithmetic from Question #8 (requests per day times
  roughly a second). Write down whether the judge runs inline or on a sample,
  and why.
- **Level 4.** Name the sentence in your prompt that was really a permission
  rule, and where the `if` now lives.

If the leak rate did not move after the fix, you added latency and nothing
else. Say so. That is a real finding about the defence.

### ✅ Deliverables

1. **Before/after leak rate and false-positive count**, in your README, both
   from one pass of your attacks and your golden inputs through the same
   rails config, so they cannot drift.
2. **The ladder table in `use_case/decisions.md`**, every row filled, with the
   *accepting instead* column written for every rung you decline. A security
   review is asking for that column.
3. **`python use_case/evals/run.py` still passing** the Week 4 baseline. A
   guardrail that broke your goldens is a regression, and `harness.compare()`
   is how you find out.

---

## 🧯 If it's blocked

### "Nothing works"

Good sign, weak evidence. Raise the optimiser budget, add fragments, and try
encoding tricks: base64, another language, splitting the instruction across a
document. Then try the indirect route, which is usually far easier than the
direct one. If you still cannot land one, weaken a copy of the app and say so.

### "Everything works — even the obvious ones"

Expected on a small local model, and it is a finding. A 3B–8B open model has
had far less adversarial training than the hosted API your app probably runs on
in production. So your table has two columns: *local, measured* and
*production model, not tested here and why*. Write both. The gap is a fact
about model choice, and Week 8's model swap will move it.

### "My app has no way to point at a different model"

Then your provider is hardcoded, which Week 1 told you to avoid and Week 9 will
make you fix. Add the one environment variable now. It is the smallest possible
version of the Week 9 work. Note in `use_case/decisions.md` that it was
missing.

### "I cannot install Ollama or pull the model"

Ask whether your firm has a gateway approved *for adversarial testing*, not
just approved, and use that. Or pair with a classmate whose laptop can serve
the model on the local network. Write the blocker in `use_case/ecosystem.md`.
Do **not** fall back to your personal API key. The whole rule exists so that
nobody's account is put at risk.

### "I don't have a system prompt to leak"

Then pick a behaviour: make it approve something it should not, produce output
outside its schema, or follow an instruction from a retrieved document. The
canary becomes an assertion about state. Step 1 covers it.

### "My fix broke normal use"

That is the real trade-off, so write it up plainly. Both numbers in the table
matter. A fix too blunt to ship is a finding about the defence, not a failure
on your part. Your Step 5 pass tells you which legitimate inputs were blocked
and by which rung, so start there.

### "I'm on a closed API and Level 0 doesn't exist for me"

Correct, and it is a finding. Write it in `use_case/ecosystem.md`, check
whether your provider's structured-output mode covers your closed-set outputs,
and start the ladder at Level 1. Week 8 may give the rung back.

### "The judge makes every request a second slower"

Then at that volume it is an evaluator for you, not a guardrail. Run it on a
sample after the fact, let what it finds become next week's rule, and write
that decision in the Level 3 row. Session 12's Task 6 makes this exact call.

### "`generate` raises: *You are using the sync `generate` inside async code*"

Your app's handler is `async`. Gradio and FastAPI handlers often are, and so is
a notebook cell. Use `await rails.generate_async(...)` there, with the same
options. The harness scorer is a plain function, so it keeps `generate`.

### "Every request fails with `LLMCallException`"

Your judge rung (`self check input`) cannot reach the model in `config.yml`.
Failing is the right behaviour: that is the guardrail failing closed. Fix the
endpoint. Do not catch the exception and let the input through.

### "The classifier or topical rail is stuck downloading"

Those rungs embed text with all-MiniLM-L6-v2, about 90 MB from Hugging Face on
first use. Pass `cache_dir` in the embeddings model's `parameters`, as Session
12 did. Otherwise FastEmbed caches it in a temp directory and downloads it
again. If the download is blocked at work, the rules and judge rungs need no
embeddings and still run. Write the blocked download in
`use_case/ecosystem.md`.

### "The guardrails work locally and not in Docker"

`nemoguardrails` is in a week group, not in your app's dependencies, so the
image never installed it. Run `uv add "nemoguardrails>=0.24"`, then rebuild.

### "Should I report this to my security team?"

If you found something in a *production* system and not just your prototype,
yes, immediately, through whatever channel your firm has. That is also a good
`use_case/stakeholders.md` entry, and exactly the contact Week 9 needs you to
have made.

---

## 👥 Step 6 — Show a real person what it did before you fixed it

The most persuasive thing you produce this week is the transcript from before
the fix: a legitimate question, an innocent-looking document, and your app
doing the thing it must never do. Show that to someone real and write down what
they said. Good choices are the person from your charter, whoever owns the data
your app reads, or the person at your company who would sit in the incident
review.

Keep it light on ceremony, but it has to be real. A ten-minute screen-share
counts. Imagining how it would go does not.

**Ask three things, in this order:**

1. *"What is the worst thing this could have done, in our setup?"* Ask before
   you explain the fix. Listen for a leg of the trifecta you had not weighed.
2. *"Which of these rungs would you want, and which would you switch off the
   first time it refused you?"* Put the ladder table in front of them for this
   one.
3. *"Who else needs to see the before?"*

> **Your agent will help you structure this and will not invent it.** Ask it
> how to run the session, how to turn messy notes into three findings, or how
> to tighten the write-up. It will decline to write the feedback itself,
> because it was not in the room.

### ✅ Deliverables

1. **A row in [`use_case/stakeholders.md`](../../use_case/stakeholders.md)**:
   who you showed it to by role, what you asked, what you learned, and the
   follow-up.
2. **A line in [`use_case/decisions.md`](../../use_case/decisions.md)** naming
   one thing their answers changed: a rung switched, a door you had called
   closed, a leg you now remove. If nothing changed, write that and say why.

---

## 📤 Step 7 — Share: bring it to work

This week's pattern: *attack before you defend, remove before you filter, and
never report coverage without the false positives beside it*. Somewhere at your
company there is an assistant, a vendor tool or an automation that reads text
somebody outside the team can write: a ticket queue, a shared mailbox, uploaded
documents. Find one where nobody has checked what happens when that text is
addressed to the model, and write down which one.

### ✅ Deliverables

1. **Which system at work this is for**, one line under `## Bring it to work`
   in your README. *"The support assistant summarises tickets customers file,
   and nobody has tried putting instructions in one"* names one; *"AI
   security"* does not.
2. **What you would swap**: three lines under the same heading, one each for
   - the **data**: which sources it reads, and who can write to them
   - the **model or endpoint**: whether you have logit access or structured
     output, which decides whether Level 0 exists
   - the **access or approval** you would need to ask for

   Put the false-positive count from Step 5 next to them, marked *measured*.
   It says how many real users the guardrail would refuse. This is what
   turns the notebook into the version your team could run.
3. **Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)**,
   and comments on at least two other students' submissions after the deadline.

---

## What this challenge deposits for later

| What you write | Where it lives | When it comes back |
| --- | --- | --- |
| The winning attack as a scored case | `use_case/evals/harness.py`, `attacks.jsonl` | **Week 8**: the model swap is checked against it automatically. **Week 9**: the deploy gate runs it. |
| The ladder table | `use_case/decisions.md` | **Week 8**: voice pushes you down the ladder, and a local model may reopen Level 0. **Week 9**: the guardrails section of the deployment checklist. |
| Who can write to what it reads | `use_case/ecosystem.md` | **Week 9**: data boundaries and trust levels per source. |
| The vulnerability and the fix | Your README | **Week 10**: the security section of the final report. |
| The three swap lines | Your README, `## Bring it to work` | **Week 10**: the final report's "what it would take to run" section. |

---

## Your Final Submission

Please include the following in your final submission:

1. **A public link to your repo**, containing:
   1. **A five-minute-or-less Loom video**: the attack landing, the fix, and
      `run.py` reporting the regression case.
   2. **A written document addressing each deliverable above**: the canary,
      the attack rates by door, the fix and which leg it removes, the
      before/after numbers from one pass through your rails, the ladder table,
      the Step 6 answers, and the swap lines.
   3. **All relevant code**, committed and pushed. `use_case/evals/` runs from
      a clean checkout. **Never the data.**
2. **Your `use_case/` directory updated**: `evals/` with the new case,
   `decisions.md` with the ladder table, `ecosystem.md` with the sources list,
   and the new row in `stakeholders.md`.

### How to submit

1. **Post your repo link** in
   [our community on Maven](https://bit.ly/fde1-maven-community). That is where
   every technical challenge is submitted.
2. **Push your `use_case/` updates to that repo** before you post, so the link
   shows your project's current state.
3. **After the deadline, comment on at least two other students' submissions.**
   Read their ladder table and leave something specific: a door they called
   closed that you think is open, a rung whose *accepting instead* line you
   would push on, a false-positive count that looks too clean.

> **Never commit real company data.** `use_case/data/` is gitignored for this
> reason. `attacks.jsonl` holds the inputs you wrote, not anything from a real
> corpus. If your poisoned document was a copy of a real one, keep the
> synthetic twin. Do not post screenshots of internal infrastructure,
> hostnames, or anything your firm would consider confidential. Never post a
> real secret, even a leaked one.

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A working exploit against your own application, the specific fix, and that
exploit kept as a permanent case in your eval harness. Then a guardrail ladder
priced in cost, latency and false positives, with a written line for every rung
you are *not* shipping.

Eight questions are asked inside the notebooks as you work through them. *They
are not submitted and not graded.* They are how you work out what the challenge
is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | What in your system prompt must never come out, or, if nothing, which behaviour you would put a canary on instead | S11 |
| 2 | Every place untrusted text enters your system, who can write there, and which entry you would poison first | S11 |
| 3 | Which defence *removes* the thing at risk instead of filtering for it, and what in your prompt could move out of the model's reach tomorrow | S11 |
| 4 | Which of the three legs (private data, untrusted content, a way out) your app has today, and which you could remove most cheaply | S11 |
| 5 | Which of your outputs is a closed set, and whether you can make anything outside it unreachable through logits or your provider's structured output | S12 |
| 6 | Which of your failures you can spell as a regex, and how many of your golden inputs Levels 1 and 2 wrongly block | S12 |
| 7 | Which sentence in your prompt is really a permission rule, which service should own the `if`, and who signs when the model is uncertain | S12 |
| 8 | At your requests per day and latency budget, whether your judge is a guardrail or an evaluator, and whether a user gets refused when it fires | S12 |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar, for example `#discuss-question-7`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **A canary in your system prompt** (or a behaviour canary if there is no secret), with the `leaked()` check that scores it
- [ ] **At least one working exploit**, with the exact input recorded. If the hand-written ones failed, the optimiser's budget and its rate
- [ ] **The other doors tried:** indirect injection if you retrieve anything, a poisoned tool description if you expose tools, a sandbox escape if you run model-written code. Each gets a result, or one line saying that door is closed and why
- [ ] **The specific fix**, and the winning attack wired into `use_case/evals/` as a scorer that runs it through your NeMo Guardrails config, so it runs with everything else
- [ ] **Before/after leak rate and false-positive count**, both from one pass of your attacks and your golden inputs through the same rails config, so they cannot drift
- [ ] **The ladder table in `use_case/decisions.md`:** every rung, ships or declines, cost and latency, real answers withheld, and what you are accepting instead
- [ ] It still runs in Docker

### 📤 Share

- [ ] **Shown to a real person:** what your app did *before* the fix, with what they asked recorded in your own words. This one is graded
- [ ] **What you would swap to run this at work:** data, model or endpoint, and the approval you would need, as three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## Where this goes next

| Week | What it adds to this work |
| --- | --- |
| 7 | Memory: a store the model reads is one more thing somebody can write to, so the *who can write there* question applies to it. |
| 8 | Fine-tuning: the injection case is re-run against the new model automatically, and a local model may give you the logit access Level 0 needs. |
| 9 | Infrastructure: the policy layer gets its enforcement point, and the ladder table becomes the guardrails section of the deployment checklist. |
| 10 | Production: the vulnerability and the fix are the security section of the final report, and the swap lines join "what it would take to run for real". |

From here on, your app has been attacked by you, has a test that proves the
hole stays closed, and has a written position on every rung it does not run.
