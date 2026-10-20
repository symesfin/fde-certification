# Datasheet

## What this data is

**Generated on:** 2026-10-20

**Generated from:** three invented seed rows (`02_Open_Weights/challenge/seeds.jsonl`, built from Week 1's `make_samples.py` invoices, not from real records) and the 50 axis combinations below, by `02_Open_Weights/challenge/generate.py`. Labels follow Week 1's `EXTRACTION_PROMPT`, which the generator imports, plus the status rules and two labeling rules in its own prompt.

**Labels:** prototyping data, not backtesting. Every label was written by the generator. Validation checks the schema and the status rules, not whether a value is correct. Pilot rows (not in this file) were checked against their inputs, field by field and for arithmetic: 24 by Claude Code (combinations 0, 17, 38 and 49), three by Codex (combination 17) and three by the author (combination 0). None were checked by a domain expert.

The Step 3 read (`read_50.md`, one row per combination) was done first by Claude Code, an AI assistant, then reviewed and verified row by row by the author. It found no wrong labels in the 50 rows read. That doesn't establish an error rate: both reviewers checked against the prompt rules the generator followed, and neither is an accounts-payable expert, so a mistake they share would pass. If the review missed nothing, the rule of three would put the label error rate in this file below about 6% (3/50, the 50 being one random row per combination). The three rows generated after the read (raw lines 151 to 153) were checked the same way: 0 wrong labels. The domain check is Step 6.

Two labeling conventions came up in the read and are now decided:

- **Vendor-name case.** A name printed in capitals is labeled in title case (read row 46), so Week 4 compares vendor names case-insensitively.
- **An OCR swap that needs arithmetic.** In read row 7 an S stands for 8 in the total, which only the line items can resolve. The row is kept on purpose, as a harder case than the condition axis promises.

**Settings:** `openai/bedrock/gpt-5.6-sol`, reasoning effort medium, temperature and top_p not set; 3 rows per call; 50 combinations; dedupe threshold 0.7; `seeds.jsonl` sha256 `d6dd6495634192519b85911e11a4eba3b693583bba2ad2a7b4df029b5d30e03d`. The full record, including every pair dedupe dropped, is in `synthetic_v1.run.json` beside the data (gitignored).

**Counts:**

| Generated | Unparseable lines | Dead combinations | Empty combinations | After dedupe | Schema-valid | Removed after reading | Final |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 153 | 0 | 0 | 0 | 153 | 153 | 3 | 150 |

51 calls: 50 for the first run and 1 to regenerate combination 43 (below). 255,401 tokens (91,825 in, 163,576 out), 1,933 s. Of the 150 final rows, 90 are `ok` (30 invoices, 30 invoices with a decoy, 30 credit memos) and 60 are `failed` (30 reversals, 30 with nothing to extract); every row's status matches its combination's outcome.

**Removed after reading:** one line per row. `finish()` in `generate.py` drops them, so a rebuild with `--from-raw` keeps them out. Line numbers are raw-file lines (`_raw_line` in each row).

- Raw line 130 (combination 43): the vendor phone has no 555, so it may reach a real person.
- Raw line 131 (combination 43): same reason.
- Raw line 132 (combination 43): same reason.

The numbers are left out here; they stay in the gitignored raw file.

That emptied combination 43 (one-person shop, born-digital, reversal), so it was generated again (raw lines 151 to 153) after the prompt gained a rule that every phone number is 555-01xx. The other 147 rows came from the prompt without that rule.

**Renamed after reading:** vendor names too close to a real company's. `finish()` replaces them in the input and the label, keeping each name's length and initial.

- Raw line 39: "East River Counties Electric Cooperative" became "Elderbrook Counties Electric Cooperative" (East River Electric Power Cooperative is a real South Dakota co-op).
- Raw line 40: "High Plains Electric Cooperative" became "Hawk Plains Electric Cooperative" (High Plains Power is a real Wyoming co-op).
- Raw line 66: "Aurora Nutrition Systems, LLC" became "Avelin Nutrition Systems, LLC" (Aurora Cooperative is a real Nebraska feed and grain co-op).

**What dedupe did:** nothing. No pair reached 0.7: the closest scored 0.37, no row's nearest neighbour reached 0.4, and the median nearest neighbour was 0.2. The repetition left in the data is in words, not whole rows, which character 4-grams can't see: 119 of 120 vendor names are distinct, but "Prairie" appears in 75 of 150 rows (15 vendor names, 31 client names, plus towns and roads), street number 742 in 17 rows and the fax time 08:42 in 10.

**How it was made:**

- One call per combination to `openai/bedrock/gpt-5.6-sol` at medium reasoning effort, three rows per call. Temperature and top_p can't be set at that effort.
- Variety comes from the prompt instead. Each example is assigned a state, a month (November 2025 to October 2026) and a vendor-name initial, seeded by the combination. Without that, separate calls opened with the same defaults: a "Prairie" vendor at "742 …, Red Mesa, OK", dated 11/05/2026.
- The bill-to is always the client, written as one of its invented "Example" entities or cost centers.
- Rows are deduplicated (character 4-gram Jaccard at 0.7), then validated against `InvoiceExtraction` and the pipeline's status rules.

**Rows:** 150 (153 schema-valid, 3 removed after reading)

## Variation axes

Full values in `02_Open_Weights/challenge/axes.py`; keep both in sync. 5 × 2 × 5 = 50 combinations, 20 of them `failed` by design.

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
2. **The app's status**, which is decided by app code from the extraction: a negative Invoice fails, and a document with nothing billed fails because there is no extraction to post.

A score measures how often the extractor agrees with the generator's labels, not how often it is right. The read can't rule out mistakes the reviewers share (see Labels), so the 6% bound there is conditional and this file gives no range for the true rate; a larger sample checked by a domain expert would. Scores per combination show which rule or layout breaks, and the set works as a regression check when the prompt or model changes. The rows are text, so scoring the PDF extractor on them means rendering each one to a PDF first.

## What it cannot validate

- **Accuracy on the real queue.** Every combination gets the same number of rows, and 40% of them decline by design, so the mix is nothing like the queue's. 95% here is not 95% of real invoices.
- **Reading scans.** The production extractor reads page images. Scanned rows here are text with simulated OCR errors, which stand in for a scan but don't reproduce how a vision model misreads one.
- **Failure modes outside the axes:** two invoices in one file, bundles longer than two pages, invoices printed from email, handwriting, splitting multi-site bills by cost center, and matching vendors against the vendor master.
- **Decoy-free credits, reversals and empty documents.** Each outcome comes with its usual decoy, so those cases don't exist here.
- **Labels where generator and extractor share a blind spot.** Both are GPT-5.6 models (Sol writes, Luna extracts), and a person has checked 52 of the 150 final labels (50 read, less 1 removed afterward, plus 3 regenerated).
- **Whether a rule is right.** The generator labeled every row by the extractor's own prompt, so a wrong rule (the fax rule, the statement date as invoice date, null for an account number) produces matching wrong labels and a perfect score. Only the goldens and shadow mode test the rules themselves.
- **Invoice-number generation.** When a bill has no number, as in ex3 and ex6, the pipeline makes one up. These rows only check that the extracted number is null.
- **An exact rerun.** The model has no dated snapshot, so regenerating may give different rows.

## Known limits of realism

From the Step 3 read. These rows are fine to keep, and good material for the Step 6 "would this ever happen?" review.

- **Documents with nothing billed are built from an invoice.** They keep a statement date, an invoice number or "Due on receipt" (read rows 5, 45 and 50), as if the generator took an invoice and removed the amount.
- **Details an accountant might question:** "Net 22" terms (read row 22), finisher meal at $176 a ton (read row 27), and a delivery manifest whose bulk-weight total, 286,520 lb, doesn't match its lines, 334,120 lb (read row 40).
- **OCR swaps beyond the axis's promise:** an S for 8 in a total (read row 7) and a 0 for an a in a vendor name (read row 38).
- **Repeated defaults:** street number 742 or 7420 in 7 of the 50 rows, shop invoice number 963 twice and 4826 three times at different vendors, and the surname Mercer three times, including two shops owned by "Calvin Mercer" and "Cal Mercer".

## What it must never be compared against

The real ground truth is `use_case/evals/golden.private.jsonl` (gitignored) with its PDFs, `ex1.pdf` to `ex6.pdf`, in private storage at `$EVAL_S3_URI`. Its expected values were reviewed against each document: what the document shows, even where the posted record differs (ex1), and the posted value only where the document is blank (the Week 1 row in `decisions.md`). Shadow mode in production compares against posted records, so its accuracy is a lower bound. These rows are not ground truth. A score on them is not an accuracy figure, and must never be reported next to, averaged with, or used in place of a score on the goldens or from shadow mode.

## Leakage check — outward (what left)

- [x] No real record was used as a seed.
- [x] No real entity names, IDs, or identifiers appear.
- [x] No distinctive internal formats that would identify the firm.
- [x] Rare categories were generated, not copied.

The seeds were written by hand from Week 1's `make_samples.py` invoices. What the checks found:

- **`leak_check`** (seed strings that reappear in the output): 7 hits, all generic labels or
  the year: "AMOUNT DUE", "Account Name", "Statement Date", "Due Date", "Invoice Date", "WEIGH
  TICKET", "2026". None is a name or an identifier.
- **Phone numbers, every row:** in the first run's 150 rows, 642 phone-like numbers, 639 with
  555 in the middle. The three without it were vendor phones in combination 43; those rows
  were removed (above), and `finish()` now drops any row like them. The three regenerated rows
  use 555-01xx numbers.
- **Names:** no row mentions the client, and every bill-to is an invented "Example" entity.
  Claude Code read all 150 vendor names, then searched the web for the six most plausible as
  real businesses; none matched exactly. Three were close to real co-ops and were renamed
  (above). A web search is not a business registry, so a coincidental match is still
  possible.

Box 2 is ticked on that basis; real town names and ZIP codes remain, as places rather than
entities.

Box 3: no client document reached the generator, only the invented seeds and the prompt, so it
had no internal format to copy.

Box 4: every category, rare ones included, comes from an axis value written for this dataset;
no real record was an input.

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
No. Overlap: scenarios, not text. Week 1's `EXTRACTION_PROMPT` was written in the same commit
as the goldens (`c4b660a`), and three of its rules restate golden `why` fields: not an account
number (ex3); and, for ex4, a trailing minus means negative (the app then posts the negative
`CreditMemo` positive) and not a referenced original invoice. This file's labels follow that prompt, and its outcome axis covers the ex3 and ex4 scenarios
and ex5's `failed`. Its seeds were invented, so it shares no text with the goldens. If Week 8
fine-tunes on this file, scores on ex3 to ex5 are inflated by training on their scenarios;
report them apart from ex1, ex2 and ex6. Whether the goldens also shaped the client's production
prompt's later revisions isn't recorded. Any Week 8 fine-tuning set must also exclude the
`ex1` to `ex6` PDFs themselves, matched on the sha256 in `golden.jsonl`.

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** not measurable as
specified. A golden's `input` is `{"file", "sha256"}`, a pointer to a PDF rather than invoice
text, so a Jaccard score against these rows would be near zero whatever the overlap. Two checks
would answer it: the same 4-gram Jaccard against text extracted from `ex1.pdf` to `ex6.pdf` in
private storage, and a read of the goldens' `why` fields against the axes table for shared
scenarios, which character overlap can't see. Neither has been run.
