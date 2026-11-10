<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Week 6 — Guardrails &amp; Adversaries</h1>
  <p><strong>🛤️ Break it first, then price every layer that would have stopped it</strong></p>
</div>

---

## 🎯 What you'll be able to do

Break your own app on purpose, close the hole, and prove it stays closed. Then
say what each layer of defence costs in latency, money and refused users.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S11 | [`Prompt_Injection`](./sessions/S11_Prompt_Injection.py) | Attack a help assistant with **promptfoo**: hand-written and searched attacks, a poisoned document, both defences measured both ways, a poisoned tool, a sandbox escape. | Coming soon | Coming soon |
| S12 | [`The_Guardrail_Ladder`](./sessions/S12_The_Guardrail_Ladder.py) | The guardrail ladder as one **NeMo Guardrails** config, cheapest rung first, with every rung timed and the price of a topical rail measured. | Coming soon | Coming soon |

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC6 — Exploit your own app, close it, and price the ladder**](./challenge/README.md) | Coming soon |

---

## 📖 Overview

Your assistant reads text it did not write: a retrieved document, a tool's
description, a ticket a customer filed. A language model cannot reliably tell
text it should *use* from text it should *obey*. So anyone who can put words in
front of your model can try to give it orders. That is **prompt injection**.
This week we do it to your own app before anyone else does, then decide, with
numbers, what to put in the way.

Both sessions follow one engineer through one incident. Theo built the internal
help assistant at a freight company. A carrier uploaded a page to the partner
portal with a hidden note in it. The assistant read that page while answering a
routine question, and handed a customer-service rep a code it was never
supposed to reveal. Nobody attacked the assistant. Something it read did.

**Session 11 is the attack.** Theo reproduces the incident with a *canary*, a
made-up secret whose only job is to be easy to spot. Now "did it leak?" is a
check he can run a hundred times. He tries the obvious attacks and runs a search
over hundreds more. Then one poisoned document gets the secret out on an
innocent question! He adds two defences and measures each one twice: leaks
stopped, and real answers withheld. The business switches off a fix that blocks
real questions. Last, he opens the two other doors a security team will ask
about: code the model writes, and the description of a tool it calls.

**Session 12 is the price of every defence.** Guardrails come as a ladder. The
bottom rung is free and absolute, but it needs access to the model's raw
scores, which a closed API does not give you. The top rung is a human: slow,
expensive, and sometimes the right answer. Theo builds the rungs and measures
each one on the same inputs. One of them, an AI judge, costs hundreds of times
more than the others. That gap marks the line between a check that blocks a bad
answer and one that only notices it afterwards. He ends with one table for the
review: every rung, whether it ships, what it costs, how many real questions it
refuses, and what he accepts instead of each rung he declines.

**The challenge** is Theo's week on your own app. Plant a canary, land an
attack, and try the doors that apply to you. Fix the specific hole and make the
attack a permanent test. Fill in the ladder with your numbers. Then show
someone what your app did before you fixed it.

The big idea this week: **every defence needs two numbers, the attacks it stops
and the real users it refuses.** A defence you never attacked is a guess. A
guardrail you never checked for false positives refuses an unknown number of
real users.

---

## 🔀 Theo's path, and where yours diverges

Every decision in the notebooks is one Theo made for *his* setup: a closed API,
internal users, retrieval over a portal outsiders can write to, one tool, and
1,400 questions a day. Your answers may differ. The notebooks carry these same
forks next to each decision.

