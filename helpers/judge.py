"""LLM-as-a-judge, with the calibration step attached.

Tier 2. Declare `litellm` in your notebook's PEP 723 block.

Week 4 Session 1 builds a judge from scratch, and then makes the point that
matters: **an uncalibrated judge is worse than no judge**, because it produces a
number and numbers end conversations. This is that judge, packaged, with the
calibration impossible to skip — `Judge.score()` refuses to run until you have
called `calibrate()` and it passed.

That refusal is the whole design. Everything else here is plumbing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable, Sequence

DEFAULT_RUBRIC = """You are scoring one answer against a reference.

Question:
{input}

Reference answer (written by a domain expert):
{expected}

Answer to score:
{actual}

Score 0 to 1 on whether the answer conveys the same substance as the reference.
Differences in wording, length, or style do not matter. Missing or contradicting
a fact does.

Reply with JSON only: {{"score": <0-1>, "why": "<one sentence>"}}"""


def parse_json(text: str) -> dict | None:
    """Pull the first JSON object out of a model reply.

    Balanced-brace scan rather than a regex, because models wrap JSON in prose,
    in fences, and — with reasoning models — after a paragraph of thinking that
    may itself contain braces.
    """
    if not text:
        return None
    depth = 0
    start = -1
    in_string = False
    escape = False
    for position, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 0:
                start = position
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start : position + 1])
                except json.JSONDecodeError:
                    start = -1      # keep scanning for a later, valid object
    return None


@dataclass
class Calibration:
    """Evidence that the judge can tell good from bad. Report this, always."""

    accepted: float = 0.0
    wrong: float = 0.0
    n: int = 0
    passed: bool = False
    detail: list = field(default_factory=list)

    @property
    def separation(self) -> float:
        return self.accepted - self.wrong

    def __str__(self) -> str:
        verdict = "USABLE" if self.passed else "DO NOT TRUST"
        return (
            f"{verdict}: accepted {self.accepted:.2f} (want >0.8), "
            f"wrong {self.wrong:.2f} (want <0.3), "
            f"separation {self.separation:.2f}, n={self.n}"
        )


class Judge:
    """A scorer you are not allowed to trust until it has proved itself.

        judge = Judge(CFG)
        print(judge.calibrate(goldens))     # must pass
        score = judge.score(actual, case)
    """

    def __init__(self, cfg, *, rubric: str = DEFAULT_RUBRIC, max_retries: int = 3,
                 timeout: float = 120.0, model: str | None = None,
                 stats=None):
        self.cfg = cfg
        self.rubric = rubric
        self.max_retries = max_retries
        self.timeout = timeout
        # Grading a suite is the easiest place in the course to spend real money
        # without noticing. Pass a CallStats in and you can see what it cost.
        self.stats = stats
        # A judge should not be the model under test. Allow an override so you
        # can grade with something other than what produced the answer.
        self.model = model
        self.calibration: Calibration | None = None

    def _kwargs(self) -> dict:
        kw = dict(self.cfg.kwargs())
        if self.model:
            kw["model"] = self.model
        return kw

    def _ask(self, prompt: str) -> str:
        # Shared with every other model call in the repo: explicit timeout, and
        # retries only for failures a retry can fix. See helpers/llm.py.
        from .llm import chat

        kw = self._kwargs()
        return chat(
            self.cfg,
            prompt,
            model=kw.get("model"),
            timeout=self.timeout,
            max_retries=self.max_retries,
            stats=self.stats,
        )

    def _raw_score(self, actual: str, case: dict) -> float:
        reply = self._ask(
            self.rubric.format(
                input=case.get("input", ""),
                expected=case.get("output", ""),
                actual=actual,
            )
        )
        parsed = parse_json(reply)
        if not parsed or "score" not in parsed:
            # An unparseable judgement is a FAILED judgement, never a pass.
            return 0.0
        try:
            return max(0.0, min(1.0, float(parsed["score"])))
        except (TypeError, ValueError):
            return 0.0

    def calibrate(self, goldens: Sequence[dict], *,
                  wrong_answer: str = "The answer is 42.",
                  min_accepted: float = 0.8, max_wrong: float = 0.3) -> Calibration:
        """Score known-good and known-bad answers. Must pass before `score()` works.

        `goldens` are your hand-written examples — the ones a human accepted.
        The judge should score those high and an obviously wrong answer low. If
        it cannot separate them, every number it later produces is noise.
        """
        detail = []
        for case in goldens:
            good = self._raw_score(case.get("output", ""), case)
            bad = self._raw_score(wrong_answer, case)
            detail.append({"case": str(case.get("input", ""))[:48],
                           "accepted": round(good, 3), "wrong": round(bad, 3)})

        divisor = len(detail) or 1
        cal = Calibration(
            accepted=sum(row["accepted"] for row in detail) / divisor,
            wrong=sum(row["wrong"] for row in detail) / divisor,
            n=len(detail),
            detail=detail,
        )
        cal.passed = cal.accepted > min_accepted and cal.wrong < max_wrong
        self.calibration = cal
        return cal

    def score(self, actual: str, case: dict) -> float:
        if self.calibration is None:
            raise RuntimeError(
                "Judge.score() called before calibrate(). An uncalibrated judge "
                "produces a number nobody should act on — run calibrate(goldens) "
                "first and check that it passed."
            )
        if not self.calibration.passed:
            raise RuntimeError(
                f"Judge failed calibration ({self.calibration}). Fix the rubric — "
                "narrow the question, add examples of a 0 and a 1, or ask for a "
                "binary decision — and re-calibrate before scoring anything."
            )
        return self._raw_score(actual, case)

    def as_scorer(self) -> Callable[[str, dict], float]:
        """Adapt to the Week 4 harness signature `(actual, case) -> float`."""
        return self.score
