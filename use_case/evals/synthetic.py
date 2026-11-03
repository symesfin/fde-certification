"""Write synthetic.jsonl: named corruptions of the masked utility goldens.

    uv run python use_case/evals/synthetic.py

Built from `golden.jsonl` (masked), so the file holds no real values. Each line
is one corruption of one bill: {input, original, corrupted, failure_mode, hard}.
`hard` marks corruptions that keep the bill internally consistent, so an
add-up check inside the bill can't see them.
"""

from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _flip(s: str) -> str:
    """Change the last digit before the decimal point (or the last digit, if there is none)."""
    head, dot, tail = s.partition(".")
    i = len(head) - 1
    d = head[i]
    return head[:i] + str((int(d) + 1) % 10) + head[i + 1 :] + dot + tail


def _money(x: Decimal) -> str:
    return str(x.quantize(Decimal("0.01")))


def _rebalance(bill: dict) -> None:
    """Recompute the header from the accounts, so the corruption adds up."""
    cur = sum(Decimal(a["current_charges"]) for a in bill["accounts"])
    bill["current_charges"] = _money(cur)
    bill["total_due"] = _money(cur + Decimal(bill["carried_balance"]) + Decimal(bill["late_fees"]))


def digit_flip_account(b):
    a = b["accounts"][0]
    a["account_number"] = _flip(a["account_number"])


def digit_flip_amount(b):
    a = b["accounts"][0]
    a["current_charges"] = _flip(a["current_charges"])


def amount_off_10pct(b):
    a = b["accounts"][0]
    a["current_charges"] = _money(Decimal(a["current_charges"]) * Decimal("1.1"))
    _rebalance(b)


def dropped_tier(b):
    # failures.md #2: the first 750 kWh tier lost.
    for a in b["accounts"]:
        for u in a["usage"]:
            if u["kind"] == "billed":
                q = u["quantity"]
                u["quantity"] = q - 750 if q > 750 else round(q * 0.9, 1)
                return


def swap_current_carried(b):
    b["current_charges"], b["carried_balance"] = b["carried_balance"], b["current_charges"]


def duplicate_account(b):
    b["accounts"].append(copy.deepcopy(b["accounts"][0]))


def extra_summary(b):
    # Stands in for the client's appended allocation sheet being read as more accounts.
    b["accounts"] += copy.deepcopy(b["accounts"])


MODES = {
    "digit_flip_account": (digit_flip_account, False),
    "digit_flip_amount": (digit_flip_amount, False),
    "amount_off_10pct": (amount_off_10pct, True),
    "dropped_tier": (dropped_tier, False),
    "swap_current_carried": (swap_current_carried, False),
    "duplicate_account": (duplicate_account, False),
    "extra_summary": (extra_summary, False),
}


def build() -> list[dict]:
    goldens = [
        json.loads(line)
        for line in (HERE / "golden.jsonl").read_text().splitlines()
        if line.strip()
    ]
    rows = []
    for g in goldens:
        if g.get("track") != "utility":
            continue
        for mode, (corrupt, hard) in MODES.items():
            bad = copy.deepcopy(g["output"])
            corrupt(bad)
            rows.append(
                {
                    "input": g["input"],
                    "original": g["output"],
                    "corrupted": bad,
                    "failure_mode": mode,
                    "hard": hard,
                }
            )
    return rows


if __name__ == "__main__":
    rows = build()
    (HERE / "synthetic.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"wrote {len(rows)} corruptions to synthetic.jsonl")
