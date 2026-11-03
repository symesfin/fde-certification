# TC4 submission: Auto Invoicing, utility bills

Use case: [`use_case/CHARTER.md`](../../use_case/CHARTER.md). This week the use case was rescoped to utility bills, following the client's PRD v2.0 ([decision row](../../use_case/decisions.md)). General invoices are Phase 2.

**The system under test is a replay.** The client repo ran a time-boxed extraction spike on 2026-11-02: 17 utility bills, `gemini-3.5-flash`, three strategies, with hand-checked labels. `run.py` reads those recorded outputs from `SPIKE_RESULTS` (a path in `.env`, outside this repo) and scores them. Re-running extraction lives in the client repo. Nothing from the spike is copied here.

| Strategy | What it does |
|---|---|
| A (single request) | The whole bill in one model call |
| B (page by page) | One call per page, results merged |
| C (hybrid) | A cheap model classifies pages, each page is read on its own, then assembly sums and cross-checks (account lines vs header, summary vs detail, duplicates) |

**Walkthrough:** written, in this file, in place of the Loom video. The demo itself is given live (see *Demo*).

---

## 🚢 Ship

### Failure taxonomy
[`use_case/evals/failures.md`](../../use_case/evals/failures.md). All 66 runs read (17 bills × A, B, C, plus a repeat of the 5 statement bills × A, B, C).

**18 of 66 runs had at least one failure; 1 of those was caught by an assembly check.** A failed 8 of 22, B 10 of 22, C 0 of 22. The top failure (8 runs): a file of several complete statements merged with no roll-up page, where A left the bill totals blank and B took the first statement's totals as the whole file's.

Hand scores (`human_scores.jsonl`): skipped. Recommended, not graded; noted in the decision row.

### Test set
- [`golden.jsonl`](../../use_case/evals/golden.jsonl): the 6 general-invoice goldens (now `"track": "general"`, Phase 2) plus 5 masked utility bills: six merged statements with a carried balance, a late fee, a running-balance trap, a scanned diesel ticket, one account with three service sections. Masking: account numbers replaced by same-length fakes (consistent), amounts scaled and the header recomputed (current = sum of accounts; total = current + carried + late), vendor names and file paths removed. Usage and every `why` are unchanged.
- `golden.private.jsonl` (gitignored): all 17 utility bills with their real labels, one `why` each. This is what `run.py` scores.
- [`synthetic.jsonl`](../../use_case/evals/synthetic.jsonl): 35 generated failures, 7 named corruptions × the 5 masked bills, built by [`synthetic.py`](../../use_case/evals/synthetic.py). No real values.

### Scorers, echo and oracle
[`use_case/evals/harness.py`](../../use_case/evals/harness.py). Each scorer's comment names the `failures.md` line it covers. Money is `Decimal`; account numbers compare on digits only.

| Scorer | Returns | `failures.md` |
|---|---|---|
| `accounts` | 1 if the extracted accounts are exactly the true ones (none missed, extra or repeated) | #3–#6 |
| `amounts` | Share of true accounts whose current charges match to the cent (entries for one account summed) | #3, #7 |
| `usage` | Share of true billed-usage lines matched within 0.05, rate tiers summed | #2, #9 |
| `header` | 1 if the bill's current charges and carried balance both match | #1, #8 |
| `fully_right` | 1 only if all four above are 1 | all |
| `no_silent_error` | 1 if fully right, or wrong with at least one failed check; 0 if wrong and unflagged | header line (FR-11.2) |

| System | accounts | amounts | usage | header | fully right | no silent error |
|---|---|---|---|---|---|---|
| echo | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| A (single request) | 1.00 | 0.94 | 1.00 | 0.88 | 0.71 | 0.76 |
| B (page by page) | 0.88 | 1.00 | 1.00 | 0.82 | 0.71 | 0.71 |
| C (hybrid) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| oracle | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

n = 17 bills, main run. A's usage is 0.997 (a rate tier dropped on 2 of 111 statement accounts) and rounds to 1.00. B's double count (failure #3) shows in `accounts`, not `amounts`: the true account's amount was right; the misread duplicate is an extra account.

### LLM judge
Rubric `JUDGE_RUBRIC` in `harness.py`, for `failures.md` #3, #4 and #7: "do the two list exactly the same accounts, each with the same current charges to the cent?", answer `{"score": 0 or 1, "why": ...}`. Judge model: `gpt-5.6-luna` through the gateway. The outputs scored here are Gemini's, so no model grades its own work. `gpt-5.6-luna` is also the Week 1 app's extractor for general invoices (Phase 2), which this harness doesn't score; if the course app is ever scored here, the judge moves to a third model. The label is reduced to account numbers and current charges before it goes in the prompt.

- Calibration: `USABLE: accepted 1.00, wrong 0.00, separation 1.00, n=17` (wrong answer `{"accounts": []}`).
- Separation: echo 0.00 / oracle 1.00. Strategy C: 1.00.
- On the generated failures it caught exactly what `amounts_exact` caught, mode for mode (table below), including every digit flip.

**Separation 0.00 / 1.00; agreement not checked; used as a column only, not the headline, because a function scores amounts exactly.**

Judge calls: 120 per `run.py --judge` (measured: 34 calibration, 51 echo/C/oracle, 35 synthetic; 105K tokens). `run.py` without `--judge` makes no calls.

### Generated failures
Natural failures in 66 recorded runs: 19 (in 18 runs). Generated: 35.

| Failure mode | n | accounts | amounts | usage | header | fully right | judge |
|---|---|---|---|---|---|---|---|
| digit_flip_account | 5 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 |
| digit_flip_amount | 5 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 |
| amount_off_10pct (hard) | 5 | 0.00 | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| dropped_tier | 5 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 | 0.00 |
| swap_current_carried | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 |
| duplicate_account | 5 | 1.00 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 |
| extra_summary | 5 | 1.00 | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 |

Each cell is the share caught (score below 1). `no_silent_error` catches all 35, since corrupted labels carry no checks. "Hard" keeps the bill internally consistent (header recomputed), so an add-up check inside the bill can't see it; comparing against the label still can. The judge misses the usage and header corruptions because its rubric asks only about accounts and amounts.

This table scores the scorers, not C's checks. FR-11.4 (planted errors run through C's own assembly checks) is not done here.

