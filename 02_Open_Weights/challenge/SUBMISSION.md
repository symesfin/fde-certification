# TC2 submission: Auto Invoicing synthetic data

Use case: [`use_case/CHARTER.md`](../../use_case/CHARTER.md). The datasheet is the main document: [`use_case/data/DATASHEET.md`](../../use_case/data/DATASHEET.md). The data itself is gitignored.

**Walkthrough:** written, in this file, in place of the Loom video.

---

## 🚢 Ship

### Variation axes
[`axes.py`](./axes.py), with a one-line reason above each axis, and the matching *Variation axes* table in the datasheet. Three axes, 5 × 2 × 5 = 50 combinations:

- **source**: co-op billing system (one or two pages), feed or supply ERP (one or two pages), one-person repair shop or vet. Combines who produced the document with how long it runs.
- **condition**: born-digital, or scanned/faxed with OCR damage to the scored fields.
- **outcome**: invoice, invoice with a decoy near the total, credit memo, and two declines: a reversal and a document with nothing to extract.

Seeds: three invented rows in [`seeds.jsonl`](./seeds.jsonl), none taken from real invoices.

### Generation, counts and settings
[`generate.py`](./generate.py), which makes one call per combination. Rows are saved as each call returns, and `--from-raw` reruns dedupe and validation without making model calls.

| Generated | After dedupe | Schema-valid | Removed after reading | Final | Dead combinations |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 153 | 153 | 153 | 3 | 150 (90 `ok`, 60 `failed`) | 0 |

**Settings:** `gpt-5.6-sol` at medium reasoning effort, through the Bifrost gateway to Bedrock. Temperature and top_p can't be set at that effort, so variety comes from the prompt instead. 3 rows per call. Dedupe uses character 4-gram Jaccard at 0.7; the closest pair scored 0.37. 51 calls, about 255K tokens. Full detail is in the datasheet.

### Leak check and the 50-row read
[`sample.py`](./sample.py) picked one row per combination with a fixed seed. I then reviewed and verified each one. The results, the removals and the renames are in the datasheet's *Leakage check* sections.

### Datasheet
[`DATASHEET.md`](../../use_case/data/DATASHEET.md): prototyping vs backtesting, what it can and cannot validate, what it must never be compared against, and whether the goldens are disjoint from anything the system is tuned on.

### Model/endpoint decision
[`use_case/decisions.md`](../../use_case/decisions.md), the Week 2 rows: the generator model, and the `vendor_phone` fax rule.

---

## 📤 Share

### Step 6: shown to someone who knows the real data
**Pending.** The client's contacts have been unavailable last week and this week, so nothing has been shown to anyone yet and there are no answers to record. As soon as I'm able to, the plan is to send 20 rows and the datasheet, with the three questions in order, and record what they say in their own words. Logged in [`use_case/stakeholders.md`](../../use_case/stakeholders.md).

### Bring it to work
**Project:** the client's invoice pipeline, this use case. No project is blocked on access; I have the real invoices. Synthetic data still helps in two places: a regression set for prompt and model changes, because the real queue sends too few reversals, credit memos and faxed bills to test each change on; and anything shown outside the client team, such as a demo or this course, where real invoices can't go.

**Data:** seeded from a description of the queue, not from records. Records would give truer layouts, but they carry vendor names, account numbers and amounts into the output, and `leak_check` only catches exact strings. Even this week's invented seeds let three real-looking phone numbers and three near-real vendor names through. The axes would come from shadow-mode disagreements and dead-letter reasons, which show what breaks without copying any invoice.

**Model or endpoint:** the same one, `gpt-5.6-sol` on Bedrock through the gateway, which is a different model family from the production extractor (Gemini). The local Week 1 extractor is `gpt-5.6-luna`, the same family, as the datasheet notes. With invented seeds and a written description, nothing from the client is in the prompt, so this data can leave the network. Seeding from records would need an endpoint the client already approves for its invoices.

**Approval:** none to generate it. Before invoices modeled on the client's vendors and sites go into a demo or anything else shown outside the team, the client contact should agree: the names are invented, but the structure still describes their business.

---

## How to rerun

```
uv run python 02_Open_Weights/challenge/generate.py              # all 50 combinations
uv run python 02_Open_Weights/challenge/generate.py --from-raw   # dedupe and validation only
uv run python 02_Open_Weights/challenge/sample.py                # the 50-row reading sheet
```
