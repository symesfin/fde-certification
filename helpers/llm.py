"""One place where model calls are made, so there is one place to fix them.

Tier 2. Declare `litellm` in your notebook's PEP 723 block.

Every notebook in this course teaches its own model call from scratch, and that
is deliberate — a `completion()` you can read is worth more than a wrapper you
trust. This module is what you reach for *after* that lesson, when the call has
stopped being the subject and started being plumbing.

Three things it does that a bare `completion()` does not, each one earned:

**An explicit timeout.** Week 3 measured what an inherited default costs: a
request that outruns the client timeout is cancelled server-side, the work
already done is discarded, and a naive retry re-sends the identical request to
fail identically. Forty minutes, no result, and an error naming nothing useful.
A timeout you chose is a timeout you can reason about.

**Retrying only what retrying can fix.** A 429 is worth another attempt. A 400
is not — the request is malformed and will be just as malformed in four seconds.
Blind `for attempt in range(3)` loops turn a fast, clear failure into a slow,
confusing one, and they are the most common thing people copy out of a blog post.

**A count of what you spent.** Token usage is the number that decides whether a
project survives contact with a budget, and it is free to collect at the call
site. Ignoring it until someone asks is how teams discover their per-request
cost in a meeting rather than in a dashboard.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

# Substrings that identify a failure as permanent. Checked against the exception
# type name and its message, because providers are inconsistent about which they
# put a useful signal in.
_PERMANENT = (
    "context length",
    "context_length",
    "maximum context",
    "too many tokens",
    "string too long",
    "invalid api key",
    "incorrect api key",
    "authentication",
    "unauthorized",
    "permission",
    "not found",
    "does not exist",
    "unsupported",
    "invalid_request",
)

# Substrings that identify a failure as worth another attempt.
_TRANSIENT = (
    "timeout",
    "timed out",
    "rate limit",
    "ratelimit",
    "overloaded",
    "capacity",
    "service unavailable",
    "bad gateway",
    "connection",
    "temporarily",
    "try again",
)


def is_retryable(exc: BaseException) -> bool:
    """Is another attempt worth making?

    Status code first, because it is the only unambiguous signal: 429 and 5xx
    are the server's way of saying "later"; any other 4xx is the server saying
    "no". Falls back to matching the message, and when nothing matches, returns
    False — an unrecognised error should surface now, not in four attempts'
    time.
    """
    status = getattr(exc, "status_code", None)
    if not isinstance(status, int):
        status = getattr(exc, "code", None)
    if isinstance(status, int) and 100 <= status < 600:
        # The 4xx codes that mean "later", not "no". This list is not a detail:
        # LiteLLM raises its Timeout with status_code=408, so classifying every
        # non-429 4xx as permanent means a timeout is never retried and the
        # error tells you it was not — the opposite of the right behaviour.
        # Found by running against a real endpoint; a stubbed exception with no
        # status code fell through to message matching and hid it.
        if status in (408, 425, 429) or status >= 500:
            return True
        if 400 <= status < 500:
            return False

    text = f"{type(exc).__name__} {exc}".lower()
    # Permanent wins ties: "invalid request: context length" contains both a
    # permanent marker and, in some providers' wording, "try again".
    if any(marker in text for marker in _PERMANENT):
        return False
    return any(marker in text for marker in _TRANSIENT)


@dataclass
class CallStats:
    """What the calls cost. Print it; put it in your trace; watch it in Week 10."""

    calls: int = 0
    retries: int = 0
    failures: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def __str__(self) -> str:
        rate = f"{self.seconds / self.calls:.2f}s/call" if self.calls else "—"
        return (
            f"{self.calls} calls · {self.total_tokens} tokens "
            f"({self.prompt_tokens} in / {self.completion_tokens} out) · "
            f"{self.seconds:.1f}s · {rate}"
            + (f" · {self.retries} retries" if self.retries else "")
            + (f" · ⚠️ {self.failures} failed" if self.failures else "")
        )


def with_retry(
    fn: Callable[[], Any],
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
    stats: CallStats | None = None,
    describe: str = "call",
) -> Any:
    """Run `fn`, retrying only failures that another attempt could fix.

    Exponential backoff with jitter. The jitter is not decoration: without it,
    every client that failed against the same overloaded endpoint retries in
    lockstep and arrives together, which is how a brief blip becomes an outage.
    """
    delay = base_delay
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as exc:
            last = attempt == max_retries - 1
            if not is_retryable(exc):
                if stats:
                    stats.failures += 1
                raise RuntimeError(
                    f"{describe} failed permanently and was not retried: {exc}\n\n"
                    f"This error will not be fixed by trying again — the request "
                    f"itself needs to change (model name, credentials, or size)."
                ) from exc
            if last:
                if stats:
                    stats.failures += 1
                raise RuntimeError(
                    f"{describe} failed after {max_retries} attempts: {exc}\n\n"
                    f"The failures looked transient, so every attempt re-sent the "
                    f"same request. If this is a timeout, the request is probably "
                    f"too big rather than the endpoint too slow — send less per "
                    f"call, or raise the timeout deliberately."
                ) from exc
            if stats:
                stats.retries += 1
            time.sleep(delay * (0.5 + random.random()))   # jitter, see above
            delay *= 2


def complete(
    cfg,
    messages: Sequence[dict],
    *,
    timeout: float = 600.0,
    max_retries: int = 3,
    model: str | None = None,
    stats: CallStats | None = None,
    **kwargs,
):
    """A chat completion with a timeout you chose and retries that make sense.

    Returns the full response, so tool calls and finish reasons stay reachable.
    Use `chat()` when you only want the text.
    """
    from litellm import completion

    kw = dict(cfg.kwargs())
    if model:
        kw["model"] = model
    kw.update(kwargs)

    started = time.perf_counter()
    response = with_retry(
        lambda: completion(
            **kw, messages=list(messages), timeout=timeout
        ),
        max_retries=max_retries,
        stats=stats,
        describe=f"completion({kw.get('model')})",
    )
    if stats is not None:
        stats.calls += 1
        stats.seconds += time.perf_counter() - started
        usage = getattr(response, "usage", None)
        if usage is not None:
            stats.prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
            stats.completion_tokens += getattr(usage, "completion_tokens", 0) or 0
    return response


def chat(cfg, prompt_or_messages, **kwargs) -> str:
    """The text of one reply. Accepts a string or a messages list.

        answer = chat(CFG, "Summarise this incident in one line.")

    Returns `""` rather than None when a model replies with no content, because
    every caller downstream does string things to the result.
    """
    messages = (
        [{"role": "user", "content": prompt_or_messages}]
        if isinstance(prompt_or_messages, str)
        else list(prompt_or_messages)
    )
    response = complete(cfg, messages, **kwargs)
    try:
        return response.choices[0].message.content or ""
    except (AttributeError, IndexError, KeyError):
        return ""
