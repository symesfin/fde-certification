"""Generate the synthetic Auto Invoicing dataset (TC2).

Sends one generation call per axis combination and counts what came back.

    uv run python 02_Open_Weights/challenge/generate.py
    uv run python 02_Open_Weights/challenge/generate.py --from-raw   # no model calls

--from-raw re-runs dedupe, validation and saving on the raw rows already on disk,
so a threshold experiment takes seconds. Each call's rows are appended to synthetic_v1.raw.jsonl as soon as it returns,
and a rerun skips the combinations already there, so a crash costs at most the
call in flight. Delete that file to start over.
"""

import json
import random
import sys
from calendar import month_name
from dataclasses import asdict
from datetime import date
from hashlib import sha256
from pathlib import Path
from string import ascii_uppercase
from typing import Literal

import litellm
from pydantic import BaseModel, ValidationError, model_validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# The repo root for helpers/, and Week 1's challenge for the extractor's prompt.
sys.path[:0] = [str(ROOT), str(ROOT / "01_Product_Engineering" / "challenge")]

from axes import AXES
from helpers.llm import CallStats, chat
from helpers.nb import bootstrap
from helpers.sdg import SDGReport, combinations, dedupe, jaccard, leak_check, shingles
from llm import EXTRACTION_PROMPT
from schema import InvoiceExtraction

# Otherwise LiteLLM prints a "Provider List" notice on every call to a model
# name it doesn't recognise.
litellm.suppress_debug_info = True

# The generator's own model, not LLM_MODEL: Week 1's extractor reads LLM_MODEL,
# and the model that writes the labels shouldn't be the one scored against them.
MODEL = "openai/bedrock/gpt-5.6-sol"
REASONING_EFFORT = "medium"
LIMIT = None  # None runs all 50 combinations
PER_COMBO = 3  # rows asked for per call
DEDUPE_THRESHOLD = 0.7  # character 4-gram Jaccard; the run record lists every pair it dropped
SEEDS_FILE = HERE / "seeds.jsonl"
OUT = ROOT / "use_case" / "data" / "synthetic_v1.jsonl"
RAW = OUT.with_name("synthetic_v1.raw.jsonl")  # every parsed row, before dedupe and validation
RUN = OUT.with_name("synthetic_v1.run.json")  # settings and counts, for the datasheet

CFG = bootstrap(start=HERE)
SEEDS = [json.loads(line) for line in SEEDS_FILE.read_text().splitlines() if line.strip()]

# Each example gets its own state, month and vendor initial. Without them every
# call starts from the same defaults (a "Prairie" vendor in "Red Mesa, OK" dated
# 11/05/2026). Seeded by the combination, so a rerun sends the same prompt.
STATES = ["OK", "KS", "NE", "IA", "MO", "TX", "CO", "AR", "NC", "MN", "SD", "IL"]
MONTHS = [f"{name} 2025" for name in ("November", "December")] + [
    f"{name} 2026" for name in month_name[1:11]
]
LETTERS = [letter for letter in ascii_uppercase if letter not in "QXZ"]

