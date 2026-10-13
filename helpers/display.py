"""Rendering model output in a marimo cell, including live streaming.

This is a rewrite rather than a port. The Jupyter version of these helpers is built
on IPython display handles, which do not exist here — marimo streams by repeatedly
calling `mo.output.replace()` on the running cell.

Tier 1: stdlib + marimo only.
"""

from __future__ import annotations

import time

# How often to repaint while streaming. Every token is far too chatty over SSH or a
# remote kernel and makes the cell feel laggy rather than fast.
_REPAINT_SECONDS = 0.08


def show(*parts: object) -> None:
    """Render one or more values as the cell's output.

    Strings are treated as markdown, so `show("**done**")` does what it looks like.
    """
    import marimo as mo

    rendered = [mo.md(part) if isinstance(part, str) else mo.as_html(part) for part in parts]
    mo.output.replace(mo.vstack(rendered) if len(rendered) > 1 else rendered[0])


def _deltas(chunk) -> tuple[str, str]:
    """Pull (content, reasoning) out of one streamed chunk.

    Reasoning models expose their chain of thought as `delta.reasoning` (OpenAI
    style) or `delta.reasoning_content` (vLLM style). Providers that don't reason
    simply never populate either.
    """
    try:
        delta = chunk.choices[0].delta
    except (AttributeError, IndexError):
        return "", ""
    content = getattr(delta, "content", None) or ""
    reasoning = (
        getattr(delta, "reasoning", None)
        or getattr(delta, "reasoning_content", None)
        or ""
    )
    return content, reasoning


def _render(answer: str, reasoning: str, show_reasoning: bool):
    import marimo as mo

    if reasoning and show_reasoning:
        thinking = mo.Html(
            f'<div style="opacity:.55;font-style:italic;font-size:.9em;'
            f'border-left:2px solid currentColor;padding-left:.75em;margin-bottom:.5em;">'
            f"{mo.md(reasoning).text}</div>"
        )
        return mo.vstack([thinking, mo.md(answer)])
    return mo.md(answer)


def stream_md(stream, *, show_reasoning: bool = True) -> str:
    """Render a streaming completion live, and return the finished text.

    While the model thinks, its reasoning shows in a dimmed block above the answer;
    that block is wiped when the stream ends, so the saved notebook keeps only the
    answer.

        reply = stream_md(completion(**cfg.kwargs(), messages=msgs, stream=True))
    """
    import marimo as mo

    answer, reasoning, last = "", "", 0.0

    for chunk in stream:
        content, thought = _deltas(chunk)
        answer += content
        reasoning += thought

        now = time.monotonic()
        if (content or thought) and now - last >= _REPAINT_SECONDS:
            mo.output.replace(_render(answer, reasoning, show_reasoning))
            last = now

    mo.output.replace(mo.md(answer))  # final paint drops the reasoning block
    return answer


def stream_chat(stream, *, show_reasoning: bool = True) -> dict:
    """Like `stream_md`, but also assembles streamed tool-call fragments.

    Returns `{"content": str, "tool_calls": [...]}` so an agent loop can act on the
    calls. Tool calls arrive in pieces across chunks — index, then name, then the
    arguments a few characters at a time — so they have to be stitched by index.
    """
    import marimo as mo

    answer, reasoning, last = "", "", 0.0
    calls: dict[int, dict] = {}

    for chunk in stream:
        content, thought = _deltas(chunk)
        answer += content
        reasoning += thought

        try:
            fragments = chunk.choices[0].delta.tool_calls or []
        except (AttributeError, IndexError):
            fragments = []

        for fragment in fragments:
            slot = calls.setdefault(
                fragment.index, {"id": None, "name": "", "arguments": ""}
            )
            if getattr(fragment, "id", None):
                slot["id"] = fragment.id
            function = getattr(fragment, "function", None)
            if function is not None:
                slot["name"] += getattr(function, "name", None) or ""
                slot["arguments"] += getattr(function, "arguments", None) or ""

        now = time.monotonic()
        if (content or thought) and now - last >= _REPAINT_SECONDS:
            mo.output.replace(_render(answer, reasoning, show_reasoning))
            last = now

    mo.output.replace(mo.md(answer))
    return {
        "content": answer,
        "tool_calls": [calls[index] for index in sorted(calls)],
    }
