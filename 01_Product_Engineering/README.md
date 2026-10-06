<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Week 1 — Product Engineering</h1>
  <p><strong>☯️ Neither product nor engineering alone is enough</strong></p>
</div>

---

## 🎯 What you'll be able to do

Take a problem you actually have at work, pin it down until it is concrete enough
to build against, ship it as a container, and find out where inside your firm it
would really run.

> **⚠️ Do the [prerequisites](../00_Prerequisites/README.md) before Session 1.**
> Session 1 audits your machine and probes what your network allows — it needs a
> machine that is already set up in order to have anything to say.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S1 | [`Enterprise_Dev_Environment`](./sessions/S1_Enterprise_Dev_Environment.py) | A record of what your network allows, a real branch-and-push cycle, the repo's own checks, a model call that survives its provider being blocked, and a drill treating `CLAUDE.md` as source code. | Coming soon | Coming soon |
| S2 | **No notebook.** [Thinking like a product person](#-session-2--thinking-like-a-product-person) — a discussion built on [Getting to Concreteness](https://bit.ly/fde-concreteness) | A problem statement with a real user and a real cost, an honest answer to whether it needs an agent at all, and the argument for writing five correct answers by hand before any code exists. The written versions are the first four steps of the challenge. | Coming soon | Coming soon |

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC1 — Pin it down, build it, containerize it, place it**](./challenge/README.md) | Coming soon |

**To open the notebook**, from the repository root:

```bash
uv run marimo edit --sandbox 01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
```

A browser tab opens on `localhost`. (`make nb F=<that path>` is the same
command, if you have `make`.) The full walkthrough is in
[prerequisites guide 5](../00_Prerequisites/5_Your_Notebooks/README.md).

---

## 📖 Overview

This week is about two things that sound unrelated and are not: **picking the
right problem**, and **getting a small program to run somewhere other than your
own laptop.**

Most AI projects inside companies fail at one of those two ends. Either the
team builds something clever for a problem nobody actually has, or they find a
real problem and the prototype never leaves the notebook it was written in.
The whole week is a rehearsal for avoiding both, at small scale, on a problem
you already have at work.

**Session 1 is about your environment.** Before you can ship anything you need
to know what your company's network lets your laptop reach, how your work
becomes something a colleague can review, and how to talk to an AI model in a
way that keeps working when the vendor changes. None of it is hard. All of it
is the kind of thing that costs a week when it goes wrong later, and minutes
when you check it now. You will also spend real time on `CLAUDE.md` — a plain
text file that tells an AI coding assistant how your project works — because
writing one well is the single most useful habit this course teaches.

**Session 2 is about the idea, and there is no notebook.** It is a discussion,
and it asks you to think the way a product person thinks before you think the
way an engineer thinks: who exactly has this problem, what do they do about it
today, what does that cost them, and what would a correct answer look like —
written down, by hand, before any code exists. You will also ask an
unglamorous question most projects skip: *does this need an "agent" at all, or
is it a fixed sequence of steps?* Nothing gets typed in the session. Everything
discussed in it becomes the first four steps of the challenge, and the files
those steps produce are read by every week that follows.

**The challenge** puts it together: the charter, the contract, and five
hand-written examples in your `use_case/` folder; a tiny chat application
built against that contract and packaged so it runs anywhere; plus the
question no tutorial can answer for you — *where inside your firm would this
actually be deployed?* You go and ask. The application is deliberately small;
the thinking and the conversation are the assignment.

If you take one idea from this week: **evidence beats assumption.** Measure
what your network allows rather than guessing. Write the correct answer down
before building the thing that produces it. Ask where it will run before
building it for somewhere it cannot.

---

## 🔑 Required accounts, keys, and setup

Everything is covered in the [prerequisites](../00_Prerequisites/README.md):
Docker, VS Code, Git, Python 3.12+, uv, Claude Code, your repo, and a model.

