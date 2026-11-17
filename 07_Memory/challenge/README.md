# Technical Challenge 7 — Memory, and evals that test it

> **Read first:** [`use_case/CHARTER.md`](../../use_case/CHARTER.md).

Add memory to your application, plus evals that test the memory **directly**.
Testing the whole app and hoping the memory works doesn't count.

<table>
  <tr><td width="110"><strong>Outcome</strong></td>
  <td>Memory that demonstrably works, and three tests that would catch it when it stops.</td></tr>
  <tr><td><strong>Due</strong></td>
  <td>End of Week 7.</td></tr>
</table>

---

## Part 1 — Pick one kind, and say why

You do not need all three. Most applications need one, and choosing is part of
the work:

- **Semantic**, if your users have stable facts your app keeps asking for.
- **Procedural**, if your app solves the same kind of problem again and again
  and works it out from scratch each time.
- **Episodic**, if anyone will ever ask "why did it do that?" In a regulated
  firm, they will.

Write down your choice, and the kinds you rejected, in `use_case/decisions.md`.
**If your app does not need memory, that is a valid answer.** Say so, with the
reason, and build the smallest version anyway so you have measured the thing
you are declining.

## Part 2 — Build it

SQLite is the recommended default. It is transactional, does full-text search,
is one file, and has no server. Reach for a vector store only if you can say
what search by meaning buys you that full-text search (FTS) does not.

**Handle the staleness problem explicitly.** Facts change. Supersede-on-write
keeps one live entry per subject, and it is the default we recommend.
Session 13 shows what happens without it.

## Part 3 — Three tests, in the Week 4 harness

"The app seems to remember" is not a test. These tests target the memory:

1. **Staleness.** Store a fact, change it, and assert the current value comes
   back and the old one does not.
2. **Cost saving.** Run a task twice, measure steps or tokens, and assert
   attempt two is cheaper. This is the metric a business understands.
3. **Truthfulness.** Have the agent do something, ask it to explain, and assert
   the explanation matches **your** log of what happened. The model's account
   of itself is not the log.

**If your app has any notion of users, add the leakage test.** Two users ask
the same question. Assert neither sees the other's facts.

---

## Submission

- [ ] One kind of memory, implemented, with the choice and rejects in `decisions.md`.
- [ ] Staleness handled explicitly. Say which of recency / supersede / validity
      windows you used.
- [ ] Three memory tests in `use_case/evals/`, running with everything else.
- [ ] The leakage test, if you have users.
- [ ] A before/after on your Week 4 numbers. **Memory can make things worse.**
      A wrong fact retrieved confidently is worse than no fact, and you should
      find out whether that happened in your app.

**Strongly recommended**

- [ ] Measure recall quality at 10, 100, and 1,000 entries. The curve tells you
      when FTS stops being enough.
- [ ] One spec file, from Session 14, for a real piece of your work.

---

## If you get stuck

**"My app has no memory need."** Good, say so with a reason. Then build
semantic memory for one user preference anyway. It takes ten minutes, and it
means your "we don't need it" is measured.

**"The memory makes answers worse."** That is a real and common result. A
retrieved wrong fact pushes out correct reasoning. Work out whether it is
retrieval (the wrong entry) or staleness (the right entry, out of date). The
fixes are completely different.

**"I can't measure the procedural saving."** Count anything: tool calls, model
calls, turns, seconds. An imperfect proxy you actually measure beats a perfect
metric you don't.

**"My episodic explanations are plausible but I can't verify them."** Then you
have found the important failure. Write episodic entries from **observed
events**. Log the tool call that happened, not the model's description of it.
