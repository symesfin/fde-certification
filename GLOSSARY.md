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
| **Batching** | Serving several requests through one forward pass, multiplying the cache by requests in flight | Week 2: S3, the hardware section |
| **CA bundle** | The list of authorities your tools trust; Python's is not your operating system's | Week 1: The remediation you will need if Task 1 shows your employer's name |
| **Character n-gram Jaccard** | Overlap between two texts' sets of 4-character shingles — a model-free near-duplicate detector | Week 2: S4 Task 4 |
| **Datasheet** | The document that says where a dataset came from and what it cannot validate | Week 2: S4 Task 7 |
| **Forward pass** | One run of the network over the input, producing a score for every vocabulary token at the next position | Week 2: S3 Task 1, and Task 7's generation loop |
| **Generated artifacts** | A file built from another file is never hand-edited or hand-merged — it is regenerated | Week 1: S1 Task 2, and the only correct way to resolve an `.ipynb` conflict |
| **Golden examples** | Inputs paired with outputs a human judged correct, written before any system exists | Week 1: S2 discussion, and TC1 Step 7 |
| **KV cache** | The per-request memory that lets token 200 cost one forward pass instead of two hundred; it is what you provision alongside the weights | Week 2: S3, the hardware section |
| **Leak (inward)** | Your evaluation set drawn from the same data the system was tuned on, so the score measures self-consistency | Week 2: S4 Task 6 |
| **Leak (outward)** | A distinctive string from your seeds surviving into data you will share | Week 2: S4 Task 6 |
| **Logit** | The raw score for each candidate next token, before it is turned into a probability | Week 2: S3 Task 1 |
| **Open weights** | A model whose parameters you can download and run yourself | Week 2: S3 Task 7 onward |
| **origin and upstream** | Your fork is where you push; the course repository is where you pull updates from. Different remotes, different jobs | Week 1: S1 Task 2 |
| **Prompt caching** | A hosted provider keeping a processed prompt *prefix* and charging far less to reuse it | Week 2: S3 Task 9 |
| **Prototyping vs backtesting data** | Generated to exercise a pipeline, versus drawn from real outcomes and able to support a production number | Week 2: S4 Task 1, and the datasheet |
| **Provider abstraction** | One calling convention over many model vendors, so the vendor is a config value | Week 1: S1 Task 4 |
| **Sampling** | Choosing one token from those probabilities — the only place randomness enters | Week 2: S3 Tasks 2–6 |
| **Seed** | The number that makes a random choice repeatable | Week 2: S3 Task 6; Legal's requirement |
| **Softmax** | The step that turns logits into probabilities that sum to one | Week 2: S3 Task 1 |
| **TLS and certificate chains** | Your client trusts a server because a certificate authority it already trusts signed that server's certificate | Week 1: S1 Task 1 — the "Signed by" column |
| **TLS interception** | A corporate proxy terminates your encrypted connection, reads it, and re-signs it with the firm's own CA | Week 1: S1 Task 1, and every failed `pip install` for the rest of your career |
| **Token** | The unit a model reads and writes — usually a word piece; 30 tokens is roughly 20 words | Week 2: S3 intro, and every count in Task 9 |
| **Unit economics** | Cost per request × requests, against the cost of the work being replaced | Week 1: S2 discussion, and TC1 Step 13 |
| **Variation axes** | The dimensions along which real inputs differ, which you generate across on purpose | Week 2: S4 Task 2 |
| **Vocabulary** | The fixed list of every token a model knows, and the only things it can ever output | Week 2: S3 Task 1 |

---

*Maintainers: this file is generated from the `### Terms you'll meet` table in
each week's README — add a term there, then run
`uv run python scripts/make_glossary.py`. Do not edit the table above by hand;
`--check` in CI will fail if it drifts. Weeks without a terms table yet: none.*
