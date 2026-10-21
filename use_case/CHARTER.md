# Project charter

<!--
  Fill this in during TC1 Step 4, from your Getting to Concreteness form.
  Later weeks' notebooks read this file and stop if it is still the template.
  That is on purpose.
-->

**Department:** Accounting — Accounts Payable. Sponsor: COO.

**Working title:** Auto Invoicing

---

## The problem

**Who has it?** One real role, not a department.

AP accountants, each assigned a geographic region — 9 junior/associate accountants (per the AP systems lead, 2026-04-09) — plus one accountant in the same role who handles company-wide vendors such as feed directly.

**What are they trying to do?**

Record each vendor bill correctly — right vendor, amount, date, invoice #, and right farm/cost center — so it gets approved and paid on time, once.

**How do they handle it today?**

1. Invoices arrive by paper mail, email, or vendor portal. Paper is scanned to PDF on a desk scanner.
2. The accountant drops the PDF (or an Excel allocation sheet) into their own folder via a desktop share drive.
3. The document processor (image recognition software) checks the folders every 30 seconds. Its OCR reads vendor, total, date, due date, and invoice #. The client calls it "~80%" accurate.
4. In the document processor's verification screen the accountant fixes fields by hand, looking up the vendor by phone # against the accounting general ledger.
   - **No invoice # on the bill:** they make one up: an identifier + a month code + the year. Utilities start with the account number printed on the bill, other vendors with the vendor ID. Month codes vary (APR26, AP26). Typos defeat the accounting ERP's duplicate check, so duplicates get paid.
   - **Multi-site utility/internet bills:** they type each meter's total into an Excel template; the document processor splits it into one invoice per cost center, and the sheet also goes to the sow production ERP for the journal entry. Late fees and credits make this harder.
5. Submit sends XML + PDF to an export folder, and the accounting ERP imports it automatically within seconds.
6. After that, outside scope: the accountant assigns an approver by hand, the approver codes the GL account, anything over $5k gets a second approval, and it posts to the accounting general ledger.

OCR failures: wrong vendor, wrong total, wrong number pulled as invoice #, blank fields. Worst fields: vendor, total, invoice #.

**What does that cost — time, money, risk, or relationships?**

- **Volume:** ~2,300 invoices/wk in total. ~1,100/wk (~160/day, ~4,700/mo) go through the document processor and are in scope; the rest are feed invoices handled in the sow production ERP.
- **Time:** simple invoice ~3–5 min (est.); allocation-sheet utility bill 20–60 min (est.). Roughly 55–90 hrs/wk across the team (est.).
- **Accuracy:** "~80%" is the client's guess, and nobody defined what it counts. His other statement — "every other invoice needs a correction" — means only ~50% of invoices come through clean.
- **Mistakes:** duplicates paid twice "occasionally"; wrong approver assigned "pretty frequently", so the invoice sits up to a month and goes past due (late fees implied); GL miscoding and missed capital projects downstream. No dollar figures captured.

**The problem in one sentence. No solution in it.**

AP accountants hand-correct about half of ~1,100 invoices a week before they reach the accounting ERP. Their hand-made invoice numbers and allocation sheets let duplicates and errors through.

---

## Success

**What does the new world look like for that person?**

Accountants drop PDFs in the same folder. Vendor, total, date, invoice #, and vendor ID reach the accounting ERP already filled. They stop retyping in
verification, stop inventing invoice #s, and stop typing utility totals into allocation sheets. They check results instead, and only failures need hands-on work.

**How would the firm measure it? Which numbers should move?**

- **Primary:** % of invoices reaching the accounting ERP with zero manual corrections (today ~50%).
- **Secondary:** duplicate payments per month (baseline unknown for now).

---

## The first product

**Your solution in one sentence.**

An AI pipeline reads each invoice dropped in the accountant's existing folder, finds the vendor ID, splits multi-site bills by cost center, and writes the same XML the accounting ERP imports from the document processor today. It runs alongside the document processor until it's more accurate.

**Scope.** Reads the printed header fields. Matches the vendor ID against the general ledger's vendor master (phone first, then fuzzy name). Generates an invoice # when one is missing, following the accountants' scheme (see "How do they handle it today?"). Splitting multi-site bills by cost center is out of scope for Week 1, though the hand-typed allocation sheet is the biggest time sink (20–60 min, est.); it is the first item after Week 1. No PO matching. Approver assignment and general GL coding are Phase 2.

**Input → Output.** Be specific enough that someone could build it wrong and you would notice.

| | |
| --- | --- |
| **In** | PDFs only, as raw bytes: scanned paper (image-only) and digital PDFs from email/portals. The model reads the PDF directly, scans included. Excel allocation sheets aren't handled. No photos or direct email intake — the accountant saves the file to the folder.<br>One file can hold several documents: invoice + scale ticket + bill of lading, an allocation sheet bundled in varying order, utility bills up to 300 pages. Some files likely hold two invoices; only one is extracted per file — a known gap. |
| **Out** | Accounting ERP import fields, header only: DocType, Total, Date, Number, Vendor_ID, Vendor_Name, Recognition, BatchNo, Processor, Company, GroupName. No line items go to the ERP; multi-site bills post as one record for the full total; the split goes to the sow production ERP. Credit memos post as DocType CreditMemo with a positive total and "CM" appended to the number. A negative total (a reversal) fails to the dead-letter queue.<br>**Unmatched vendor:** still goes through, with Vendor_ID blank and flagged.<br>**Can't process** (no vendor name, total missing or ≤0, bad date, line items missing or ≠ total): goes to a dead-letter queue with the specific errors and a link to the audit bundle.<br>**Review:** shadow mode now — nothing goes into the ERP; output is compared against the document processor. After cutover, accountants review 100% from a review folder, tapering to spot checks. What accountants see after cutover is still undecided. |

---

## Decisions made later

<!--
  Amended as the cohort goes. Keep the reasoning, not just the choice — Week 5
  asks you to defend your architecture against the options you rejected, and
  Week 10's handoff doc is largely this section.
-->

| Week | Decision | Why, and what you rejected |
| --- | --- | --- |
| 3 | Retrieval approach | <!-- TC3 --> |
| 5 | Agent architecture | <!-- TC5 --> |
| 8 | Model | <!-- TC8 --> |