| Decision | What Theo chose, and why | What flips it |
| --- | --- | --- |
| **What to canary** | A string, the override code, because a substring check is the whole scorer | Your risk is a *behaviour* (an approval, a tool call, a paragraph where a category was due). Then the canary is an assertion about state |
| **How hard to push direct attacks** | Ran them, expected them to bounce, and kept the number. His users are logged-in colleagues | **External users**: direct injection is a live surface, the classifier becomes mandatory, and the hand-written list starts a regression suite |
| **How strong a search to run** | Fragment recombination, reported as weak evidence. It is the best a closed API allows | **Open weights**: a logit-guided search is far stronger, and a null result from it means more. **A gateway that upgrades under you**: automate the search before widening it |
| **Which door is the incident** | The retrieved document. Four hundred carriers can write to the partner portal | **No retrieval**: go to the tool description. **Retrieval only over sources your team controls**: lower priority, but write down who can write there. **Anything customers or suppliers can influence**: this is your incident |
| **What the fix is** | Remove the secret from the prompt entirely. The wrapper and the output check are the backstop for the secret he forgot | **The model has to know the sensitive thing to do its job**: the output check is the primary defence, and its false-positive count decides whether it ships. **Output is a closed set**: constrain the shape instead |
| **Whether the code door is open** | Closed. The assistant runs no model-written code, so this is a line for the neighbouring team's review | **You run model-written code**: the question is what the process can reach, not which builtins you removed. Use a container with no credentials, or the sandbox is only a comment |
| **Whether the tool door is open** | Open next quarter: a carrier-written MCP server. Its description gets pinned and reviewed like a package | **No tools you did not write**: closed. **Any third-party server or manifest**: run this before the retrieval test. **The app can act, not only answer**: blast radius before any filter |
| **Level 0** | Declined for free-text replies (closed API). Shipped for the four-way router through structured output | **Logits available**: ship it first for every closed-set output. **Everything is free text**: the row is empty, and that is a finding |
| **Levels 1 and 2** | Rules on every reply, classifier on every question. Both free, both with a false-positive count of zero on the goldens | **Exactly specifiable failures**: rules do most of the work. **Describable but not spellable**: the classifier, and the blocked-request log is where its labels come from |
| **Level 3** | An evaluator, nightly, on a 5% sample. 1,400 questions a day at 1.8 s could not absorb a second each | **Low volume, expensive failures**: inline, it is a guardrail. **High volume *and* expensive failures**: a fast classifier inline, the judge on the sample. **Latency budget already spent** (voice): evaluator, whatever the stakes |
| **Level 4** | The fix. The override code and the $50k rule are `if` statements in the refunds service | Does not flip. What varies is how many sentences of *your* prompt are permission rules in disguise |
| **Level 5** | Refunds above the rep's limit go to a person | Varies with stakes: every decline, or nothing at all |

Every row names the **condition** behind Theo's answer. When your condition is
different, the last column tells you which way to go.

---

## 🔑 Required accounts, keys, and setup

**This week runs on a local model, and the notebooks enforce it.** Both
sessions and the challenge's exploit steps read `INJECTION_MODEL` and
`INJECTION_API_BASE` from `.env`, never `LLM_MODEL`. They halt at Setup if
those are unset. Here is why, checked against the providers' current policies:

> Every major hosted provider's usage policy prohibits "circumventing
> safeguards" or (Anthropic's, verbatim) "prompt injection". There is **no
> carve-out for testing your own application**, even though their own developer
> guides tell you to red-team it. Enforcement is automated pattern-matching that
> cannot see whose system prompt is being attacked. On an enterprise Azure
> tenant, Prompt Shields flag exactly this week's content by default: direct
> attacks, role-play, encoding tricks, *and* instructions embedded in documents.
> Those flags feed abuse monitoring that throttles or **suspends the
> subscription**, and that subscription is your employer's. Nobody should lose
> an account for following the class. So attack-shaped prompts go to a model on
> your laptop, or to a gateway your firm has *explicitly* approved for this.
> Nothing else.

**Set it up (about fifteen minutes, once).** Four things, in this order.
Every step is the same on Windows, macOS and Linux unless a line says
otherwise; the commands are for a terminal (PowerShell on Windows). Where a
step installs something, do it before class: the downloads are the only part
that cannot happen live.

