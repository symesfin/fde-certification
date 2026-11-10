# Session 9: Demos, with stakeholder-style critique

There is no notebook for this session. You present your app, and the room
questions you the way your stakeholders would. Kindly, but hard. This file is
the rubric. Read it as a checklist before you arrive, and keep it open while
you listen to everyone else.

---

## Table of Contents

- Why the critique is hostile on purpose
- The five minutes
- What the room asks
- How to be critiqued well
- How to critique well
- Scoring
- Bring with you

**Five minutes each, timed.** The timer doesn't bend, because the real version
of this meeting won't either.

---

## Why the critique is hostile on purpose

Sooner or later a real sponsor will review your project and ask these same
questions. If that happens three months in, a bad answer can get the project
cancelled. Here, the worst case is an uncomfortable Tuesday.

The room is on your side. The questions are tough on purpose.

---

## The five minutes

| Minute | What | The failure mode |
| --- | --- | --- |
| 0–1 | **The problem.** One person, one workflow, what it costs today. | Starting with the architecture |
| 1–2 | **The demo.** The thing running. | A slide deck *about* the thing running |
| 2–3.5 | **The numbers.** What you measured, on what data, and what it does not prove. | A score with no denominator |
| 3.5–5 | **What is next**, and what you need from whom. | "More research" |

If you are still describing your stack at minute two, you are spending the
demo's minute on it.

---

## What the room asks

Everyone gets some of these. Prepare for all of them.

### On the problem
- Who *specifically* has this problem? What is their job title?
- Have you shown this to them? What did they say?
- What happens if you do nothing? Who is currently absorbing that cost?
- Is this the biggest problem they have, or the one easiest to build for?

### On the numbers
- **What is the denominator?** Forty cases or four?
- Where did the eval set come from? Did you write it before or after the system?
- What does this number *not* cover?
- What is the baseline? Better than what?
- Would your judge score a wrong answer highly? How do you know?

### On the architecture
- What did you consider and reject?
- What would make you change this?
- What breaks first when volume goes up 10×?
- **How much data does each call return, and what does that cost you?** The
  architecture that is cheapest at demo scale is often the expensive one at
  real response sizes. Ask whether they measured it.
- Which part of this would you have to rewrite to deploy where you work?

### On the honest bits
- **What is the worst failure you have seen it produce?**
- What does it do when it does not know?
- What would you not let it do unsupervised?

> If you can't answer *"what is the worst thing you've seen it do"*, use your
> own system more before you present it.

---

## How to be critiqued well

**Volunteer the failure.** Show the ugly case yourself. That makes the good cases credible, and the room can't
spring it on you.

**Say "I don't know" cleanly.** Then say what you would do to find out, and by
when.

**Don't defend the first version.** You built it in three weeks. The room does
not expect it to be right. They want to know whether *you* know where it is wrong.

**Separate "this is wrong" from "I did not explain it".** Ask which one it is.
Some hostile questions are really confusion.

**Write the questions down while they are asked**, not after. That list is
worth more than the feedback.

---

## How to critique well

You sit in on everyone else's demo, and the quality of your questions is part
of your own assessment.

- **Ask about the problem before the technology.** That is where the real
  weaknesses are.
- **Ask for the denominator.** Always. It is the fastest way to find out
  whether a number means anything.
- **Ask "what did you reject?"** If an architecture has no rejected
  alternatives, nobody chose it. It was the default. Then follow up with *did
  you build it, or did you reason about it?* That separates a real answer from
  a rehearsed one.
- **Be specific.** "I did not follow the eval section" is useful. "Interesting,
  nice work" is not.
- **One hard question each.** Not five. A pile-on teaches nobody anything.

---

## Scoring

This is not a grade. It gives everyone the same words for feedback.

| | 1 — thin | 2 — solid | 3 — strong |
| --- | --- | --- | --- |
| **Problem** | A category ("customer service") | One role and one workflow | One person, named cost, and you have spoken to them |
| **Demo** | Slides, or it broke | It ran | It ran, including a case you knew would fail |
| **Numbers** | "It works well" | A score, with a denominator | A score, a baseline, and what it does not cover |
| **Architecture** | Whatever you knew already | A choice with a reason | A choice, the rejects, a number you measured on at least one of them, and the switch condition |
| **Honesty** | Only the happy path | Admitted a limitation when asked | Led with the worst failure |
| **Next** | "More research" | A plan | A plan, and the named person you need something from |

Aim for 3s in **Honesty** and **Numbers**.

---

## Bring with you

- [ ] Your app, running. Locally is fine. **Test it on the room's wifi first.**
- [ ] **Ten minutes early in your breakout room**: screen shared, audio
      confirmed, the app run once on the call.
- [ ] Your eval numbers from your harness, with the denominator on the slide.
- [ ] One failure you can show on purpose.
- [ ] A five-minute rehearsal already done, out loud, with a timer.
- [ ] `use_case/decisions.md` open, because you will be asked about a reject.

After the session, write what you were asked into `use_case/decisions.md`.
Most of the questions land in the chat, so copy it before you leave the room.
Then check your TC5 thread on Maven for the ones that arrived later. **The
questions you could not answer are the first step of this week's challenge!**