# The extraction rules are Week 1's EXTRACTION_PROMPT, imported rather than
# copied, so the labels follow the same rules the extractor is scored against.
PROMPT = """These are documents an accountant dropped in their invoice folder, each with the output the pipeline should return and why:

{examples}

Write {n} NEW examples in the same JSON format. All {n} must match this profile:
{profile}

Give each example its own vendor location, document month and vendor name initial:
{spread}

Format:
- One JSON object per line with the keys "input", "output" and "why". Write newlines inside "input" as \\n.
- "input" is the document's text as extracted from the PDF.
- "output" is {{"status": ..., "errors": [...], "extraction": ...}}.
- "why" is two to four sentences: what makes this document hard, and why the output is right.

Status:
- "ok": errors is [] and extraction is filled in.
- "failed", nothing to extract (no amount due anywhere): extraction is null and errors has one line like "model could not read the document: <what the document is>, no invoice total".
- "failed", reversal (doc_type Invoice with a negative total): extraction is filled in and errors has one line like "negative total <invoice_total> on an Invoice: reversal, enter by hand".
- No other status.

"extraction" is what the pipeline's extractor should return. These are the instructions it is given; label by them exactly:

{extraction_prompt}

Two more labeling rules:
- Every value is what is correct on the document. Where OCR has damaged a field, give the true value, not the misread text.
- "Due on receipt" with no date printed means due_date is null.

Content:
- The bill-to is always the client: a hog producer billed under several entities and cost centers (a parent company, farm entities, sow farms, nurseries, finishing sites), each with its own name and address. Put "Example" in every client name, as the examples do. Vendors are businesses that sell to that client.
- Amounts add up: line items sum to any subtotal, and the subtotal plus tax, fees and freight equals the total. Where a line shows a quantity and a unit price, its amount is their product. Unit prices are realistic for the product.
- Invent every vendor, person, address, phone number, amount, date and reference number; never reuse one from the examples. Make the {n} examples differ from each other in vendor, layout, amounts and dates.

Output only the JSON lines, nothing else."""


def profile(combo: dict) -> str:
    return "\n".join(f"- {axis}: {value}" for axis, value in combo.items())


def spread(combo: dict, n: int) -> str:
    rng = random.Random(profile(combo))
    return "\n".join(
        f"- example {i}: vendor in {rng.choice(STATES)}, dated {rng.choice(MONTHS)}, "
        f"vendor name starting with {rng.choice(LETTERS)}"
        for i in range(1, n + 1)
    )


def build_prompt(seeds: list[dict], combo: dict, n: int) -> str:
    """The text sent to the model for one axis combination."""
    return PROMPT.format(
        examples="\n".join(json.dumps(seed, ensure_ascii=False) for seed in seeds),
        n=n,
        profile=profile(combo),
        spread=spread(combo, n),
        extraction_prompt=EXTRACTION_PROMPT,
    )


class Output(BaseModel):
    status: Literal["ok", "failed"]
    errors: list[str]
    extraction: InvoiceExtraction | None

    @model_validator(mode="after")
    def follows_the_status_rules(self):
        extraction = self.extraction
        if extraction and extraction.doc_type not in ("Invoice", "CreditMemo"):
            raise ValueError(f"doc_type {extraction.doc_type!r}")
        reversal = bool(
            extraction and extraction.doc_type == "Invoice" and extraction.invoice_total < 0
        )
        if self.status == "ok" and (self.errors or extraction is None or reversal):
            raise ValueError("ok needs an extraction, no errors and no negative Invoice")
        if self.status == "failed" and not (self.errors and (extraction is None or reversal)):
            raise ValueError("failed needs errors, and either no extraction or a negative Invoice")
        return self


class Row(BaseModel):
    """One generated row: schema-valid, with a status that follows the app's rules."""

    input: str
    output: Output
    why: str


def load_raw() -> list[dict]:
    return [json.loads(line) for line in RAW.read_text().splitlines()] if RAW.exists() else []


def opening(row: dict) -> str:
    return " ".join(str(row.get("input", "")).split())[:80]


