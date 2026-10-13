"""Spans, the four metrics, and instrumentation that cannot take your app down.

Tier 2 by convention. Standard library only.

Week 10 Session 1 builds `span()` from scratch in about fifteen lines, and that
is the right way to meet it — a context manager with a `try/finally` is genuinely
all a tracer is. This is the version the student's *application* imports, so the
marimo notebook that taught it can then be pointed at real traffic and become the
observability console rather than a simulation of one.

Three things it does that the fifteen-line version does not:

**It never raises into your request path.** A tracer that can throw is a new
failure mode you added voluntarily, in the name of reliability. Every recording
path here is wrapped; if tracing breaks, the request still completes and the
tracer reports its own error count. Instrumentation that can take down the thing
it observes is worse than no instrumentation.

**It tracks parents without you passing them.** Manual parent IDs are fine for
one demo and wrong by the third nested call, and the bug is invisible — you get
a flat trace that looks plausible.

**It counts tokens and money alongside latency.** A latency trace tells you the
system is slow. A cost trace tells you why the project is being cancelled, and
those are different conversations. `helpers.llm.CallStats` drops straight in.
"""

from __future__ import annotations

import contextvars
import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterator, Sequence

_current: contextvars.ContextVar = contextvars.ContextVar("fde_span", default=None)


@dataclass
class Span:
    id: str
    name: str
    parent: str | None = None
    ms: float = 0.0
    status: str = "ok"
    error: str | None = None
    attributes: dict = field(default_factory=dict)

    @property
    def cost(self) -> float:
        return float(self.attributes.get("cost_usd") or 0.0)

    @property
    def tokens(self) -> int:
        return int(self.attributes.get("tokens") or 0)


def _blob(attributes: dict) -> str:
    """Attributes as lowercase text, never raising. Callers put arbitrary objects
    in here and a metrics call must not be the thing that fails a request."""
    try:
        return json.dumps(attributes, default=str).lower()
    except Exception:
        try:
            return " ".join(f"{key}={value!s}" for key, value in attributes.items()).lower()
        except Exception:
            return ""


def percentile(values: Sequence[float], p: float) -> float:
    """Nearest-rank percentile. No numpy, because this runs in the request path.

    p50 and p95 rather than a mean: a mean latency hides the tail entirely, and
    the tail is what users describe when they say the system is slow.
    """
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, int(round(p / 100 * len(ordered) + 0.5)) - 1))
    return ordered[rank]


class Tracer:
    """Collects spans. Safe to leave switched on.

        tracer = Tracer()
        with tracer.span("request", user="a.patel") as root:
            with tracer.span("retrieve", k=5):
                ...
        print(tracer.summary())
    """

    def __init__(self, *, capacity: int = 10_000):
        # Bounded on purpose. An unbounded list in a long-running process is a
        # memory leak with a dashboard attached.
        self.capacity = capacity
        self.spans: list[Span] = []
        self.dropped = 0
        self.internal_errors = 0

    # -- recording ---------------------------------------------------------

    @contextmanager
    def span(self, name: str, **attributes) -> Iterator[Span]:
        """Time a block and record it, whether or not it succeeded."""
        try:
            record = Span(
                id=uuid.uuid4().hex[:12],
                name=name,
                parent=_current.get(),
                attributes=dict(attributes),
            )
            token = _current.set(record.id)
        except Exception:
            # Even setting up the span must not break the caller.
            self.internal_errors += 1
            yield Span(id="", name=name)
            return

        started = time.perf_counter()
        try:
            yield record
        except Exception as exc:
            record.status = "error"
            record.error = f"{type(exc).__name__}: {exc}"[:300]
            raise
        finally:
            # The finally is the whole point: a span that only records on the
            # happy path tells you nothing about the requests you care about.
            try:
                record.ms = (time.perf_counter() - started) * 1000
                _current.reset(token)
                self._append(record)
            except Exception:
                self.internal_errors += 1

    def _append(self, record: Span) -> None:
        if len(self.spans) >= self.capacity:
            self.dropped += 1
            self.spans.pop(0)
        self.spans.append(record)

    def record_usage(self, span: Span, stats, *, usd_per_1k_prompt: float = 0.0,
                     usd_per_1k_completion: float = 0.0) -> None:
        """Attach `helpers.llm.CallStats` to a span, in tokens and in money."""
        try:
            span.attributes["tokens"] = stats.total_tokens
            span.attributes["cost_usd"] = round(
                stats.prompt_tokens / 1000 * usd_per_1k_prompt
                + stats.completion_tokens / 1000 * usd_per_1k_completion,
                6,
            )
            span.attributes["llm_calls"] = stats.calls
            if stats.retries:
                span.attributes["retries"] = stats.retries
        except Exception:
            self.internal_errors += 1

    # -- reading -----------------------------------------------------------

    def roots(self) -> list[Span]:
        return [span for span in self.spans if span.parent is None]

    def summary(self, *, refusal_marker: str = "refused") -> dict:
        """The four numbers worth alerting on.

        Latency and cost per *request* — meaning root spans — because per-span
        averages are dominated by whichever span you happen to emit most.
        """
        roots = self.roots()
        latencies = [span.ms for span in roots]
        by_root_cost: list[float] = []
        for root in roots:
            kin = [root] + self._descendants(root.id)
            by_root_cost.append(sum(span.cost for span in kin))

        errors = sum(1 for span in roots if span.status == "error")
        # `default=str` because an attribute may be any object a caller passed
        # in, and a summary that raises on an unserialisable value is the exact
        # failure this module exists to prevent.
        refusals = sum(1 for span in roots if refusal_marker in _blob(span.attributes))
        request_count = len(roots)
        return {
            "requests": request_count,
            "p50_ms": round(percentile(latencies, 50), 1),
            "p95_ms": round(percentile(latencies, 95), 1),
            "error_rate": round(errors / request_count, 4) if request_count else 0.0,
            "refusal_rate": round(refusals / request_count, 4) if request_count else 0.0,
            "cost_per_request": round(sum(by_root_cost) / request_count, 6) if request_count else 0.0,
            "cost_total": round(sum(by_root_cost), 6),
            "spans": len(self.spans),
            "dropped": self.dropped,
            "tracer_errors": self.internal_errors,
        }

    def _descendants(self, span_id: str) -> list[Span]:
        children = [span for span in self.spans if span.parent == span_id]
        out = list(children)
        for child in children:
            out.extend(self._descendants(child.id))
        return out

    def slowest(self, n: int = 5) -> list[Span]:
        return sorted(self.spans, key=lambda span: -span.ms)[:n]

    # -- export ------------------------------------------------------------

    def to_jsonl(self, path: str | Path) -> Path:
        """One span per line. Every log pipeline on earth can read this, which
        is the point — you do not need a vendor to start."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "".join(
                json.dumps(asdict(span), ensure_ascii=False, default=str) + "\n"
                for span in self.spans
            ),
            encoding="utf-8",
        )
        return target

    def clear(self) -> None:
        self.spans.clear()
        self.dropped = 0
        self.internal_errors = 0
