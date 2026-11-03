"""Scorers, judge rubric and interval for the utility-bill extraction eval (TC4).

Every scorer has the harness signature `(actual: str, case: dict) -> 0..1`:
`actual` is the extracted bill as JSON text, `case["output"]` is the label.
Money is compared as Decimal, never float. Account numbers are compared on
their digits only.

Each scorer names the `failures.md` line it covers.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation

import numpy as np

Z = Decimal(0)
USAGE_TOLERANCE = Decimal("0.05")  # same as the spike; quantities are whole kWh or gallons to 0.1


# ------------------------------------------------------------------ parsing


def _bill(actual: str) -> dict | None:
    try:
        bill = json.loads(actual)
    except (TypeError, ValueError):
        return None
    return bill if isinstance(bill, dict) and isinstance(bill.get("accounts"), list) else None


def dec(v) -> Decimal:
    """Money as Decimal. Missing is zero, as in the spike's scorer: a blank carried balance means none."""
    if v is None or v == "":
        return Z
    s = str(v).replace("$", "").replace(",", "").strip()
    neg = s.endswith("-") or s.endswith("CR") or (s.startswith("(") and s.endswith(")"))
    s = s.strip("()").removesuffix("CR").rstrip("-").strip()
    try:
        d = Decimal(s)
    except InvalidOperation:
        return Decimal("NaN")
    return -d if neg else d


def acct_key(a) -> str:
    return re.sub(r"\D", "", str(a or ""))


def _keys(bill: dict, truth: dict) -> list[str]:
    """Extracted account keys, one per entry (duplicates kept), mapped onto the label's keys.

    One rule from the spike: a single-account bill with one extracted account
    matches if either number ends with the other, because fuel tickets print
    their number with or without a prefix.
    """
    got = [acct_key(a.get("account_number")) for a in bill["accounts"]]
    true = [acct_key(a["account_number"]) for a in truth["accounts"]]
    if truth.get("kind") == "single" and len(true) == 1 and len(got) == 1:
        g, t = got[0], true[0]
        if g and (g == t or g.endswith(t) or t.endswith(g)):
            return [t]
    return got


