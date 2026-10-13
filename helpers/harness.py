"""Eval runs you can persist, re-run, and compare — the referee for Weeks 5-8.

Tier 2 by convention (not re-exported from `helpers/__init__`), though it
imports nothing heavier than the standard library, so it is safe anywhere.

Week 4 Session 1 builds `run_eval` and `report` from scratch, and that is the
lesson. This is what those become once *other weeks* have to trust the number.

The problem it solves is stated in TC4 and then left manual: "record the
baseline number in `use_case/decisions.md`." A number typed into prose cannot be
compared by anything, drifts the moment the case set changes, and quietly
becomes a claim rather than a measurement. TC8 — replace the closed model with a
fine-tuned open one and **pass the same harness** — is unfulfillable if the
baseline is a sentence someone wrote in week four.

So a run is an artifact:

    report = run(cases, my_system, SCORERS, name="baseline")
    save(report, CFG.use_case / "evals" / "baseline.json")

    # ... five weeks later, a different model ...
    candidate = run(cases, new_system, SCORERS, name="finetuned")
    print(compare(load(path), candidate))

**The comparison refuses when the case sets differ.** This is the whole point.
0.94 on the twelve cases you had in Week 4 versus 0.91 on the sixty you have by
Week 8 is not a regression, and treating it as one — or worse, treating 0.94 on
three cases as a win over 0.91 on sixty — is the most common way eval numbers
come to mean nothing. Every report carries a fingerprint of the cases and
scorers that produced it, and `compare()` will not silently cross that line.
"""

from __future__ import annotations

import hashlib
import json
import time
import traceback
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Mapping, Sequence

Scorer = Callable[[str, dict], float]