def generate(combos: list[dict]) -> tuple[list[dict], dict]:
    """One call per combination not already in RAW.

    Returns every raw row, and the generation half of the run record.
    """
    stats = CallStats()
    raw = load_raw()
    resumed = len(raw)
    done = {json.dumps(row["_axes"], sort_keys=True) for row in raw}
    unparseable = 0
    dead: list[int] = []
    print(f"model: {MODEL}, reasoning_effort: {REASONING_EFFORT}, {len(combos)} combinations")
    if raw:
        print(f"resuming: {resumed} rows from {len(done)} combinations already in {RAW.name}")
    print()

    for number, combo in enumerate(combos):
        if json.dumps(combo, sort_keys=True) in done:
            continue
        # A dead combination must not end the run, but it has to be counted, or
        # the coverage the axes promise is quietly smaller than it looks.
        try:
            reply = chat(
                CFG,
                build_prompt(SEEDS, combo, PER_COMBO),
                model=MODEL,
                reasoning_effort=REASONING_EFFORT,
                timeout=300,
                stats=stats,
            )
        except RuntimeError as exc:
            dead.append(number)
            print(f"combination {number} failed: {exc}", flush=True)
            continue

        rows = []
        for line in reply.splitlines():
            line = line.strip().strip("`")
            if not line.startswith("{"):
                continue
            try:
                rows.append({**json.loads(line), "_axes": combo})
            except json.JSONDecodeError:
                unparseable += 1
        with RAW.open("a") as f:
            f.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
        raw.extend(rows)
        print(f"[{number + 1}/{len(combos)}] {len(raw)} rows so far", flush=True)

    print(stats)
    generation = {
        "date": date.today().isoformat(),
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "per_combo": PER_COMBO,
        "seeds_sha256": sha256(SEEDS_FILE.read_bytes()).hexdigest(),
        "combinations": len(combos),
        "resumed_rows": resumed,  # rows from an earlier, interrupted run; stats cover this one only
        "unparseable": unparseable,
        "dead_combos": dead,
        "stats": asdict(stats),
    }
    # Written before finish(), so a failure there still leaves the record of what was generated.
    RUN.write_text(json.dumps({"generation": generation}, indent=2) + "\n")
    return raw, generation


def finish(raw: list[dict], combos: list[dict], generation: dict) -> None:
    """Dedupe, validate, save, and write the run record. Makes no model calls."""
    report = SDGReport(
        generated=len(raw),
        unparseable=generation.get("unparseable", 0),
        failed_combos=len(generation.get("dead_combos", [])),
    )
    # Replied, but not one parseable row: as lost to coverage as a dead combination.
    present = [row["_axes"] for row in raw]
    empty = [
        number
        for number, combo in enumerate(combos)
        if combo not in present and number not in generation.get("dead_combos", [])
    ]
    kept, dropped = dedupe(raw, threshold=DEDUPE_THRESHOLD)
    report.after_dedupe = len(kept)
    valid = []
    for row in kept:
        try:
            Row.model_validate(
                {key: value for key, value in row.items() if not key.startswith("_")}
            )
            valid.append(row)
        except ValidationError as exc:
            where = combos.index(row["_axes"]) if row.get("_axes") in combos else "?"
            print(f"invalid, combination {where}: {exc.errors()[0]['msg']}")
    report.valid = len(valid)
    report.leaks = leak_check(SEEDS, valid)
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in valid))

    # Every pair dedupe dropped, closest first: the evidence for the threshold.
    pairs = sorted(
        (
            {
                "score": round(
                    jaccard(
                        shingles(str(row.get("input", ""))), shingles(str(twin.get("input", "")))
                    ),
                    3,
                ),
                "dropped": opening(row),
                "kept": opening(twin),
            }
            for row, twin in dropped
        ),
        key=lambda pair: pair["score"],
        reverse=True,
    )
    for pair in pairs:
        print(f"{pair['score']:.2f}  dropped {pair['dropped']}\n      kept    {pair['kept']}")

    record = {
        "generation": generation,
        "finish": {
            "date": date.today().isoformat(),
            "dedupe_threshold": DEDUPE_THRESHOLD,
            "report": asdict(report),
            "empty_combos": empty,
            "dropped": pairs,
        },
    }
    RUN.write_text(json.dumps(record, indent=2) + "\n")

    print(f"\n{report}")
    print(f"dead combos: {generation.get('dead_combos')}, empty combos: {empty}")
    print(f"possible leaks: {report.leaks}")
    print(f"saved {report.valid} rows to {OUT.relative_to(ROOT)}, run record to {RUN.name}")


if __name__ == "__main__":
    combos = combinations(AXES)[:LIMIT]
    if "--from-raw" in sys.argv[1:]:
        if not RAW.exists():
            sys.exit(f"{RAW} does not exist; run without --from-raw first")
        # Keep the record of the run that generated the rows.
        generation = json.loads(RUN.read_text()).get("generation", {}) if RUN.exists() else {}
        finish(load_raw(), combos, generation)
    else:
        raw, generation = generate(combos)
        finish(raw, combos, generation)
