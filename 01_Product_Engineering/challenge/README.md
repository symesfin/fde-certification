<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Technical Challenge 1</h1>
  <p><strong>Pin the problem down. Build it. Containerize it. Find out where it actually goes.</strong></p>
</div>

---

## Overview

Most "build your first LLM app" tutorials end at a public URL. That is where
this one starts getting interesting.

You are going to pin a real problem from your own work down until it is
concrete enough to build against, write the contract for it before any code
exists, build a working chat application against that contract, put it in a
Docker container, and then go ask a question no tutorial can answer for you:

> **"Where should I deploy this so it has visibility across the firm?"**

The application is small on purpose. **The problem statement and the
deployment question are the assignment.**

> 💡 **You already know enough to be dangerous.** Session 1 gave you the
> evidence-gathering habit, the branch-and-push cycle, the API surface, and the
> container. Session 2 gave you the product questions — who has the problem,
> what it costs them, what a correct answer looks like — and the discussion of
> why a schema and five hand-written examples are worth more than any amount of
> code. This is where you put it together.

<table>
  <tr>
    <td width="120"><strong>Outcome</strong></td>
    <td>A charter, a typed contract, and five golden examples in <code>use_case/</code>; a containerized LLM application running on your machine with an endpoint that implements the contract; and a real answer about where it would be deployed.</td>
  </tr>
  <tr>
    <td><strong>Tools</strong></td>
    <td>VS Code, Claude Code, Docker, Gradio, LiteLLM, pydantic.</td>
  </tr>
  <tr>
    <td><strong>Due</strong></td>
    <td>End of the week. Post your repo link in the Maven Community.</td>
  </tr>
  <tr>
    <td><strong>Before you start</strong></td>
    <td>The <a href="../../00_Prerequisites/README.md">prerequisites</a> — tooling, Claude Code, your repo, a model — and the <a href="https://bit.ly/fde-concreteness">Getting to Concreteness</a> form, which Step 4 turns into your charter.</td>
  </tr>
</table>

---

<!-- deliverables:start — this block also appears, word for word, in the week README and twice in this file. Edit it in one place and copy; CI checks the three match -->
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

## 📖 Official documentation

Everything this challenge uses, from the people who maintain it.

