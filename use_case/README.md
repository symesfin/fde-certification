# Your use case

**This directory is yours.** Everything else in this repository is teaching
material we wrote. This is the one place you work.

> **One use case, all ten weeks, no restarts.**

That rule is the whole design. The most common way this cohort goes wrong is a
student switching use cases halfway because the first one got hard — and then
arriving at fine-tuning with nothing to train against, and at the final report
with nobody to send it to. Choose something you actually own, at work, that
annoys you weekly.

---

## The files

### [`CHARTER.md`](./CHARTER.md) — the definition of what you are building

One page: the problem, whose problem it is, how you will know it worked, and the
input/output contract. It is the shortest file here and the only one everything
else depends on.

**Why it matters:** a vague charter does not produce a vague product, it produces
a product that cannot be evaluated. If you cannot say what a correct output looks
like, no amount of engineering downstream will tell you whether you built the
right thing — and you will find that out late.

### [`stakeholders.md`](./stakeholders.md) — the people, not the org chart

Everyone you spoke to: name, role, what you asked, what they said, what they
still owe you. It grows every week.

**Why it matters:** this is the difference between a project and an experiment.
Software that no named person is waiting for does not get adopted, and the people
who answer a question from a colleague they do not have to help are exactly the
people you will need again. Keeping the log costs a minute per conversation and
is unreconstructable afterwards.

### [`ecosystem.md`](./ecosystem.md) — what your firm will actually let you run

Where compute lives, what identity provider you are behind, how secrets arrive,
what egress is permitted, who signs off on a deployment. Answers from real
people, not assumptions.

**Why it matters:** most AI projects inside large firms do not fail on model
quality. They fail because nobody asked where the thing would run until it was
already built, and the answer turned out to be "not there." Every hour spent here
early is a week saved later, and the answers change how you build — not just
where you deploy.

### [`decisions.md`](./decisions.md) — what you chose, and what would change your mind

An architecture-decision log. For each real choice: what you picked, what you
rejected **after actually trying it**, the reasoning, and the condition under
which you would switch.

**Why it matters:** the last field is the one people skip and the one you get
asked about. *"We chose dense retrieval; we would move to hybrid if exact-match
queries went above about 20% of traffic"* is an engineering position. *"We chose
dense retrieval"* is a preference. You will have to defend these decisions out
loud, and reconstructing the reasoning six weeks later does not work.

### [`evals/golden.jsonl`](./evals/) — the examples you wrote by hand

A small set of inputs paired with the outputs you consider correct. You write the
first five yourself, deliberately, before any tooling exists.

**Why it matters:** these are the bar. Everything measurable about your project
is measured against them — whether synthetic data is realistic, whether a change
helped, whether a smaller self-hosted model is good enough to replace an API. Five
examples you thought hard about are worth more than five hundred generated ones,
because they encode a judgement no model has.

### [`evals/baseline.json`](./evals/) — the run itself, saved

The Week 4 harness run — your scorers over your cases against your endpoint —
saved as a file with a fingerprint of what was measured, alongside the
scorers, scenarios and generated failures that produced it. See
[`evals/README.md`](./evals/README.md) for the full list.

**Why it matters:** a number typed into a document cannot be compared by
anything and stops being true the moment you add a case. A saved run can be
re-run, compared and gated on — and `helpers.harness.compare()` refuses when
the case set changed, which is what stops a later "win" from being a change
of suite. Week 8's fine-tuned model has to beat this file.

### [`data/DATASHEET.md`](./data/DATASHEET.md) — what your data can and cannot prove

How the dataset was made, what it covers, what it does not, and what conclusions
it will not support.

**Why it matters:** synthetic data is generated from assumptions, and those
assumptions become invisible about a day after you make them. The datasheet is
what stops you reporting a number your data was never capable of supporting —
which is the failure that damages credibility rather than just the schedule.

### `app/` — the thing itself

Your application. It starts as a container that answers one endpoint and grows
each week.

**Why it matters:** it is the only artifact here that a non-engineer can be shown.

---

Nothing in this directory is busywork. Each file exists because something later
becomes impossible without it — and each one is far cheaper to write while the
work is fresh than to reconstruct from memory at the end.

---

## 🔒 Never commit real company data

`data/` is gitignored except its datasheet. That is deliberate and it is not
negotiable — this repository leaves your machine.

| Don't commit | Do commit |
| --- | --- |
| Real records, tickets, documents, customer names | Synthetic data you generated |
| Internal hostnames, IPs, architecture diagrams | The *shape* of the answer: "on-prem k8s, SAML, no egress" |
| Credentials, tokens, connection strings | `.env.example` with placeholders |
| Screenshots of internal tools | Screenshots of your own app |

When describing your firm's infrastructure, describe the pattern, not the
specifics. "Images go to an internal registry; Docker Hub is blocked" is useful
to everyone and identifies nobody.

If in doubt, leave it out.
