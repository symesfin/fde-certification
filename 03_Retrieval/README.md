<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Week 3 — Retrieval</h1>
  <p><strong>🔍 Retrieval vs. agentic search variants</strong></p>
</div>

---

## 🎯 What you'll be able to do

Decide what sits between a model and your corpus — a retriever that selects
chunks, or the pages themselves — and defend the choice with a trace and a
measurement, not a preference.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S5 | [`Agentic_Retrieval`](./sessions/S5_Agentic_Retrieval.py) | One agent, two corpus interfaces, everything else held constant: Agentic RAG (a BM25 chunk search the model can call again) versus Direct Corpus Interaction over an LLM Wiki (list, grep, read). Six reviewed questions, each written to favour one side for a reason you can see in the code, one loop, and a results table that keeps the trace, the evidence read and the latency next to the pass mark — predicted against observed. Told through a second-line support engineer at a regional broadband operator building the one page her manager will sign. | [Recording!](https://us02web.zoom.us/rec/share/2N7OCVlMBM1zyIE-VzUaaiwLEfByKZNtfjGQuPBEAlU6EETnuPWn7ISeRrwNjPmL.5aCsDtyGW7elj1K8) <br> passcode: `lHhex*4.` | [Slides](https://canva.link/oxp3pbq8tlnd9a6) |
| S6 | [`Multimodal_Retrieval`](./sessions/S6_Multimodal_Retrieval.py) | A vision-language model used two ways — as a parser that turns charts into searchable records, and as a reader that answers from the pixels — with three cross-modal retrieval strategies (caption→text, one shared CLIP space, separate stores fused by rank) built on Qdrant and measured against the same questions, then the whole pipeline on a video with timestamp citations. The support engineer's ticket attachments are the running example — modem screenshots, scanned runbooks, recorded calls — and the page gets one more line. | [Recording!](https://us02web.zoom.us/rec/share/Mes_AsM362yK3wDlNOmkJYux0shqqdUPDrr2nZRc9eDHxKrIUUxqFvI3wsK9v-ZI.nSF1Fxup29WveNu2) <br> passcode: `5E!?2i7C` | [Slides](https://canva.link/l4wz4ni88qlpq1x) |


📚 **Need a refresher?** Review the [Spring 2026 AI Engineering Bootcamp materials](../00_Prerequisites/RAG_Fundamentals/README.md) for beginner-friendly explanations of RAG prerequisite concepts.

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC3 — Your MVP, with the retrieval technique you can defend**](./challenge/README.md) | Coming soon |

---

## 📖 Overview

Most AI applications inside a company answer questions from documents the
company already has — tickets, policies, manuals, invoices, recordings. The
step that finds the right document before the model writes an answer is
called **retrieval**, and it is where most of these systems quietly fail. This
week is about choosing that step *by measuring*, rather than by reputation.

**Session 5 is about what sits between the model and the pages.** A
knowledge base already exists — runbooks, tariffs, a glossary of codes,
data-handling rules — and a model that can call tools. There are two ways to
connect them. Put a retriever in between, so the model receives ranked chunks
and can search again (*Agentic RAG*); or hand the model the pages themselves
— an index, a search, a read — and let it investigate (*Direct Corpus
Interaction over an LLM Wiki*). You will build both over the same seven pages,
run six reviewed questions — each written to favour one side for a reason
you can see in the code — through the same loop, and read the traces, not
just the answers. The point is not that one wins. It is that the
*interface* decides what can be found, what an auditor can reconstruct, what
the question costs, and who owns freshness and access — and that you can
measure all four in an afternoon.

**Session 6 is about everything that is not text.** Charts, scanned forms,
screenshots, slide decks, recordings. A text embedding model cannot see and a
vision model cannot be indexed, so every working design is a way of getting
the picture into a space where comparison already works — and there are three
such ways. The notebook opens with the one-step version — LlamaIndex's
`MultiModalVectorStoreIndex` over the same folder, thirty lines, one button,
one answer — and then asks what that framework decided on your behalf. You
will build all three ways on one vector database to find out: describe each
image with a vision model and index the description; put pixels and words in
one shared space so a question matches an image directly; or keep a store per
modality and merge the results by rank. Then the part that decides real
projects: the shared space can *find* the right chart and still cannot say
what the bar reads, so the answer comes from handing the retrieved pixels to a
model that can look — three candidates, never the corpus — and from checking
every number a model reads before it is trusted. The same pipeline runs on a
45-second video at the end, and the answer comes back with a timestamp.

