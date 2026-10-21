<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Technical Challenge 3</h1>
  <p><strong>Your MVP — the retrieval technique you can defend, over your own data, with sources.</strong></p>
</div>

---

## Overview

> **Read first:** [`use_case/CHARTER.md`](../../use_case/CHARTER.md). This
> challenge implements the schema you wrote in Week 1, over the synthetic data
> you generated in Week 2. If either is still the template, finish that week.

Build the smallest version of your product that actually works: an endpoint on
your app that answers a real question from your use case, grounded in
retrieved context, naming its sources.

**This is the first week your app does something real.** Weeks 1 and 2
produced a container and a dataset. This one produces a thing a person could
use — and the question this week asks is not *which* retrieval technique, it is:

> **"Which technique did you measure it against, and what would make you switch?"**

The endpoint is a few dozen lines. **The measured decision is the assignment.**

> 💡 **You already know enough to be dangerous.** Session 5 gave you one
> tool-calling loop and two corpus interfaces — a BM25 chunk search the model
> can call again, and list/grep/read over a wiki — scored against reviewed
> questions on one corpus, with the trace next to the pass mark. Session 6 gave you the same discipline for
> charts, screenshots and video — three cross-modal strategies on one vector
> database, and the parse check that decides most document architectures.
> This is where you run the comparison on your own corpus and your own
> questions.

<table>
  <tr>
    <td width="120"><strong>Outcome</strong></td>
    <td>A working endpoint that answers a real question from your use case, grounded in retrieved context, with sources — and a written decision naming what it beat and what would change your mind.</td>
  </tr>
  <tr>
    <td><strong>Tools</strong></td>
    <td>numpy, LiteLLM (chat and embeddings), pydantic, Gradio, Docker. A vector database only if you have measured that you need one.</td>
  </tr>
  <tr>
    <td><strong>Due</strong></td>
    <td>End of the week. Post your repo link in the Maven Community.</td>
  </tr>
  <tr>
    <td><strong>Before you start</strong></td>
    <td>TC1's charter with its <code>Request</code>/<code>Response</code> schema, and TC2's <code>use_case/data/synthetic_v1.jsonl</code> with its datasheet.</td>
  </tr>
</table>

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

An endpoint on your app that answers real questions from your use case over
your own data, with sources — and the measurement, against ten questions you
labelled, that says why it uses the retrieval technique it uses.