def fingerprint(cases: Sequence[dict], scorers: Mapping[str, Scorer]) -> str:
    """Identity of *what was measured*, so two runs can be compared honestly.

    Covers the cases' inputs and expected outputs plus the scorer names. It
    deliberately does not cover the system under test — changing that is the
    entire point of comparing.
    """
    payload = json.dumps(
        {
            "cases": [
                {"input": case.get("input"), "output": case.get("output")} for case in cases
            ],
            "scorers": sorted(scorers),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class Result:
    """One case, one system, every scorer's verdict."""

    index: int
    input: str
    expected: str
    actual: str
    scores: dict = field(default_factory=dict)
    error: str | None = None
    seconds: float = 0.0

    @property
    def mean(self) -> float:
        return sum(self.scores.values()) / len(self.scores) if self.scores else 0.0


@dataclass
class RunReport:
    """A run, as something you can write to disk and argue with later."""

    name: str
    fingerprint: str
    n: int = 0
    means: dict = field(default_factory=dict)
    errors: int = 0
    seconds: float = 0.0
    meta: dict = field(default_factory=dict)
    results: list = field(default_factory=list)

    @property
    def mean(self) -> float:
        return sum(self.means.values()) / len(self.means) if self.means else 0.0

    def __str__(self) -> str:
        per = "  ".join(f"{key} {value:.3f}" for key, value in sorted(self.means.items()))
        tail = f"  · ⚠️ {self.errors} errored" if self.errors else ""
        return f"{self.name}: n={self.n}  mean {self.mean:.3f}  [{per}]{tail}"


def run(
    cases: Sequence[dict],
    system: Callable[[str], str],
    scorers: Mapping[str, Scorer],
    *,
    name: str = "run",
    meta: dict | None = None,
    progress: Callable[[int, int], None] | None = None,
    keep_results: bool = True,
) -> RunReport:
    """Run every case through `system`, score it, and report honestly.

    **A case that raises does not stop the run and does not disappear.** It is
    recorded with its traceback and scored zero, because the alternative —
    letting the exception propagate — means one malformed row hides the other
    fifty-nine, and skipping it silently inflates every average you report.
    """
    if not cases:
        raise ValueError(
            "No cases to run. This is almost always a golden file that was never "
            "filled in, or a path pointing somewhere else — check "
            "use_case/evals/golden.jsonl before trusting an empty pass."
        )

    report = RunReport(
        name=name,
        fingerprint=fingerprint(cases, scorers),
        meta={"scorers": sorted(scorers), **(meta or {})},
    )
    totals: dict[str, float] = {label: 0.0 for label in scorers}
    started = time.perf_counter()

    for index, case in enumerate(cases):
        case_started = time.perf_counter()
        actual, error = "", None
        try:
            actual = system(case.get("input", "")) or ""
        except Exception:
            error = traceback.format_exc(limit=3)
            report.errors += 1

        result = Result(
            index=index,
            input=str(case.get("input", ""))[:2000],
            expected=str(case.get("output", ""))[:2000],
            actual=str(actual)[:2000],
            error=error,
            seconds=time.perf_counter() - case_started,
        )
        for label, scorer in scorers.items():
            try:
                value = 0.0 if error else float(scorer(actual, case))
            except Exception:
                # A scorer that blows up scores zero. It never scores "skip" —
                # a scorer you cannot run is a test you did not pass.
                value = 0.0
            value = max(0.0, min(1.0, value))
            result.scores[label] = value
            totals[label] += value

        if keep_results:
            report.results.append(result)
        if progress:
            progress(index + 1, len(cases))

    report.n = len(cases)
    report.seconds = time.perf_counter() - started
    report.means = {label: totals[label] / report.n for label in scorers}
    return report


# ------------------------------------------------------------------ persistence


def save(report: RunReport, path: str | Path) -> Path:
    """Write the run as JSON. Commit it — that is what makes it a baseline."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    payload["results"] = [asdict(result) if not isinstance(result, dict) else result
                          for result in report.results]
    target.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def load(path: str | Path) -> RunReport:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    results = [Result(**row) for row in raw.pop("results", [])]
    return RunReport(**raw, results=results)


# ------------------------------------------------------------------ comparison


@dataclass
class Comparison:
    """Did it get better, and are we even allowed to ask?"""

    baseline: str
    candidate: str
    comparable: bool
    deltas: dict = field(default_factory=dict)
    regressions: list = field(default_factory=list)
    improvements: list = field(default_factory=list)
    reason: str = ""

    @property
    def passed(self) -> bool:
        return self.comparable and not self.regressions

    def __str__(self) -> str:
        if not self.comparable:
            return f"NOT COMPARABLE: {self.reason}"
        rows = "  ".join(f"{key} {value:+.3f}" for key, value in sorted(self.deltas.items()))
        verdict = "PASS" if self.passed else "REGRESSION"
        return f"{verdict}  {self.baseline} → {self.candidate}  [{rows}]"


def compare(
    baseline: RunReport,
    candidate: RunReport,
    *,
    tolerance: float = 0.02,
    require_same_cases: bool = True,
) -> Comparison:
    """Per-scorer deltas, and a verdict you can gate a merge on.

    `tolerance` is the drop we are willing to call noise. It is not zero, and it
    should not be: an LLM-judged score moves a little between runs even with
    nothing changed, and a gate that fires on every such wobble gets disabled
    within a fortnight, which is worse than having no gate.

    `require_same_cases=False` exists for the one legitimate case — you grew the
    suite on purpose and want to see the numbers side by side — and it labels the
    result rather than pretending the comparison is clean.
    """
    cmp = Comparison(baseline=baseline.name, candidate=candidate.name, comparable=True)

    if require_same_cases and baseline.fingerprint != candidate.fingerprint:
        cmp.comparable = False
        cmp.reason = (
            f"different cases or scorers (baseline {baseline.fingerprint} vs "
            f"candidate {candidate.fingerprint}; n={baseline.n} vs {candidate.n}). "
            f"Re-run the baseline against the current suite, or pass "
            f"require_same_cases=False if you grew it deliberately — but do not "
            f"report the two numbers as though one beat the other."
        )
        return cmp

    shared = sorted(set(baseline.means) & set(candidate.means))
    missing = sorted(set(baseline.means) ^ set(candidate.means))
    if not shared:
        cmp.comparable = False
        cmp.reason = "no scorers in common"
        return cmp
    if missing:
        cmp.reason = f"note: scorers only on one side, ignored: {', '.join(missing)}"

    for key in shared:
        delta = candidate.means[key] - baseline.means[key]
        cmp.deltas[key] = delta
        if delta < -tolerance:
            cmp.regressions.append(key)
        elif delta > tolerance:
            cmp.improvements.append(key)
    return cmp


def gate(report: RunReport, *, minimum: float = 0.0, baseline: RunReport | None = None,
         tolerance: float = 0.02) -> tuple[bool, str]:
    """One boolean for CI, and a sentence explaining it.

        ok, why = gate(report, minimum=0.7, baseline=load("baseline.json"))
        if not ok:
            raise SystemExit(why)
    """
    if report.errors:
        return False, f"{report.errors} of {report.n} cases raised — fix those first"
    if report.mean < minimum:
        return False, f"mean {report.mean:.3f} is below the floor of {minimum:.3f}"
    if baseline is not None:
        cmp = compare(baseline, report, tolerance=tolerance)
        if not cmp.comparable:
            return False, str(cmp)
        if cmp.regressions:
            return False, f"regressed on {', '.join(cmp.regressions)} — {cmp}"
    return True, f"{report} — passed"