**The challenge** is your MVP: an endpoint on your app that answers a real
question from your use case over the synthetic data you generated last week,
names the records it drew on, and was chosen by measuring at least three
techniques against ten questions you labelled yourself.

If you take one idea from this week: **you cannot pick retrieval by
reputation.** Ten labelled questions and an afternoon of measurement will
tell you more about your corpus than any blog post, and the interface you
reject with a trace and a number is worth more than the one you chose without
one.

---

## 🔑 Required accounts, keys, and setup

**S5 needs a chat model that can call tools** — `LLM_MODEL` in `.env`, through
any provider or gateway LiteLLM reaches. Tool calls go out with LiteLLM's
default `tool_choice`, so gateway aliases such as `openai/bedrock/...` that
reject the parameter when it is sent explicitly work unchanged. That is the only
requirement: the RAG side uses a local BM25 index, so there is no embedding
endpoint to approve and nothing to download. The two run buttons make roughly 8 and 30–50 model calls;
a full run is a few minutes. If your provider rejects `temperature=0`, the
notebook notices on the first call and runs at the provider's default.

**Both notebooks run with `--sandbox`** (`make nb F=<file>`), which installs
their packages from each file's own header. To open them from the root
environment instead, run `make setup-week W=3` once first.

**S6 needs one of two things for text embeddings** — a hosted `EMBED_MODEL`
(used when `OPENAI_API_KEY`, `EMBED_API_KEY` or `EMBED_API_BASE` is set, or
when the model name carries a provider prefix such as `voyage/voyage-3.5`), or
nothing at all, in which case it downloads a 67 MB local model once. Anthropic
has no embedding endpoint, so an Anthropic-only `.env` takes the local path and
the measured token count reads 0; to see a real count, add either
`OPENAI_API_KEY` (embeddings only — chat stays on Claude) or
`EMBED_MODEL=voyage/voyage-3.5` with `VOYAGE_API_KEY`. Everything else in S6
degrades gracefully:

- **The vision model is behind three buttons** (parse the charts, answer four
  questions, answer from the video). It needs `VLM_MODEL` in `.env` — any
  OpenAI-compatible endpoint serving a multimodal model. There is deliberately
  no fallback to `LLM_MODEL`: a text-only model accepts an image payload and
  answers confidently about nothing, which is worse than an error. Without
  it, the reference parses that ship with the corpus stand in, and every
  retrieval measurement still runs.
- **The one-step opener is behind one button** and uses the same two
  downloads as the rest of the notebook (the local text model and CLIP), with
  LlamaIndex doing the indexing. If the downloads are blocked it shows a
  warning panel; nothing later depends on it.
- **CLIP is behind one button** and is a ~600 MB download from Hugging Face on
  first use, served as ONNX by FastEmbed — no PyTorch. On a network that
  blocks the download, Strategy A still runs end to end and Strategies B and
  C show a panel instead of a traceback. The notebook's Conclusion names the
  two production alternatives: a hosted multimodal embedding endpoint, or the
  same files mirrored onto your firm's artifact store.
- **Keyframes** are sampled from the video with OpenCV; if that fails, the
  reference frames that ship with the corpus are used.

```bash
make nb F=03_Retrieval/sessions/S5_Agentic_Retrieval.py
make nb F=03_Retrieval/sessions/S6_Multimodal_Retrieval.py
```

**An embedding model is needed for one thing only in S5:** the first Harder
Bonus Task, where you swap BM25 for a dense index over the same sections. That
is deliberate — a local lexical index is how everyone in the room compares the
same numbers, and embedding your own data is where cost and rate limits stop
being hypothetical.

### The corpus

**S5's corpus is seven pages of a fictional regional broadband operator's
knowledge base** — a field guide, a glossary of codes, the tariffs and service
levels, the fault runbook, the data-handling rules, network operations, and a
quarterly metrics CSV — plus a one-page wiki index and **six reviewed
questions** in `sessions/data/eval_cases.jsonl`, each labelling the page, the
answer terms and the approach it was written to favour before anything runs.
The shapes: an exact acronym, a question with none of the page's words in it,
an answer past the retriever's cap, a "which pages mention X", and two broad
questions scattered across several pages. The corpus is machine-generated and CC0; it is a re-skin
of the ACME Analytics corpus from AI Makerspace's Titanium Engineer programme,
redrawn so the pages belong to the operator the retrieval sessions follow. See
[`sessions/data/README.md`](./sessions/data/README.md).

