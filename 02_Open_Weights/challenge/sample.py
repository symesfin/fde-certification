"""Pick the rows to read in TC2 Step 3: one valid row per axis combination.

Writes a reading file with each row's invoice text laid out as it would print,
its label and why, and a table to fill in while reading. The seed is fixed, so a
rerun picks the same rows.

    uv run python 02_Open_Weights/challenge/sample.py [rows.jsonl] [out.md]
"""

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from axes import AXES
from helpers.sdg import combinations

DATA = ROOT / "use_case" / "data"
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA / "synthetic_v1.jsonl"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else DATA / "read_50.md"  # gitignored with the data
SEED = 0

CHECKS = """What to check on every row:

- **Labels right?** The total is the amount due, with its printed sign; `doc_type`; the invoice
  number or null; the phone (first non-fax number); invoice date vs due date vs fax date; true
  values under OCR damage; the arithmetic adds up.
- **Would an accountant see this?** Anything the real queue would never send.
- **Leak?** Real names, the client's real entity names, internal number formats, a rare
  category copied rather than generated."""


def short(value: str) -> str:
    """An axis value up to its first colon or semicolon: enough to tell values apart."""
    return value.split(":")[0].split(";")[0].strip()


def main() -> None:
    rows = [json.loads(line) for line in SOURCE.read_text().splitlines() if line.strip()]
    rng = random.Random(SEED)
    picked, missing = [], []
    for index, combo in enumerate(combinations(AXES)):
        # Line numbers in SOURCE, so a removal can name the exact row.
        matches = [line for line, row in enumerate(rows, 1) if row.get("_axes") == combo]
        if matches:
            picked.append((index, rng.choice(matches)))
        else:
            missing.append(index)

    out = [
        "# Step 3 reading sheet",
        "",
        f"{len(picked)} rows from `{SOURCE.name}`, one per axis combination, seed {SEED}. "
        f"**Line** is the row's line in `{SOURCE.name}`.",
    ]
    if missing:
        out.append(f"\n**No rows for combinations {missing}.** Read a row from the closest combination instead, and say so.")
    out += [
        "",
        CHECKS,
        "",
        "| # | Line | Combination | Labels right? | Would an accountant see this? | Leak? | Removed? Why |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for number, (index, line) in enumerate(picked, 1):
        labels = " · ".join(short(value) for value in rows[line - 1]["_axes"].values())
        out.append(f"| {number} | {line} | {index}: {labels} | | | | |")

    for number, (index, line) in enumerate(picked, 1):
        row = rows[line - 1]
        out += ["", "---", "", f"## {number} · line {line} · combination {index}", ""]
        out += [f"**{axis}:** {value}  " for axis, value in row["_axes"].items()]
        out += [
            "",
            "````text",
            str(row.get("input", "")),
            "````",
            "",
            "**Label**",
            "",
            "```json",
            json.dumps(row.get("output"), indent=2, ensure_ascii=False),
            "```",
            "",
            f"**Why:** {row.get('why', '')}",
        ]

    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {len(picked)} rows to {OUT}")
    if missing:
        print(f"no rows for combinations {missing}")


if __name__ == "__main__":
    main()