Eight questions are asked inside the notebooks as you work through them. *They
are not submitted and not graded* — they are how you work out what the challenge
is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | Which of your ten questions need exact text, which need two pages — and whether your corpus has the headings and stable page names that make direct corpus interaction possible at all | S5 |
| 2 | Which parts of the tool trace you would keep in every answer so someone not in the room can see why it says what it says — and which interface makes that easier | S5 |
| 3 | Which of calls, evidence volume and latency would push your endpoint over budget first — and the one change to the *tools* that brings it back | S5 |
| 4 | What per-user authorisation looks like on `list`, `search` and `read` for your corpus, which interface you can get approved, and what would change your mind | S5 |
| 5 | Which of the three ways to make a text question return an image fits your non-text content — and what about that content decides it | S6 |
| 6 | The two weaknesses of one shared space, and what compensates for each — which is also which model never sees the whole corpus, and what narrows it first | S6 |
| 7 | Why the answer is read from the pixels and not the caption — and what would verify a model's reading of the identifiers your users search by | S6 |
| 8 | Why two embedders' lists are merged by rank, not score — and how many of your ten real queries carry a number, a code or a name, which says whether you need a lexical index too | S6 |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-7`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **Ten labelled questions** in `use_case/evals/retrieval.jsonl` — real ones, each naming the record(s) that should answer it
- [ ] Your `Request`/`Response` schema from Week 1 **implemented, not redesigned** — or the charter updated and the reason written down
- [ ] **At least three techniques measured** against those labels, with the results table — pass, cited source, calls, evidence read, latency — in your repo
- [ ] A new `@app.api` endpoint that retrieves over **your** TC2 data and **names its sources** in every answer
- [ ] `use_case/decisions.md` has the retrieval decision — what shipped, what you rejected, why, and what would change your mind — plus the four non-text answers
- [ ] It still runs in Docker

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
| LiteLLM | the answer call, and `embedding()` for your own corpus | [docs.litellm.ai](https://docs.litellm.ai/) |
| rank-bm25 | the chunk index on the Agentic RAG side — the same `search_chunks` as Session 5 | [github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25) |
| numpy | cosine over your own rows, if your third technique is dense | [numpy.org/doc](https://numpy.org/doc/stable/) |
| pydantic | the `Request`/`Response` contract your endpoint implements | [pydantic.dev/docs](https://pydantic.dev/docs/validation/latest/get-started/) |
| Gradio | the `@app.api` endpoint you add | [gradio.app/docs](https://www.gradio.app/docs) |
| sentence-transformers | a cross-encoder, if you add a reranker in Step 3 | [sbert.net — Cross-Encoders](https://sbert.net/docs/cross_encoder/usage/usage.html) |

---

## Setting Expectations

**Budget six to eight hours**, spread across the week. Labelling is fast and
decides everything after it; the measurement is mostly waiting for a model to
finish its tool loop; the endpoint is the part that feels like the work and is
the smallest.

| Step | What it is | Rough time |
| :---: | --- | --- |
| 1 | Label ten questions | 30 min |
| 2 | Implement the schema you already wrote | 45 min |
| 3 | Measure at least three techniques against the labels | 2 hrs, mostly waiting on the loop |
| 4 | Ship it as an endpoint that cites its sources | 1–2 hrs |
| 5 | Write the decision, including the non-text one | 30 min |
| 6 | Show it to the person whose question it answers | 30 min, plus their calendar |
| 7 | Share: bring it to work | 30 min |

> **Do Step 1 before anything else, and send the Step 6 message today.** Ten
> labelled questions turn every sentence in Step 5 from a preference into a
> finding, and the person from your charter is the only one who can tell you
> whether the answers are ones they would act on.

---

## What you are building

| File | Role |
| --- | --- |
| `use_case/evals/retrieval.jsonl` | Ten real questions, each labelled with the record(s) that answer it. **The retrieval half of your eval harness** |
| Your retrieval code, in your app | Agentic RAG, direct corpus interaction, dense — whichever you measured. Readable, because you defend it out loud in Week 5 |
| A new `@app.api` endpoint | Implements `Response`. Every answer carries its sources |
| `use_case/decisions.md` | The retrieval row, and the four non-text answers |
| `CLAUDE.md` | The instructions Claude Code reads before it touches anything |

> **What is already written for you, and what is not.** Session 5 had you write
> a BM25 chunk index, three wiki tools, one tool-calling loop and a scorer over
> seven pages; that code runs unchanged over your rows and pages. For the
> plumbing around it, `helpers/rag.py` has `load_jsonl_corpus`,
> `chunk` and `format_docs`, and `helpers/vectorstore.py` persists an index to
> `.npy` + `.jsonl` with metadata filtering applied **before** ranking — which
> is the part that matters once Week 9 gives your records access levels. Use
> them for plumbing. The ranking, the measurement and the decision are yours.

`CLAUDE.md` puts Claude Code into **instructor mode** for this directory: it
will explain, debug, and review, and it will decline to write your retrieval
code, your comparison, or your decision. That is deliberate. The comparison
looks like a table, so it feels harmless to have it filled in. It is the whole
assignment.

---

## Step 1 — Label ten questions

Session 5's corpus had labels because its four questions were written page
and terms first, answer second. Yours does not yet, and that is the real
difference between the notebook and Monday.

Take **ten real questions** from your use case — from a ticket, a chat log, a
colleague, the person from your charter. Not invented ones. For each, write
down which record in `use_case/data/synthetic_v1.jsonl` *should* answer it.
**Both, if two are needed** — and notice how many of yours need two, because
that number alone rules out top-1. Session 5's `cross_page` case is the worked
example: *"how is customer data protected at rest, in transit, and from
unauthorised access?"* needs three sections of one page, and the top chunk
by similarity carries one of them.

```json
{"question": "...", "gold": ["<record id>", "<record id>"], "kind": "lookup | multi-hop | decline"}
```

Include at least one question the system **should decline** — a question your
data cannot answer. Retrieval always returns its top *k*; the labels are how
you find out whether your endpoint knows when *k* results are the wrong
answer. Session 5's `decline` case is the worked example, down to how it is
scored: a pass is a refusal that invents no figure.

> Ten minutes of labelling is the highest-value ten minutes this week. Without
> it every sentence you write in Step 5 is a preference.

### ✅ Deliverables

1. **`use_case/evals/retrieval.jsonl`** — ten lines, real questions, labelled.
2. **One line in the file's header comment or your README**: how many of the
   ten need more than one record. That is your top-*k* floor.

---

## Step 2 — Implement the schema you already wrote

Week 1's challenge had you write `Request` and `Response` pydantic models and
a `solve()` stub that raised `NotImplementedError`. Implement it.

The signature does not change. If you find yourself wanting to change it, that
is worth noticing — either you learned something real about the problem, in
which case update `CHARTER.md` and say why, or you are drifting toward what is
easy to build rather than what was worth building.

Your `Response` needs one field it may not have yet: **`sources`**, a list of
the record ids the answer was grounded in. If the charter's schema has no room
for it, that is the one change this challenge permits without a charter
rewrite — add it, and say in `decisions.md` that you did.

### ✅ Deliverables

1. **`solve()` implemented** against your schema, in your app.
2. **If the schema changed:** the charter updated and a `decisions.md` line
   saying what changed and why.

---

## Step 3 — Measure at least three techniques against the labels

Run at least **three** retrieval techniques over your rows and score them
against Step 1's labels with the measure Session 5 used: **the reviewed terms
appear in the answer, the expected record is cited, and the trace is kept** —
calls, evidence read, latency, how the loop stopped. Session 5's `run_agent`
and `score` run unchanged if you give them your tools and your labels.

Two of the three are the ones Session 5 built; the third is yours.

| Technique | What you need | What Session 5 showed |
| --- | --- | --- |
| **Agentic RAG** | a BM25 index over your rows and the one `search_chunks` tool — forty lines, no model to approve | economical when a question maps to a few sections; blind to anything the chunk boundary cut |
| **Direct corpus interaction** | your rows as named pages with headings, an index page, and `list` / `grep` / `read` | earns its extra calls on exact identifiers, procedures and cross-page questions; reads several times more evidence to do it |
| **Your third** | dense (`embedding()` over every row and cosine), hybrid (RRF over BM25 and dense), or a reranker over BM25's top 20–50 | Session 6's `TextEmbedder` and `reciprocal_rank_fusion` are the pieces to lift for the first two; the recommended reading has the reranker |

**Chunking.** Session 5 split at `##` headings because the corpus had them;
yours arrives as rows, one per record, from your own generator. Start with the
boundary the record already gives you. Cut inside it only if you measured that
you needed to, and then `helpers.rag.chunk` is the plumbing — the decision
about *where* is still yours.

**The wiki is a prerequisite, not a given.** Direct corpus interaction needs
stable names, headings and an index somebody maintains. If your rows have
none of that, the first move is to make the wiki — name, head, index — and
the time it takes is a measurement too. If nobody will own that index at
work, write that down in Step 5; it decides the comparison before any run.

**What dense retrieval costs, if it is your third.** A few hundred rows
through `embedding()` is cheap; write down the token count it reports anyway,
because you will re-embed every time the chunking changes and that number is
what decides the architecture at scale.

> **Keep the trace next to the pass mark.** A correct answer can hide a
> wasteful trajectory, and a cheap wrong answer is still wrong. Session 5's
> results table has six columns for a reason; your table should too.

> **Optional, and worth trying: a reranker over the RAG side.** Retrieve 20–50
> with BM25, reorder with a cross-encoder, keep the top 5 — a
> `sentence-transformers` `CrossEncoder` and a few lines; the recommended
> reading has the exact call. If it is your third technique, measure it like
> the others rather than assuming it wins.

### ✅ Deliverables

1. **The results table** in your repo: technique × pass rate, citation rate,
   calls, evidence read, latency, on your ten questions. Three techniques
   minimum.
2. **The settings** next to it — model, turn budget, chunking (if any),
   embedding model and RRF `k` or reranker and first-stage size where used —
   so someone can reproduce the run.
3. **The embedding token count** from your run, marked *measured* — or *n/a*
   if no technique embedded anything, which is itself a finding.

---

## Step 4 — Ship it as an endpoint that cites its sources

A new `@app.api` endpoint on your app, conforming to your `Response` model.
Same rules as Week 1: named for what it does, typed arguments, a real
docstring. In Week 5 it becomes an MCP tool and that docstring becomes its
whole interface.

The shape — and it is a shape, not code you copy:

```
retrieve(question) -> hits          # the technique Step 3 picked
context = format_docs(hits)         # each passage tagged with its record id
answer  = complete(prompt(question, context))
return Response(answer=..., sources=[hit.source for hit in hits])
```

**Every answer names the records it came from.** Not optional, and not a
nicety. An answer a user cannot trace is a rumour, and in Week 4 you will need
to know *which retrieved passage* caused a wrong answer in order to fix it.
Systems that drop provenance to save tokens are the ones nobody trusts by the
second month.

Two things the sessions showed you that belong in this endpoint:

- **The expensive model never sees the whole corpus.** Session 6's production
  shape — narrow with something cheap, read with something slow — is the same
  trade as reranking. Your answer model reads the top 3–5, never the top 50.
- **A decline is a valid answer.** When the best hit is below a similarity you
  chose, or the labelled decline-question comes in, the endpoint says so rather
  than answering from the nearest irrelevant passage. Session 5's point about
  top-*k* stands: retrieval cannot say "nothing matched", so your endpoint has
  to.

### ✅ Deliverables

1. **The endpoint, running**, answering your ten questions with sources.
2. **Its docstring**, written for an agent that will read it as the whole
   interface.
3. **What it does on the decline question**, in one line in your README.

---

## Step 5 — Write the decision, including the non-text one

In [`use_case/decisions.md`](../../use_case/decisions.md), the retrieval row:

| Field | What it means |
| --- | --- |
| **Decision** | Which technique you shipped |
| **What you rejected** | The other two you actually measured |
| **Why** | Corpus size, question shape, freshness, latency, auditability, or what you could get approved |
| **What would change your mind** | The condition under which you would switch |

That last column is the one people skip and the one people ask about. *"We
chose dense retrieval; we would move to hybrid if exact-match queries went above
about 20% of traffic"* is an engineering position. *"We chose dense retrieval"*
is a preference. **Week 5 asks you to defend this in front of the room.**

Then Session 6's four questions about the non-text content in *your* corpus —
scans, screenshots, diagrams, recordings — even if the answer is "there is
none yet, and here is what would arrive first":

1. Is the information actually visual, or text rendered as pixels?
2. Does the number you need live only in the pixels — and if so, which
   strategy finds the image, what reads it, and what checks the reading?
3. Do you have descriptions — or will you pay one parse per image, and where
   would that batch job run?
4. For video or audio: does the transcript alone answer it?

*"We considered multimodal retrieval and OCR was the right tool"* is a good
decision, well recorded. Session 6's support engineer recorded exactly that
for her scanned runbooks, and a different answer — a parsing batch job inside
the network, with every extracted code checked — for her modem screenshots. Two
answers for two kinds of attachment is the normal result.

### ✅ Deliverables

1. **The retrieval row** in `use_case/decisions.md`, all four columns.
2. **The four non-text answers**, in the same file, one line each.

---

## 🧯 If it's blocked

### "Retrieval returns nothing useful"

Read your rows. Print ten of them. The problem is nearly always the unit —
boundaries in the wrong place, or a record so long that the relevant sentence
is diluted by 800 characters of unrelated text. Session 5's side-by-side of
`search_chunks` and `grep_wiki` on the same code is the view to reproduce on
your own data.

### "It works for me but not for my colleague's questions"

Vocabulary mismatch. They say "leg", the records say "hop". Options: synonyms
at query time, a hybrid retriever, a different embedding model, or fixing the
records — and the last one is often correct and almost never considered.

### "My retrieval scores look fine but the answers are wrong"

Check whether your questions need more than one record. A pass on reviewed
terms with the wrong record cited is the model guessing from the nearest
chunk; Session 5 tracks the citation separately for exactly this reason. If
you only measured whether *something* relevant came back, re-measure whether
*every* labelled record did.

### "I can't get an embedding model approved"

Then you have your answer: both of Session 5's interfaces need no embedding
model — BM25 needs no approval, and `list` / `grep` / `read` over the records
needs no index at all. Both are legitimate engineering choices, not
consolation prizes, and both will be running in production while a
vector-database proposal is still in review. Your third technique can be a
reranker over BM25 rather than dense. Write the blocked approval in
`use_case/ecosystem.md`.

### "The embedding endpoint answered 501, or 'does not support embeddings'"

A model appearing in `/v1/models` is not a promise that the route exists —
serving chat and serving embeddings are separate switches on the same server,
and llama.cpp refuses unless it was started with `--embeddings`. The fix is on
the server, not in your code.

---

## 👥 Step 6 — Show it to the person whose question it answers

You have an endpoint that answers questions with sources. The only person who
can tell you whether the answers are ones they would act on is someone who
asks those questions for real — the person from your charter, or whoever is
closest.

**Ask them to type five questions of their own, and write down what they
said.** Not your ten; theirs. Not a summary of what you think they meant — what
they actually said, in their words.

The bar is deliberately low on ceremony and high on it being real. A
ten-minute screen-share counts. A short recording of them using it counts.
What does not count is imagining how it would go.

**Ask three things, in this order:**

1. *"Would you act on that answer?"* — after each one, before you explain
   where it came from.
2. *"Does the source it named convince you, or would you go check?"*
3. *"What did you want to ask that you didn't?"*

The third answer is usually a question your corpus cannot answer yet, and
knowing that now is the most valuable thing you will learn this week.

> **Your agent will help you structure this and will not invent it.** Ask it how
> to run the session, how to turn messy notes into three clear findings, or how
> to tighten the write-up. It will decline to write the feedback itself, because
> it was not in the room.

### ✅ Deliverables

1. **A row in [`use_case/stakeholders.md`](../../use_case/stakeholders.md)** —
   who you showed it to by role, what you asked, what you learned, and the
   follow-up.
2. **A line in [`use_case/decisions.md`](../../use_case/decisions.md)** naming
   one thing their feedback changed — a question added to `retrieval.jsonl`, a
   threshold moved, a record fixed. If nothing changed, write that and say why.
3. **Their five questions**, added to `use_case/evals/retrieval.jsonl` with
   labels, so next week's harness scores them too.

---

## 📤 Step 7 — Share: bring it to work

This week's pattern is *measure retrieval against labelled questions before you
pick it, and ship the answer with its sources*. Somewhere at your company there
is a search that "works" because nobody measured it, or a chatbot whose answers
nobody can trace. This step is where you write down which one, and what this
week's work would be worth applied to it.

### ✅ Deliverables

1. **Which search or chatbot at work this is for**, one line under
   `## Bring it to work` in your README. *"Tier-2 engineers search three
   Confluence spaces by hand and answer from memory"* names one; *"knowledge
   management"* does not.
2. **What you would swap** — three lines under the same heading, one each for
   the **data** (which corpus at work, and whether it is text, scans or
   recordings), the **model or endpoint** (which embedding and answer models,
   and whether the corpus may leave the network), and the **access or
   approval** you would need to ask for — with the embedding token count from
   Step 3 next to it, marked *measured*, because it is the number that decides
   whether re-indexing at work is cheap or a budget line.
3. **Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)**,
   and comments on at least two other students' submissions after the deadline.

---

## What this challenge deposits for later

| What you write | Where it lives | When it comes back |
| --- | --- | --- |
| Ten labelled questions, plus your user's five | `use_case/evals/retrieval.jsonl` | **Week 4** — the retrieval half of your eval harness, already written. |
| The endpoint with sources | Your app | **Week 4** debugs wrong answers by retrieved passage. **Week 5** exposes it as an MCP tool. **Week 6** attacks it through retrieved content. |
| The retrieval decision | `use_case/decisions.md` | **Week 5**, out loud, against the alternatives. |
| The non-text answers | `use_case/decisions.md` | **Week 8**, where the same data constraint returns and you cannot synthesise a photograph. |
| A blocked embedding model or endpoint | `use_case/ecosystem.md` | **Week 9**, which extends this file with the full deployment checklist. |
| The three swap lines | Your README, `## Bring it to work` | **Week 10** — the final report's "what it would take to run" section. |

---

## Your Final Submission

Please include the following in your final submission:

1. **A public link to your repo**, containing:
   1. **A five-minute-or-less Loom video** showing the endpoint answering two
      of your questions with sources, and walking through the results
      table.
   2. **A written document addressing each deliverable above** — the labels,
      the schema decision, the results table with its settings, the
      endpoint's docstring and decline behaviour, the decision row, the
      non-text answers, the Step 6 answers, and the swap lines.
   3. **All relevant code**, committed and pushed. **Never the data.**
2. **Your `use_case/` directory updated** — `evals/retrieval.jsonl`, and the
   new rows in `decisions.md`, `stakeholders.md` and `ecosystem.md`.

### How to submit

1. **Post your repo link** in
   [our community on Maven](https://bit.ly/fde1-maven-community). That is where
   every technical challenge is submitted.
2. **Push your `use_case/` updates to that repo** before you post, so the link
   shows the current state of your project rather than last week's.
3. **After the deadline, comment on at least two other students' submissions.**
   Read their decision row, and leave something specific — a condition in
   "what would change your mind" you would push on, or a technique they did
   not measure.

> **Never commit real company data.** `use_case/data/` is gitignored for this
> reason. If your retrieval works on real documents locally, that is fine —
> commit the synthetic version. Do not post screenshots of internal
> infrastructure, hostnames, or anything your firm would consider confidential.

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

An endpoint on your app that answers real questions from your use case over
your own data, with sources — and the measurement, against ten questions you
labelled, that says why it uses the retrieval technique it uses.

Eight questions are asked inside the notebooks as you work through them. *They
are not submitted and not graded* — they are how you work out what the challenge
is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | Which of your ten questions need exact text, which need two pages — and whether your corpus has the headings and stable page names that make direct corpus interaction possible at all | S5 |
| 2 | Which parts of the tool trace you would keep in every answer so someone not in the room can see why it says what it says — and which interface makes that easier | S5 |
| 3 | Which of calls, evidence volume and latency would push your endpoint over budget first — and the one change to the *tools* that brings it back | S5 |
| 4 | What per-user authorisation looks like on `list`, `search` and `read` for your corpus, which interface you can get approved, and what would change your mind | S5 |
| 5 | Which of the three ways to make a text question return an image fits your non-text content — and what about that content decides it | S6 |
| 6 | The two weaknesses of one shared space, and what compensates for each — which is also which model never sees the whole corpus, and what narrows it first | S6 |
| 7 | Why the answer is read from the pixels and not the caption — and what would verify a model's reading of the identifiers your users search by | S6 |
| 8 | Why two embedders' lists are merged by rank, not score — and how many of your ten real queries carry a number, a code or a name, which says whether you need a lexical index too | S6 |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-7`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **Ten labelled questions** in `use_case/evals/retrieval.jsonl` — real ones, each naming the record(s) that should answer it
- [ ] Your `Request`/`Response` schema from Week 1 **implemented, not redesigned** — or the charter updated and the reason written down
- [ ] **At least three techniques measured** against those labels, with the results table — pass, cited source, calls, evidence read, latency — in your repo
- [ ] A new `@app.api` endpoint that retrieves over **your** TC2 data and **names its sources** in every answer
- [ ] `use_case/decisions.md` has the retrieval decision — what shipped, what you rejected, why, and what would change your mind — plus the four non-text answers
- [ ] It still runs in Docker

### 📤 Share

- [ ] **A demo to a real user, with their feedback recorded in your own words** — graded, and the one people skip
- [ ] **What you would swap to run this at work** — data, model or endpoint, and the approval you would need — three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## Where this goes next

| Week | What it adds to this endpoint |
| --- | --- |
| 4 | Evals — your labelled questions become pass and citation rates tracked per change, and wrong answers get debugged by trace and retrieved passage. |
| 5 | Tools, skills, MCP — this endpoint becomes a tool, and you defend its retrieval choice out loud. |
| 6 | Guardrails — your corpus is an injection surface; the attacks arrive through retrieved content. |
| 7 | Memory — semantic memory is retrieval over a corpus that grows, and this is the retrieval. |
| 8 | Fine-tuning — the same data constraint, sharper: you cannot synthesise a photograph. |
| 9 | Infrastructure — the access levels your records will have, filtered before ranking. |
| 10 | Production — the final report, with every week's swap lines as its "what it would take to run" section. |

Everything after this week assumes your app answers from your data and can say
where the answer came from.