**S6's corpus is six charts, six memos and one 45-second video** from a
fictional regional broadband operator (CC0, machine-generated), with a data
dictionary that says which question each chart answers. Four of the six
numbers appear in no text file — a question about them can only be answered by
retrieving the chart and reading it. See
[`sessions/data/multimodal/README.md`](./sessions/data/multimodal/README.md);
regenerate with `uv run --with matplotlib --with imageio --with imageio-ffmpeg python scripts/make_multimodal_corpus.py`.

---

## 📚 Recommended reading

The first three close gaps the challenge leaves open — the session holds the
retriever at BM25 and the loop at six turns; the challenge asks you to measure
a third technique of your own and to ship the loop as an endpoint. The rest are
the canonical texts behind the two sessions.

- [LiteLLM — function calling](https://docs.litellm.ai/docs/completion/function_call) — **the tool-call shape both of Session 5's loops use**, and how to make it work against your own endpoint or gateway
- [Dense Passage Retrieval](https://arxiv.org/abs/2004.04906) — the paper that made dense retrieval the default; **the retriever you swap in for Session 5's Harder Bonus Task** and the natural third technique for the challenge. The code to lift is already in the week: Session 6's `TextEmbedder` (Task 3, with the token count the challenge asks for) and its `reciprocal_rank_fusion` (Task 5) if you go hybrid
- [sentence-transformers — Cross-Encoders](https://sbert.net/docs/cross_encoder/usage/usage.html) — `CrossEncoder.rank(query, passages)` in three lines, if your third technique is a reranker over the BM25 candidates
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — the loop in Session 5's Task 2, with a budget
- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — simple loops with good tools over orchestration; the design choice Session 5 holds constant
- [BM25: The Probabilistic Relevance Framework](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) — the forty lines behind `rank_bm25`; §3 for the intuition
- [Reciprocal Rank Fusion](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf) — six pages, one formula; Session 6's Task 5 and the hybrid variant of the challenge
- [Anthropic: Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) — a practical fix for chunk-level context loss, and a reason a section-level chunk often beats a fixed-size one
- [Chroma — Evaluating Chunking Strategies](https://www.trychroma.com/research/evaluating-chunking) — the measurement most teams skip
- [CLIP](https://arxiv.org/abs/2103.00020) — the two towers Session 6's Strategy B searches with; §2 and Figure 1
- [Mind the Gap](https://arxiv.org/abs/2203.02053) — why text and image vectors sit apart even in one shared space; Session 6's unified-search result, explained
- [ColPali](https://arxiv.org/abs/2407.01449) — retrieval over document *images* rather than extracted text; the most direct answer to "should I OCR this or not"

**Pre-reads, from the session briefs** — ten minutes each, before the session they belong to:

- [Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG](https://arxiv.org/abs/2501.09136) — before S5. The loops a model can drive; S5's RAG side is the smallest of them
- [Model Context Protocol](https://modelcontextprotocol.io/) — before S5. The standard shape `list`, `search` and `read` take once a corpus interface becomes a service; S5's DCI tools are that shape in-process
- [Project GraphRAG](https://www.microsoft.com/en-us/research/project/graphrag/) — before S5. When the question is about the whole corpus rather than a page in it
- [An Easy Introduction to Multimodal RAG](https://developer.nvidia.com/blog/an-easy-introduction-to-multimodal-retrieval-augmented-generation/) — before S6. The strategies — describe-then-index, or one shared space — which are S6's Tasks 3 and 4
- [CLIP](https://arxiv.org/abs/2103.00020) and [ColPali](https://arxiv.org/abs/2407.01449) — before S6, and listed above

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

## 📊 What the notebooks measure

Notebooks ship without outputs, so this is where the numbers live for anyone
reading on GitHub.

### Session 5 — one agent, two corpus interfaces

Session 5 runs six reviewed questions through one tool-calling loop twice:
once with a single `search_chunks` tool over a BM25 index of the seven pages
(Agentic RAG), once with `list_pages`, `grep_wiki` and `read_page` over the
same pages as a wiki (DCI). The model, the corpus, the questions, the loop and
the scoring are identical. Six columns come back per run: **pass** (the
reviewed terms appear in the answer), **cited the expected page**, **calls**,
**evidence characters read**, **latency**, and **how the loop stopped** — plus
the approach each question was written to **favour**, decided before the run.

**The seven questions are traps with the mechanism showing.** `vocabulary` asks
for the £45 tariff as "forty-five pounds" so BM25 has nothing to rank on;
`deep_section` puts the answer past the retriever's visible 1,000-character
cap on the truck-roll stage; `which_pages` asks a question top-k cannot answer
and one grep can; `broad_churn` and `broad_incident` scatter the answer across
pages so that ranking's fixed cost beats reading them whole. `exact` is the
baseline both pass in one call. `decline` asks for a year the corpus does not
cover: neither interface can say "nothing matched", so the pass mark is a
refusal that invents no figure — the behaviour the challenge's endpoint has
to show on its own labelled decline question.

**Measured, with `anthropic/claude-sonnet-5` as the model and six turns as the
budget — predicted against observed:**

| case | favours | RAG pass | DCI pass | RAG calls | DCI calls | RAG chars | DCI chars | RAG s | DCI s |
| --- | --- | :---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `exact` | either | ✅ | ✅ | 1 | 1 | 1,922 | 671 | 2.7 | 2.9 |
| `vocabulary` | DCI | ✅ | ✅ | 2 | 1 | 3,805 | 4,777 | 3.2 | 2.3 |
| `deep_section` | DCI | ❌ | ✅ | 1 | 2 | 2,416 | 8,487 | 7.5 | 5.1 |
| `which_pages` | DCI | ✅ | ✅ | 1 | 1 | 1,838 | 1,882 | 7.6 | 6.4 |
| `broad_churn` | RAG | ✅ | ✅ | 2 | 3 | 4,834 | 2,224 | 6.8 | 12.5 |
| `broad_incident` | RAG | ✅ | ✅ | 2 | 4 | 3,943 | 12,465 | 7.6 | 11.6 |
| `decline` | either | ✅ | ✅ | 3 | 2 | 5,284 | 866 | 5.7 | 8.1 |

Averaged: Agentic RAG passed 6 of 7 at 1.7 calls, about 3,430 evidence
characters and 5.9 s per question; DCI passed 7 of 7 at 2.0 calls, about
4,480 characters and 7.0 s.

**The cap decides what a retriever can find.** `deep_section` is the clean
row: BM25 ranked the truck-roll stage first and the RAG agent still failed,
because the contact-on-the-day item sits past the 1,000-character cap that
`search_chunks` applies to every section. `read_page` returned the whole
stage. Every chunk retriever has that cap somewhere; this one is in the
function so the room can see it bite.

**Vocabulary decides how many searches it takes.** On `vocabulary` — the £45
tariff asked for as "forty-five pounds" — the RAG agent's first search had
nothing to rank on and it needed a second; the DCI agent read the index, saw
a page called tariffs, and read it once. Both passed. The route is the
finding.

**"Which pages mention X" is one grep.** DCI answered `which_pages` in a
single call for 1,882 characters with page and line numbers; RAG matched it
on pass and on cost here, but a ranked top-k cannot promise to list *every*
page, and a grep can. The first run of this case also showed the trap: the
field guide originally said "the Coast *aggregation* cache", the exact-string
grep missed it, and BM25 — scoring the two words separately — did not.

**Breadth is where ranking is cheap.** On the two `broad_*` questions both
approaches passed, and DCI paid 3–4 calls to RAG's 2 and roughly twice the
wall-clock to do it. On `broad_incident` that meant 3.2× the evidence
(12,465 characters — the runbook and the network page read whole); on
`broad_churn` DCI happened to pick short pages and read *fewer* characters
than RAG, but still took 12.5 s against 6.8 s, because each read is a round
trip. Reading whole pages costs what the pages cost and ranking costs what
the top sections cost; the round trips are the part the character count
does not show.

**Declining is a tool-shape problem too.** On `decline` neither interface
can return "nothing matched" — `search_chunks` always returns a top-k, and
grep returns an empty list the model has to interpret. RAG searched three
times (5,284 characters of near-misses) before saying no; DCI read the index,
grepped for the year, got nothing, and said so in 866 characters. Both
refused without inventing a figure, which is the pass mark.

**Latency follows round-trips, not characters.** The two slowest runs are
DCI's multi-call `broad_*` answers (12.5 s and 11.6 s); the fastest run in
the table is DCI's single read on `vocabulary` (2.3 s), which beat RAG's two
searches (3.2 s). And `which_pages` and `deep_section` took 6–8 s on *one*
RAG call, because the model wrote a long answer — generation time is part
of the cost line too, and evidence volume predicts tokens better than it
predicts seconds.

**What the marks are.** `pass` is a keyword check — every reviewed term
appears in the answer — and `cited` is a page name in the answer text. A ❌
is "the reviewed words were missing", not "the answer was wrong"; the first
run of `broad_churn` failed both sides on a label that named the *fix* for
churn rather than a cause, and the answers were correct. Read the trace
before trusting the mark; that discipline is Step 1 of the challenge.

### Session 6 — three strategies over the same twelve records

Session 6 builds three ways of retrieving across text and images on one Qdrant
instance and scores each with recall@3 against eight gold questions. The
corpus is small by design — six charts and six memos — so the numbers are a
harness and a side-by-side, not a benchmark; what they show is *where* each
strategy fails, which is the thing that transfers to a corpus of nine hundred
screenshots.

**Four of the six numbers exist only as pixels.** Ticket volume, churn,
latency and the root-cause split are in no memo. So the first demo question —
*which quarter had the most tickets, and how many?* — can be answered only by
a pipeline that retrieves the right chart *and* reads it, and a text-only
pipeline returns the nearest memo with a confident wrong answer.

**The parse check is the number that decides the architecture.** Every chart's
machine-written parse is compared, number by number, against the values the
chart was drawn from. A vision model that reads `27` as `21` produces a caption
that is fluent, indexable and wrong, and retrieval never notices — until
somebody searches for the number. The `invented` column of that table is what
has to be zero before a caption is allowed to feed the index unreviewed.

**The shared space finds the chart and cannot read it.** With CLIP loaded,
*"a bar chart comparing line latency across regions"* ranks the latency chart
first among the images with no caption involved — and in the unified ranking a
memo outranks it, because text vectors and image vectors occupy different
regions of the same space (the modality gap). Neither the shared space nor the
caption can say `240 ms`; the answer model reads it off the retrieved pixels,
and reads three candidates, never the corpus.

**Fusion is by rank because the scores do not compare.** Strategy C merges a
text-store list and an image-store list with Reciprocal Rank Fusion. A cosine
of 0.31 from the text embedder and 0.27 from CLIP mean different things; a
rank of 1 and a rank of 2 do not.

**Measured, with CLIP loaded and `anthropic/claude-sonnet-5` as the parser:**

| strategy | recall@3 over 8 gold questions |
| --- | ---: |
| A — caption → text | 1.00 |
| B — one shared CLIP space | 0.25 |
| C — separate stores, fused by rank | 1.00 |

**A and C tie, and B is the number that explains both.** A wins because the
captions carry the facts in the words the questions use, and a good parser on
twelve records is hard to beat. C wins the same questions by a different
route — the memo questions from the text store, the chart questions from
CLIP's image store, fused by rank — at the price of two searches per query.
B loses six of eight because memos and charts compete in one ranking and
CLIP's text and image vectors sit in different regions of that space: a
question about NPS lands next to the memo that mentions NPS, not the chart
that shows it. That is the modality gap, measured — and the reason Task 4's
images-only filter and Strategy C exist.

**Why A and C tie, and where they separate.** Those eight questions are
*factual* — they ask what a chart says, in the words the caption uses — and
on that phrasing a caption index cannot lose. Task 7 also scores three
*visual* questions ("a pie chart", "a line chart that goes up, dips, then
rises again"), which no caption mentions because the parser was asked for
content, not form. That is the caption bottleneck, and the only regime where
the pixels can win: A has nothing to match, C finds the chart through its
image store. It is also the cost case for the screenshots — nine hundred
vision calls before A's first search, or nine hundred cheap embeddings for C.

**Measured, same run:**

| strategy | recall@3 · factual (8 q) | recall@3 · visual (3 q) |
| --- | ---: | ---: |
| A — caption → text | 1.00 | 0.33 |
| B — one shared CLIP space | 0.25 | 0.00 |
| C — separate stores, fused by rank | 1.00 | 0.67 |

On *"a pie chart"*, A's top three are a memo and two other charts — no
caption contains the word — while C places the root-cause pie second from
its image store. On *"a line chart that goes up, dips, then rises again"*,
A and B return only memos and C places the NPS chart second. C's miss is
the vaguest phrasing, *"a chart made of coloured wedges"*; A's one hit is
that same question, which on twelve records with three slots is a lucky
draw rather than a match. B scores zero because even a question about
appearance lands nearer the memos in a mixed ranking.

**The parse check, same run:** every number the model read off the six
charts matched the answer key, and the "invented" column carried two
derived figures — a headcount total of 105 and a 19-point NPS rise — that
are correct and are in no chart. The check cannot tell a correct inference
from a hallucination; a person can, which is why the column exists.

### Terms you'll meet

You do not need to know any of these in advance. This is what each one means
in one sentence, and where it comes up. Every term from every week is also
collected, alphabetically, in the repository's [`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it bites |
| --- | --- | --- |
| **LLM Wiki** | A knowledge base kept as Markdown pages with stable names, headings and an index page a model can read — a course term, not a protocol | S5 Task 1, and the precondition for the second approach |
| **Direct Corpus Interaction (DCI)** | The agent lists, searches and reads the pages itself; no retriever selects context on its behalf | S5 Task 1 |
| **Agentic RAG** | The agent can run several chunk searches and reformulate between them, but only ever sees ranked chunks | S5 Task 1 |
| **Chunking** | Long documents are split before indexing — here at every `##` heading — because one entry for forty pages means nothing specific | S5 Task 1, and most retrieval bugs anywhere |
| **Inverted index / BM25** | Terms that are frequent here and rare everywhere are the informative ones; how search worked before embeddings | S5 Task 1 |
| **Tool-calling loop** | The model asks for a tool, the code runs it and returns the result, and the model decides whether to ask again or answer — with a turn budget | S5 Task 2 |
| **Trace** | The ordered record of every tool call, its arguments and what came back; what an auditor replays and what a cost line is built from | S5 Tasks 2–4 |
| **Top-k** | Retrieval always returns the *k* best matches — there is no "nothing matched" | S5 Task 1, S6 Task 3 |
| **Vision-language model** | A model that looks at an image and writes about it; reading is a different operation from embedding | S6 Task 2 as a parser, Task 6 as a reader |
| **Contrastive learning** | Pull matched pairs together and push mismatched ones apart, so two kinds of thing land in one comparable space — CLIP's text and image towers | S6 Task 4 |
| **Modality gap** | In a shared image–text space, text vectors cluster apart from image vectors, so a text query sits closer to any text than to the right image | S6 Task 4, and why one mixed collection is fragile |
| **Reciprocal Rank Fusion** | Merge ranked lists by giving each item `1/(k + rank)` from every list and summing — ranks compare, raw scores from different embedders do not | S5 Task 5, S6 Task 5 |
| **Keyframe** | One sampled frame standing in for a window of video, attached to the transcript segment it belongs to | S6 Task 8 |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions rarely use the words a
syllabus uses, and that costs people interviews. This week is advertised as
**context engineering** — also **retrieval systems**.

"RAG" is printed surprisingly rarely as a keyword; the same work is advertised
as retrieval systems, query planning, and "knowing how to actually measure good
search results".

**Back to Week 1** — the pydantic schema you wrote in Session 2 is the contract
this endpoint implements. You are not designing now; you are building what you
specified.

**Back to Week 2** — you retrieve over the synthetic data you generated, and its
`DATASHEET.md` tells you what that data can and cannot prove.

**Forward to Week 4** — the questions you use to compare techniques become the
retrieval half of your eval harness. Label which document *should* answer each
one and you have recall@k for free.

**Forward to Week 5** — you will be asked to defend this architecture against
the options you rejected. `use_case/decisions.md` is where that answer lives, so
write it while you still remember the reasoning.

**Forward to Week 6** — your corpus is an injection surface. The attacks arrive
through retrieved content, and the questions you labelled this week are the
ones they must not break.

**Forward to Week 8** — the same data constraint returns, sharper: you cannot
synthesise a photograph. The non-text decision you wrote this week is where
that conversation starts.

**Forward to Week 10** — the three "what you would swap" lines from Step 7
join the final report's list of what it would take to run for real.

### Where the industry is headed

**Long context did not delete retrieval, and the reason is not accuracy.**
Models now take hundreds of thousands of tokens, and for a small corpus you can
often skip retrieval entirely. What stops it is cost and latency, which scale
with every token on every request, and the fact that a model given everything
attends unevenly to the middle of it. Retrieval is increasingly a *cost and
precision* decision rather than a capability one.

**Agentic search is eating top-k.** The direction of travel is away from "embed
everything, retrieve k chunks, stuff the prompt" and toward giving a model
search tools and letting it run several queries, read, and search again. The
trade moves cost from indexing to inference and makes latency harder to
predict — which is why Session 5 measures it against the alternatives rather
than assuming it.

**The OCR-versus-visual question is moving.** Document-image retrieval is
improving quickly; the transcript is still the right index for most video, and
that is unlikely to change. The unglamorous parts — chunking, provenance,
freshness, access control — are where retrieval systems actually fail, and no
embedding model has ever fixed any of them.
