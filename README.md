<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>The AI Forward-Deployed Engineering Certification</h1>
  <p><strong>#FDE1 — v1.1</strong></p>
</div>

Welcome to [The AI Forward-Deployed Engineering Certification](https://maven.com/aimakerspace/ai-fde-certification).

> 🎯 **This course is built so that you engage with your own company as a
> world-class AI Forward-Deployed Engineer.** Not a sample dataset, not a demo
> use case — the actual problem you have at the actual place you work.

> [!NOTE]
> This repository is still being built out ahead of launch. Expect new notebooks
> and material to appear over the coming days. Everything you need will be here
> before each session.

---

## How this works

**10 weeks. Two sessions and one technical challenge per week.**

Each week is a directory. Inside it, `sessions/` holds the two notebooks and
`challenge/` holds that week's technical challenge. View full detailed curriculum schedule [here](https://absorbing-toaster-713.notion.site/The-AI-FDE-Certification-v1-1-Curriculum-Detailed-Schedule-373cd547af3d80b59666f7a43b4390de?pvs=74)

> ### One use case, all ten weeks, no restarts
>
> You choose a problem in Week 1 and carry it the whole way. Week 2 generates
> data for it, Week 3 builds retrieval on it, Week 4 measures it, Week 8
> fine-tunes for it, and Week 10 reports on it to the people you have been
> talking to since Week 1.
>
> That work accumulates in [`use_case/`](./use_case/README.md) — your directory,
> in your fork. The most common way this cohort goes wrong is switching use cases
> halfway, so choose something you actually own and actually find annoying.

---

## The stack

| | | Why |
| --- | --- | --- |
| **VS Code** | *(Zed works too)* | Where you work |
| **Claude Code** | *(Codex works too)* | The agent, and `CLAUDE.md` is how you steer it |
| **marimo** | *(not Jupyter)* | Notebooks are `.py` files — diffable, and deployable as apps |
| **uv** | *(not pixi/conda)* | One command to a working environment |
| **Gradio Server + Docker** | | Your app is an API with a disposable UI, shipped as a container |

**Gradio Server is the product; marimo is the instrument panel.** Gradio gives
you an API other things can call — which is what makes Week 5's MCP work
possible. marimo gives you notebooks that are also deployable: the eval harness
you write in Week 4 becomes a dashboard you can `marimo run` and containerize,
and the same file becomes your Week 10 observability console.

### Where are LangChain, LlamaIndex, and LangGraph?

Mostly absent, and deliberately — but **not because they are bad**. Several of
them are the right choice for production work, and you will meet teams using
them well.

The reason is that this course's unit of value is *understanding*, and a
framework's job is to let you skip the understanding. That is a good trade when
you already have it and a terrible one when you do not, because the day it
breaks you are debugging an abstraction over a thing you never learned.

So the pattern throughout is: **build the primitive from scratch, then name the
library that does it properly.** A tool loop is about thirty lines; you write
those, then you see why a real one adds schema derivation and error handling. A
retriever is a dot product; you write that, then you use a vector store. An eval
harness is a loop and a scorer; you write it, then Week 4 shows you Ragas.

After that, picking a framework is a normal engineering decision and you can
read its source when it misbehaves. That is the whole aim — the frameworks are
downstream of it, and you will adopt one much faster having done this than
having started there.

> **One exception worth naming:** where a protocol or a format is the point
> rather than the plumbing — MCP, UTCP, OpenTelemetry's conventions — you use
> the real thing, because the value is interoperating with tools you did not
> write.

They are named where they are the right next step: **Ragas** for eval metrics,
**Chroma** and **Qdrant** for vector stores, and **`deepagents`** — LangGraph
underneath — for subagents, planning, and long-running work, once you have
written the small version and can see what it adds.

---

## Getting started

> ### 🧰 Start with the [prerequisites](./00_Prerequisites/README.md)
>
> Tooling, Claude Code, your repo, and a model — **before Session 1**, because
> Session 1 verifies a machine that is already set up. There is a path for a
> managed corporate laptop and a path for your own, and a checker script that
> tells you which boxes are still open.
>
> Budget 45–90 minutes. On a work machine the long pole is approvals, not
> installation, which is exactly why you want to start early.

You need [uv](https://docs.astral.sh/uv/getting-started/installation/), [Docker](https://docs.docker.com/get-started/get-docker/),
and [Claude Code](https://code.claude.com/docs/en/overview). The prerequisites walk through installing all three,
Windows-first.

> ### 🔑 You bring the model
>
> There is no shared class server. Bring **either** an API key from a provider
> (OpenAI, Anthropic, Azure) **or** an endpoint you can reach — your firm's
> internal gateway, a server you run, or a model on your own laptop.
>
> `.env.template` has a worked example of each. Everything routes through
> LiteLLM, so switching between them is one line and no code changes.
>
> This is deliberate. Plenty of you cannot reach `api.openai.com` from a work
> machine at all, and finding that out in Week 1 is much better than finding it
> out in Week 9.

```bash
git clone https://github.com/<YOUR_USERNAME>/The-AI-Forward-Deployed-Engineer-Certification.git
cd The-AI-Forward-Deployed-Engineer-Certification
cp .env.template .env      # add your API key
make setup
```

Open a notebook:

```bash
make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
make nb F=02_Open_Weights/sessions/S3_Local_Inference_Fundamentals.py
make nb F=03_Retrieval/sessions/S5_Agentic_Retrieval.py
```

That runs it in its own sandboxed environment from the dependencies declared
inside the file, so it works even if you skipped `make setup`.

> **Prefer Jupyter?** Every notebook ships with an `.ipynb` next to it. Those are
> **generated** from the `.py` — read or run them freely, but make edits in the
> `.py`, or your changes will be overwritten.
>
> Lost on a word? [`GLOSSARY.md`](./GLOSSARY.md) has every term the course has
> used so far, in one sentence each, with the week it first comes up.

---

## 🧑‍🤝‍🧑 Your team

- [Dr. Greg Loughnane](https://www.linkedin.com/in/gregloughnane/), Owner/CEO @ AI Makerspace
- [Tyler Laughlin](https://www.linkedin.com/in/tykanoalaughlin/), Instructor 
- [Matt Sharp](https://www.linkedin.com/in/matthewsharp/), Instructor — co-author of *LLMs in Production*
- [Jacob Kilpatrick](https://www.linkedin.com/in/jacobkilpatrickai/), Course Operations Lead @ AI Makerspace
- ["Coach Mark" Walker](https://www.linkedin.com/in/mark-l-walker/), Student Success Manager @ AI Makerspace
- [Ovo Okpubuluku](https://www.linkedin.com/in/ovokpus/), FDE Technical Expert @ AI Makerspace
- [Phil Mui](https://www.linkedin.com/in/philmui/), FDE Technical Expert @ AI Makerspace

---

## 🙏 Contributions

Contributions, ideas, and feedback are welcome. Reach out to
`jacob@aimakerspace.io` with questions or suggestions.

Keep building, shipping, and sharing, and we'll do the same 🏗️🚢🚀