Session 1 needs a model and makes **one** call, behind a button. Session 2
needs nothing but the form below, filled in. The command that opens the
notebook is under [Quicklinks](#-quicklinks) above.

> Each notebook ships with an `.ipynb` alongside it for anyone who can't install
> marimo. It is **generated** — edit the `.py`.

### Before the sessions

- **Do [Getting to Concreteness](https://bit.ly/fde-concreteness) before
  Session 2.** Forty minutes. It is a form, not code, and Session 2 is a
  discussion of *your* answers to it — a student who arrives without them has
  nothing to discuss. Its output is `use_case/CHARTER.md`, which the
  challenge's Step 4 fills in and which every later week reads.
- **Bring one real input.** A ticket, an email, a form, a document — something
  the problem in your charter actually starts from, with names removed. The
  discussion of what a "correct answer" looks like is much shorter with one in
  front of you.
- **Know what the work costs today.** Roughly how many times a day does the
  problem come up, and how long does one pass take a person? Two numbers, and
  they decide whether the thing is worth building before anyone builds it.

---

## 🧠 Session 2 — Thinking like a product person

There is no notebook for this session. Everything in it is a conversation
about the form you filled in, and about three things that have to be written
down before any code is worth writing. The challenge turns each of them into
a step; this section is what the discussion covers, so the room and the
challenge agree.

### Why "we should use AI for this" is not a specification

It has no input type, no output type, and no pass condition — so there is
nothing to build against and nothing to test. A product person's first job is
to turn that sentence into a problem that someone specific has, that costs
them something you can name, and that would be visibly solved if a particular
thing existed. Getting to Concreteness asks that in seven questions, and they
map onto the charter almost one-to-one:

| The question | What a concrete answer looks like | What a vague one looks like |
| --- | --- | --- |
| **Who has the problem?** | One role, and roughly how many of them — *"tier-2 support engineers, about twelve"* | A department — *"Customer Success"* |
| **What are they trying to do?** | The task, in their words — *"find which policy version applies to a ticket"* | Your solution, in disguise — *"get AI-powered answers"* |
| **How do they handle it today?** | The actual workaround — *"search three Confluence spaces by hand and ask on Slack"* | *"Manually"* |
| **What does that cost?** | A number with a unit — *"six minutes a ticket, forty tickets a day, and about one in ten answered from an old version"* | *"A lot of time"* |
| **The problem in one sentence** | No solution in it. If "AI", "chatbot" or "agent" appears, you wrote the answer and skipped the question | *"We need an AI assistant for support"* |
| **What does success look like?** | The new world for that person, and which of the firm's numbers moves | *"Better answers"* |
| **In → Out** | Specific enough that someone could build it wrong and you would notice — *"a ticket's text in; a two-sentence summary, an urgency level, and a needs-a-human flag out"* | *"Questions in, answers out"* |

The last row is the one to be pickiest about. It becomes a pair of types in
the challenge, an endpoint the week after, and the thing every later week
implements against.

### The three artifacts, and why they come before the code

**A contract.** The In → Out row, written as two types — what goes in with
its required and optional fields, and what comes back. Not for tidiness: a
type makes a change to any of those show up as a diff someone has to approve,
rather than a sentence quietly reinterpreted. The one field people leave out
is the way to say *no answer* — distinct from a low-confidence answer, because
one routes to a person and the other is shown with a caveat, and if the only
output is an answer, every failure is silently rendered as one.

**A decision about whether this needs an agent.** An agent decides its own
next step. That costs non-deterministic latency, a token bill that scales with
steps rather than requests, evaluation against traces instead of outputs, and
debugging where the same input takes a different path each run. Those costs
are worth paying when the control flow genuinely cannot be written in advance.
Four questions decide it — does the number of steps depend on the input, must
it call out to systems to answer at all, must it notice its own mistakes, is
the input open-ended — and for most enterprise use cases the honest count is
zero or one. *"We considered an agent and chose not to"* is a stronger
position than having built one.

**Five correct answers, written by hand.** Five input/output pairs where you
would accept the output — not fifty, and not generated. An example a model
produces encodes what the model already does, so scoring against it later
measures self-consistency and reports success for a system that is uniformly
wrong. A label you wrote is independent of the thing under test, which is the
only property that makes it a test. Five is enough because you will read every
failure individually; volume comes later, generated from these.

### Two numbers that decide whether it is worth building

Both can be estimated before any code exists: what a call costs in tokens,
and what the manual process it replaces costs in salaried minutes. Cost per
call × calls per day × 250 working days, against minutes per pass × loaded
hourly rate × the same volume. Above about twenty to one, the model cost is
noise and the effort belongs on quality; under three to one, the project is
hard to defend and it is much better to know that now than at deploy time.
The number that arithmetic does not show is **latency**: if the workflow it
replaces is a person glancing at something for six seconds, a twenty-second
answer will not be used no matter how good it is. Write the p95 you need down
before you build, not after someone has decided the thing feels slow.

### ❓ Questions for the room

These are Questions #5–8 for the week. They are not submitted and not graded;
each points at a step of the challenge.

| # | Question | Points at |
| :---: | --- | --- |
| 5 | Your output has a field for a low-confidence answer and a separate way to say *no answer*. What breaks downstream if those two collapse into one field — and which caller of your endpoint notices first? | Step 5 |
| 6 | An agent's token bill scales with **steps** rather than requests. Why does that make a cost estimate harder to defend for an agent than for a fixed pipeline? | Steps 6 and 13 |
| 7 | An example generated by the model encodes the model's current behaviour. Why would scoring against it report success for a system that is uniformly wrong — and what does that mean for the five you write by hand? | Step 7 |
| 8 | You have a cost-per-call figure and a p95 latency target. Which of the two is more likely to stop your application being used, and why is writing the latency number down *before* you build different from measuring it after? | Step 13 |

---

## 📚 Recommended reading

The first two close the gap between the Session 2 discussion and the
challenge steps it becomes. The rest are the canonical texts behind Session 1.

- [Building effective AI agents](https://www.anthropic.com/engineering/building-effective-agents) — **the agent-or-workflow decision the challenge's Step 6 asks for**, argued at length, and the best short piece on when *not* to build an agent. If you read one thing on this list, read this one
- [Why pydantic](https://docs.pydantic.dev/latest/why/) — **what a schema gives you that validation code does not**: the design argument behind the challenge's Step 5, not the API reference
- [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) — read before Session 1; Task 5 is this idea as a drill
- [Writing an effective `CLAUDE.md`](https://code.claude.com/docs/en/memory) — the file the agent loads before every session, on every machine
- [The Twelve-Factor App: Config](https://12factor.net/config) — two pages, written in 2011, and still the reason your keys are in the environment rather than the repository
- [LiteLLM: providers](https://docs.litellm.ai/docs/providers) — not a read-through. Skim it once to see how long the list is, which is the argument for using it

---

<!-- deliverables:start — this block also appears, word for word, at the top and bottom of challenge/README.md. Edit it in one place and copy; CI checks the three match -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A problem statement concrete enough to build against, the typed contract and
five hand-written examples that pin it down, and a containerized LLM
application with an endpoint that implements that contract.

Four questions are asked inside the Session 1 notebook as you work through it,
and four more are put to the room in Session 2. *They are not submitted and not
graded* — they are how you work out what the challenge is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | What the certificate issuer column predicts that the status column cannot | S1 |
| 2 | How `make check` can pass on a notebook that raises on cell three | S1 |
| 3 | Why an approved internal gateway costs one line in `.env`, and what a vendor SDK would have cost | S1 |
| 4 | What `/clear` reveals about a rule you wrote | S1 |
| 5 | What breaks when a low-confidence answer and *no answer* share one field | S2 discussion |
| 6 | Why a token bill that scales with steps is harder to defend than one that scales with requests | S2 discussion |
| 7 | Why scoring against a model-generated example reports success for a system that is uniformly wrong | S2 discussion |
| 8 | Whether cost or latency is more likely to stop your application being used | S2 discussion |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-3`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **`use_case/CHARTER.md` filled in** from the Getting to Concreteness form — no template text left
- [ ] **`Request` and `Response` types** in your app, with a `solve()` signature, matching the charter's In → Out row
- [ ] **The agent-or-pipeline decision** in `use_case/decisions.md`, with the option you rejected
- [ ] **Five golden examples, written by hand**, in `use_case/evals/golden.jsonl` — one an edge case, one a decline
- [ ] A second `@app.api` endpoint for your own work, running, implementing the contract
- [ ] The app running in a Docker container on your machine
- [ ] Your infrastructure answers — where this would actually live
- [ ] Vibe check, with the aspect named for every prompt
- [ ] `use_case/` updated and pushed to your repo

### 📤 Share

- [ ] **A demo to a real user, with their feedback recorded in your own words** — graded, and the one people skip
- [ ] **What you would swap to run this at work** — data, model or endpoint, and the approval you would need — three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## 📊 What the notebooks measure

The notebook's outputs are not stored in the repository — they are produced
when you run it — so this section is where the numbers live if you are reading
on GitHub. Session 2 has no notebook; its content is the section above.

**Your network is not neutral, and S1 measures how.** The probe resolves and TLS-
connects to seven hosts — PyPI *and the separate host its wheels download
from*, OpenAI, jsDelivr, Hugging Face, Docker Hub, GitHub — and reports the
**certificate issuer** for each. The PyPI pair matters: an allowlist that
permits `pypi.org` and forgets `files.pythonhosted.org` resolves, connects, and
then fails every install. On a managed laptop the issuer column names your own
employer rather than DigiCert, which is TLS interception stated as a fact rather
than a suspicion. Three outcomes are possible and each means
something different:

| What you see | What it means |
| --- | --- |
| All seven reachable, public CAs | Open network. Nothing here will bite you |
| Reachable, but signed by your employer | TLS is intercepted. Expect certificate errors from tools that ignore the system trust store |
| Some hosts fail | You are behind an allowlist. Note exactly which — Weeks 2, 8, and 9 need those hosts |

**That table is the deliverable**, not the notebook. It goes into
`use_case/ecosystem.md` and it is the single most useful thing to put in front of
an infrastructure team, because it is measured rather than assumed.

**Configuration validated where it is loaded, not where it is used.** S1 calls
`bootstrap()` with a deliberately missing key so you see the failure arrive at
startup with a readable message, instead of forty minutes into a run.

**One call, two providers, zero code changes.** Point `LLM_MODEL` at a different
vendor and the same cell works. This is what makes the egress result survivable:
if the probe shows no route to `api.openai.com` and an approved internal gateway
instead, that costs one line in `.env` rather than every call site.

### Terms you'll meet

You do not need to know any of these in advance. This is what each one means
in one sentence, and where it comes up. Every term from every week is also
collected, alphabetically, in the repository's [`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it bites |
| --- | --- | --- |
| **TLS and certificate chains** | Your client trusts a server because a certificate authority it already trusts signed that server's certificate | S1 Task 1 — the "Signed by" column |
| **TLS interception** | A corporate proxy terminates your encrypted connection, reads it, and re-signs it with the firm's own CA | S1 Task 1, and every failed `pip install` for the rest of your career |
| **CA bundle** | The list of authorities your tools trust; Python's is not your operating system's | The remediation you will need if Task 1 shows your employer's name |
| **origin and upstream** | Your fork is where you push; the course repository is where you pull updates from. Different remotes, different jobs | S1 Task 2 |
| **Generated artifacts** | A file built from another file is never hand-edited or hand-merged — it is regenerated | S1 Task 2, and the only correct way to resolve an `.ipynb` conflict |
| **Provider abstraction** | One calling convention over many model vendors, so the vendor is a config value | S1 Task 4 |
| **A schema as a contract** | The same type definition used by the API, the tests, and the eval harness, so they cannot disagree | S2 discussion, and TC1 Step 5 |
| **Agent vs. pipeline** | An agent decides its own next step; a pipeline follows the steps you wrote | S2 discussion, which is the argument of that session, and TC1 Step 6 |
| **Golden examples** | Inputs paired with outputs a human judged correct, written before any system exists | S2 discussion, and TC1 Step 7 |
| **Unit economics** | Cost per request × requests, against the cost of the work being replaced | S2 discussion, and TC1 Step 13 |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions call it
**forward-deployed engineering**, or **applied AI / solutions engineering** —
someone who can take a vague problem and deliver a working system into
infrastructure they do not own. That is this week.

Four things you write down this week are picked up by later weeks:

**Forward to Week 9** — the infrastructure answers you gather in the
challenge's Step 10 go in `use_case/ecosystem.md`. **Week 9 picks up that
exact file** and finishes it.

**Forward to Weeks 2, 4, and 8** — your typed schema and five golden examples,
written in the challenge's Steps 5 and 7. Week 2 generates data matching the
schema, Week 4 scores against the goldens, and Week 8 has to beat Week 4's
numbers. You do not redesign the schema later; you implement it, and not
changing it is part of the lesson.

**Forward to Week 5** — the agent-or-pipeline verdict from Step 6 is the first
row of `use_case/decisions.md`, and Week 5 asks you to defend it out loud.

**Forward to Week 10** — everyone you talk to goes in `use_case/stakeholders.md`,
and **Week 10's final deliverable is a report to those people**; a distribution
list of one is a thin ending to ten weeks. The napkin math from Step 13 is where
that report's cost section starts, and the three "what you would swap" lines you
add each week are its list of what it would take to run for real.

**One use case, all ten weeks, no restarts.** Choose carefully; you are going to
live with it.

### Where the industry is headed

**Managed laptops are getting more managed, not less.** Interception, endpoint
agents, and egress allow-lists are becoming the default posture rather than the
regulated exception. The engineers who get unblocked are the ones who can produce
evidence about their own environment rather than a report that "it doesn't work"
— because they have handed someone a ticket that can be actioned.

**Provider portability is becoming the norm.** Picking a model vendor is turning
from an architecture decision into a routing decision, made per request, on cost
and latency and what your compliance team approved this quarter. Code that
hardcodes a vendor is code that will be rewritten.

**"Agentic" is being applied to things that are not agents,** and the gap is a
real source of failed projects. Being able to say *"we considered an agent and
chose not to"* is a stronger position than having built one, and it is getting
stronger as the first wave of agent deployments reports back.