def _by_account(bill: dict, truth: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for key, a in zip(_keys(bill, truth), bill["accounts"]):
        out[key].append(a)
    return out


# ------------------------------------------------------------------ scorers


# failures.md #3, #4, #5, #6: misread or invented account, account read twice, accounts lost.
def accounts_exact(actual: str, case: dict) -> float:
    """1 if the extracted accounts are exactly the true ones: none missed, none extra, none repeated."""
    bill, truth = _bill(actual), case["output"]
    if bill is None:
        return 0.0
    true = sorted(acct_key(a["account_number"]) for a in truth["accounts"])
    return float(sorted(_keys(bill, truth)) == true)


# failures.md #7 (one account's sections half kept) and #3 (an account counted twice).
def amounts_exact(actual: str, case: dict) -> float:
    """Share of true accounts whose current charges match to the cent.

    Entries with the same account number are summed first: one account can
    print several service sections, and the account's charge is their sum.
    """
    bill, truth = _bill(actual), case["output"]
    if bill is None:
        return 0.0
    got = _by_account(bill, truth)
    hits = 0
    for a in truth["accounts"]:
        entries = got.get(acct_key(a["account_number"]), [])
        total = sum((dec(e.get("current_charges")) for e in entries), Z)
        hits += bool(entries) and total == dec(a["current_charges"])
    return hits / len(truth["accounts"])


def _usage_hit(true_line: dict, got: list[dict]) -> bool:
    qty = Decimal(str(true_line["quantity"]))
    unit = true_line["unit"]
    lines = [u for u in got if u.get("unit") == unit]
    for u in lines:
        try:
            if abs(Decimal(str(u.get("quantity"))) - qty) <= USAGE_TOLERANCE:
                return True
        except InvalidOperation:
            continue
    # Rate tiers ("750 kWh at one rate, the rest at another") come back as several
    # billed lines; their sum is the billed quantity.
    billed = [u for u in lines if u.get("kind") == "billed"]
    if len(billed) > 1:
        try:
            return abs(sum(Decimal(str(u["quantity"])) for u in billed) - qty) <= USAGE_TOLERANCE
        except (InvalidOperation, KeyError):
            return False
    return False


# failures.md #2 (first rate tier dropped) and #9 (wrong billed quantity).
def usage_match(actual: str, case: dict) -> float:
    """Share of true billed-usage lines found on the right account, within 0.05, rate tiers summed."""
    bill, truth = _bill(actual), case["output"]
    if bill is None:
        return 0.0
    got = _by_account(bill, truth)
    lines = [
        (acct_key(a["account_number"]), u)
        for a in truth["accounts"]
        for u in a["usage"]
        if u["kind"] == "billed"
    ]
    if not lines:
        return 1.0
    hits = 0
    for key, u in lines:
        usage = [x for e in got.get(key, []) for x in (e.get("usage") or [])]
        hits += _usage_hit(u, usage)
    return hits / len(lines)


# failures.md #1 (merged statements: wrong or blank bill totals) and #8 (late fee read as carried).
def header_ok(actual: str, case: dict) -> float:
    """1 if the bill's current charges and carried balance both match the label."""
    bill, truth = _bill(actual), case["output"]
    if bill is None:
        return 0.0
    return float(
        dec(bill.get("current_charges")) == dec(truth["current_charges"])
        and dec(bill.get("carried_balance")) == dec(truth["carried_balance"])
    )


PARTS = {
    "accounts": accounts_exact,
    "amounts": amounts_exact,
    "usage": usage_match,
    "header": header_ok,
}


# Every line of failures.md: the unit FR-11.2 gates on.
def bill_fully_right(actual: str, case: dict) -> float:
    """1 only if every other model-free scorer is 1."""
    return float(all(f(actual, case) == 1.0 for f in PARTS.values()))


# failures.md header line: 17 of 18 failing runs were silently wrong (FR-11.2).
def no_silent_error(actual: str, case: dict) -> float:
    """1 if the bill is fully right, or wrong with at least one failed check; 0 if wrong and unflagged."""
    if bill_fully_right(actual, case) == 1.0:
        return 1.0
    bill = _bill(actual)
    if bill is None:
        return 0.0
    return float(any(c.get("ok") is False for c in bill.get("checks") or []))


SCORERS = {
    **PARTS,
    "fully_right": bill_fully_right,
    "no_silent_error": no_silent_error,
}
HEADLINE = "no_silent_error"


# ------------------------------------------------------------------ judge

# failures.md #3, #4, #7: wrong accounts or wrong per-account charges.
# Narrow and binary on purpose: one checkable property, so a 0 and a 1 mean something.
JUDGE_RUBRIC = """You compare two extractions of the same utility bill.

Bill id: {input}

Reference extraction (checked by hand):
{expected}

Extraction to check:
{actual}

Question: do the two list exactly the same accounts, each with the same current
charges to the cent? Compare account numbers digit by digit and amounts digit by
digit. Ignore formatting, letter case, number formatting (commas, trailing
zeros), field order and every other field. An account missing, an extra or
repeated account, one changed digit in an account number, or one changed digit in
an amount means 0. If the text to check is not a bill extraction, the answer is 0.

Example of a 1: reference {{"accounts": [{{"account_number": "1234", "current_charges": "10.50"}}]}},
extraction {{"accounts": [{{"account_number": "1234", "current_charges": 10.5, "usage": []}}]}}.
Example of a 0: same reference, extraction {{"accounts": [{{"account_number": "1234", "current_charges": "10.60"}}]}}.

Reply with JSON only: {{"score": 0 or 1, "why": "<one sentence>"}}"""

# Not Gemini: the extractor shouldn't grade itself. A gateway model from .env.
JUDGE_MODEL = None  # None = LLM_MODEL from .env


def make_judge(cfg, stats=None):
    from helpers.judge import Judge

    return Judge(cfg, rubric=JUDGE_RUBRIC, model=JUDGE_MODEL, stats=stats)


def judge_view(case: dict) -> dict:
    """The label as the judge sees it: account numbers and current charges only.

    The full label carries usage, pages and notes the rubric says to ignore;
    sending only what is compared keeps prompts short on the 37-account bills.
    """
    out = case["output"]
    return {
        **case,
        "output": json.dumps(
            {
                "accounts": [
                    {"account_number": a["account_number"], "current_charges": a["current_charges"]}
                    for a in out["accounts"]
                ]
            }
        ),
    }


# ------------------------------------------------------------------ interval


def bootstrap_ci(scores, n_resamples: int = 5000, level: float = 0.95, seed: int = 0):
    """Session 7's percentile bootstrap: resample the cases, take the spread of the means."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(scores, dtype=float)
    means = arr[rng.integers(0, len(arr), size=(n_resamples, len(arr)))].mean(axis=1)
    lo, hi = np.percentile(means, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return float(arr.mean()), float(lo), float(hi)


def wilson_ci(successes: int, n: int, z: float = 1.96):
    """Wilson score interval for a pass rate.

    Needed because the bootstrap collapses to [1, 1] when every case passes:
    resampling seventeen 1s only ever gives 1. Wilson still says how low the
    true rate could be after n passes in a row.
    """
    p = successes / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)
