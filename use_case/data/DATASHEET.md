# Datasheet

## What this data is

**Generated on:** 2026-10-20

**Generated from:** three invented seed rows (`02_Open_Weights/challenge/seeds.jsonl`, built
from Week 1's `make_samples.py` invoices, not from real records) and the 50 axis combinations
below, by `02_Open_Weights/challenge/generate.py`. Labels follow Week 1's `EXTRACTION_PROMPT`,
which the generator imports, plus the status rules and two labeling rules in its own prompt.

**Labels:** prototyping data, not backtesting. Every label was written by the generator.
Validation checks the schema and the status rules, not whether a value is correct. No person
has checked the labels in this file yet. Pilot rows (not in this file) were checked against
their inputs, field by field and for arithmetic: 24 by Claude Code (combinations 0, 17, 38 and
49), three by Codex (combination 17) and three by the author (combination 0). None were checked
by a domain expert. The Step 3 read of 50 rows is the first check of this file.

**Settings:** `openai/bedrock/gpt-5.6-sol`, reasoning effort medium, temperature and top_p not
set; 3 rows per call; 50 combinations; dedupe threshold 0.7; `seeds.jsonl` sha256
`d6dd6495634192519b85911e11a4eba3b693583bba2ad2a7b4df029b5d30e03d`. The full record, including
every pair dedupe dropped, is in `synthetic_v1.run.json` beside the data (gitignored).

**Counts:**

| Generated | Unparseable lines | Dead combinations | Empty combinations | After dedupe | Schema-valid |
| --- | --- | --- | --- | --- | --- |
| 150 | 0 | 0 | 0 | 150 | 150 |

50 calls, 251,248 tokens (90,010 in, 161,238 out), 1,903 s (38 s a call). 90 rows are `ok`
(30 invoices, 30 invoices with a decoy, 30 credit memos) and 60 are `failed` (30 reversals, 30
with nothing to extract); every row's status matches its combination's outcome. `leak_check`
flagged 7 strings, all generic labels or the year: "AMOUNT DUE", "Account Name", "Statement
Date", "Due Date", "Invoice Date", "WEIGH TICKET", "2026".

**What dedupe did:** nothing. No pair reached 0.7: the closest scored 0.37, no row's nearest
neighbour reached 0.4, and the median nearest neighbour was 0.2. The repetition left in the
data is in words, not whole rows, which character 4-grams can't see: 119 of 120 vendor names
are distinct, but "Prairie" appears in 75 of 150 rows (15 vendor names, 31 client names, plus
towns and roads), street number 742 in 17 rows and the fax time 08:42 in 10.

**How it was made:**

- One call per combination to `openai/bedrock/gpt-5.6-sol` at medium reasoning effort, three
  rows per call. Temperature and top_p can't be set at that effort.
- Variety comes from the prompt instead. Each example is assigned a state, a month (November
  2025 to October 2026) and a vendor-name initial, seeded by the combination. Without that,
  separate calls opened with the same defaults: a "Prairie" vendor at "742 …, Red Mesa, OK",
  dated 11/05/2026.
- The bill-to is always the client, written as one of its invented "Example" entities or cost
  centers.
- Rows are deduplicated (character 4-gram Jaccard at 0.7), then validated against
  `InvoiceExtraction` and the pipeline's status rules.

**Rows:** 150

## Variation axes

Full values in `02_Open_Weights/challenge/axes.py`; keep both in sync. 5 × 2 × 5 = 50
combinations, 20 of them `failed` by design.

| Axis | Values | Real variation it covers |
| --- | --- | --- |
| source | 1. Co-op, one page: one meter, account number but no invoice number, service period beside the statement date, toll-free and local office phones | Who produced it and how long it runs. Utility billing systems, supplier ERPs and shop templates print the vendor name, phones, reference numbers and dates differently. One axis because one-person shops don't send two-page bills grouped by site. |
| | 2. Co-op, two pages: ten or more meters grouped by site, header repeats, closing block on page 2 only | |
| | 3. Feed or supply ERP, one page: order, PO, BOL and scale-ticket numbers near the invoice number, phone and fax lines, remit-to lockbox | |
| | 4. Feed or supply ERP, two pages: ten or more deliveries grouped by site, header repeats, closing block on page 2 only | |
| | 5. One-person repair shop or vet, one page: name only in a header line, cell number, three- or four-digit invoice number, month-name dates, "Due on receipt" | |
| condition | 1. Born-digital: clean text, columns aligned | Clean PDFs vs scans and faxes: columns drift from their labels, a fax banner adds a second phone and date, and OCR damages the scored fields. |
| | 2. Scanned or faxed: drifting columns, fax banner with the sender's fax number and transmission date, OCR swaps a reader can undo in the vendor name, total and all-digit invoice numbers; the label is the true value | |
| outcome | 1. Invoice, nothing near the total to mistake for it → `ok` | What the document is, paired with the decoy it usually carries. Sets the status and whether the extraction is kept. |
| | 2. Invoice with a decoy near the total (previous balance, subtotal before tax and freight, late-payment amount) → `ok` | |
| | 3. Credit memo: trailing minus or parentheses, cites the original amount or a previous balance → `ok`, `CreditMemo`, negative total | |
| | 4. Reversal: mostly plain INVOICE or STATEMENT with a "Reverses invoice" line, sometimes REVERSAL, never credit → `failed`, fields filled in | |
| | 5. Nothing to extract: packing slip, delivery or weigh ticket, work order or usage summary, with weights or meter reads where a total would sit → `failed`, extraction null | |

## What it can validate

Two things, scored separately in Week 4:

1. **The extractor's fields**, on the layouts and traps in the axes table:
   - the amount due over a decoy beside it (previous balance, subtotal, late-payment amount,
     the original amount on a credit or reversal)
   - the printed sign, and `CreditMemo` vs `Invoice`, on credits and reversals
   - a null invoice number when only an account, PO or referenced number is printed
   - the first non-fax phone number in the body
   - true values under OCR swaps a reader can undo
2. **The app's status**, which is decided by app code from the extraction: a negative Invoice
   fails, and a document with nothing billed fails because there is no extraction to post.

Until the Step 3 read gives a label error rate, a 95% score measures how often the extractor
agrees with the generator, not how often it follows the rules. With a measured label error rate
of e, the true rate is within e points of the score either way. Hand-checked labels with a low
error rate are what would let the claim be stated about the rules. Scores per combination show
which rule or layout breaks, and the set works as a regression check when the prompt or model
changes. The rows are text, so scoring the PDF extractor on them means rendering each one to a
PDF first.

## What it cannot validate

- **Accuracy on the real queue.** Every combination gets the same number of rows, and 40% of
  them decline by design, so the mix is nothing like the queue's. 95% here is not 95% of real
  invoices.
- **Reading scans.** The production extractor reads page images. Scanned rows here are text
  with simulated OCR errors, which stand in for a scan but don't reproduce how a vision model
  misreads one.
- **Failure modes outside the axes:** two invoices in one file, bundles longer than two pages,
  invoices printed from email, handwriting, splitting multi-site bills by cost center, and
  matching vendors against the vendor master.
- **Decoy-free credits, reversals and empty documents.** Each outcome comes with its usual
  decoy, so those cases don't exist here.
- **Labels where generator and extractor share a blind spot.** Both are GPT-5.6 models (Sol
  writes, Luna extracts), and no person has checked every label.
- **Whether a rule is right.** The generator labeled every row by the extractor's own prompt,
  so a wrong rule (the fax rule, the statement date as invoice date, null for an account
  number) produces matching wrong labels and a perfect score. Only the goldens and shadow mode
  test the rules themselves.
- **Invoice-number generation.** When a bill has no number, as in ex3 and ex6, the pipeline
  makes one up. These rows only check that the extracted number is null.
- **An exact rerun.** The model has no dated snapshot, so regenerating may give different rows.

## What it must never be compared against

The real ground truth is `use_case/evals/golden.private.jsonl` (posted values, gitignored) with
its PDFs, `ex1.pdf` to `ex6.pdf`, in private storage at `$EVAL_S3_URI`; in production, it is
the posted records shadow mode compares against. These rows are not ground truth. A score on
them is not an accuracy figure, and must never be reported next to, averaged with, or used in
place of a score on the goldens or from shadow mode.

## Leakage check — outward (what left)

- [x] No real record was used as a seed.
- [ ] No real entity names, IDs, or identifiers appear.
- [ ] No distinctive internal formats that would identify the firm.
- [ ] Rare categories were generated, not copied.

The seeds were written by hand from Week 1's `make_samples.py` invoices. The other three
boxes wait for the Step 3 read of 50 rows.

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
No. Overlap: scenarios, not text. Week 1's `EXTRACTION_PROMPT` was written in the same commit
as the goldens (`c4b660a`), and three of its rules restate golden `why` fields: not an account
number (ex3), and a trailing minus means negative and not a referenced original invoice (ex4).
This file's labels follow that prompt, and its outcome axis covers the ex3 and ex4 scenarios
and ex5's `failed`. Its seeds were invented, so it shares no text with the goldens. If Week 8
fine-tunes on this file, scores on ex3 to ex5 are inflated by training on their scenarios;
report them apart from ex1, ex2 and ex6. Whether the goldens also shaped the the client production
prompt's later revisions isn't recorded. Any Week 8 fine-tuning set must also exclude the
`ex1` to `ex6` PDFs themselves, matched on the sha256 in `golden.jsonl`.

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** not measurable as
specified. A golden's `input` is `{"file", "sha256"}`, a pointer to a PDF rather than invoice
text, so a Jaccard score against these rows would be near zero whatever the overlap. Two checks
would answer it: the same 4-gram Jaccard against text extracted from `ex1.pdf` to `ex6.pdf` in
private storage, and a read of the goldens' `why` fields against the axes table for shared
scenarios, which character overlap can't see. Neither has been run.
