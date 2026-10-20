# TC2 submission: Auto Invoicing synthetic data

Use case: [`use_case/CHARTER.md`](../../use_case/CHARTER.md). The datasheet is the main
document: [`use_case/data/DATASHEET.md`](../../use_case/data/DATASHEET.md). The data itself is
gitignored.

**Loom (≤ 5 min):** _link_

---

## 🚢 Ship

### Variation axes
[`axes.py`](./axes.py), with a one-line reason above each axis, and the matching *Variation
axes* table in the datasheet. Three axes, 5 × 2 × 5 = 50 combinations:

- **source**: co-op billing system (one or two pages), feed or supply ERP (one or two pages),
  one-person repair shop or vet. Combines who produced the document with how long it runs.
- **condition**: born-digital, or scanned/faxed with OCR damage to the scored fields.
- **outcome**: invoice, invoice with a decoy near the total, credit memo, and two declines:
  a reversal and a document with nothing to extract.

Seeds: three invented rows in [`seeds.jsonl`](./seeds.jsonl), none taken from real invoices.

### Generation, counts and settings
[`generate.py`](./generate.py), which makes one call per combination. Rows are saved as each
call returns, and `--from-raw` reruns dedupe and validation without making model calls.

| Generated | After dedupe | Schema-valid | Removed after reading | Final | Dead combinations |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 153 | 153 | 153 | 3 | 150 (90 `ok`, 60 `failed`) | _fill in_ |

**Settings:** `gpt-5.6-sol` at medium reasoning effort, through the Bifrost gateway to Bedrock.
Temperature and top_p can't be set at that effort, so variety comes from the prompt instead.
3 rows per call. Dedupe uses character 4-gram Jaccard at 0.7; the closest pair scored 0.37.
51 calls, about 255K tokens. Full detail is in the datasheet.

### Leak check and the 50-row read
[`sample.py`](./sample.py) picked one row per combination with a fixed seed. Every row was
read by hand. The results, the removals and the renames are in the datasheet's *Leakage
check* sections.

### Datasheet
[`DATASHEET.md`](../../use_case/data/DATASHEET.md): prototyping vs backtesting, what it can
and cannot validate, what it must never be compared against, and whether the goldens are
disjoint from anything the system is tuned on.

### Model/endpoint decision
[`use_case/decisions.md`](../../use_case/decisions.md), the Week 2 rows: the generator model,
and the `vendor_phone` fax rule.

---

## 📤 Share

### Step 6: shown to someone who knows the real data
_Fill in: who, by role, and the status. The three answers once they come back. See
[`use_case/stakeholders.md`](../../use_case/stakeholders.md)._

### Bring it to work
_Fill in: the project at work this is for, then one line each for the **data**, the **model or
endpoint**, and the **access or approval** you would need._

---

## How to rerun

```
uv run python 02_Open_Weights/challenge/generate.py              # all 50 combinations
uv run python 02_Open_Weights/challenge/generate.py --from-raw   # dedupe and validation only
uv run python 02_Open_Weights/challenge/sample.py                # the 50-row reading sheet
```
