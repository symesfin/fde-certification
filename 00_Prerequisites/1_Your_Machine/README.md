# 1 · Your machine

Five tools. Install them in this order — `uv` is last because it is the one
people skip, and Session 1 probes for it.

| Tool | Why the course needs it |
| --- | --- |
| **Docker** | Week 1 containerizes your app; Week 9 deploys the container |
| **VS Code** | Where you work. Zed works too |
| **Git** | You will clone this repo and commit to your own copy every week |
| **Python 3.12+** | Everything runs on it |
| **uv** | One command to a working environment. Not pip, not conda |

---

## 🪟 Windows

Most of you are on a managed Windows laptop. That is the realistic case, so it is
the one documented first.

1. **Docker Desktop** — [download](https://www.docker.com/products/docker-desktop/).
   It will prompt you to enable WSL 2. Say yes.
2. **VS Code** — [download](https://code.visualstudio.com/).
3. **Git** — [download](https://git-scm.com/download/win).
4. **Python 3.12+** — [download](https://www.python.org/downloads/windows/).
   **Check "Add python.exe to PATH" during install.** This is the single most
   common Windows setup mistake and it produces a confusing error much later.
5. **uv** — in PowerShell:
   ```powershell
   irm https://astral.sh/uv/install.ps1 | iex
   ```

Verify — all five should print a version:
```powershell
docker --version
git --version
python --version
uv --version
```

> **WSL or native Windows?** Either works for this course. If you already live in
> WSL, use it and follow the Linux instructions instead. If you do not, native
> Windows is fine and is one less thing to configure.

---

## 🍎 macOS

```bash
brew install --cask docker visual-studio-code
brew install git python@3.12
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or download [Docker Desktop](https://www.docker.com/products/docker-desktop/) and
[VS Code](https://code.visualstudio.com/) directly if you do not use Homebrew.

Verify:
```bash
docker --version && git --version && python3 --version && uv --version
```

---

## 🐧 Linux

Use your distribution's package manager for Git and Python, then:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Docker, install **Docker Engine** (not Desktop) unless you want the GUI —
follow [the official install guide](https://docs.docker.com/engine/install/) for
your distribution, then add yourself to the `docker` group so you do not need
`sudo`:

```bash
sudo usermod -aG docker $USER    # log out and back in for this to take effect
```

## 🟩 Node.js — needed from Week 6

Week 6's prompt-injection session runs **promptfoo**, an open-source test
runner for LLM apps. promptfoo is a Node.js program, and the notebook starts it
with `npx`, which comes with Node. You need **Node.js 22.22 or newer**
(promptfoo's own minimum). The current LTS release is fine.

**Windows (PowerShell):**
```powershell
winget install OpenJS.NodeJS.LTS
```
Or download the LTS installer from [nodejs.org](https://nodejs.org/en/download).
Open a **new** terminal afterwards so `node` and `npx` are on your `PATH`.

**macOS:**
```bash
brew install node
```

**Linux:** follow the instructions for your distribution on
[nodejs.org](https://nodejs.org/en/download). Many distributions package an
older version than 22.22, so check.

Verify, and let `npx` download promptfoo once so the session doesn't wait for
it (the first run takes about a minute):
```bash
node --version                         # v22.22.0 or newer
npx -y promptfoo@0.125.1 --version     # prints 0.125.1
```

---


## 🧯 If it's blocked

### Docker Desktop is not allowed

This is the most common corporate block, because Docker Desktop's licence
requires a paid subscription at companies over a certain size and many firms
simply ban it rather than buy it.

**Ask for [Rancher Desktop](https://rancherdesktop.io/) or
[Podman Desktop](https://podman-desktop.io/) instead.** Both are open source,
both run the same containers, and both are far easier to get approved. Podman is
close to a drop-in replacement:

```bash
alias docker=podman
```

Everything in this course works with any of the three. **Write down which one you
had to use** — that is a real constraint on how your app ships, and Week 9 asks.

### `pip` or `uv` fails with an SSL certificate error

Your firm is intercepting TLS. This is normal and it is fixable — the tools just
do not know about your company's certificate authority yet.

First, get the CA bundle. On a managed machine it is usually already on disk;
your IT team can tell you where, and it is often something like
`C:\ProgramData\<company>\ca-bundle.crt`. Then:

**Windows (PowerShell):**
```powershell
$env:REQUESTS_CA_BUNDLE = "C:\path\to\ca-bundle.crt"
$env:SSL_CERT_FILE      = "C:\path\to\ca-bundle.crt"
```

**macOS / Linux:**
```bash
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
export SSL_CERT_FILE=/path/to/ca-bundle.crt
```

Set them permanently once you know they work — in your PowerShell profile, or
your `~/.zshrc` / `~/.bashrc`. Session 1 prints the value of these variables, so
you will see them again.

> **Do not** use `pip install --trusted-host` or `curl -k` to get past this. They
> work, and they work by turning off the check that the certificate exists to
> perform. Using the real CA bundle is the same amount of effort and does not
> teach you a habit you will regret in front of your stakeholders.

### PyPI itself is blocked

Many firms run an internal mirror instead. Point `uv` at it:

```bash
export UV_DEFAULT_INDEX=https://your-internal-mirror/simple
```

If you do not know whether you have one, that is the question to ask — and the
answer belongs in [`use_case/ecosystem.md`](../../use_case/ecosystem.md).

### You cannot install anything at all

You still have options, in rough order of preference:

1. **A cloud dev environment** — GitHub Codespaces, or a VM your firm already
   provides. This is often approved when local installs are not.
2. **Your personal machine** for the course, with the deployment questions
   answered about the work environment. You lose the ability to measure your
   firm's restrictions, but not the ability to ask about them.
3. **Start the approval process now and do
   [Getting to Concreteness](https://bit.ly/fde-concreteness)
   while you wait.** It needs no tooling at all and it is the input to everything
   else.

---

## ➡️ Next

[**2 · Claude Code**](../2_Claude_Code/README.md) — install it, authenticate it,
and learn the loop.
