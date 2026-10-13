"""Synthetic data generation, and the deduplication that decides its real size.

Tier 2. Declare `litellm` in your notebook's PEP 723 block.

Week 2 Session 2 builds this from scratch. This is the packaged version, and it
keeps the two things students most often drop:

**The axes are the coverage.** Generating "200 more like these" gives 200
paraphrases of five things. Generating across named axes gives you a dataset
whose blind spots you can describe — which is the only kind worth having.

**The honest count.** The size of your dataset is not how many rows you
generated. It is how many survived deduplication *and* schema validation. That
number is usually far smaller, and quoting the first one is how teams come to
believe they tested something they did not.
"""

from __future__ import annotations

import itertools
import json
import re
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

GENERATION_PROMPT = """Here are real examples of inputs to a system, with the outputs a
domain expert accepted:

{examples}

Generate {n} NEW examples in the same JSON format, one per line.
They must match this profile:
{profile}

Rules:
- Invent all names, identifiers, and companies. Never reuse any from the examples.
- Vary the substance, not just the wording.
- If the profile says the system should decline, the output should say so plainly.
- Output only JSON lines, nothing else."""


# ------------------------------------------------------------------ dedupe


def shingles(text: str, n: int = 4) -> set[str]:
    """Character n-grams. Cheap, needs no model, and catches the near-duplicates
    exact matching misses: reordered clauses, changed names, different
    punctuation."""
    flat = " ".join(str(text).lower().split())
    return {flat[start : start + n] for start in range(max(len(flat) - n + 1, 1))}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def dedupe(rows: Sequence[dict], *, threshold: float = 0.7, key: str = "input"):
    """Keep a row only if it is unlike everything kept so far.

    Returns `(kept, dropped)` where dropped is `[(row, the_row_it_matched)]` —
    look at that list before trusting the threshold. Too high keeps
    paraphrases; too low discards genuinely different rows that share
    vocabulary.

    Character n-grams will NOT catch "floor 3" vs "floor three". Embeddings
    would; they arrive in Week 3, and the upgrade is deliberate.
    """
    kept: list[dict] = []
    kept_shingles: list[set] = []
    dropped: list[tuple] = []
    for row in rows:
        sig = shingles(str(row.get(key, "")))
        twin = next(
            (index for index, other in enumerate(kept_shingles) if jaccard(sig, other) >= threshold),
            None,
        )
        if twin is None:
            kept.append(row)
            kept_shingles.append(sig)
        else:
            dropped.append((row, kept[twin]))
    return kept, dropped


# ------------------------------------------------------------- leak checking


def leak_check(seeds: Sequence[dict], generated: Sequence[dict]) -> list[str]:
    """Distinctive strings from the seeds that survived into the output.

    Catches names, companies, and identifiers. It cannot catch a distinctive
    scenario, an unusual document structure, or a category only one of your
    clients has — so a clean result is not a clearance. Read a sample yourself.
    """
    blob = " ".join(
        f"{row.get('input', '')} {row.get('output', '')}" for row in generated
    ).lower()
    found: list[str] = []
    for seed in seeds:
        text = f"{seed.get('input', '')} {seed.get('output', '')}"
        candidates = set(
            re.findall(r"\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,})+\b", text)
        )
        candidates |= set(re.findall(r"\b[\w-]*\d[\w-]*\b", text))
        for candidate in candidates:
            if len(candidate) > 3 and candidate.lower() in blob and candidate not in found:
                found.append(candidate)
    return found


# ---------------------------------------------------------------- generation


@dataclass
class SDGReport:
    """The honest numbers. Report all four, not just the first."""

    generated: int = 0
    unparseable: int = 0
    failed_combos: int = 0
    after_dedupe: int = 0
    valid: int = 0
    leaks: list = field(default_factory=list)

    @property
    def variety(self) -> float:
        return self.after_dedupe / self.generated if self.generated else 0.0

    def __str__(self) -> str:
        return (
            f"generated {self.generated} ({self.unparseable} unparseable) → "
            f"{self.after_dedupe} distinct ({self.variety:.0%}) → "
            f"{self.valid} schema-valid"
            + (f" · ⚠️ {self.failed_combos} combos failed" if self.failed_combos else "")
            + (f" · ⚠️ {len(self.leaks)} possible leaks" if self.leaks else "")
        )


def combinations(axes: dict[str, Sequence[str]]) -> list[dict]:
    """Every point in the axis space. Name your axes; the cross-product is free."""
    return [dict(zip(axes, values)) for values in itertools.product(*axes.values())]


def generate(
    cfg,
    seeds: Sequence[dict],
    axes: dict[str, Sequence[str]],
    *,
    per_combo: int = 3,
    limit: int | None = None,
    validate: Callable[[dict], bool] | None = None,
    dedupe_threshold: float = 0.7,
    progress: Callable[[int, int], None] | None = None,
    max_retries: int = 3,
    timeout: float = 120.0,
    stats=None,
) -> tuple[list[dict], SDGReport]:
    """Generate across the axis space, dedupe, validate, and report honestly.

    `validate` is your pydantic model's check — anything that raises or returns
    False drops the row. Most generated data dies here, and that is the system
    working.
    """
    from .llm import chat

    combos = combinations(axes)
    if limit:
        combos = combos[:limit]

    shown = "\n".join(json.dumps(seed, ensure_ascii=False) for seed in seeds[:3])
    report = SDGReport()
    raw: list[dict] = []

    for combo_number, combo in enumerate(combos, 1):
        prompt = GENERATION_PROMPT.format(
            examples=shown,
            n=per_combo,
            profile="\n".join(f"- {axis}: {value}" for axis, value in combo.items()),
        )
        # One dead combination should not kill a generation run that has already
        # produced hundreds of rows — but it must be *counted*, or the coverage
        # you think your axes give you is quietly smaller than you believe.
        try:
            reply = chat(
                cfg, prompt, timeout=timeout, max_retries=max_retries, stats=stats
            )
        except RuntimeError:
            reply = ""
            report.failed_combos += 1

        for line in reply.splitlines():
            line = line.strip().strip("`")
            if not line.startswith("{"):
                continue
            try:
                raw.append({**json.loads(line), "_axes": combo})
            except json.JSONDecodeError:
                report.unparseable += 1
        if progress:
            progress(combo_number, len(combos))

    report.generated = len(raw)
    kept, dropped = dedupe(raw, threshold=dedupe_threshold)
    report.after_dedupe = len(kept)

    if validate:
        valid = []
        for row in kept:
            payload = {key: value for key, value in row.items() if not key.startswith("_")}
            try:
                if validate(payload) is not False:
                    valid.append(row)
            except Exception:
                pass
        kept = valid
    report.valid = len(kept)
    report.leaks = leak_check(seeds, kept)
    return kept, report
