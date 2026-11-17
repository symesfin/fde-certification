<div align="center">
  <img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" width="200" alt="AI Makerspace logo" />
  <h1>Week 7 — Memory &amp; Harness Engineering</h1>
  <p><strong>🧠 For agents that run longer than one conversation</strong></p>
</div>

---

## 🎯 What you'll be able to do

Give your agent memory that still works with a second user and on the thirtieth
turn, and write the three tests that catch it when it starts to slip.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S13 | [`Three_Kinds_of_Memory`](./sessions/S13_Three_Kinds_of_Memory.py) | Semantic, procedural and episodic memory with **LangMem** on a **LangGraph store**, each with the test that catches it failing, plus the two-user leakage test. | Coming soon | Coming soon |
| S14 | [`Loop_Engineering`](./sessions/S14_Loop_Engineering.py) | A spec a machine can check, a checker you break on purpose, and a bounded loop around a fresh **LangChain Deep Agent** each iteration. | Coming soon | Coming soon |

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC7 — Memory, plus evals that test memory**](./challenge/README.md) | Coming soon |

---

## 📖 Overview

An assistant that forgets everything between conversations makes people repeat
themselves, so we give it memory. The catch is that memory gets worse over
time. It goes out of date and pulls back the wrong entry, and a wrong memory
looks just like a right one. So this week every kind of memory comes with a
test that catches it failing.

**Session 13 is memory inside your product.** "Memory" covers three different
jobs:

- **Semantic** memory holds facts, like which team a user is on.
- **Procedural** memory holds a learned how-to, so the agent doesn't work the
  same thing out twice.
- **Episodic** memory records what happened, so the agent can explain a past
  decision.

We build all three with LangMem, a memory library, on top of a LangGraph store,
which is a simple place to put and look up records. Each kind fails in its own
way. A fact goes stale when someone changes teams. A learned shortcut only
counts if you measure the saving. An episode the model writes about itself can
include a step it never took. We finish with the test that matters most at
work: two users ask the same question, and neither one sees the other's memory.

**Session 14 is memory around your own workflow.** Long agent runs drift as
mistakes pile up. A **Ralph loop** avoids that by restarting a fresh agent from
a written spec each time, carrying only short notes about what went wrong. We
build one around a LangChain Deep Agent. The hard part is the checker that
decides when the loop is done. We write one that looks strict, then watch a
lazy implementation that never reads its input pass it on the first try!

**The challenge** asks you to pick the one kind of memory your app needs, build
it, and write three tests that catch it failing: a stale fact, a saving you can
count, and an explanation checked against your own log. If your app has more
than one user, add the leakage test.

The big idea this week: **until you test your memory, you don't know what it
remembers.**

---

## 🔁 Ralph loops, and why they connect back to Week 1

A long agent run gets worse as it goes. Context degrades and mistakes
compound, so by turn forty you can be debugging the agent's confusion instead of
the problem. That is why a Ralph loop throws the conversation away each time
and keeps only short, curated notes.

> **You have been doing spec-driven development since Week 1.** `CLAUDE.md` is
> a spec: a written statement of how work should be done, read by a fresh agent
> every session. Week 1 asked you to fix the file, not the prompt, whenever the
> agent got the same thing wrong twice. That is the note-taking step of a Ralph
> loop, done by hand.

---

## 🔑 Required accounts, keys, and setup

Both notebooks need a chat model that can **call tools**. LangMem extracts
memories through a tool call, and a deep agent writes its answer with one. Set
it as `LLM_MODEL` in `.env`, reached through any OpenAI-compatible endpoint.
S13's Tasks 1 and 5 and S14's Tasks 1–3 make no model calls. A small local model
is enough:

```bash
unsloth run --model unsloth/Qwen3-4B-GGUF:Q4_K_M -p 8893
```

The packages (`langmem`, `langgraph`, `langchain-openai`, `deepagents`) are in
the `week7` group, so either route works:

```bash
make nb F=07_Memory/sessions/S13_Three_Kinds_of_Memory.py    # sandboxed, from the notebook's own header
make setup-week W=7                                         # or install the group into the root environment
```

The notebooks build LangChain's `ChatOpenAI` from `LLM_MODEL` and strip an
`openai/` prefix. A LiteLLM-only provider name (`anthropic/...`) will not work
here. Point at an OpenAI-compatible endpoint or gateway instead.

### Before the sessions

- **Find where your own tooling keeps its memory.** Claude Code has `CLAUDE.md`
  and a memory directory, and other assistants have their own. Open the files
  and read them. What a working system chose to write down teaches more than a
  description of what it could.
