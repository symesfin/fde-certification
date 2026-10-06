# 3 · Clone and run

Get your own copy of the repository, wire it to a remote you control, then get
the Week 1 application serving on your machine. When this works, you are ready
for Session 1.

---

## Get the repository

**This repository is private, so you cannot fork it.** You have been given read
access instead. Clone it, then point it at a repository of your own.

That is not a workaround — it is the same shape as the two-remote setup you get
from a fork, and it is what you will do at work with any repository you consume
but do not own.

1. **Clone it:**

   ```bash
   git clone https://github.com/AI-Maker-Space/The-AI-Forward-Deployed-Engineer-Certification.git
   cd The-AI-Forward-Deployed-Engineer-Certification
   ```

2. **Rename our remote to `upstream`.** You will pull from it, never push to it:

   ```bash
   git remote rename origin upstream
   ```

3. **Create an empty repository of your own on GitHub.** No README, no
   `.gitignore`, no licence — it has to be empty or the first push will conflict.
   Name it whatever you like.

4. **Point `origin` at it and push:**

   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/<your-repo>.git
   git push -u origin main
   ```

5. **Confirm both remotes are right.** This is worth ten seconds now:

   ```bash
   git remote -v
   # origin    https://github.com/<you>/<your-repo>.git   <- yours. You push here.
   # upstream  https://github.com/AI-Maker-Space/...       <- ours. You pull from here.
   ```

Then open it:

```bash
code .
```

> **Your repository is public, and that is deliberate** — your classmates read
> each other's work, and your final report links to it. That makes one rule
> absolute: **never commit real company data, credentials, internal hostnames,
> or architecture.** Write down the *shape* of an answer, never the specifics.
> `use_case/data/` is gitignored for exactly this reason.

### Picking up new material later

New sessions land in our repository while you are working. Pull them in:

```bash
git fetch upstream
git merge upstream/main        # or: git rebase upstream/main
```

---

## Set up the root environment

From the repository root:

```bash
make setup
```

That is `uv sync` — it reads `pyproject.toml` and builds the environment every
notebook uses. One command, and it is reproducible, which is why this course
uses `uv` rather than pip or conda.

> **The Week 1 application has its own environment**, declared in
> `01_Product_Engineering/challenge/pyproject.toml`. It needs `gradio`, which
> the root environment deliberately does not carry. Running the app builds that
> environment on the spot — see below.

> **`make` not found on Windows?** You do not need it. Every `make` target is a
> one-line shortcut; run `uv sync` directly instead. The `Makefile` at the repo
> root shows what each target actually does.

> **One `uv` behaviour worth knowing now, because it will confuse you later.**
> `uv sync` is *exact*: it makes the environment match what it was asked for and
> **uninstalls anything else**. Some sessions ask you to add an optional group:
>
> ```bash
> uv sync --group local     # torch, transformers -- a few hundred MB
> ```
>
> Run a plain `uv sync` afterwards and that group is removed again, silently. A
> notebook that worked yesterday then fails with `ModuleNotFoundError` and you
> have done nothing wrong. `make setup` keeps the group if it is already
> installed; if you run `uv` directly, use `uv sync --group local` to restore
> it, or `uv sync --inexact` to sync without removing extras.

---

## Set up your key

There is one `.env` at the repository root, and everything reads from it —
notebooks and the Week 1 application alike. Copy the template:

**macOS / Linux:**
```bash
cp .env.template .env
```

**Windows (PowerShell):**
```powershell
copy .env.template .env
```

You fill it in during [guide 4](../4_Your_Model/README.md). For now it just has
to exist.

---

## Run the Week 1 app

```bash
cd 01_Product_Engineering/challenge
uv run python app.py
```

One command on every platform. `uv run` reads the `pyproject.toml` in that
directory, builds the environment if it does not exist yet, and runs the app —
no virtualenv to create, no activation step to forget, and nothing different to
remember on Windows.

Open <http://localhost:7860>. You should get a plain, slightly ugly chat window
that works.

Then check <http://localhost:7860/health>. That endpoint exists because every
load balancer on earth will ask for one — a small thing that turns out to matter
in Week 9.

> The chat will not answer until you have a model configured. If the page loads
> and the box is there, this guide is done — go to
> [guide 4](../4_Your_Model/README.md).

---

## Open a notebook

Session 1 is a [marimo](https://marimo.io/) notebook — a `.py` file, not
`.ipynb`, which means it diffs properly and deploys as an app. Try opening it:

```bash
make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
```

That runs it in its own sandbox from the dependencies declared inside the file,
so it works even if `make setup` failed.

> **Prefer Jupyter?** Every notebook ships with an `.ipynb` next to it. Those are
> **generated** from the `.py` — read or run them freely, but make edits in the
> `.py` or your changes get overwritten.

---

## 🧯 If it's blocked

### `git clone` fails with a permission or authentication error

You need read access granted to the GitHub account you are authenticated as.
If you have more than one account, check which one your machine is using:

```bash
gh auth status        # if you use the GitHub CLI
```

If you were granted access on a personal account but your machine is signed in
with a work account, that is the whole problem.

### `git push` to your own repository is rejected

Almost always because the repository you created is not empty. Delete the
auto-created README on GitHub, or force the first push:

```bash
git push -u origin main --force
```

Safe here only because it is a repository you just made and nobody else uses.

### The chat window loads but nothing happens when you send a message

Open the browser console first. The frontend loads the Gradio client from a CDN
(`cdn.jsdelivr.net`), and on a network that blocks it the page renders perfectly
and does nothing. The backend is fine; the browser never got the code to call it.

**This is the single most common way a demo that worked on your laptop dies on
contact with a corporate network**, and it is worth meeting now rather than in
front of your stakeholders.

The fix is to vendor the file instead of fetching it. Download
`@gradio/client` once on a machine that can reach the CDN, commit it next to
`frontend/index.html`, and change the import to a relative path. Week 1's Step 5
comes back to this — for now, just confirm whether it happens to you, and write
it down.

### `uv run` fails with a certificate error

Same cause and same fix as in [guide 1](../1_Your_Machine/README.md) — set
`REQUESTS_CA_BUNDLE` and `SSL_CERT_FILE` to your firm's CA bundle. If PyPI itself
is blocked, set `UV_DEFAULT_INDEX` to your internal mirror.

### Port 7860 is already in use

Something else is on it. Either stop that, or run on another port:

**macOS / Linux:**
```bash
GRADIO_SERVER_PORT=7861 uv run python app.py
```

**Windows (PowerShell):**
```powershell
$env:GRADIO_SERVER_PORT=7861; uv run python app.py
```

### You cannot reach GitHub at all

Some firms block it outright, or allow only an internal mirror. If GitHub is
unreachable from your work machine, clone from a personal machine and work
there. **Write it down** — "we cannot reach github.com" shapes how anything you
build gets delivered, and Week 9 will ask.

---

## ➡️ Next

[**4 · Your model**](../4_Your_Model/README.md) — the key or endpoint that makes
the chat box answer.
