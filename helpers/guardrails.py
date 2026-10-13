"""A guardrail ladder you can measure, and therefore defend.

Tier 2 by convention. Imports nothing heavier than the standard library; the
rungs you pass in may import whatever they like.

Week 6 Session 12 builds the ladder from scratch — logit masking, regex, a
trained classifier, an LLM judge, a policy layer — and the point of building all
five is that they cost wildly different amounts and catch different things. This
packages the part that makes it deployable rather than demonstrable.

**Order is the design.** Rungs run cheapest-first and the ladder short-circuits
on the first block, so the expensive judge only ever sees what the free checks
let through. Put the LLM judge first and you have paid for it on every single
request, including the 99% a regex would have cleared for nothing.

**The number that decides whether it ships is the false-positive rate.** A
guardrail that catches every attack and also blocks four percent of legitimate
traffic will be switched off within a month, and then you have no guardrail at
all. Catching attacks is the easy half. `evaluate()` therefore refuses to report
coverage without also reporting what the ladder did to your known-good cases —
your Week 4 golden set is exactly the right input.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Sequence

# A rung returns True/False, or a dict with "allowed", or a Verdict-ish object.
Rung = Callable[[str], object]


def _allowed(result: object) -> tuple[bool, str]:
    """Normalise whatever a rung returned into (allowed, reason).

    Deliberately permissive about the shape, because the notebook builds five
    rungs with five different natural return types and forcing one on them
    would be a worse lesson than accepting all of them.
    """
    if isinstance(result, bool):
        return result, ""
    if isinstance(result, dict):
        reason = str(result.get("reason") or result.get("raw") or "")
        if "allowed" in result:
            return bool(result["allowed"]), reason
        if "blocked" in result:
            return not bool(result["blocked"]), reason
        return True, reason
    allowed = getattr(result, "allowed", None)
    if allowed is not None:
        return bool(allowed), str(getattr(result, "reason", ""))
    # A rung that returned nothing meaningful must not silently allow.
    raise TypeError(
        f"a guardrail rung returned {type(result).__name__}, which cannot be read "
        f"as a decision. Return a bool, or a dict with 'allowed'. Guessing here "
        f"would mean failing open, and a guardrail that fails open is decoration."
    )


@dataclass
class Verdict:
    allowed: bool
    rung: str | None = None          # which rung blocked it, if any
    reason: str = ""
    seconds: float = 0.0
    ran: list = field(default_factory=list)   # rungs actually executed


@dataclass
class LadderReport:
    """Coverage, false positives, and what each rung cost — all three or none."""

    caught: float = 0.0              # share of unsafe inputs blocked
    false_positive: float = 0.0      # share of safe inputs blocked  <- the killer
    n_safe: int = 0
    n_unsafe: int = 0
    by_rung: dict = field(default_factory=dict)     # rung -> times it blocked
    reached: dict = field(default_factory=dict)     # rung -> times it ran
    seconds_per_call: float = 0.0
    missed: list = field(default_factory=list)      # unsafe inputs that got through
    blocked_safe: list = field(default_factory=list)  # safe inputs wrongly blocked

    def __str__(self) -> str:
        return (
            f"caught {self.caught:.0%} of {self.n_unsafe} attacks · "
            f"false-positive {self.false_positive:.0%} of {self.n_safe} legitimate · "
            f"{self.seconds_per_call * 1000:.0f}ms per call"
        )

    @property
    def deployable(self) -> bool:
        """Not a law, a starting point: a guardrail that blocks more than 1% of
        real traffic gets disabled by whoever is on support that week."""
        return self.false_positive <= 0.01


class Ladder:
    """Cheapest check first, short-circuit on the first block.

        ladder = Ladder([("regex", rule_check), ("classifier", classify),
                         ("judge", judge_check)])
        verdict = ladder.check(user_input)
        print(ladder.evaluate(safe=golden_inputs, unsafe=known_attacks))
    """

    def __init__(self, rungs: Sequence[tuple[str, Rung]]):
        if not rungs:
            raise ValueError("a ladder with no rungs allows everything")
        self.rungs = list(rungs)

    def check(self, text: str) -> Verdict:
        started = time.perf_counter()
        ran: list[str] = []
        for name, rung in self.rungs:
            ran.append(name)
            try:
                ok, reason = _allowed(rung(text))
            except TypeError:
                raise
            except Exception as exc:
                # A rung that errors must FAIL CLOSED. The alternative is that a
                # flaky classifier quietly turns your guardrail off, and nothing
                # in the logs says so.
                return Verdict(
                    allowed=False,
                    rung=name,
                    reason=f"{name} errored, failing closed: {exc}",
                    seconds=time.perf_counter() - started,
                    ran=ran,
                )
            if not ok:
                return Verdict(False, name, reason,
                               time.perf_counter() - started, ran)
        return Verdict(True, None, "", time.perf_counter() - started, ran)

    def evaluate(self, *, safe: Sequence[str], unsafe: Sequence[str]) -> LadderReport:
        """Run both sets. Reporting one without the other is how guardrails ship
        broken — 100% coverage is trivial if you are allowed to block everything.
        """
        if not safe:
            raise ValueError(
                "evaluate() needs known-good inputs too. Coverage without a "
                "false-positive rate is not a result: a rung that blocks every "
                "request scores 100%. Pass your Week 4 golden set as `safe`."
            )
        report = LadderReport(n_safe=len(safe), n_unsafe=len(unsafe))
        total = 0.0

        for text in unsafe:
            verdict = self.check(text)
            total += verdict.seconds
            for name in verdict.ran:
                report.reached[name] = report.reached.get(name, 0) + 1
            if not verdict.allowed:
                report.by_rung[verdict.rung] = report.by_rung.get(verdict.rung, 0) + 1
            else:
                report.missed.append(text[:120])

        for text in safe:
            verdict = self.check(text)
            total += verdict.seconds
            for name in verdict.ran:
                report.reached[name] = report.reached.get(name, 0) + 1
            if not verdict.allowed:
                report.blocked_safe.append({"input": text[:120], "rung": verdict.rung,
                                            "reason": verdict.reason[:120]})

        case_count = len(safe) + len(unsafe)
        report.caught = (
            (len(unsafe) - len(report.missed)) / len(unsafe) if unsafe else 0.0
        )
        report.false_positive = len(report.blocked_safe) / len(safe)
        report.seconds_per_call = total / case_count if case_count else 0.0
        return report


def as_scorer(ladder: Ladder, *, expect_blocked: bool = True):
    """Adapt a ladder to the Week 4 harness signature `(actual, case) -> float`.

    This is how a Week 6 attack becomes a permanent regression case rather than
    a screenshot: add the attack to your golden set, score it with this, and
    Week 8's model swap is checked against it automatically.
    """

    def scorer(actual: str, case: dict) -> float:
        blocked = not ladder.check(case.get("input", "")).allowed
        return 1.0 if blocked == expect_blocked else 0.0

    return scorer