- **Hold a conversation past twenty turns, then ask about turn three.** Does
  the assistant get it right? Does it tell you when it is unsure? That drift is
  what S14's loop is built to avoid.
- **Write down one thing your app would need to remember between sessions.** A
  preference, a prior decision, a correction a user made. The challenge asks
  which of the three kinds it is, and the answer decides how you build it.
- **Find a task you have asked an agent to do more than three times.** A
  migration, a repetitive refactor, a data cleanup, a batch of similar
  endpoints. S14 ends on where a loop applies, and a real candidate makes that
  concrete.
- **Write that task's acceptance criterion as a command** that exits 0 or
  non-zero. If you can't, you have found S14's main point early. That is
  useful to know about the work.

---

## 📚 Recommended reading

- [SQLite FTS5](https://www.sqlite.org/fts5.html) — read the external-content table section
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — why fresh context beats long context
- [MemGPT / Letta](https://arxiv.org/abs/2310.08560) — memory tiers treated as an operating-system problem, with more machinery than you need
- [Generative Agents](https://arxiv.org/abs/2304.03442) — memory streams ranked by recency, importance and relevance, and the best-known worked example of episodic memory
- [Lost in the Middle](https://arxiv.org/abs/2307.03172) — models miss facts in the middle of a long context, which is why a bigger window is not a memory strategy
- [A Survey on LLM-based Autonomous Agents](https://arxiv.org/abs/2308.11432) — the wider map of where memory sits next to planning and tool use
- [How to Build an Agent](https://ampcode.com/how-to-build-an-agent) — Thorsten Ball builds an agent in a few hundred lines, and the loop stops looking like magic
- [Claude Code — Memory](https://docs.claude.com/en/docs/claude-code/memory) — how `CLAUDE.md` works, now that you know it is a spec
- [GitHub Spec Kit](https://github.com/github/spec-kit) — spec-driven development with more structure, to compare against the loop you build in S14
- [Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374) — the pass@k paper: sample many attempts and keep what passes the test, which is the case for restart-and-retry
- [Martin Fowler — Exploring Generative AI](https://martinfowler.com/articles/exploring-gen-ai.html) — a sceptical practitioner's series on agentic workflows, good for calibrating your enthusiasm

---

## 🏗️ Build | 🚢 Ship | 📤 Share

### 🏗️ Build
Three kinds of memory, each with the eval that catches its specific failure.
Then a loop that restarts an agent from a spec until a checker passes.

### 🚢 Ship
Give your app memory. Then add three tests to your eval suite that catch it
remembering the wrong thing. Memory can look fine right up until it is badly
wrong. See [`challenge/README.md`](./challenge/README.md).

### 📤 Share
Show a colleague a case where your agent remembered the *wrong* thing, and what
it took to notice.

---

## 📊 What the notebooks measure

### Three kinds of memory, three tests

| Kind | Holds | The test | The failure |
| --- | --- | --- | --- |
| **Semantic** | Facts | Ask for a fact from 30 turns ago | Confidently returns a *stale* fact |
| **Procedural** | Learned how-to | Is attempt two cheaper than attempt one? | Repeats a wrong method efficiently |
| **Episodic** | What happened | Can it explain a past decision? | An audit trail that lies |

### Staleness, reproduced and fixed

A naive store appends. The old fact and the new fact both match the query, and
the old one often ranks higher. S13 reproduces that bug, then fixes it with
supersede-on-write.

With LangMem the bug has a specific cause. The memory manager can only update
what its search shows it. With no index, a search returns the first five
entries. Tomás has six facts, and his team is the sixth. Told he moved, the
manager never saw the old team, so it added a new entry. Measured on Qwen3-4B:

| Schema | Entries after the change | Staleness test |
| --- | ---: | --- |
| LangMem's default collection | 7 | ❌ both teams recalled — 7 of 7 runs, thinking on and off |
| `UserProfile`, `enable_inserts=False` | 1 | ✅ one record, `team` updated in place |

### An episode that records what never happened

The assistant's reply said it checked a connection pool. No tool did. Asked to
record the conversation as an episode, LangMem recorded the check in five of
five runs. Episodic memory has to come from the tool log, not the model's
account.

### Procedural saving, counted

With procedures LangMem learned from two logs of failed attempts, the depot
lookup took 1 approach of 4 and the expense question 1 of 3. The scanner reset
had no procedure and still took 3 of 3.

### Cross-user leakage

If memory is keyed by anything less specific than the user, two people asking
the same question can get each other's context. In a regulated firm that can
be a reportable incident. S13's test is two users, the same question, and an
assertion that neither answer contains the other's facts. Writing it takes
about ten minutes.

### The loop, and its checker

S14's Ralph loop has three exits: success, budget exhausted, and **no progress**.
Two identical failures mean a third attempt will not help.

The session writes a reasonable-looking checker. Then it shows an
implementation that *never reads the ticket text* passing it, with a constant
urgency and an empty summary. The hole is easy to miss. Asserting `urgency in
{low, normal, high}` checks membership, not the value, so every constant
passes. Here is the same lazy agent against both checkers:

| Stop condition | Outcome | Iterations | What it shipped |
| --- | --- | ---: | --- |
| the lenient checker | ✅ "passed" | 1 | **the cheat** |
| the hardened checker | ✅ passed | 2 | a real implementation |

A loop produces whatever your checker accepts, faster and with more confidence
than you would.

### Notes carried between runs

The loop's notes are procedural memory, so S14 asks S13's question of your own
workflow: *is attempt two cheaper than attempt one?* A **scripted** agent shows
the mechanism, but it improves because it was written to. **The meaningful
number comes from a live agent:** a fresh LangChain Deep Agent each iteration,
reading its notes from an `AGENTS.md` in a LangGraph store keyed by a hash of
the spec. Measured on Qwen3-4B (thinking off), three cold-then-warm pairs:

| Run | Iterations | Stopped on | Passed |
| --- | --- | --- | --- |
| cold | 2, 2, 5 | no progress, no progress, budget | 0 of 3 |
| warm (seeded with the cold run's notes) | 5, 4, 2 | no progress ×3 | 0 of 3 |

None passed, and every run said why it stopped. Mostly the model never mapped
*urgent* to `high` or *whenever* to `low`. In two of three pairs the warm run
started further along: its first failure was the cold run's last. So the notes
changed where the loop started, and did nothing for whether it finished. Each
deep agent model call carried about 3,700 prompt tokens of framework before the
spec. S13 is where the saving is actually counted: approaches tried until one
works, `1 of 4` with a procedure against `3 of 3` without.

### Terms you'll meet

You do not need to know any of these in advance. The three kinds of memory are
in the table at the top of this section. The repository also has a
[`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it comes up |
| --- | --- | --- |
| **Context window** | The fixed amount of text a model can read at once | Why memory exists at all |
| **Stateless model** | The model remembers nothing between calls. Your application holds the state and sends it again | Why memory exists at all |
| **Retrieval as memory** | Store facts outside the context window and fetch them when they're relevant | S13 Task 2 |
| **Write policy** | Deciding what is worth remembering, which is harder than storing it | S13 Tasks 2 and 4 |
| **Supersede on write** | When a fact about a subject changes, replace the old entry so only one is live | S13 Task 2 |
| **Namespace** | The label a store files memories under; putting the user in it keeps users apart | S13 Tasks 1 and 5 |
| **Spec** | A goal, acceptance criteria a machine can check, and constraints | S14 Task 1 |
| **Spec-driven development** | Writing the acceptance criteria before the implementation, precisely enough to check | S14 Task 1 |
| **Machine-checkable criterion** | A test, a schema or a compiler: something that returns pass or fail with no human involved | S14 Task 2 |
| **Value vs. membership** | `x in {a, b, c}` passes for every constant. `x == expected` checks the value | S14 Task 2 |
| **Context degradation** | Long agent sessions pile up confusion, so later turns are worse than earlier ones | S14, the reason the loop restarts |
| **Bounded retry** | A loop that gives up after N attempts and says why it stopped | S14 Task 3 |
| **Note accumulation** | The only thing carried from one iteration to the next is what was written down | S14 Tasks 3 and 5 |
| **Idempotent restart** | Every iteration starts from the same state, so the results are comparable | S14 Task 4 |
| **Checker** | The code that runs the acceptance criteria and decides when the loop stops | S14 Task 2 |
| **Ralph loop** | A fresh agent restarted from the spec each iteration, carrying only short notes | S14 Task 3 |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions rarely use a syllabus's words.
This week is advertised as **context engineering**, and also as **agent
memory and state**. Postings mention context-window management and what an
agent carries between turns.
"Memory" on its own shows up less often than the problem does.

**Back to Week 1.** `CLAUDE.md` was a spec all along.

**Back to Week 3.** You built retrieval. Memory is retrieval over things the
agent wrote, instead of documents it was given. Swapping full-text search for
your embeddings is mechanical.

**Back to Week 4.** The memory tests run in that harness. Memory that isn't in
the harness isn't maintained.

**Forward to Week 10.** Episodic memory is where incident explanations come
from. It is how your agent answers "why did it do that?"
