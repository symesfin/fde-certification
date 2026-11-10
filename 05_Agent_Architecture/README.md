<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Week 5 — Agent Architecture</h1>
  <p><strong>🧑‍💻 Demos with stakeholder-style critiques, and architecture decisions</strong></p>
</div>

---

## 🎯 What you'll be able to do

Present your work to a tough room, and answer "why did you build it that way?"
with a comparison you actually ran.

---

## 🔗 Quicklinks

| # | 📓 Material | What you'll build | ⏺️ Recording | 🖼️ Slides |
| --- | --- | --- | --- | --- |
| S9 | **No notebook.** [`Demo_Critique_Rubric`](./sessions/S9_Demo_Critique_Rubric.md) | Your five-minute demo, timed, then a sponsor's questions from the room. You leave with the ones you could not answer. | [Recording!](https://us02web.zoom.us/rec/share/B2k2V0xkdzoahopuC2kifjhugTvs2owjTF3KkIahYfF5dga3g6Ov6a5JU6DTw3MF.hH0_5nbax9XDzy4X) <br> passcode: `1yni.s*N` | [Slides](https://canva.link/xrm1agdozo9i7kg) |
| S10 | [`Six_Ways_to_Call_a_Capability`](./sessions/S10_Six_Ways_to_Call_a_Capability.py) | **FastMCP**: one function served six ways, a counter separating model calls from capability calls on all six (MCP over stdio included), and a sweep showing whose token bill grows. | [Recording!](https://us02web.zoom.us/rec/share/7kCBUCJ6mQ2oXFt0NJiZIwvRTmUX0EYNo5-DMTXlIh4eCWxMEJbN0oQ764djovzc.8FmORNXr3IQXmZTK) <br> passcode: `&AEr4mmZ` | [Slides](https://canva.link/n1itpi53q119stz) |

| 📝 Technical Challenge | 📁 Feedback |
| --- | --- |
| [**TC5 — The refined demo, and an architecture you measured**](./challenge/README.md) | Coming soon |

---

## 📖 Overview

Someone in a design review will ask why your system is built the way it is.
This week you practise being asked, and then you go and get a real answer.

**Session 9 is your demo, critiqued.** You present for five minutes, timed.
Then the room asks what your real stakeholders would ask a few months in:

- Who exactly has this problem?
- What is the number, and what is it out of?
- What did you consider and reject?
- What is the worst thing you have seen it do?

The questions are tough on purpose, and the room is on your side. You will not
be able to answer all of them. Write down the ones you can't, because they
become the first step of the challenge. There is no notebook, just a rubric.
The best preparation is to answer every question in it, in writing, before
you arrive.

**Session 10 gets you a real answer to "what did you reject?"** There are at
least six ways to let a model do something:

- hand it a function to call (a **tool**)
- give it a folder of instructions (a **skill**)
- hand the job to a second model (a **subagent**)
- run a separate server that other software can discover (an **MCP server**)
- let it write code against your functions (**Code Mode**)
- describe an HTTP API that already exists (**UTCP**)

We build all six around the same tiny function, one that looks up who is on
call for a service. Then we put a counter on them that shows what each one actually did: how many times the
model was called, how many times the function ran, and how many tokens
crossed between them.

The taught notebook builds all six with FastMCP, a Python framework that
generates the plumbing once you define the function. The deep dive builds
each one by hand. Several of the results contradict the usual advice. The
biggest one: for some ways, the cost grows with the size of what your
function returns, and for others it stays flat. On a toy you can't see the
difference. On real data it is large!

**The challenge** is your own architecture decision. You build a second
version of your endpoint, in the way the session's ordering says is second
best. You measure both at the size your endpoint really returns. Then you
write down which one you are keeping, what you rejected, why, and what would
make you switch. Finally, you refine the demo around what the room asked and
show it to a real stakeholder.

The big idea this week: **an architecture decision needs a rejected
alternative that you built and measured.**

---

## 🔑 Required accounts, keys, and setup

**Session 9 needs no environment at all.** Bring your app running, your
numbers, and the rubric.

**Session 10 needs a model that can call tools.** The taught notebook reads
the skill directory in `sessions/skills/` and starts
`sessions/oncall_fastmcp_server.py` as a subprocess. It writes nothing. The
deep dive writes a skill directory and an MCP server file to disk as it goes.

```bash
make nb F=05_Agent_Architecture/sessions/S10_Six_Ways_to_Call_a_Capability.py
```

**On Windows, or anywhere `--sandbox` is blocked**, open them from the root
environment instead:

```powershell
uv run python scripts/nb.py 05_Agent_Architecture\sessions\S10_Six_Ways_to_Call_a_Capability.py
```

The script installs the `week5` group into `.venv` (`uv sync --inexact
--group week5`) and starts marimo through Python. The reasoning is in
[`00_Prerequisites/5_Your_Notebooks`](../00_Prerequisites/5_Your_Notebooks/README.md#two-ways-to-run-a-notebook).

**The taught notebook runs FastMCP**, the standalone `fastmcp` package,
`fastmcp>=4.1`. It is in the notebook header and in the `week5` dependency
group (`make setup-week W=5` if you open it without `--sandbox`).

- It is not the `mcp.server.fastmcp` module older tutorials import. The `mcp`
  2.0 release **removed** that module. The SDK's own successor is `MCPServer`
  in `mcp.server`, which the deep dive uses.
- The deep dive's header installs `mcp` too, although it only *writes* its
  server file: recent LiteLLM releases import `mcp` for tool calls. Running
  that server outside the notebook still needs it installed (`uv add mcp`).
- FastMCP 4 is a separate project built on `mcp` 2.x.
- Code Mode's production sandbox is the `fastmcp[code-mode]` extra
  (`pydantic-monty`). The notebook does **not** install it. It runs the
  model's programs in a deliberately unsafe stand-in and says so.

**What reaches the network, for a managed laptop:** only your model provider,
through `CFG.kwargs()`. Every MCP client in the notebook is in-memory or a
local stdio subprocess, and the "existing HTTP API" is served in-process.
FastMCP checks PyPI for a newer version whenever a server prints its startup
banner. The stdio server here runs with `show_banner=False`, so it does not.
Set `FASTMCP_CHECK_FOR_UPDATES=off` to turn the check off for every server you
run.

**The measurement cells are behind buttons.** Together they cost about fifty
model calls, and nothing fires on open. The numbers under *What the notebooks
measure* are one run against one model. Press the buttons and get your own.
The parallel-tool-call result in particular depends on your model and its
tool-call parser.

### How Session 9 runs

- **Breakout rooms.** One room cannot hear thirty five-minute demos. Expect
  three or four rooms of eight to ten, each with an instructor or SME
  moderating and keeping the clock. Room assignments are posted in the Maven
  community the day before. Check yours.
- **Questions go in the Zoom chat while you present**, so they don't eat your
  five minutes. The moderator picks the hard ones to ask aloud afterwards. The
  rest stay in the chat for you to copy into `use_case/decisions.md`.
- **Feedback after the session goes on your TC5 thread in Maven.** Peers who
  run out of time, or want to think longer, post there. So do SMEs who could
  not be in your room.
- **AV check, ten minutes before your room starts.** Join early, share your
  screen, confirm your audio, and run your app once on the call. Don't spend
  your first minute on "can you see my screen?"
- **If you arrive without a demo**, you still attend, still critique, and
  still post your questions. You present first the following week. The
  critique needs a full room.
- **Sign up for a slot** through the form linked in the Maven community once
  it is posted. Slots go in submission order, and the earliest ones get the
  freshest room.

### Before the sessions

- **Rehearse the five minutes out loud, against a clock, at least three
  times.** If your first run is seven minutes, that is how you find the
  ninety seconds to cut.
- **Read the rubric's *What the room asks* list and write an answer to every
  question.** Sentences, not slides. Work longest on the ones you struggle
  with.
- **Get one number with a denominator**, and decide your ask in advance: who,
  specifically, and for what. *"I need thirty minutes with the platform
  engineering lead"* is an ask. *"I'd welcome any thoughts"* is not.
- **Look at a tool definition you already use** (in your own app, in Claude
  Code, in any framework) and count its tokens. You pay for them on every
  request, whether the tool is called or not. That cost is the argument for
  Session 10's second way, the skill.
- **Have your endpoint runnable.** The challenge implements it a second way.

---

## 📚 Recommended reading

The first two close the gap between Session 10 and the challenge. The
session builds six ways around a four-key dictionary. The challenge builds one
of them around your real endpoint. The rest are the core texts behind the two
sessions.

- [Gradio: Building an MCP server](https://www.gradio.app/guides/building-mcp-server-with-gradio). **How the `@app.api` endpoint you already have becomes an MCP server**, without writing a server by hand. The likeliest second way for most students
- [FastMCP: Composing servers](https://gofastmcp.com/servers/composition). `mount`, the one call that turns several teams' servers into one endpoint other clients can discover. Read it before you promise anyone a platform
- [LiteLLM: function calling](https://docs.litellm.ai/docs/completion/function_call). **The `completion(tools=...)` loop, including parallel tool calls.** Count them on the first turn before you believe any round-trip arithmetic
- [Model Context Protocol: Introduction](https://modelcontextprotocol.io/docs/getting-started/intro). The specification's own overview. Read the architecture section and note what it assumes about who is on each end
- [Anthropic: Tool use overview](https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview). Way 1, in depth. The description field is the interface
- [Anthropic: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills). The progressive-disclosure argument behind Way 2
- [Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp). The argument behind Code Mode, with the token arithmetic worked out
- [UTCP](https://www.utcp.io/). The specification. Short. Read it with "who holds the credential" in mind
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). The vocabulary for your architecture answer, and the reading for the critique
- [AI Agents That Matter](https://arxiv.org/abs/2407.01502). On numbers that do not survive scrutiny. Read the section on cost-controlled comparison, then look at your own claims again

**Pre-reads for Session 10**, ten minutes each. All five are listed above:

1. the MCP introduction
2. the tool-use overview
3. Agent Skills
4. Code execution with MCP
5. UTCP

After the MCP overview, that is the order the Ways appear in the session.
Arrive with one question about which of them your own endpoint is.

---

<!-- deliverables:start -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A second implementation of your endpoint, in the way you judged second best,
measured against the first at your real response size. That measurement is
what lets you defend the decision.

Four questions are asked inside the Session 10 notebook as you work through
it. *They are not submitted and not graded.* They help you work out what the
challenge is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | What your endpoint's dispatcher does today on a tool name it does not have, and which of the five failure rows a user of your app would meet first | S10 |
| 2 | Who outside your codebase would need to discover your capability in the next year (a named client), and what MCP buys you if the answer is nobody | S10 |
| 3 | How many bytes your endpoint really returns per call, how many calls a request needs, and where that puts you on the tool-loop slope | S10 |
| 4 | Which of the six ordering questions decides it for *your* endpoint, and the condition under which you would switch | S10 |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar, for example `#discuss-question-3`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which has the full detail.

- [ ] **The room's questions written down** in `use_case/decisions.md`: the two you will fix, and the one you could not answer
- [ ] **A second implementation of your endpoint**, in the way you judged second best, running
- [ ] **Both implementations measured**: model calls, **capability calls**, latency and tokens, on the same two requests
- [ ] **The token measurement repeated at your endpoint's real response size**, with the size in bytes recorded
- [ ] `use_case/decisions.md` has the architecture row: decision, closest reject, why in terms of the six questions, and **switch condition**
- [ ] It still runs in Docker

### 📤 Share

- [ ] **The refined demo, shown to a real stakeholder**, with what changed after critique and what they asked, recorded in your own words. Graded
- [ ] **What you would swap to run this at work**: data, model or endpoint, and the approval you would need, as three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## 📊 What the notebooks measure

Notebooks ship without outputs, so this is where the numbers live for anyone
reading on GitHub. Session 9 has no notebook. Its material is the rubric.

### Session 10: the six ways on FastMCP, measured

Measured with `unsloth/Qwen3-4B-GGUF` on a laptop GPU, thinking disabled for
speed. We used a small model on purpose. Two of the findings below are about
what a small model does with what you hand it.

**Six ways, four lookups, one counter.** Middleware on the server counts
`capability calls`, so it sees every call that reaches the tool and nothing
that does not. The one exception is MCP over stdio: the server is in another
process, so its calls are counted on the client — the same blind spot the
skill has, handled by moving the counter. Two models, same cells:

| 4 lookups | Model calls | Capability calls | Tokens (Qwen3-4B) | Tokens (claude-sonnet-5) |
| --- | :---: | :---: | ---: | ---: |
| **Tool** | 2 | 4 | 739 | 1,928 |
| **MCP (stdio)** | 2 | 4 *(client-side)* | — | *Tool's numbers, plus ~0.7 s to start* |
| **Skill** | 2 | *0 — in a subprocess* | 708 | 1,428 |
| **Subagent** | 1 | *0 — reciting its prompt* | 240 | 426 |
| **Code Mode** | 2 | 4 | 1,025 | 1,957 |
| **UTCP** (`from_openapi`) | 2 | 4 | 822 | 1,912 |

Code Mode costs two model calls here. FastMCP's `execute` is a tool, so its
return value goes back to the model to write the answer. Both models issued
all four lookups in one turn, so `Tool` is 2 model calls either way. The
larger model costs more tokens everywhere — longer answers, and a longer
program in Code Mode — and the shape of the table is identical.

**Code Mode stays flat, as long as the program returns only what it needs.**
Same four lookups, growing what each one returns, with Code Mode run three
times per size:

| Record size | Tool (Qwen3-4B) | Code Mode, median of 3 | worst of 3 | Tool (claude-sonnet-5) | Code Mode, median of 3 | worst of 3 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 118 B | 874 | 1,019 | 1,025 | 1,989 | 1,956 | 1,957 |
| 900 B | 2,300 | 1,025 | 1,025 | 3,578 | 1,958 | 1,962 |
| 2,468 B | **5,361** | **1,025** | 1,025 | **6,855** | **1,958** | 1,967 |

At the bare record Code Mode costs *more*, because its brief and its program
are a fixed price. At 2.5 KB the tool loop costs 5.2× as much on the small
model and 3.5× on the large one — and on the large one the worst of three
runs was within ten tokens of the median every time, which is the brief
holding.

The flat line depends on the tool description:

- Drafts of the brief said what to return ("only the fields the question asks
  for, never whole records") but not why. With those, the same model returned
  whole records in at least 6 of 30 Code Mode sweep runs. Those runs cost
  **2,568 to 5,652** tokens, more than the tool loop at the same record size.
- Adding *why* ("whatever you return is sent back to you in full") took that
  to 0 of 27.

These counts combine this notebook's sweep and a scratch script running the
same sweep. The notebook shows one run of three per size.

**FastMCP refuses a tool it does not have, and a small model gives up when
told only that.** A stale tool list offers `lookup_team`, and the model asks
for it. A loop with no name check would run `who_is_oncall` and answer from
it. The MCP client returns `Unknown tool: 'lookup_team'` instead.

- **Told only that message**, the model apologised and said it had no
  information: 12 of 12 scratch runs of the same two calls, and 4 of 4 runs of
  the notebook's cell.
- **Told the tools that exist as well**, it called `who_is_oncall` next: 12 of
  12 scratch runs, and 3 of 4 notebook runs (the fourth said it would look and
  did not).
- **With Qwen3's thinking left on**, in the one full run, the same model
  recovered from the bare message too. A reasoning model can infer the right
  tool. A non-reasoning one needs to be told.

**With thinking on, everything costs more and Code Mode gets fragile.** This
is one full run with Qwen3's default thinking.

- Four lookups cost the tool loop 1,270 tokens and 19.5 s (739 and 1.6 s
  without thinking).
- Code Mode repeatedly sent its program as one line of literal `\n` escapes.
  It was told only "unexpected character after line continuation character",
  and sent the same line back until the loop's six rounds ran out. That cost
  15,545 tokens on the four-lookup question for no answer, and up to 33,206 on
  one sweep run.
- Telling it what was wrong helped only partly. In a scratch sweep of 12 runs,
  2 recovered and 3 still gave up.
- So the notebook's sandbox now restores the line breaks when, and only when,
  the program cannot parse as sent. The same scratch sweep then ran 9 of 9
  clean at 1,874–2,541 tokens per run, flat across record sizes.

Reasoning tokens count in `total_tokens`, so expect every number above to be
larger on a thinking model.

**MCP's cost is a process to start.** Same server, same call:

- in-memory: 3 ms to connect and 5.6 ms per call (1 ms and 2.6 ms on a
  Windows laptop)
- as a stdio subprocess: 1,316 ms to start and complete the handshake, and
  109 ms for the first call (486–1,316 ms across runs; 727 ms and 196 ms on
  the Windows laptop)

Four subprocess spawns for the skill took 58 ms.

### Session 10 deep dive: the reference run

**One capability, six implementations, and a counter.** The deep dive writes
all six by hand against the same on-call lookup, then measures five of them on
the same two questions. Every number below came out of a cell. Yours will
differ.

**Start with the `capability calls` column.** Asked for four services:

| 4 lookups | Model calls | Capability calls | Tokens |
| --- | :---: | :---: | ---: |
| **Tool** | 2 | 4 | 1,264 |
| **Skill** | 2 | *0 — in a subprocess* | 739 |
| **Subagent** | 1 | *0 — reciting its prompt* | 358 |
| **Code Mode** | 1 | 4 | 637 |
| **UTCP** | 2 | 4 | 1,309 |

<sub>Reference run, DeepSeek-V4-Flash on a local vLLM. MCP is left out on purpose: over stdio it is Way 1's arithmetic plus a process.</sub>

**Four lookups is four invocations in every architecture.** The work never
changes. What changes is how much of it crossed the model boundary. The
`Subagent` zero is a model reciting a table from its prompt, and that table is
stale the moment the data moves.

**Parallel tool calls cut the round trips.** Four tool requests arrive in
*one* assistant turn, so the tool loop costs **2 model calls, not 5**. The
common claim that "N tools means N+1 round trips" depends on the model.
Session 10 has you check yours.

**Code Mode's real advantage is that intermediate data never enters the
context.** Same four lookups, growing what each one returns:

| Record size | Tool | Code Mode |
| ---: | ---: | ---: |
| 118 B | 1,281 | 420 |
| 900 B | 2,719 | 146 |
| 2,468 B | **5,613** | **173** |

The tool loop scales with your data, because every result is read back into
the conversation. Code Mode stays flat. At 2.5 KB records that is **32× fewer
tokens**, and real capabilities return more than a four-key dict.

**A schema is cheaper than a sentence.** Asking a model for the same four-item
decision in prose cost **687–1,216 output tokens and 15–26 seconds**, with a
worst case of 86. Asking with a tool schema cost **~100 tokens and ~2
seconds**, and barely varied. Capping the prose version with `max_tokens`
returned an empty string. A reasoning model spends the budget thinking, so
truncation gets you no answer at all.

**A tool loop that does not check `call.function.name` runs the wrong function
and never says so.** The deep dive reproduces this in one model call with a
stale schema. Then it fixes it with the rule behind all six architectures: a
tool failure is a message, not an exception. The model is the only party who
can correct a bad tool call, so the error has to be addressed to it.

### The decision ladder, in the order that resolves fastest

1. Does it **already exist as an HTTP API**? UTCP. You describe it instead of
   building it. Settle who holds the credential.
2. Does anything **outside your codebase** need to discover this? MCP.
   Discovery is what the process boundary buys, and the only thing.
3. Does one request need **several calls, or calls that return a lot**? Code Mode.
4. Does the **knowledge change more often than the code**? A skill.
5. Does the work **read a lot to produce a little**? A subagent.
6. Otherwise a **tool**. The boring answer is usually right.

> **Don't reach for MCP just because it is the one people have heard
> of.** MCP earns its cost when a client you did not write needs to
> discover your capability. If your app is the only caller, you have taken on
> a deployment target for nothing.

**Code Mode's `SAFE_BUILTINS` is not a sandbox**, and Session 10 says so where
it builds it. Next week you are the person trying to break it.

### Terms you'll meet

You do not need to know any of these in advance. Each one gets one sentence
here, plus where it comes up. Every term from every week is also collected,
alphabetically, in the repository's [`GLOSSARY.md`](../GLOSSARY.md).

| Idea | The one-sentence version | Where it bites |
| --- | --- | --- |
| **The denominator** | A score means nothing without *on how many, of what* | S9, minute 2–3.5, and the first question the room asks |
| **Baseline** | What you are beating; without one, "84%" is unanchored | S9, the second question |
| **Tool / function calling** | The model emits a structured request; your code runs it and returns the result | S10 Way 1, and the foundation of the other five |
| **The docstring is the interface** | The model chooses a tool by reading its description, so that text works as the API | S10 Way 1 onward |
| **Parallel tool calls** | A model can request several tools in one turn, so N tools need not mean N round trips | S10 Task 5, where you check whether yours does (deep dive: Task 7) |
| **Context window cost** | Every tool definition, and every result a tool returns, takes up tokens on every request | S10 Way 2, and the whole of Task 5's sweep (deep dive: Task 8) |
| **Progressive disclosure** | Load the detailed instructions only once the capability is selected | S10 Way 2 |
| **Subagent** | A separate model invocation with its own context, returning a summary | S10 Way 3 |
| **stdio / JSON-RPC** | The transport most local MCP servers speak | S10 Way 4 |
| **Code Mode** | The model writes code that calls your function, instead of emitting a tool call | S10 Way 5 |
| **UTCP** | A manifest describing an existing HTTP API so the client calls it directly | S10 Way 6 |
| **OpenAPI document** | The machine-readable description an HTTP API already publishes; FastMCP generates tools from it | S10 Way 6 |
| **Mount** | Put one MCP server behind another under a namespace, so clients see one endpoint | S10 Way 4 |
| **Capability calls** | How many times the underlying function actually ran: the work, as opposed to the loop | S10 Task 5, the column to read first (deep dive: Task 7) |
| **Switch condition** | The trigger under which you would change the decision; without one, a decision is a preference | TC5 Step 6 |

---

## 🧭 Where this connects

**What the market calls this.** Job descriptions rarely use a syllabus's
words. This week is advertised as **agent harness**, and also as
**orchestration layer**.

One posting says an agent's reliability "depends on the orchestration layer
that wraps around it". That means the routing, execution logic and tool
dispatch you compared six ways of building.

**Back to Week 1.** Your `@app.api` endpoint has a name, typed arguments, and a
docstring for exactly this week. Session 10 shows what those become. The
agent-or-pipeline verdict you wrote in TC1 is the row the room will ask about
first.

**Back to Week 4.** Your demo leads with the numbers from your harness, with
the denominator on the slide. A subagent needs its own evals too.

**Forward to Week 6.** Code Mode's `SAFE_BUILTINS` is not a sandbox. Next week
you escape this exact namespace through the `__globals__` of the very function
you handed it. The tool descriptions you wrote here become an attack surface
in the same session.

**Forward to Week 9.** Which process runs where, and who holds which
credential, is the first page of the deployment checklist. The architecture
row you write this week is where those answers come from.

**Forward to Week 10.** The demo you rehearse here is the shape of the final
readout, with better numbers and a bigger audience. The decision row is most
of the handoff doc. The three "what you would swap" lines from Step 8 join the
final report's list of what it would take to run for real.

### Where the industry is headed

**MCP is widely adopted as the interoperability layer.** The open question
now is *when it is worth the cost*. One failure to watch for is
over-adoption: a server stood up for a capability with exactly one caller,
paying protocol overhead for discovery nothing uses.

**Context economics are becoming the central design constraint.** As agents
get more tools, the tool definitions themselves fill the window. Skills,
progressive disclosure, Code Mode and tool search are all responses to that
one pressure, and it is likely to keep driving architecture for a while.

**Code Mode is probably underrated right now.** For workflows that combine
several capabilities, having the model write code that calls them keeps every
intermediate result out of the context. That advantage grows with the size of
what your capabilities return, and real systems keep returning more. Expect
it to become the default for composition-heavy agents. The sandbox is the part
that has to get better.

**Auth is the unsolved part.** Each of the six handles credentials
differently, and none handles enterprise SSO cleanly. Know it before you
promise a delivery date.

**Demos are getting cheap, so the bar is going up.** A convincing prototype
can take an afternoon now. What a demo needs beyond that is evidence: a
number, a denominator, a named user, and a clear account of what is not
covered.
