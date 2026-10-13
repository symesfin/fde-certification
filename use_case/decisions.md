# Decision log

One row per architectural decision, with the option you rejected and why.

> **Week 5 asks you to defend your agent architecture against the alternatives.**
> **Week 10's handoff doc is largely this file.** Both are much easier if you
> wrote the reasoning down while you still remembered it.

A decision without a rejected alternative is not a decision, it is a default.
If you cannot name what you did not do, you did not choose.

| Week | Decision | What you rejected | Why | What would change your mind |
| --- | --- | --- | --- | --- |
| 1 | **Pipeline:** a fixed workflow with one model call. Scored 1 of 4 below. | An agent that chooses its own tools: re-reading pages, trying another vendor search, re-splitting. | Money moves, so every result has to be repeatable and explainable. Shadow mode's field-by-field comparison against the document processor only means something if the process is the same for every invoice. Cost stays predictable at ~160/day, and each step can be tested on its own. The hard part, reading messy layouts, already happens inside one model call; an agent adds variance in steps and cost without removing it. | Shadow-mode data showing most dead-letter items (more than 50%, est.) each need a different fix-up: a missed page in a 300-page bill, a vendor found by address instead of phone, page sorting in bundled files, splitting two invoices. If one fix-up dominates, add it as one more pipeline step (e.g. re-ask the model once when line items don't add up). Switch only when the branches pile up. Phase 2 (GL coding and approver assignment, which need judgment over history) is the likelier trigger. |
| 1 | **Splitting multi-site bills is out of scope for Week 1.** `Response` has no allocations. | Scoring the split with example #2's bundle. | The bundle already contains the sheet the accountant typed, so the model would copy it rather than split anything. Nobody has seen the sow production ERP's journal import format yet. Cost: the biggest time sink (20–60 min per bill, est.) goes unmeasured. | It becomes the first item after Week 1 once three inputs exist: the vendor bill alone, the site template, and the posted journal entry as the answer. A call with the people who run the journal import is on offer. |
| 1 | **An expected value is what's correct on the document, not what was posted.** Applies only to fields the document shows; where it's blank (the made-up invoice numbers in ex3 and ex6) the posted value is the only source. | Treating posted records as ground truth. | ex1's posted total is $1.00 off the printed total, which the bill's line items confirm. The error got past OCR and the accountant into the ERP, and the model got it right. Scoring against the posted record would count a correct answer as a failure. Shadow-mode accuracy against posted records is therefore a lower bound. | Reviewing shadow-mode disagreements shows posted values that differ from the document on purpose: disputed or unowed charges taken off, a tax exemption applied, a discount taken, a partial payment. If those are more than rare, then for that field the truth is what should be paid, not what's printed, and the expected value goes back to the posted record. Separately, if disagreements are too many to review by hand, fall back to posted values plus a sampled audit. |
| 1 | **Scope narrowed after the proof-of-concept demo:** from GL coding and approver prediction to replacing the document processor's OCR, in shadow mode. | Building GL coding and approver prediction first. | In the demo, the OCR-plus-XML slice was called "a pretty big win", and the work isn't in the current SOW, so it runs in the background where it can be judged on shadow reports. | Virtually nothing. The first step is reading accurately what's in an invoice; if we could go straight from ingestion to GL and approver coding, we would. Only a model that already had the client's specific GL and approver context could skip this step, which is unrealistic. GL and approver coding build on this solution. |
| 3 | <!-- retrieval approach --> | <!-- --> | <!-- --> | <!-- --> |
| 5 | <!-- agent architecture --> | <!-- --> | <!-- --> | <!-- --> |
| 6 | <!-- guardrail level --> | <!-- --> | <!-- --> | <!-- --> |
| 7 | <!-- memory type --> | <!-- --> | <!-- --> | <!-- --> |
| 8 | <!-- model --> | <!-- --> | <!-- --> | <!-- --> |

### Week 1: agent or pipeline

| # | True of this use case? | Answer |
| :---: | --- | --- |
| 1 | The number of steps depends on the input | **No.** The workflow is fixed: extract → validate, vendor lookup, allocation, XML → audit → shadow compare or dead-letter queue. Only the number of XMLs varies (1 to N), and that's splitting the data, not adding steps. |
| 2 | It must call out to systems to answer at all | **Yes, but the calls are fixed:** the model (Gemini), the vendor master database, and object storage (the PDF, the vendor's allocation lookup, ground truth). Every invoice gets the same calls in the same order; the model chooses none of them. |
| 3 | It has to notice its own mistakes and try something else | **No.** It notices problems (line items that don't add up, bad dates, unresolved accounts, unmatched vendors) and sends them to a person rather than trying again. Retries cover temporary errors only: up to 3, with backoff. |
| 4 | The input is open-ended | **No.** Layouts vary across hundreds of vendors, but the single model call absorbs that. The cases can be listed: single-site, multi-site with a template, no invoice #, unmatched vendor, credits, bundled documents, two invoices in one file. |

**The strongest case for an agent.** Every item in the dead-letter queue is one
an accountant fixes with a few standard moves: page back through the PDF,
re-add the lines, search the vendor by address or a name variant, notice a
second invoice in the file. An agent can make those same moves, so it would turn
much of the queue into clean results, and the queue is exactly where the manual
work remains after cutover. A fixed pipeline settles for routing those invoices
to a person.

---

The last column is the one people skip and the one people ask about. "We chose
dense retrieval; we would switch to hybrid if exact-match queries went above ~20%
of traffic" is an engineering position. "We chose dense retrieval" is a
preference.