1. **Install Ollama**, the local model server, and pull a model that can
   **call tools** (the tool-description task needs it, which rules out Gemma
   through Ollama's tool API).

   | OS | Install |
   | --- | --- |
   | Windows | Download and run the installer from [ollama.com/download](https://ollama.com/download). It installs as a background service, so there is no `ollama serve` to run. Open a **new** terminal afterwards. |
   | macOS | `brew install ollama` and then `brew services start ollama`, or the installer from the same page. |
   | Linux | `curl -fsSL https://ollama.com/install.sh \| sh`, which also registers the service. |

   Then, from any folder:

   ```bash
   ollama pull qwen2.5:7b      # the default: best small-model tool calling, about 4.7 GB
   ollama pull qwen2.5:3b      # CPU-only laptop: faster, a little noisier
   ollama run qwen2.5:7b "Say ready"   # a one-line check that the server answers
   ```

2. **Tell the notebooks where it is.** Add these two lines to `.env` at the
   repo root (create the file from `.env.template` if you have not already).
   The `ollama_chat/` prefix is what makes LiteLLM pass tool calls through.
   Ollama needs no key.

   ```bash
   INJECTION_MODEL=ollama_chat/qwen2.5:7b
   INJECTION_API_BASE=http://localhost:11434
   ```

   Any other local OpenAI-compatible server works too (LM Studio, vLLM,
   llama.cpp): use `openai/<model id the server reports>` and the server's
   `/v1` URL, plus `INJECTION_API_KEY` if it wants one. So does a firm gateway
   approved *for adversarial testing specifically*. `.env.template` has every
   variant.

3. **Install Node.js 22.22 or newer** — S11 runs
   [promptfoo](https://www.promptfoo.dev/), an open-source test runner for LLM
   apps, through `npx`, which ships with Node. S12 does not need it.

   | OS | Install |
   | --- | --- |
   | Windows | `winget install OpenJS.NodeJS.LTS`, or the LTS installer from [nodejs.org](https://nodejs.org/en/download). Open a **new** terminal afterwards so `node` and `npx` are on your `PATH`. |
   | macOS | `brew install node` |
   | Linux | Your distribution's package, or the instructions on [nodejs.org](https://nodejs.org/en/download). |

   Then download promptfoo once, so class does not wait for it (about a
   minute; the `npm warn deprecated` lines it prints are harmless):

   ```bash
   node --version                          # v22.22 or newer
   npx -y promptfoo@0.125.1 --version      # prints 0.125.1
   ```

   The longer version of this step, per OS, is in
   [`00_Prerequisites/1_Your_Machine`](../00_Prerequisites/1_Your_Machine/README.md#-nodejs--needed-from-week-6).

4. **Open S11.** Setup prints `✅ attack target: ollama_chat/qwen2.5:7b …` and
   `✅ npx: …`, and you are ready. A ⚠️ on either line names the step above
   to redo. Press the buttons top to bottom; Task 4's two are the slow ones
   (the whole notebook is a few minutes on a laptop GPU, longer on CPU).

**S12 needs a little more.** Its Level 0 runs on recorded logits and needs no
model. The rest runs on [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails),
which the notebook's own header installs under `--sandbox` (from the root
environment, run `make setup-week W=6`).

- The classifier and topical rail embed text with all-MiniLM-L6-v2: about
  90 MB from Hugging Face on first use, cached in `~/.cache/fastembed`. If that
  download is blocked, Level 0 still runs, the cells after it fail at the
  download. Write that in `use_case/ecosystem.md` and ask for the download to be allowed.
- The judge and the answers go to the same `INJECTION_*` endpoint as S11. NeMo
  talks to it through its own OpenAI-compatible client, so you need no
  LangChain package.
- On an Unsloth server NeMo sends `enable_tools: false` in the request body.
  The judge's call is 93 prompt tokens with it and 1,449 without.

**What to expect from a small local model**, so nobody thinks their setup is
broken:

- Hand-written direct attacks land far more often than they do on a frontier
  API. That is the model's own alignment showing, and S11 makes it the week's
  second lesson.
- CPU-only laptops are slower. Both measurement cells have a run-count slider
  (default 8; drop to 4 live if the session is running long).
- The tool-description task may show a few rows where a 3B model answered in
  text instead of calling the tool. The cell handles it.
- S11's promptfoo runs four model calls at a time. A laptop server that handles
  one request at a time just queues them.

```bash
make nb F=06_Guardrails/sessions/S11_Prompt_Injection.py
make nb F=06_Guardrails/sessions/S12_The_Guardrail_Ladder.py
```

**On Windows, or anywhere `--sandbox` is blocked**, open them from the root
environment instead. The script installs the `week6` group (NeMo Guardrails)
into `.venv` with `uv sync --inexact --group week6` and starts marimo through
Python, so no new executable is ever spawned:

```powershell
uv run python scripts/nb.py 06_Guardrails\sessions\S11_Prompt_Injection.py
uv run python scripts/nb.py 06_Guardrails\sessions\S12_The_Guardrail_Ladder.py
```

The reasoning is in
[`00_Prerequisites/5_Your_Notebooks`](../00_Prerequisites/5_Your_Notebooks/README.md#two-ways-to-run-a-notebook).
Either route reads the same `.env`, so steps 1–3 above are needed once,
not per route.

### Before the sessions

- **Install Ollama and pull `qwen2.5:7b` (or `3b`) before class.** The pull is
  a few GB, and it is the one thing we cannot do live. If your firm blocks the
  download, write that in `use_case/ecosystem.md`. Your fallbacks are a gateway
  your firm has approved for adversarial testing, or a classmate whose laptop
  serves the model on the local network.
- **Install Node.js and run `npx -y promptfoo@0.125.1 --version` once.** S11
  needs both, and the first download is the slow part. If your firm blocks Node
  or the npm registry, note the block in `use_case/ecosystem.md` and pair with a
  classmate for the session; the challenge itself needs no promptfoo.
- **Play [Lakera Gandalf](https://gandalf.lakera.ai/)** for twenty minutes.
  It's fun! You talk a model into revealing a password across escalating
  defence levels. Note *which* defence finally stopped you: it is a rung on
  S12's ladder.
- **List every place untrusted text enters your system**, and next to each,
  who can write there. User input is the obvious one. The others: retrieved
  documents, file names, tool outputs, error messages, database fields another
  team fills in, anything a colleague can edit. S11's Task 3 and Question #2
  are much sharper against a real list.
- **Write down one output your system must never produce.** A customer
  identifier, a price commitment, a promise about delivery. S12 asks which rung
  would catch it.
- **Have your Week 4 golden set to hand.** We measure false positives against
  it.

---

## 📚 Recommended reading

S11's pre-reads come first, then S12's, then the texts behind both sessions.

- [Formalizing and Benchmarking Prompt Injection Attacks and Defenses](https://arxiv.org/abs/2310.12815), Liu et al. Before S11: the major attack surfaces and the defence classes, as a framework instead of a bag of tricks
- [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837), Beurer-Kellner et al., 2025. Before S11: architectural patterns that limit what a successful injection can reach. S11's Task 3 arrives at the same containment answer
- [Building Guardrails for Agents](https://openai.github.io/openai-agents-python/guardrails/), OpenAI Agents SDK. Before S12: where guardrails sit in an agent system and when each runs
- [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs), OpenAI. Before S12: constrained decoding as a hosted feature, which is Level 0 from behind a closed API
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073), Anthropic, 2022. Before S12: how explicit principles guide model behaviour, the layer below everything on the ladder
- [The Lethal Trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/), Simon Willison. Private data, untrusted content, a way out: the five-minute decision rule behind Question #4
- [Not What You've Signed Up For](https://arxiv.org/abs/2302.12173), Greshake et al., 2023. The paper that established indirect injection as a class of attack
- [Universal and Transferable Adversarial Attacks](https://arxiv.org/abs/2307.15043), Zou et al., 2023. Automated attack search, and evidence that attacks transfer between models. It is why S11's null result from a fragment search is weak evidence
- [Simon Willison's prompt injection archive](https://simonwillison.net/tags/prompt-injection/). Years of documented real cases; the three in S11's Task 3 came from here
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/). LLM01 is prompt injection. Your security team will use this vocabulary in the review
- [NeMo Guardrails](https://arxiv.org/abs/2310.10501), Rebedea et al., 2023. The toolkit S12 builds the ladder on: input, dialog and output rails, and why the dialog layer is programmable
- [Llama Guard](https://arxiv.org/abs/2312.06674). Level 2 done properly: a small model as a safety classifier, with the taxonomy explained
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework). The closest thing to a best-practice framework. It gives you a vocabulary (govern, map, measure, manage), not a checklist. The ladder table is the *measure* row

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

## 📊 What the notebooks measure

Notebooks ship without outputs, so the numbers live here for anyone reading on
GitHub.

### Session 11 — one document beats twenty-two attacks

**A canary makes success unambiguous.** A unique token in the system prompt
turns "did the attack work?" into a string comparison. Now hundreds of attempts
can be scored automatically.

**On a frontier model, direct injection bounced and indirect injection did
not.** One reference run on DeepSeek-V4-Flash: **0 of 22**
direct attempts leaked the canary (7 hand-written, 15 from the optimiser), each
refused cleanly. The same model, handed **one** poisoned document on an
innocent SLA question, **leaked on 10 of 12 runs**.

**Your local column will read differently. That is the second lesson.**
The notebooks run against a small open model on your laptop (see setup). It
has had far less adversarial training than a frontier API, so hand-written
attacks that bounce off the hosted model often land on it. The model's own
alignment is the rung below every guardrail on the ladder, and it varies
enormously between models. The gap between the two columns is a fact about
model choice, so it goes in your decision record. Your rates come from S11's
Tasks 2–4.

**Measured with the framework notebook** on Qwen3-4B (Q4_K_M, served by
Unsloth, thinking on, temperature 0.7), two runs of every button:

- Hand-written direct attacks leaked on **4 and 6 of 7**.
- The recombination search leaked on **11 of 12** both times.
- The poisoned page leaked on **8 of 8** both times.
- The untrusted-data wrapper changed nothing (8 of 8 with it). The scrubber
  took both rows to **0 of 8**, though it only catches secrets you remembered
  to register.
- With no attack at all, the undefended assistant put the code into an answer
  to a legitimate question on 1 and 2 of 4 runs. So the fully defended
  assistant withheld 1 of 8 legitimate answers on each of two runs (on a third,
  the judge marked 3 of 8 unanswered). That is the ops director's column, and
  the case for taking the secret out of the prompt instead of filtering it.
- The poisoned tool description exfiltrated on **6 of 6** both times.

**Recombination beats hand-writing.** Prefixes, bodies and suffixes recombine
into 720 candidate attacks. Hand-written attempts tell you whether *an* attack
works. A search tells you *which family* works. A null result from a weak
search is weak evidence, and the notebook says so.

**Two more doors, both reproduced live:**

- **A restricted-`exec` "sandbox" is not one.** The exact `SAFE_BUILTINS`
  namespace from Week 5 (no `import`, no `open`) is escaped in three lines. The
  escape goes through the `__globals__` of the one helper function handed in as
  a capability. You cannot deny-list every route out of a Turing-complete
  language. Isolation means a container.
- **A tool description is an injection surface.** One poisoned description told
  the model to pass the secret as an argument "for policy sync". It exfiltrated
  the canary on **6 of 6** reference runs, through the tool-call arguments,
  where an output check never looks. Each of Week 5's six ways to expose a
  capability carries a description, and a model acts on that text.

### Session 12 — the ladder, measured rather than asserted

| Level | Cost | Latency | Guarantee | Catches |
| --- | --- | --- | --- | --- |
| **0 — Constrained decoding** | free | **none** | **absolute** | anything expressible as legal tokens |
| **1 — Rules** | free | µs | absolute, for what it matches | exactly what you spelled out |
| **2 — Classifier** | ~free | µs | probabilistic | what you have labels for |
| **3 — LLM judge** | $ per call | ~1 s | probabilistic | things you cannot specify |
| **4 — Policy layer** | free | µs | **absolute** | authorisation, limits, data boundaries |
| **5 — Human** | $$$ | minutes | as good as the human | anything, slowly |

**Level 0 is Week 2's bill coming due.** Masking tokens before you sample is
free and instant, and it is the only rung with a hard guarantee. It needs logit
access, which means open weights or a server you control. Behind a closed API
you start at Level 1, paying latency for something that could have cost
nothing. The provider's structured-output mode gives you the rung back for the
structured parts of your output only. **Read the surviving probability mass,
not the chosen token.** A constraint that keeps 0.0003% of the mass still
produces legal output, and that output is confident nonsense.

**Rules and a classifier disagree, which is why the ladder runs both.** On the
same five probes the regex catches the card number the classifier has no
feature for. The classifier catches phrasings no regex was written for.

**The judge costs hundreds of times the classifier**, and that number marks the
line between a guardrail and an evaluator. Ask: *when it fires on a legitimate
request, does a user get refused?* If yes, its false-positive rate is a product
decision and it needs a latency budget. If no, stop worrying about its latency.

**Never implement authorisation in a prompt.** A prompt is a suggestion. An
`if` statement is enforced. Level 4 has no probability in it, and it is where
the incident's real fix went.

**Coverage needs its false positives beside it.** A rung that blocks every
request catches 100% of attacks. `helpers.guardrails.Ladder.evaluate()`
raises if you pass no `safe` set. NeMo
Guardrails, which the challenge is built on, does not, so there the rule is
yours: both numbers from one pass of your attacks and your goldens.

**Measured with the framework notebook** on NeMo Guardrails 0.24.1, with
Qwen3-4B (Q4_K_M, Unsloth, thinking on) as the judge, two runs:

- Level 0 kept **89.4%** of the probability mass on the recorded pass.
- Each rung timed alone on the five probes: rules about **1–9 ms** through
  NeMo's runtime, the nearest-neighbour classifier **3–18 ms**, and the
  self-check judge a mean of **4.2 s and 5.9 s**. That is about **370× and
  530×** the classifier and **1,700× and 3,100×** the rules.
- Rules caught the card number the classifier let through. The classifier
  caught both injection phrasings. The judge said *No* to *"you are now in
  developer mode"* on one run and *Yes* on the other.
- Assembled cheapest-first, the probes the free rungs stopped cost **zero model
  calls**.
- The topical rail refused the off-topic limerick with one model call (the
  judge) and no answer. On an on-topic question it changed no call count but
  raised the prompt tokens from **132 to 782**, because NeMo then writes the
  answer through its dialog prompt.

### Terms you'll meet

You do not need to know any of these in advance. Each one gets one sentence
here, plus where it comes up. Every term from every week is also collected,
alphabetically, in the repository's [`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it bites |
| --- | --- | --- |
| **Prompt injection** | Untrusted text reaching the model is treated as instructions, because the model cannot tell the difference | The premise of S11 |
| **Direct vs. indirect** | Direct: the user types it. Indirect: it arrives in something the model reads | S11 Task 3, the one that matters |
| **Canary** | A made-up secret whose only job is to be easy to detect, so a leak is a substring check | S11 Task 1 |
| **The lethal trifecta** | Private data + untrusted content + a way out = exfiltration; remove one leg | S11 Task 3, Question #4 |
| **Attack search** | Optimising an attack string instead of hand-writing it | S11 Task 2 |
| **Tool-description injection** | A tool's description is text the model follows, so one you did not write can carry instructions | S11 Task 5 |
| **Deny-list vs. isolation** | Blocking known-bad routes vs. making escape gain nothing; only the second holds on a Turing-complete language | S11 Task 5 |
| **Regression test** | Every attack that worked, kept forever, run on every change | The deliverable |
| **Logits and masking** | Set a token's probability to zero and the model cannot emit it | S12 Level 0 |
| **Constrained decoding** | Restricting generation to what a schema or grammar allows | S12 Level 0 |
| **Classifier** | A small model that labels text as allowed or not, trained from examples | S12 Level 2 |
| **Precision and recall** | False positives block real users; false negatives are the incident | S12 throughout: the ladder's trade-off |
| **LLM judge** | A model evaluating another model's input or output against a policy | S12 Level 3 |
| **Guardrail vs. evaluator** | In the request path and blocking, or after the fact on a sample | S12 Task 6 |
| **Policy layer** | Authorisation in code (role, limit, data class) with no probability in it | S12 Level 4 |
| **Fail closed** | A rung that errors blocks instead of allowing, so an outage cannot switch the guardrail off | S12 Tasks 3 and 6 |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions rarely use a syllabus's words.
This week is advertised as **red-teaming**,
**trust & safety**, or **AI security**. "Guardrails" appears less often than
the work does. Also look for "safety constraints" and "layered guardrails and
supervisory controls".

**Back to Week 2.** You wrote `top_k` by masking a distribution. Level 0 is the
same operation with a different rule, and it is only available because you have
the logits.

**Back to Week 3.** Your retrieval pipeline is the indirect injection surface.
S11's first question, *who can write to what it reads?*, is a question about
your corpus.

**Back to Week 4.** The winning attack becomes a permanent case in your
harness, as a scorer that runs it through your rails. **This is the
deliverable.** An attack you fixed but did not add to the harness can come
back, because Week 8 swaps the model, and a new model behaves differently. The golden set is also what the ladder's false positives are
measured against.

**Back to Week 5.** Code Mode's `SAFE_BUILTINS` was never a sandbox, and S11
escapes it. The six ways you built to expose a capability each carry a
description, and S11 poisons one.

**Forward to Week 8.** Voice pushes you *down* the ladder, because a one-second
judge is the whole latency budget. A smaller local model also gives you logit
access, so Level 0 reopens.

**Forward to Week 9.** "Never implement authorisation in a prompt" gets its
infrastructure. The policy layer is where data boundaries and approval limits
are enforced, and the ladder table becomes the guardrails section of your
deployment checklist.

**Forward to Week 10.** The vulnerability you found, and what you did about it,
is the security section of your final report: *"we found this, here is the
mitigation."*

### Where the industry is headed

**Prompt injection remains unsolved, so the serious work has moved to
containment.** The question is now "what can the model do once it has been
tricked?" The answers are architecture: scoped credentials, a human confirming
irreversible actions, and keeping the component that reads untrusted content
apart from the one that can act.

**Agentic systems widen the blast radius.** An injected chatbot says something
wrong. An injected agent with tools takes actions with your credentials.
Third-party tool descriptions are the supply-chain version of the problem.

**Constrained decoding is becoming a standard API feature.** More hosted
providers offer structured output, which moves Level 0 from "self-hosted only"
toward the default. That makes the cheapest guardrail the most widely available
one.

**Guardrails are becoming a compliance artifact.** Under regimes like the EU AI
Act, "what controls do you have and how do you know they work?" needs a
written answer. Your ladder table, false-positive column included, is a
draft of it.