| Tool | What you use it for here | Docs |
| --- | --- | --- |
| Gradio | `gradio.Server` and the `@app.api` endpoint you write | [gradio.app/docs](https://www.gradio.app/docs) |
| pydantic | the `Request` and `Response` types that are your contract | [pydantic.dev/docs](https://pydantic.dev/docs/validation/latest/concepts/models/) |
| LiteLLM | the model call, so the provider stays configuration | [docs.litellm.ai](https://docs.litellm.ai/) |
| Docker | building the image you hand to someone else | [docs.docker.com](https://docs.docker.com/) |
| Claude Code | the agent, and the `CLAUDE.md` that steers it | [code.claude.com/docs](https://code.claude.com/docs/en/overview) |
| uv | running the app and its dependencies | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |

---

## Setting Expectations

**Budget eight to ten hours**, spread across the week rather than done in one
sitting — because one step depends on somebody else replying to you, and the
first four are thinking, not typing.

| Step | What it is | Rough time |
| :---: | --- | --- |
| 2 | Read `CLAUDE.md` | 15 min |
| 3 | Run it locally | 10 min |
| 4 | Pin the problem down — the charter | 40 min |
| 5 | Write the contract — `Request`, `Response`, `solve()` | 30 min |
| 6 | Decide whether it needs an agent | 20 min |
| 7 | Five golden examples, by hand | 45 min |
| 8 | Build your endpoint | 2–3 hrs |
| 9 | Containerize it | 30 min |
| **10** | **Where does this live?** | **30 min of your time, days of waiting** |
| 11 | Vibe check | 45 min |
| 12 | Demo to a real user | 30 min, plus their calendar |
| 13 | Share: bring it to work | 30 min |

> **Start Step 10 first and finish it last.** It is the only step gated on
> someone else's calendar, and it is the reason this course exists. Send the
> message today; do Steps 4–7 while you wait, and do not open the code before
> Step 7 is done. Every week from here reads what you write in those four
> steps, and none of them can be reconstructed later.

The work you are doing this week — scoping a real problem, building something
that addresses it, and engineering it to survive contact with a real firm's
infrastructure — is the work. It is also exactly the shape of the projects
that get funded inside firms.

---

## What you are building

| File | Role |
| --- | --- |
| `use_case/CHARTER.md` | The problem, the user, the success measure, and In → Out. **Every later week reads it** |
| `schema.py` (yours, in `challenge/`) | `Request`, `Response`, and the `solve()` signature — the contract |
| `use_case/decisions.md` | The agent-or-pipeline row, with what you rejected |
| `use_case/evals/golden.jsonl` | Five input/output pairs you wrote by hand. **The bar for the next nine weeks** |
| `llm.py` | The model call. Provider-agnostic. Streams. |
| `app.py` | `gradio.Server` — a FastAPI app with Gradio's API engine inside. |
| `frontend/index.html` | The UI. Plain on purpose. **Yours to improve.** |
| `Dockerfile` | The deployment artifact. |
| `CLAUDE.md` | The instructions Claude Code reads before it touches anything. |

> The API is the product; the UI is disposable. That split is deliberate.
> `gradio.Server` is a FastAPI application with Gradio's API engine inside it —
> you get queueing, streaming, and a published schema; you supply the interface.

`CLAUDE.md` puts Claude Code into **instructor mode** for this directory: it
will explain, debug, and review, and it will decline to write your charter,
your schema, your golden examples or your endpoint. That is deliberate. The
charter and the goldens look like writing, so it feels harmless to have them
drafted. They are the analysis the next nine weeks are built on.

### Steps 0 and 1 — done before you get here

Installing the tooling and getting your own copy of the repo are covered by the
[**prerequisites**](../../00_Prerequisites/README.md), because Session 1
*verifies* your machine — and discovering in class that nothing is installed
wastes the session.

Confirm you are ready:

```bash
./00_Prerequisites/scripts/setup_check.sh        # macOS / Linux / WSL
```
```powershell
.\00_Prerequisites\scripts\setup_check.ps1       # Windows PowerShell
```

---

## Step 2 — Read `CLAUDE.md` before you write any code

Open [`CLAUDE.md`](./CLAUDE.md). Claude Code reads it automatically at the start
of every session. It is how the agent knows what this project is, what the
conventions are, and which mistakes to avoid.

**This is the highest-leverage file in the repo.** When Claude Code keeps making
the same wrong assumption, the fix is almost always one line here, not a longer
prompt.

> ⚠️ It also puts Claude Code into **instructor mode**: it will explain, debug,
> review, and teach, and it will decline to write the graded parts for you. That
> is deliberate. Ask it to explain anything as many times as you want — it will
> just make you type the endpoint.

### ✅ Deliverables

1. You have read `CLAUDE.md`, including the Gotchas section.
2. By the end of this challenge, **at least one rule you wrote** has been added
   to it — a real one you learned from watching the agent get something wrong.

---

## Step 3 — Run it locally

Already done in the [prerequisites](../../00_Prerequisites/3_Clone_and_Run/README.md).
Bring it back up:

```powershell
cd 01_Product_Engineering/challenge
uv run python app.py
```

`uv run` builds the environment from this directory's `pyproject.toml` and
`uv.lock` the first time, so there is no virtualenv for you to create or
remember to activate.

<http://localhost:7860> is the chat window. <http://localhost:7860/health> is the
health endpoint, which exists because every load balancer on earth will ask for
one.

> **Gradio also prints `http://0.0.0.0:7860`. Do not open that one.** `0.0.0.0`
> means "bound to every interface" — it is an address to listen on, not one to
> visit. Windows browsers reject it outright; macOS and Linux quietly redirect
> it to `localhost`, which is why it only looks broken on some machines.

> **Chat box loads but nothing comes back?** Open the browser console before you
> debug the backend. The frontend fetches `@gradio/client` from a CDN, and on a
> network that blocks it the page renders perfectly and does nothing. Step 9
> comes back to this.

---

## 🧭 Step 4 — Pin the problem down

> 🧑‍💼 **You are a product person before you are an engineer.** Session 2 was
> the discussion; this is the written version of it, and it is the input to
> everything else this week.

"We should use AI for this" is not a specification. It has no input type, no
output type, and no pass condition — so there is nothing to build against and
nothing to test. This step converts it into a problem statement with a real
user, a real cost, and a success measure someone could disagree with.

> 📝 **Step 4: Complete [Getting to Concreteness](https://bit.ly/fde-concreteness), then fill in `use_case/CHARTER.md` from it**
>
> *Hints:*
>
> - *Work through the form first. Its questions map onto the charter almost
>   one-to-one, and it is faster to do it there and copy across than to stare
>   at the template.*
> - *One real role, not a department. "Tier-2 support engineers, about twelve
>   of them" is a user. "Customer Success" is an org chart.*
> - *The problem sentence has no solution in it. If the word "AI", "chatbot" or
>   "agent" appears in it, you have written the answer and skipped the question.*
> - *How do they handle it today, and what does that cost? If you do not know,
>   the person from your charter does — asking them is Step 12's first
>   conversation, started early.*

The charter's last table — **In → Out** — is the one to be pickiest about.
*"Be specific enough that someone could build it wrong and you would notice."*
That row becomes a pair of types in Step 5, an endpoint in Step 8, and the
thing every later week implements against. Vague here is expensive for nine
weeks.

### ✅ Deliverables

1. **`use_case/CHARTER.md` with no template text left** — every
   `<!-- your answer here -->` replaced. Every later challenge opens by
   linking this file, and Week 2 builds its validator from the In → Out row.
2. **The problem in one sentence**, with no solution in it, that you could say
   out loud to the person who has the problem without them correcting you.

---

## 📐 Step 5 — Write the contract

> 🧑‍💻 **You are an AI Systems Engineer.** Two decisions are cheap now and
> expensive to reverse: the shape of what goes in and comes out, and whether
> the control flow has to be decided while the thing is running. This step is
> the first.

Your charter ends with In → Out written in prose. Turn it into two classes.

The reason is not tidiness. A type says which fields are required, which are
optional, and what the caller gets back — so a change to any of those shows up
as a diff someone has to approve, rather than as a sentence quietly
reinterpreted. It also gives you somewhere to put validation, and something for
your golden examples to be instances *of*.

> 📝 **Step 5: Write `Request`, `Response` and a `solve()` signature for your use case**
>
> *Hints:*
>
> - *Required fields have no defaults; optional fields do. An output should
>   include something the caller can act on, not just text.*
> - *Your `Response` needs a way to say **no answer** that is distinct from a
>   low-confidence answer. Those two are handled differently downstream — one
>   routes to a person, the other is shown with a caveat — and if the only
>   output is an answer, every failure is silently rendered as one.*
> - *Write the signature before the implementation. `solve()` raises
>   `NotImplementedError` this week; that is the point. Building it in Step 8
>   is then a build task instead of a design task.*

Here is the shape, for a support-ticket triager. Yours will not be a triager;
what should carry over is the structure:

```python
from pydantic import BaseModel, Field

class Request(BaseModel):
    """What the user or system hands in."""
    ticket_text: str = Field(description="The raw customer message")
    product_area: str | None = Field(default=None, description="If already known")

class Response(BaseModel):
    """What comes back."""
    summary: str = Field(description="Two sentences a human can act on")
    urgency: str = Field(description="one of: low, normal, high")
    needs_human: bool = Field(description="True when the model should not decide")

def solve(request: Request) -> Response:
    """The whole product, as one function signature."""
    raise NotImplementedError("implement against this signature")
```

Note `needs_human`. That is the *no answer* field, and it is the one people
leave out.

### ✅ Deliverables

1. **`schema.py` in `challenge/`** — `Request`, `Response`, and `solve()`
   with a docstring, importing cleanly (`uv run python -c "import schema"`).
2. **The charter's In → Out row updated** if writing the types changed your
   mind about a field. It usually does; that is the step working.

---

## 🔀 Step 6 — Decide whether it needs an agent

> 🧑‍💻 **You are an AI Systems Engineer.** The second decision that is cheap
> now and expensive later.

An agent decides its own next step. Compared with a fixed pipeline that costs
you: non-deterministic latency, a token bill that scales with steps rather than
requests, evaluation against traces instead of outputs, and debugging where the
same input takes a different path each run.

Those costs are worth paying when the control flow genuinely cannot be written
in advance. Most enterprise use cases can be — they are a function with good
retrieval in front of it. Deciding this now is cheap; discovering it after you
have built an agent harness is not.

> 📝 **Step 6: Answer four questions about your use case, honestly, and write the verdict down**

| # | True of your use case? |
| :---: | --- |
| 1 | The number of steps depends on the input — you cannot draw the flowchart in advance |
| 2 | It must call out to systems (search, database, API) to answer at all |
| 3 | It has to notice its own mistakes and try something else |
| 4 | The input is open-ended — you cannot enumerate the cases |

| Count | Verdict | What to do |
| :---: | --- | --- |
| 3–4 | **Agentic — probably genuinely** | Build it as an agent — but build the non-agentic version first and keep it. It is your baseline, and *"the agent beat a single prompt by 12 points"* is an argument. *"The agent works"* is not |
| 2 | **Borderline — start simpler** | Build the single-call version with good retrieval. Add agency only where you can point at a specific failure it fixes. You can always add a loop; removing one after a stakeholder has seen it is much harder |
| 0–1 | **A function, not an agent** | A well-scoped function with solid retrieval has deterministic control flow, a fixed token cost per request, and outputs you can diff against expected values. Cheaper to run and considerably easier to get approved. Nothing downstream changes — retrieval, evals, guardrails, memory and deployment all apply to a function too |

Then argue the other side. Write the strongest case for the *opposite* verdict
in two or three sentences, in good faith, and name the one piece of evidence
that would make you switch. A design review will do this to you in Week 5; it
is cheaper to do it to yourself first.

### ✅ Deliverables

1. **A row in `use_case/decisions.md`**, all five columns: the verdict, the
   option you rejected, why, and what would change your mind.
2. **The strongest counter-argument**, two or three sentences, in the same row
   or beneath it.

---

## 🎯 Step 7 — Five golden examples, written by hand

> 🔬 **You are an AI Evaluation & Performance Engineer.** Nothing has been
> built yet, and this is the right moment to write down what correct looks
> like — before anything exists that could influence you.

Five input/output pairs, written by **you**, where you would accept the output.
Not fifty. Not generated.

Hand-written matters for a specific reason: an example produced by the model
encodes the model's current behaviour, so scoring against it measures
self-consistency and will report success for a system that is uniformly wrong.
A label you wrote is independent of the thing under test, which is the only
property that makes it a test.

Five is enough because you will read every failure individually. Volume comes
later, from generation seeded by these.

> 📝 **Step 7: Write five examples into `use_case/evals/golden.jsonl`, one per line**
>
> *Hints:*
>
> - *Use real inputs from your work, with names and identifiers removed. Each
>   `input` is an instance of your `Request`; each `output` is what you would
>   actually accept as its `Response` — not an idealised one.*
> - *Make at least one an edge case, and at least one where the right answer is
>   "I don't know" or "escalate this". A system that never declines is not
>   calibrated, it is just confident.*
> - *The `why` field is the one that earns its keep. It is what a judge gets
>   calibrated against in Week 4.*

```json
{"input": "...", "output": "...", "why": "what makes this the right answer"}
```

| What reads this file | What it does with them |
| --- | --- |
| Synthetic data generation | Seeds, and the axes your generated rows vary along |
| Your eval harness | The cases you score against, and what calibrates a judge |
| Security regressions | Injection attacks that worked get added next to them |
| A model swap | **The bar** — a cheaper or open model must pass the same harness |

> **Write the sixth one too, if you can find it** — the input where you
> genuinely do not know what the right output is. That ambiguity is real, it
> will not go away, and finding it now is much cheaper than a stakeholder
> finding it in a demo. Put it in the file with `"why": "unresolved — ..."`.

### ✅ Deliverables

1. **`use_case/evals/golden.jsonl`** — five lines, no `REPLACE ME` left,
   each with a `why`. Weeks 2 and 4 stop at their first cell if this is still
   the template.
2. **One line in your README** saying which example is the edge case and which
   is the decline.

---

## Step 8 — Build something real

> 🧑‍💻 **You are an AI Systems Engineer.** The problem statement is written; your
> job is to turn it into a working interface someone could actually call.

The app you have is a generic chat box. By the end of this step it should do one
thing that is specific to your job.

> 📝 **Step 8: Add a second `@app.api` endpoint for your own use case**
>
> *Hints:*
>
> - *The `Request` and `Response` types you wrote in Step 5 are the
>   specification for this endpoint. You already decided what goes in and what
>   comes out — this is that decision, running.*
> - *What would you name it if an agent had to pick it from a list of tools?
>   `summarize_ticket(ticket: str)` beats `process(text: str)`, and being able to
>   say why is the point.*
> - ***You write this one.*** *Claude Code will help you design it, explain
>   anything, and tell you why your code is broken. It will not write it for you.*

Here is the shape, not the answer:

```python
@app.api(name="...")           # what would an agent call this?
def ...(...) -> str:           # the -> str is required; see CLAUDE.md
    """What it does. This becomes the tool description later."""
    # build your prompt from the arguments,
    # then stream the reply back using stream_reply() from llm.py
```

### Four details carry the weight, and none of them are the body

| Detail | Why it is load-bearing |
| --- | --- |
| `name=` | The identifier something else selects this by. It is the difference between a caller picking correctly and picking at random |
| Typed arguments | The schema. A caller discovers what to send without reading your source |
| `-> str` | **Required.** The return annotation is what the schema is built from. Omit it and the endpoint is untyped — it will run, and it will return nothing |
| The docstring | The description a caller reads to decide whether this is the right thing to call at all |

### The naming test

> *If I had ten of these in a list, knew nothing else about any of them, and had
> to pick the right one — would I?*

| ❌ Weak | ✅ Strong | What changed |
| --- | --- | --- |
| `process(text: str)` | `summarize_ticket(ticket: str)` | The verb says what happens; the parameter says what kind of thing it wants |
| `run(data: str)` | `extract_invoice_fields(invoice_text: str)` | A caller can tell from the name alone whether this is the right tool |
| `handler(x: str)` | `draft_reply_from_template(customer_message: str)` | No abbreviation a reader has to decode |

> **Why this is required.** Later in the course you will expose endpoints like
> this as MCP tools — `gradio.Server` supports that natively and the decorator
> stacks on top of `@app.api`. An endpoint with a clear name, typed arguments,
> and a real docstring becomes a tool an agent can call. A chat box does not
> become anything.

Two things to leave alone this week: authentication and databases. They are
coming, and doing them now teaches the wrong lesson.

### ✅ Deliverables

1. **A second `@app.api` endpoint** that does something specific to your work —
   summarize a document, extract fields from a form, classify a ticket, draft a
   reply. It runs, it returns something useful, and its arguments and return
   match the `Request` and `Response` types from Step 5.
2. **A written answer to four questions**, in your repo:
   1. What is one thing you do at work this could take over?
   2. What exactly goes in — a string, a file, several fields?
   3. What comes back, and who reads it?
   4. What did you name it, and why would an agent pick it correctly?
3. **The endpoint has a place in the UI.** It does not have to be pretty; it has
   to work.
4. **The frontend is meaningfully yours** — restyled, or given a system-prompt
   box, or showing which model is answering, or handling errors visibly. Pick
   what matters for your use case, not all of them.

---

## Step 9 — Containerize it

> 🧑‍💻 **You are an AI Systems Engineer.** Your laptop is not a deployment target.

> 📝 **Step 9: Build the image and run your app from inside it**
>
> *Hints:*
>
> - *Read the [`Dockerfile`](./Dockerfile) before you build. Every line is
>   commented, and four of its choices are ones you will have to defend in a
>   real review.*
> - *The key is not in the image — it arrives at runtime. Anyone who can pull an
>   image can read anything baked into it.*

```powershell
docker build -t challenge .
docker run -p 7860:7860 --env-file ../../.env challenge
```

Open <http://localhost:7860> again. Same app, now in a container.

> **The `../../` is not a typo.** There is one `.env`, at the repository root,
> and `--env-file` resolves it against your working directory — which is
> `challenge/`. This is also the moment the container stops being able to find
> it on its own: outside Docker the app picks the file up from the repository
> tree, and inside there is no tree, so the key has to be handed in explicitly.

### Four choices you will be asked to defend

Read [`Dockerfile`](./Dockerfile) properly before you build. Every line is
commented; these four come up in every real review.

| Choice | Why a reviewer asks |
| --- | --- |
| **The key is not in the image.** It arrives at runtime via `--env-file` | Anyone who can pull an image can read anything baked into it. A secret in a layer is in every copy of that image, permanently, including the ones you deleted |
| **It does not run as root.** `useradd`, then `USER appuser` | The first thing a container scanner flags. A process that does not need root should not have it |
| **Dependencies are copied and installed before the code** | Docker caches layers. Put the thing that rarely changes first and rebuilds drop from minutes to seconds |
| **It installs from `uv.lock`, not `pyproject.toml`** | `pyproject` says `gradio>=6.0`, which resolves to whatever is newest on the day you build. An image built today and one built next month would be different applications wearing the same tag |

### 🔎 Notice what just broke

Look at `frontend/index.html`. It loads the Gradio client from a **public CDN**.

On your laptop, fine. Inside a firm that blocks external CDNs, the page loads and
silently does nothing. You now have a working app with a dependency on the open
internet that you did not choose deliberately.

That is the single most common way a demo that worked dies on contact with a
corporate network. It also connects straight back to your egress evidence: if
the probe showed a CDN host unreachable, you measured this failure before you
met it.

The fix is to vendor the library into the image and serve it from your own
application. One line in the Dockerfile, and an entire class of "it worked in
the demo" incident goes away.

> **The general shape of the lesson:** every external host your application
> reaches at *runtime* is a dependency you have to justify to somebody. A host
> it reaches at *build* time is one you only have to justify once.

Hold the thought — Step 10 is about to make it concrete.

### ✅ Deliverables

1. **The app runs in a Docker container on your machine**, reachable at
   `localhost:7860`.
2. **One paragraph** naming the CDN dependency and what you would do about it on
   a network that blocks it.
3. **One or two sentences** on what a container image captures that a virtual
   environment does not — and why that difference is what makes the image the
   thing you hand to a platform team.

---

## 🧯 If it's blocked

Everything below was hit on a real managed laptop while writing this challenge.
None of it means you did anything wrong.

### Docker will not start

`Docker Desktop is unable to start`, or `open \\.\pipe\dockerBackendApiServer:
Access is denied.` — almost always a backend process an update left running,
not another user. Quit Docker Desktop, then:

```powershell
Get-Process -Name "Docker Desktop","com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force
wsl --shutdown
```

Relaunch and wait for **Engine running**. Signing out of Windows, or a reboot,
clears it if that does not.

### Docker Desktop is not allowed on your machine

[Rancher Desktop](https://rancherdesktop.io/) and
[Podman Desktop](https://podman-desktop.io/) run the same containers and are far
easier to get approved; `alias docker=podman` is close to a drop-in. The
prerequisites cover this in
[1 · Your machine](../../00_Prerequisites/1_Your_Machine/README.md).

**Write down which one you had to use** in
[`use_case/ecosystem.md`](../../use_case/ecosystem.md). It is a real constraint
on how your application ships, and the deployment checklist later asks.

### `An Application Control policy has blocked this file`

An import dies with something like:

```
ImportError: DLL load failed while importing _bounded_integers:
An Application Control policy has blocked this file.
```

Your machine enforces code integrity — WDAC on most managed Windows laptops —
and a freshly downloaded compiled Python extension carries no signature it
trusts. It can be **intermittent**: the same import may succeed on a second
attempt once a reputation lookup completes. That is worse than a clean failure,
because nobody else can reproduce your bug report.

Find out what blocked it rather than guessing:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 20 |
  Format-List TimeCreated, Id, Message
```

Events **3033** and **3077** name the blocked file and, more usefully, a
**policy ID**. That ID is what whoever owns endpoint security at your firm needs
in order to tell you whether this is deliberate and what the exception process
is. Both belong in [`use_case/ecosystem.md`](../../use_case/ecosystem.md).

This is the whole exercise in miniature: the interesting output of a blocked
tool is not the workaround, it is the name of the thing doing the blocking and
the name of the person who owns it.

### Port 7860 is already in use

```powershell
$env:GRADIO_SERVER_PORT=7861; uv run python app.py
```

---

## 🎯 Step 10 — Where does this actually live?

> 🧑‍💼 **You are an AI Solutions Engineer.** This is not a coding step. It is the
> one that decides whether anything you build here ever runs anywhere.

> **This step is required, and it is the reason the course exists.** It is also
> the only step that depends on someone else's calendar — **start it first,
> finish it last.**

You have a container. A container has to run *somewhere*, and at your firm that
somewhere already exists, already has rules, and already has an owner.

> 📝 **Step 10: Find the person who owns deployment, and ask them these questions**
>
> *Hints:*
>
> - *Your manager, your platform team, your cloud team, or whoever answers in the
>   `#infrastructure` channel.*
> - *You are not expected to know these answers. You are expected to go get them.*
> - *"Unknown — asked X on the 14th" is a valid answer. A blank is not.*

Open with something like:

> *"If I had a small internal Python web app in a Docker container and I wanted
> people across the firm to be able to use it, where would it run? What would I
> have to do to get it there?"*

Then work through this list with them.

| # | Question | Why it decides things |
| :---: | --- | --- |
| 1 | **Where do internal apps run?** Kubernetes, ECS, App Service, a VM someone maintains? | Determines whether your Dockerfile is enough or you need Helm charts, task definitions, or a pipeline. |
| 2 | **Which cloud?** AWS, Azure, GCP, on-prem, or several? | Everything downstream — identity, secrets, networking — follows from this. |
| 3 | **Is there an internal container registry?** | You almost certainly cannot pull from Docker Hub in production. Where does your image get pushed? |
| 4 | **How do users log in?** Okta, Entra ID, Ping, SAML, something homegrown? | Right now your app has no auth. "Visibility across the firm" and "no authentication" cannot both be true. |
| 5 | **Can the app reach the internet?** Egress proxy? Allowlist? | If you cannot reach `api.openai.com`, your architecture changes completely. This is why `llm.py` is provider-agnostic. |
| 6 | **Where do secrets come from?** Vault, Secrets Manager, Key Vault, a config service? | `--env-file` works on a laptop and nowhere else. |
| 7 | **Who approves a deployment?** What review does it need before real users? | This is your actual timeline, and it is usually longer than the build. |
| 8 | **Is there an approved LLM endpoint already?** An internal gateway, an Azure OpenAI instance, a hosted model? | Many firms have one. Using it may be the difference between shipping in a week and shipping never. |

### What an answer looks like

You are not looking for a diagram. You are looking for enough to make the next
decision.

> **A large bank.** "Internal apps run on OpenShift on-prem. Images go to our
> Artifactory registry — Docker Hub is blocked. Auth is SAML through Ping, and a
> sidecar handles it, so you do not implement it yourself. No egress to the
> public internet from that cluster; you would use the internal LLM gateway.
> Deployment is a Jenkins pipeline and needs a security review first. Budget
> three weeks."

> **A mid-size tech company.** "Everything is on AWS. Push to ECR, deploy to ECS
> Fargate with a Terraform module — copy the one from `platform-templates`. ALB
> in front, Okta via OIDC on the listener. Secrets in Secrets Manager. Egress is
> open. Open a PR against the infra repo and tag `#platform`."

> **A company still figuring it out.** "Honestly, we do not have a story for
> this. There is an EC2 box that runs a couple of internal tools. If you want it
> to be real, talk to Dana."

That third answer is not a failure. It is the most common one, and recognizing it
is a skill — it means the deployment path is *yours to define*, which is a bigger
opportunity and a bigger risk.

### ✅ Deliverables

Fill these in directly in this README, and commit it.

**Who did you ask?** (role, not name)

<!-- Your answer here -->

**Where would this application run?**

<!-- Your answer here -->

**Which cloud provider, if any?**

<!-- Your answer here -->

**How would users authenticate?**

<!-- Your answer here -->

**Could this container reach an external LLM API? If not, what would it use instead?**

<!-- Your answer here -->

**What surprised you in this conversation?**

<!-- Your answer here -->

**What would you have to change about this app to make it deployable there?**

<!-- Your answer here -->

Then log the answers in [`use_case/ecosystem.md`](../../use_case/ecosystem.md)
and the person you asked in
[`use_case/stakeholders.md`](../../use_case/stakeholders.md). Both files are
extended by later weeks and neither is optional.

> **No one to ask?** You still have to produce a real answer — you just have to
> work harder for it. Pick a specific firm: a former employer, or one you want to
> work at. Their engineering blog, their job postings (which list the stack in
> detail), their conference talks, their GitHub. An afternoon of reading gets you
> further than you expect.
>
> Then name the person whose title you would have asked, and the channel you
> would have asked in. Knowing which door to knock on is most of the skill.
> *"I would have asked someone in IT"* means you have not done it. *"I would have
> asked the Platform Engineering lead in `#infra-help`"* means you have.
>
> A real answer from the wrong company beats a researched answer from the right
> one — so if you can reach anyone who deploys software for a living, ask them.

> ⚠️ **Do not commit real hostnames, IP ranges, internal URLs, or architecture
> diagrams to a public repo.** Describe the shape of the answer, not the
> specifics. If in doubt, leave it out.

---

## 🧪 Step 11 — Vibe check your app

> 🔬 **You are an AI Evaluation & Performance Engineer.** Nobody has measured
> this thing yet. You are the first.

A lightweight first pass to catch obvious problems. Later in the course you
replace this with something rigorous — for now, notice things, and name what you
noticed.

> 📝 **Step 11: Run your app through three passes of prompts and name what each one tests**
>
> *Hint:*
>
> - *"It gave a good answer" is not an observation. "It handled the arithmetic but
>   invented a source" is. Naming the aspect is the skill being practised.*

### The one rule that makes this worth doing

**Name the aspect each prompt tests, before you look at the answer.**

"It gave a good answer" is not an observation — it cannot be disagreed with,
compared against tomorrow's run, or handed to anyone else. Naming the aspect
first forces you to have had an expectation, which is the only thing that makes
a result informative.

| ❌ Not an observation | ✅ An observation |
| --- | --- |
| "Worked well" | "Followed the format exactly, but invented a policy number that does not exist" |
| "Pretty good summary" | "Kept all five key points; dropped the caveat in the last paragraph" |
| "Bad at math" | "Correct arithmetic, wrong units — it answered in weeks when asked for days" |

Aspects worth naming: **instruction-following**, **factual grounding**, **format
adherence**, **reasoning**, **tone**, **refusal behaviour**, **handling of
missing information**.

### Three passes, and the order is the point

| Pass | What you are looking for | Why this order |
| --- | --- | --- |
| **1 — General capability** | Does the underlying model do ordinary things competently? | If it fails here, nothing downstream is your application's fault |
| **2 — Your actual use case** | Does it do *your* job, on *your* inputs? | The only pass that decides whether this is worth continuing |
| **3 — Where it falls down** | What can it not do yet — live data, memory, access to your systems? | This list becomes your roadmap, and most of what follows is dismantling it |

The third pass is the one people skip, and it is the most valuable. A limitation
you wrote down is a plan. A limitation you noticed and forgot is a surprise in a
demo.

### Pass 1 — General capability

Run each prompt through your app. Name the capability it tests.

**1.** *Explain object-oriented programming in simple terms to a complete beginner.*
**Aspect tested:** <!-- your answer --> **Response:** <!-- your answer -->

**2.** *Read a paragraph of your choosing and summarize the key points.*
**Aspect tested:** <!-- your answer --> **Response:** <!-- your answer -->

**3.** *Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place.*
**Aspect tested:** <!-- your answer --> **Response:** <!-- your answer -->

**4.** *If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to get exactly 12 apples and 9 oranges?*
**Aspect tested:** <!-- your answer --> **Response:** <!-- your answer -->

**5.** *Rewrite a paragraph of your choosing in a professional, formal tone.*
**Aspect tested:** <!-- your answer --> **Response:** <!-- your answer -->

**❓ Are the answers correct and useful?**
<!-- your answer -->

### Pass 2 — Your actual use case

Test it with prompts from the problem you care about — your five golden
examples from Step 7 are the obvious first three.

**Prompt:** <!-- --> **Result:** <!-- -->
**Prompt:** <!-- --> **Result:** <!-- -->
**Prompt:** <!-- --> **Result:** <!-- -->

**❓ Does it behave the way you expected? Why or why not?**
<!-- your answer -->

### Pass 3 — Where it falls down

Try things it cannot do yet — real-time data, memory across sessions, access to
your systems.

**Prompt:** <!-- --> **Result:** <!-- -->
**Prompt:** <!-- --> **Result:** <!-- -->

**❓ What are the real limitations of this application?**
<!-- your answer -->

### ✅ Deliverables

1. All three passes filled in, with the **aspect tested** named for each
   prompt — not just the response pasted.
2. A written list of this application's real limitations.
3. **One or two sentences** on what a vibe check is worth as evidence. You will
   get different wording on two runs of the same prompt and judge both "fine" —
   name one thing you would have to add before the result could be compared
   across two versions of your application.

> Keep that list. Most of the next six weeks are about dismantling it: retrieval
> for the knowledge gaps, evals so you know whether any of it worked, tools for
> the systems it cannot reach, and memory for what it forgets.

---

## 👥 Step 12 — Demo it to a real user

You have a working thing. The last step is the one that decides whether it was
worth building, and it is the only one you cannot do alone.

**Show it to somebody and write down what they said.** Not a summary of what you
think they meant — what they actually asked for, in their words.

The bar is deliberately low on ceremony and high on it being real. A
screen-share of the running app to one colleague counts. A recorded walkthrough
you send to the person from your charter counts. What does not count is
imagining how it would go.

**Ask three things, in this order:**

1. *"What would you use this for?"* — before you tell them what it is for.
2. *"What is missing before you would actually use it?"*
3. *"What would you expect it to cost?"* — and compare their answer with
   your own arithmetic in Step 13.

The first answer is usually not the one you designed for, and that gap is the
most valuable thing you will learn this week.

> **Your agent will help you structure this and will not invent it.** Ask it how
> to run the session, how to turn messy notes into three clear findings, or how
> to tighten the write-up. It will decline to write the feedback itself, because
> it was not in the room.

### ✅ Deliverables

1. **A row in [`use_case/stakeholders.md`](../../use_case/stakeholders.md)** —
   who you showed it to by role, what you asked, what you learned, and the
   follow-up. That file is the distribution list for your final report, and this
   is its first real entry.
2. **A line in [`use_case/decisions.md`](../../use_case/decisions.md)** naming
   one thing their feedback changed — a field you added, a scope you cut, a
   default you flipped. If nothing changed, write that and say why.
3. **The three answers**, in your own words, in your repo.
4. **Your five golden examples, shown to them.** Which of the five would they
   reject, and what did you change as a result — one line in
   `use_case/decisions.md` or a rewritten example.

---

## 📤 Step 13 — Share: bring it to work

This week's pattern is *pin the problem down, write the contract, write the
correct answer by hand, then build*. Two numbers decide whether any of it is
worth doing, and both can be estimated before the endpoint is finished: what a
call costs in tokens, and what the manual process it replaces costs in
salaried minutes. Get the ratio wrong and you ship something more expensive
than the work it automates.

**The napkin math.** Take one real call through your endpoint and read the
token counts it reports; take a price per million tokens from your provider's
page; take a manual pass of the work from your charter's *how do they handle it
today*:

```
cost per call   = tokens_in / 1e6 × $_per_1M_in  +  tokens_out / 1e6 × $_per_1M_out
model per year  = cost per call × calls per day × 250
human per year  = minutes per pass / 60 × loaded $/hour × calls per day × 250
ratio           = human per year / model per year
```

| Ratio | What it means |
| :---: | --- |
| > 20× | **Comfortable.** The model cost is noise next to the human cost. Spend your effort on quality, not on token optimisation |
| 3–20× | **Viable, with discipline.** Real margin, but caching and model choice will matter |
| < 3× | **Thin.** Either the volume is wrong, the task is too cheap to automate, or you need a much smaller model. Worth knowing now rather than at deploy time |

**One number this does not show: latency.** If the workflow it replaces is a
person glancing at something for six seconds, a twenty-second answer will not
get used no matter how good it is. Write down the p95 you need *before* you
build against it — measuring it afterwards is a different, weaker thing.

### ✅ Deliverables

1. **The napkin math, in your README** under a `## Bring it to work` heading:
   the four lines above with *your* numbers, each marked **measured** (the
   token counts, a timed manual pass) or **looked up** (the price per token,
   the loaded hourly rate), and the ratio. If Step 12 gave you a number for
   what they expected it to cost, put it next to yours. This is a one-off —
   it is the scoping decision, and Week 10's report reuses it.
2. **Your p95 latency target**, one line, under the same heading — and whether
   cost or latency is the one more likely to stop this being used.
3. **What you would swap** — three lines, under the same heading, one each
   for the **data** (which real inputs the goldens stand in for), the **model
   or endpoint** (whether the approved gateway from Step 10 changes the price),
   and the **access or approval** you would need to ask for. Every week's Share
   step adds the same three lines for that week's pattern; by Week 10 the
   heading is a list of exactly what it would take to run each piece at work.
4. **Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)**,
   and comments on at least two other students' submissions after the deadline.

---

## What this challenge deposits for later

Week 1 is small on purpose, but six of its outputs are withdrawn much later.
Getting them right now costs minutes; reconstructing them in Week 9 costs days.

| What you write | Where it lives | When it comes back |
| --- | --- | --- |
| Your problem, user, success measure, and In → Out | `use_case/CHARTER.md` | Every week. Every challenge opens by linking it; Week 2 builds its validator from the In → Out row. |
| `Request`, `Response`, `solve()` | `schema.py` | **Week 2** generates data matching it. **Week 3** implements it. **Week 5** exposes it as a tool. |
| The agent-or-pipeline verdict | `use_case/decisions.md` | **Week 5**, out loud, against the alternatives. |
| Five golden examples, written by hand | `use_case/evals/golden.jsonl` | **Week 2** (seeds), **Week 4** (the harness, and what calibrates the judge), **Week 8** (the bar a fine-tuned model must clear). |
| The infrastructure answers from Step 10 | `use_case/ecosystem.md` | **Week 9** extends this exact file with the full checklist. |
| Everyone you asked, including whoever you demoed to | `use_case/stakeholders.md` | **Week 10** — the final report goes to these people. |
| The napkin math and the three swap lines | Your README, `## Bring it to work` | **Week 10** — the final report's cost section starts here. |

---

## Your Final Submission

Please include the following in your final submission:

1. **A public link to your repo**, containing:
   1. **A five-minute-or-less Loom video** demoing your application and
      describing the use case it serves.
   2. **A written document addressing each deliverable above** — the problem
      sentence, the schema, the agent-or-pipeline verdict, which golden is the
      edge case and which the decline, the four endpoint questions, the CDN
      paragraph, the Step 10 answers, the vibe check, the Step 12 answers, and
      the `## Bring it to work` lines.
   3. **All relevant code**, committed and pushed — including `schema.py`.
2. **Your `use_case/` directory filled in** — `CHARTER.md` with no template text
   left, `decisions.md`, `ecosystem.md`, `stakeholders.md`, and
   `evals/golden.jsonl` with five hand-written examples.

### How to submit

1. **Post your repo link** in
   [our community on Maven](https://bit.ly/fde1-maven-community). That is where
   every technical challenge is submitted.
2. **Push your `use_case/` updates to that repo** before you post, so the link
   shows the current state of your project rather than last week's.
3. **After the deadline, comment on at least two other students' submissions.**
   Read their charter and their five goldens, and leave something specific — a
   golden you think their system would get wrong, a field their `Response` is
   missing, or the thing you would have done differently.

> **Do not post screenshots of internal infrastructure, hostnames, or anything
> your firm would consider confidential.** Use roles, not names, everywhere in
> `use_case/`.

---

<!-- deliverables:start — this block also appears, word for word, in the week README and twice in this file. Edit it in one place and copy; CI checks the three match -->
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

## Where this goes next

| Week | What it adds to this app |
| --- | --- |
| 2 | Open weights and synthetic data — rows generated from your goldens, matching your schema, without touching real records. |
| 3 | Retrieval — `solve()` gets implemented over your own data, and it answers from your documents instead of guessing. |
| 4 | Evals — your goldens become a harness, and "it seems better" becomes a number you can show a VP. |
| 5 | Tools, skills, MCP, subagents — the API you built is already MCP-capable, and you defend Step 6's verdict out loud. |
| 6 | Guardrails, and writing prompt injections against your own app. |
| 7 | Memory, and the evals that prove the memory works. |
| 8 | Fine-tuning — replace the closed model with an open one that passes your harness. |
| 9 | Infrastructure, and the full version of Step 10. |
| 10 | Production, and the final report to everyone you talked to — with the napkin math redone and every week's swap lines collected. |

Everything after this week assumes your app has a contract, a bar, a place to
live, and someone specific waiting for it.
