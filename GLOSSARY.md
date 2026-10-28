# Glossary

Every term the course leans on, in one place, alphabetically — with the week
where it first bites. Each line is the same one-sentence version that appears
in that week's README under *Terms you'll meet*; this file just collects them,
so you can look something up without remembering which week introduced it.

None of these needs to be known in advance. If a session uses a word before
this file defines it, that is a bug in the course — say so in the notebook
feedback form.

| Term | The one-sentence version | Where it bites |
| --- | --- | --- |
| **A schema as a contract** | The same type definition used by the API, the tests, and the eval harness, so they cannot disagree | Week 1: S2 discussion, and TC1 Step 5 |
| **Agent vs. pipeline** | An agent decides its own next step; a pipeline follows the steps you wrote | Week 1: S2 discussion, which is the argument of that session, and TC1 Step 6 |
| **Agentic RAG** | The agent can run several chunk searches and reformulate between them, but only ever sees ranked chunks | Week 3: S5 Task 1 |
| **Batching** | Serving several requests through one forward pass, multiplying the cache by requests in flight | Week 2: S3, the hardware section |
| **Bootstrap interval** | Resample your results thousands of times to see how much the number would move with a different sample of the same size | Week 4: S7 Task 5 |
| **CA bundle** | The list of authorities your tools trust; Python's is not your operating system's | Week 1: The remediation you will need if Task 1 shows your employer's name |
| **Capability report** | Pass rate per capability rather than overall — the artifact a stakeholder reads, and the baseline a change is compared against | Week 4: S8 Task 7 |
| **Chance floor** | What a metric would read if the thing it measures were absent; a number sitting on it is not a signal | Week 4: S7 Bonus 1 |
| **Character n-gram Jaccard** | Overlap between two texts' sets of 4-character shingles — a model-free near-duplicate detector | Week 2: S4 Task 4 |
| **Chunking** | Long documents are split before indexing — here at every `##` heading — because one entry for forty pages means nothing specific | Week 3: S5 Task 1, and most retrieval bugs anywhere |
| **Contextual precision / recall** | Of the chunks retrieved, how many were needed (precision); of the chunks needed, how many were retrieved (recall) — the retrieval half of a RAG score | Week 4: S7 Task 1 |
| **Contrastive learning** | Pull matched pairs together and push mismatched ones apart, so two kinds of thing land in one comparable space — CLIP's text and image towers | Week 3: S6 Task 4 |
| **Datasheet** | The document that says where a dataset came from and what it cannot validate | Week 2: S4 Task 7 |
| **Deterministic scorer** | A function comparing output to expected with no model involved | Week 4: S7 Task 3 |
| **Direct Corpus Interaction (DCI)** | The agent lists, searches and reads the pages itself; no retriever selects context on its behalf | Week 3: S5 Task 1 |
| **End-to-end / trajectory / component** | The three levels an agent can be scored at: the final answer, the path of tool calls, each call's arguments | Week 4: S8's opener |
| **Exact match / F1** | Two ways of scoring partial correctness, and they disagree | Week 4: S7 Task 3, and the ladder in Task 5 |
| **Faithfulness** | What fraction of an answer's claims the retrieved context actually supports — in DeepEval's default, *does not contradict* | Week 4: S7 Task 1, where DeepEval computes it |
| **Forward pass** | One run of the network over the input, producing a score for every vocabulary token at the next position | Week 2: S3 Task 1, and Task 7's generation loop |
| **G-Eval** | A judge that writes its own evaluation steps from a one-sentence criterion, then scores with them; DeepEval's rubric judge | Week 4: S7 Tasks 1 and 6, S7 Bonus 1 |
| **Generated artifacts** | A file built from another file is never hand-edited or hand-merged — it is regenerated | Week 1: S1 Task 2, and the only correct way to resolve an `.ipynb` conflict |
| **Golden examples** | Inputs paired with outputs a human judged correct, written before any system exists | Week 1: S2 discussion, and TC1 Step 7 |
| **Ground truth** | The answer a human judged correct, recorded before the system ran | Week 4: S7 intro, and Question #1 |
| **Harness validation** | Testing the test — feeding it agents you know are broken and checking it notices | Week 4: S8 Task 5 |
| **Inverted index / BM25** | Terms that are frequent here and rare everywhere are the informative ones; how search worked before embeddings | Week 3: S5 Task 1 |
| **Keyframe** | One sampled frame standing in for a window of video, attached to the transcript segment it belongs to | Week 3: S6 Task 8 |
| **KV cache** | The per-request memory that lets token 200 cost one forward pass instead of two hundred; it is what you provision alongside the weights | Week 2: S3, the hardware section |
| **Leak (inward)** | Your evaluation set drawn from the same data the system was tuned on, so the score measures self-consistency | Week 2: S4 Task 6 |
| **Leak (outward)** | A distinctive string from your seeds surviving into data you will share | Week 2: S4 Task 6 |
| **LLM Wiki** | A knowledge base kept as Markdown pages with stable names, headings and an index page a model can read — a course term, not a protocol | Week 3: S5 Task 1, and the precondition for the second approach |
| **LLM-as-judge** | Using a model to score outputs a function cannot score | Week 4: S7 Task 4 |
| **Logit** | The raw score for each candidate next token, before it is turned into a probability | Week 2: S3 Task 1 |
| **Modality gap** | In a shared image–text space, text vectors cluster apart from image vectors, so a text query sits closer to any text than to the right image | Week 3: S6 Task 4, and why one mixed collection is fragile |
| **Open weights** | A model whose parameters you can download and run yourself | Week 2: S3 Task 7 onward |
| **origin and upstream** | Your fork is where you push; the course repository is where you pull updates from. Different remotes, different jobs | Week 1: S1 Task 2 |
| **`pass^k`** | The chance that *k* consecutive attempts all succeed; what a user experiences, rather than a rate | Week 4: S8 Task 6 |
| **Prompt caching** | A hosted provider keeping a processed prompt *prefix* and charging far less to reuse it | Week 2: S3 Task 9 |
| **Prototyping vs backtesting data** | Generated to exercise a pipeline, versus drawn from real outcomes and able to support a production number | Week 2: S4 Task 1, and the datasheet |
| **Provider abstraction** | One calling convention over many model vendors, so the vendor is a config value | Week 1: S1 Task 4 |
| **Reciprocal Rank Fusion** | Merge ranked lists by giving each item `1/(k + rank)` from every list and summing — ranks compare, raw scores from different embedders do not | Week 3: S5 Task 5, S6 Task 5 |
| **Regression** | A change that improves one thing and quietly breaks another — the reason the harness exists at all | Week 4: Every later week |
| **Sampling** | Choosing one token from those probabilities — the only place randomness enters | Week 2: S3 Tasks 2–6 |
| **Scenario** | A goal plus information the user has but will not volunteer unless asked, with its own success check | Week 4: S8 Task 1; composed from atoms in Task 2 |
| **Seed** | The number that makes a random choice repeatable | Week 2: S3 Task 6; Legal's requirement |
| **Separation and agreement** | The two halves of checking a judge — does it rank known-bad below known-good, and does it score the way a person would | Week 4: S7 Task 4, the step everyone skips |
| **Simulated user** | A model playing a person with a goal, talking to your system so the test can run without a human | Week 4: S8 Tasks 1 and 6 |
| **Softmax** | The step that turns logits into probabilities that sum to one | Week 2: S3 Task 1 |
| **TLS and certificate chains** | Your client trusts a server because a certificate authority it already trusts signed that server's certificate | Week 1: S1 Task 1 — the "Signed by" column |
| **TLS interception** | A corporate proxy terminates your encrypted connection, reads it, and re-signs it with the firm's own CA | Week 1: S1 Task 1, and every failed `pip install` for the rest of your career |
| **Token** | The unit a model reads and writes — usually a word piece; 30 tokens is roughly 20 words | Week 2: S3 intro, and every count in Task 9 |
| **Tool-calling loop** | The model asks for a tool, the code runs it and returns the result, and the model decides whether to ask again or answer — with a turn budget | Week 3: S5 Task 2 |
| **Top-k** | Retrieval always returns the *k* best matches — there is no "nothing matched" | Week 3: S5 Task 1, S6 Task 3 |
| **Trace** | The ordered record of every tool call, its arguments and what came back; what an auditor replays and what a cost line is built from | Week 3: S5 Tasks 2–4 |
| **Trajectory** | The full sequence of turns, tool calls with their arguments, and results — not just the final output | Week 4: The premise of S8; Task 3 records it |
| **Unit economics** | Cost per request × requests, against the cost of the work being replaced | Week 1: S2 discussion, and TC1 Step 13 |
| **Variation axes** | The dimensions along which real inputs differ, which you generate across on purpose | Week 2: S4 Task 2 |
| **Verifier** | A programmatic success check — tools called, fact stated, state changed — used wherever the outcome is checkable, before any judge | Week 4: S8 Task 4 |
| **Vision-language model** | A model that looks at an image and writes about it; reading is a different operation from embedding | Week 3: S6 Task 2 as a parser, Task 6 as a reader |
| **Vocabulary** | The fixed list of every token a model knows, and the only things it can ever output | Week 2: S3 Task 1 |

---

*Maintainers: this file is generated from the `### Terms you'll meet` table in
each week's README — add a term there, then run
`uv run python scripts/make_glossary.py`. Do not edit the table above by hand;
`--check` in CI will fail if it drifts. Weeks without a terms table yet: none.*
