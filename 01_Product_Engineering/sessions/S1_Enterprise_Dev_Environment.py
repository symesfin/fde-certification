# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Enterprise Dev Environment")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 1: Enterprise Dev Environment

    *To open this notebook from the repository root:*
    `uv run marimo edit --sandbox 01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py`
    *(or `make nb F=…` on a machine with `make`). A browser tab opens on
    `localhost`; that is the whole thing.*

    Your application is going to leave your laptop. This notebook is about the
    four seams where that goes wrong — what your network allows, how your work
    becomes reviewable, how the app talks to a model, and how it becomes an
    artifact somebody else can run — plus the habit that makes an agent useful
    on all four.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - Task 1: Record what your network actually allows
    - Task 2: Make your work reviewable
    - Task 3: Run the gates before anyone reads it
    - ❓ Question #1 · ❓ Question #2
    - Task 4: One call, two providers
    - Task 5: `CLAUDE.md` is source code
    - ❓ Question #3 · ❓ Question #4
    - Conclusion
    - Additional Context
    - Bonus Tasks

    > 📓 **Not covered here:** the application's API surface, packaging it into
    > an image, and the first pass at judging whether it is any good. Those live
    > with the challenge steps that need them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | marimo | the notebook you are reading | [docs.marimo.io](https://docs.marimo.io/) |
    | uv | environments, and running anything | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
    | LiteLLM | one call, any provider | [docs.litellm.ai](https://docs.litellm.ai/) |
    | Claude Code | the agent you steer with `CLAUDE.md` | [code.claude.com/docs](https://code.claude.com/docs/en/overview) |
    | Docker | the artifact someone else can run | [docs.docker.com](https://docs.docker.com/) |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You have a working toolchain, a reachable model, and a probe result telling
    you which hosts your network allows. That was the pre-work.

    None of what follows is hard. It is the set of things that are annoying to
    retrofit: an egress record you did not keep, a vendor SDK compiled into
    forty call sites, an agent you re-explain the same constraint to every
    morning.

    | | | What it prevents |
    | --- | --- | --- |
    | 1 | Write the egress results to a file | Reconstructing egress rules from memory under a deploy deadline |
    | 2 | Branch, commit, push, open a PR | A review that starts with "which of these 40 files matter?" |
    | 3 | Run the gates before requesting review | Burning a reviewer on a lint error |
    | 4 | Read the provider from config | A blocked vendor becomes an `.env` edit, not a refactor |
    | 5 | Put standing constraints in `CLAUDE.md` | Repeating "we use uv, not pip" in every prompt |

    Row 4 is the one with teeth. `litellm` dispatches on the model string, so
    `openai/gpt-4.1-mini` and `openai/qwen3` differ by an environment variable
    rather than an import — which is what makes a blocked vendor a config change.

    > **Skipped the pre-work?** Do it first. It installs the toolchain and runs
    > the egress probe this notebook reads from.

    **Estimated time:** 45–55 minutes, and the `CLAUDE.md` drill in Task 5 is
    a third of it.

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    print(f"✅ repo root: {CFG.root.name}")
    print(f"✅ model:     {CFG}")
    return CFG, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    Three things that are cheap now and expensive later: knowing what your
    network permits, making your work reviewable, and catching your own mistakes
    before a colleague does.

    ---
    ## Task 1 — Record what your network actually allows

    `helpers/preflight.py` opens a TLS connection to each host your application
    will depend on and reports three things per host: whether the handshake
    completed, how long it took, and **which CA signed the certificate**.

    That third column is the interesting one. If the issuer is your employer
    rather than the CA the host actually uses, you are behind a TLS-inspecting
    proxy: traffic is decrypted and re-signed in the middle. That is ordinary in
    a large firm, and IT has installed that root CA in your machine's trust
    store — which is exactly why it is invisible until it is not.

    The failure it produces later: `pip` works in your terminal and the same
    command fails inside your container with `CERTIFICATE_VERIFY_FAILED`,
    because the base image trusts Mozilla's CA bundle and has never heard of
    your employer's root. The fix is to mount the corporate root into the image
    and point `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` at it — not `verify=False`,
    which trades a broken build for a silently unverified one.

    The probe enforces a wall-clock deadline in a worker thread rather than
    relying on the socket timeout, and that detail is worth stealing.
    `socket.gethostbyname` does not honour `socket.setdefaulttimeout`, so a
    blackholed DNS query blocks until the system resolver gives up regardless of
    what you passed to `create_connection`. A diagnostic that hangs on precisely
    the networks it was written to diagnose is worse than no diagnostic.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    run_probe = mo.ui.run_button(label="Probe this machine's egress")
    mo.md(f"A few seconds, no model calls, nothing leaves except TLS handshakes. {run_probe}")
    return (run_probe,)


@app.cell
def _(mo, run_probe, ui):
    mo.stop(not run_probe.value, mo.md("*Press to probe.*"))

    from helpers.preflight import check_egress

    REPORT = check_egress()

    mo.vstack([
        ui.table(
            [{"host": _p.host, "why": _p.why, "status": _p.status,
              "signed by": getattr(_p, "issuer", "") or ""}
             for _p in REPORT.probes],
            title="Egress",
        ),
        mo.md(f"**Verdict:** {REPORT.verdict()}"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 🚢 Now put it in the file

    Copy the table and the verdict into **`use_case/ecosystem.md`**, under a
    heading with today's date.

    This file ends up in front of a platform team, and it is worth more than the
    same facts recalled later. You are running this probe on a developer machine
    with your own tools installed. The environment you eventually deploy into
    has a different egress policy, and by then you will not be able to run the
    probe interactively to find out what changed. Two dated tables answer that;
    a memory does not.

    Three readings, so you know what you are writing down:

    - **Public issuers, no proxy variables** — an open network. Nothing here
      will bite you, and that is worth recording too.
    - **The issuer is your employer's name** — TLS is being intercepted and
      re-signed. Normal, usually fine, and it explains a whole category of
      certificate errors from tools that do not read the system trust store.
    - **Some hosts pass and others fail** — an allowlist. Write down exactly
      which. `huggingface.co` blocked predicts trouble with open weights;
      `registry-1.docker.io` blocked predicts trouble the first time you build
      a container.

    > **Describe patterns, not specifics.** "On-prem, internal registry, no
    > public egress" is useful to everyone and identifies nobody. Never commit
    > real hostnames, IP ranges, or architecture. If in doubt, leave it out.

    ---
    ## Task 2 — Make your work reviewable

    You know git. The part worth reading here is the two-remote setup and the
    one merge conflict this repository resolves differently from every other
    repository you work in.

    **Your repo has two remotes, and they do different jobs.**

    ```bash
    git remote -v
    # origin    https://github.com/<you>/<your-repo>.git    <- yours. You push here.
    # upstream  https://github.com/AI-Maker-Space/...       <- ours. You pull from here.
    ```

    You never push to `upstream`. You pull from it to pick up new material, and
    you push your own work to `origin`.

    **The cycle, which you will run every time you work:**

    ```bash
    git switch -c feat/my-endpoint       # a branch per piece of work, never on main
    # ... make changes ...
    git add -A
    git commit -m "Add a shipment-status endpoint and its golden examples"
    git push -u origin feat/my-endpoint
    ```

    Then open a pull request **against your own repo** and read your own diff
    before anyone else does.

    ### Two things that go wrong, and the fix for each

    **Your branch falls behind ours.** New material lands upstream while you are
    working:

    ```bash
    git fetch upstream
    git merge upstream/main        # or: git rebase upstream/main
    ```

    **A generated notebook conflicts.** Every `.ipynb` here is generated from
    its `.py`, so never hand-resolve one:

    ```bash
    git checkout --ours <file>.ipynb && make mirrors
    ```

    Regenerating is the *only* correct resolution. A hand-edited `.ipynb` gets
    the right bytes by the wrong route, and the next `make check` will say so.

    > **Never commit real company data, credentials, or internal hostnames to a
    > public repo.** `use_case/data/` is gitignored for that reason. If you need
    > real detail, keep it in a private copy and put the *shape* of the answer
    > in the public one.

    ---
    ## Task 3 — Run the gates before anyone reads it

    ```bash
    make check       # what CI runs: mirrors, links, standalone rule, helpers, tests
    make mirrors     # regenerate every .ipynb from its .py
    make nb F=<path.py>   # open one notebook, sandboxed
    ```

    `make check` catches three things a human reviewer would otherwise spend
    their attention on: a generated `.ipynb` that no longer matches its `.py`, a
    relative link pointing at a file you renamed, and a helper module nothing
    imports.

    > **`make check` proves the two formats are byte-identical. It does not
    > prove the notebook runs.** A notebook that raises on cell three exports
    > exactly like one that works. `make execute` actually runs both formats and
    > is the only thing that catches that; it takes minutes rather than seconds,
    > which is why it is a separate target.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #1

    The probe reports the **certificate issuer** for each host, not just whether
    the host was reachable. A colleague argues the issuer column is noise —
    everything connected, so the network is fine. In one to three sentences,
    explain what the issuer column predicts that the status column cannot.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #2

    `make check` passes on a notebook that raises an exception on its third
    cell. Explain how both of those can be true at once, and what that tells you
    about what a byte-comparison gate is actually able to promise.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    A seam is a place where one part of a system can be swapped without
    rewriting the others. Two of them decide how much a change costs you later:
    where the model provider is named, and where your standing instructions to
    an agent live.

    ---
    ## Task 4 — One call, two providers

    Your app routes model calls through LiteLLM, so the provider is a string in
    `.env` rather than a code path. Watch what that buys you.
    """)
    return


@app.cell
def _(CFG, mo):
    run_call = mo.ui.run_button(label="Send one message")
    mo.md(f"Model: `{CFG}`  \n{run_call}")
    return (run_call,)


@app.cell
def _(CFG, mo, run_call):
    mo.stop(not run_call.value, mo.md("*Click the button above to make the call.*"))

    from helpers.display import stream_md
    from litellm import completion

    _stream = completion(
        **CFG.kwargs(),
        timeout=600,
        messages=[
            {
                "role": "user",
                "content": (
                    "In two sentences: why would a bank run an LLM on its own "
                    "hardware instead of calling a vendor API?"
                ),
            }
        ],
        stream=True,
    )
    reply = stream_md(_stream)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 5 — `CLAUDE.md` is source code

    `CLAUDE.md` is loaded into the agent's context before it reads anything
    else, on every session, for every person on the project. That makes it
    configuration, not documentation — and the reflex worth building is:
    **when the agent makes the same wrong assumption twice, edit the file, not
    the prompt.**

    Correcting it in chat fixes one conversation. Writing it down fixes every
    conversation after, including the ones your colleagues have on your project
    after you have moved on.

    ⏱️ **This is a hands-on drill. Budget 15 minutes.** Do it now, in
    your challenge app's directory.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The loop

    **1 — Start it, and look before you leap.**

    ```bash
    cd 01_Product_Engineering/challenge    # from the repository root
    claude
    ```

    The directory matters: Claude Code reads the `CLAUDE.md` in the folder it
    starts in, and the challenge's is the one with the rules you are about to
    edit. Started from the repository root it picks up a different file.

    Press `Shift+Tab` until you are in **plan mode**, then ask for something
    real:

    > add a helper to `llm.py` that counts the tokens in a prompt before we send it

    It proposes; it does not edit. Read the plan. Plan mode is the right default
    any time you are working in code you did not write, which — as an FDE — is
    most of the time.

    **2 — Let it run, and watch for the assumption.**

    Accept the plan. Then look at what it actually wrote, not just whether it
    works. Something in there is not how you would have done it: a naming style,
    a docstring convention, an import placement, an extra dependency you did not
    want, an inline comment explaining *what* instead of *why*.

    **That is the interesting part.** Not a bug — a taste mismatch. Those are
    what recur.

    **3 — Write one line, not a paragraph.**

    Open `CLAUDE.md` and add a single rule under `## Conventions`. Be concrete
    and testable:

    | ❌ Vague | ✅ Testable |
    | --- | --- |
    | "Write clean code" | "No new dependencies without asking — prefer stdlib" |
    | "Good comments" | "Comments explain *why*, not *what*" |
    | "Be consistent" | "Helper functions in `llm.py` take the model string first" |

    **4 — `/clear`, then ask for something similar.**

    ```
    /clear
    ```

    Fresh context, same project. Ask for a *different* small helper. The rule
    you wrote should hold without you mentioning it.

    If it does not hold, the rule was too vague to act on. Sharpen it and repeat.
    Expect two or three iterations per rule — a rule that survives a `/clear` is
    the only evidence that it is written clearly enough.

    ---

    ### 🔍 Look at the one already here

    Before you leave, read
    [`../challenge/CLAUDE.md`](../challenge/CLAUDE.md).

    It puts Claude Code into **instructor mode** — it will explain, debug, and
    review, but it declines to write your graded work for you. That is a
    `CLAUDE.md` doing something no documentation file could: changing an agent's
    behaviour, in prose, with no code involved.

    It is also why the agent pushes back when you ask it to write the graded
    parts of your challenge for you. That is the file working, not a bug — and
    it is why the drill above still works: the helper you asked for is not on
    that file's list of graded work, so the agent writes it. If it hesitates,
    say so; the file names exactly what is off-limits, and a token counter is
    not on it.

    **One more thing to try before you leave**, because it ties this task to
    the first one. Point the agent at the artifact Task 1 produced, without
    opening a session:

    ```bash
    claude -p "read use_case/ecosystem.md and tell me, in three bullets, what my network will and will not let an app reach"
    ```

    `-p` is the one-shot form — print, exit, no conversation. It is how you use
    the agent from a script or a CI step, and it is a useful habit: the file
    you wrote for a colleague to read is also a file an agent can read, and the
    summary it gives back is a quick check that you wrote it clearly.

    > **New to Claude Code?** Permission modes, authentication, and the rest are
    > in the [prerequisites](../../00_Prerequisites/2_Claude_Code/README.md).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### ❓ Question #3

    Your egress probe shows no route to a hosted provider, but an approved
    internal gateway is reachable. Explain, in one to three sentences, why that
    costs one line in `.env` here — and what specifically you would have had to
    rewrite if the code had called a vendor SDK directly.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ❓ Question #4

    You add a rule to `CLAUDE.md`, and the agent follows it for the rest of that
    conversation. After `/clear`, it goes back to the old behaviour. What does
    that specific outcome tell you about the rule you wrote — and why is
    `/clear` a better test than simply continuing the conversation?

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Conclusion

    You measured what your network permits instead of assuming it, made your
    work reviewable, ran your own gates, and then walked two seams that decide
    what a change costs later: the provider is configuration rather than an
    import, and `CLAUDE.md` is how you stop repeating yourself to an agent.

    None of it was difficult. All of it is expensive to retrofit.

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Egress checking | A one-shot probe in a notebook | Continuous synthetic monitoring from inside the VPC, alerting on certificate and reachability changes |
    | Secrets | `assert` that a key exists | Vault or Key Vault, rotated on a schedule, never written to disk |
    | Provider routing | A model string in `.env` | A gateway with routing, rate limits, per-team budgets, and audit logging |
    | Agent instructions | `CLAUDE.md` in one repo | Shared agent instructions versioned across an org and reviewed like code |

    ---
    # Additional Context

    - [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) — Task 5 is this idea as a drill
    - [The Twelve-Factor App: Config](https://12factor.net/config) — why the provider is an environment variable and not an import
    - [Writing an effective `CLAUDE.md`](https://code.claude.com/docs/en/memory) — the file the agent loads before every session
    - **Keep building:** take the egress probe and turn it into something that runs on a schedule rather than when you remember to press a button.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Bonus Tasks

    Optional. The first two are worth doing if you have the hour; the rest are
    meaningfully harder.

    ### Break a gate on purpose

    You have seen the gates pass. Passing tells you nothing you can act on —
    you want to have seen the failure output *before* you meet it under time
    pressure.

    **What to do:**

    - Run `make check` and confirm it is clean.
    - Break exactly one thing. Easiest is a link: rename a file that a README
      points at, or change a relative path in a README to something that does
      not exist.
    - Run `make check` again. Read the output properly — which gate fired, what
      it named, and whether the message was enough to fix it without guessing.
    - Restore the file and confirm the gate goes green again.

    **Briefly explain which gate caught it, what the failure output said, and
    what a human reviewer would have had to spend attention on if that gate did
    not exist:**

    ---
    ### Change the provider, not the code

    Open `.env` and point `LLM_MODEL` somewhere else — `anthropic/…`,
    `azure/…`, or `ollama/…` if you have one running locally. Re-run the two
    cells in Task 4. The call should work unchanged.

    **What to do:**

    - Swap `LLM_MODEL` to a different provider and re-run the call.
    - Note what you had to change besides that one line. If the answer is
      "nothing", that is the point.
    - Now look at your egress table from Task 1 and say which providers you
      could actually reach from this machine.

    This matters because your probe may well have shown no route to
    `api.openai.com` and an approved internal gateway instead. Routing through
    LiteLLM means that situation costs one line in `.env`. Calling
    `openai.OpenAI()` directly means it costs you every call site, plus the
    retry and streaming behaviour you had built around that SDK.

    **Briefly explain what you changed, what you did not have to change, and
    which providers your network would actually permit:**

    ---
    ### Harder

    - **Turn the egress probe into a health check.** Make it exit non-zero when
      a required host is unreachable and run it in CI, so a firewall change
      breaks the build instead of the demo.
    - **Diff two machines.** Run this notebook on your work laptop and on a
      personal one. The delta *is* your firm's security posture, and it is a
      far better conversation-starter with an infrastructure team than a list of
      questions.
    - **Find the CA.** If the issuer was your employer, locate the root
      certificate on disk and work out which of your tools trust it and which
      do not. Python, Node, Git, and Docker all answer differently.
    """)
    return


if __name__ == "__main__":
    app.run()