### Scenarios
Skipped. The pipeline is single-turn: one bill in, one extraction out. Repeats are covered by pass^2 below.

### Baseline
[`use_case/evals/baseline.json`](../../use_case/evals/baseline.json): strategy C, saved with `helpers.harness.save`. Bill ids are hashed and every result's `expected` and `actual` are blanked, because they carry real account numbers; the per-bill scores stay.

**Headline: no silent error 1.00, 95% CI [0.82, 1.00] (Wilson), n = 17 bills.** The percentile bootstrap from Session 7 gives [1.00, 1.00]: with no failures there is nothing to resample, so it reports no uncertainty at all. Wilson gives the honest width: after 17 clean bills, a true silent-error rate up to about 1 bill in 5 is still consistent with what we saw. Both are stored in `meta.ci`.

```
PASS  utility-C-spike → C (hybrid)  [accounts +0.000  amounts +0.000  fully_right +0.000  header +0.000  no_silent_error +0.000  usage +0.000]
```

pass^2: C was fully right in both the main and the repeat run on 5 of 5 statement bills (FR-11.2 counts a bill fully right only if every run is).

### Decision row
[`use_case/decisions.md`](../../use_case/decisions.md), Week 4: the headline with its interval and n, what it does not cover, what was rejected, and what would change my mind. Also two more Week 4/3 rows: the rescope, and why there is no retrieval step.

### Docker
The Week 1 app's image builds and serves on port 7860 (checked 2026-11-03: HTTP 200). `--env-file` keeps the quotes around `LLM_EXTRA_HEADERS` and the app fails at startup parsing it, so that one variable is passed with `-e` instead; see *How to rerun*.

---

## 📤 Share

### Demo
**Pending: not yet rehearsed.** Plan, five minutes:

1. **0–1, the problem:** accountants type each account on a statement bill (up to 37) into an allocation sheet, and usage is never recorded.
2. **1–2, the demo:** `run.py` printing the system table: echo, A, B, C, oracle.
3. **2–3.5, the number:** no bill was wrong without a flag, 17 of 17, but the interval runs down to 0.82. One failure: B read a non-account number as a second account and doubled the total, and nothing flagged it; C's summary-vs-detail and reconciliation checks are built to flag that. What it doesn't cover: the spike's own bills, one vendor for long statements, replayed runs.
4. **3.5–5, what's next:** held-out bills from the client's systems owner (H9), threshold sign-off from the process owner and systems owner (H10), the test import of a produced sheet (H24).

Questions, in order: *What would you do differently on Monday if this number is right? What would it take to convince you it is wrong? What did you expect to see that you didn't?* Answers go in [`stakeholders.md`](../../use_case/stakeholders.md) and one line in `decisions.md`.

### Bring it to work
**What it's for:** the per-vendor go-live eval (FR-11) for the client's utility bills, and a measurement of the current document processor's OCR, whose accuracy has only ever been estimated ("~80%").

**Data:** three months of bills per vendor with the filled allocation sheets the accountants typed, from the client's systems owner (H9). The sheets are the accountants' judgment; extraction labels are checked by hand against each bill.

**Model or endpoint:** the extractor is Gemini on Vertex AI, already approved for the client's bills. The judge is `gpt-5.6-luna` through the employer's gateway, which the client already allows invoice data through; it adds nothing over the functions here, so the work version can drop it and keep bills off a second endpoint.

**Approval:** the client's process owner and systems owner, the two lead stakeholders, sign off the go-live thresholds (H10); whoever approves the gateway for invoice data approves the judge, if kept.

**Judge calls per `run.py`:** 0 by default; 120 with `--judge` (measured).

---

## How to rerun

```
uv run python use_case/evals/synthetic.py                  # rebuild synthetic.jsonl from the masked goldens
uv run python use_case/evals/run.py                        # model-free table, headline, compare, detection
uv run python use_case/evals/run.py --judge                # adds the judge (120 calls)
uv run python use_case/evals/run.py --save-baseline        # rewrite baseline.json
```

`run.py` needs `golden.private.jsonl` and `SPIKE_RESULTS` in `.env`; without them it stops and names what's missing. From a clean public checkout neither exists, by design.

Docker (from `01_Product_Engineering/challenge/`). `--env-file` keeps the quotes around `LLM_EXTRA_HEADERS`, so pass that one with `-e`:

```
docker build -t enterprise-fde-challenge .
H="$(sed -n "s/^LLM_EXTRA_HEADERS=//p" ../../.env | sed "s/^'//; s/'$//")"
docker run -p 7860:7860 --env-file <(grep -v '^LLM_EXTRA_HEADERS=' ../../.env) -e LLM_EXTRA_HEADERS="$H" enterprise-fde-challenge
```
