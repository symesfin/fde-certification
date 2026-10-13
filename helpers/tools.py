"""Tool dispatch that survives the model getting it wrong.

Tier 2 by convention. Standard library only.

Week 5 Session 10 writes the tool loop by hand — schema, dispatch, feed the result
back — and that loop is the lesson. What it leaves out is every way the model
breaks it, which in production is most days:

    json.loads(call.function.arguments)   # truncated JSON -> ValueError
    who_is_oncall(**args)                 # invented kwarg  -> TypeError
                                          # missing kwarg   -> TypeError
                                          # wrong tool name -> silently ignored

The last one is the nastiest and the easiest to write by accident: a loop that
dispatches to a hard-coded function without checking `call.function.name` will
happily run the wrong tool when the model asks for a different one, and return a
confident answer built on it.

**The governing rule: a tool failure is a message, not an exception.** Every
error here is caught and returned as the tool's *result*, phrased for the model
to read. A model that gets back `unknown tool 'lookup_team'; available:
who_is_oncall` will usually correct itself on the next turn. A model that gets
back a Python traceback gets nothing, because your process already died.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable

_JSON_TYPES = {
    str: "string", int: "integer", float: "number", bool: "boolean",
    list: "array", dict: "object",
}


@dataclass
class ToolResult:
    name: str
    ok: bool
    content: str                    # exactly what goes back to the model
    error: str | None = None
    call_id: str | None = None

    def as_message(self) -> dict:
        return {"role": "tool", "tool_call_id": self.call_id or "", "content": self.content}


@dataclass
class Toolbox:
    """A registry that can describe itself to a model and survive its mistakes.

        box = Toolbox()
        box.register(who_is_oncall, "Find which team owns a service.")

        first = completion(**cfg.kwargs(), messages=msgs, tools=box.schemas)
        msgs += box.run(first.choices[0].message)
    """

    max_result_chars: int = 4000
    _fns: dict = field(default_factory=dict)
    _schemas: dict = field(default_factory=dict)

    # -- registration ------------------------------------------------------

    def register(self, fn: Callable, description: str = "", *,
                 name: str | None = None, schema: dict | None = None) -> Callable:
        """Add a function. The schema is derived from its signature unless given.

        Deriving it matters more than it looks: a hand-written schema and the
        function it describes drift apart within weeks, and the symptom is a
        model politely passing an argument the function stopped accepting.
        """
        key = name or fn.__name__
        self._fns[key] = fn
        self._schemas[key] = schema or self._derive(fn, key, description)
        return fn

    def _derive(self, fn: Callable, key: str, description: str) -> dict:
        props, required = {}, []
        for param in inspect.signature(fn).parameters.values():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            json_type = _JSON_TYPES.get(param.annotation, "string")
            props[param.name] = {"type": json_type}
            if param.default is inspect.Parameter.empty:
                required.append(param.name)
        return {
            "type": "function",
            "function": {
                "name": key,
                "description": description or (inspect.getdoc(fn) or "").split("\n")[0],
                "parameters": {"type": "object", "properties": props, "required": required},
            },
        }

    @property
    def schemas(self) -> list[dict]:
        return [self._schemas[key] for key in sorted(self._schemas)]

    @property
    def names(self) -> list[str]:
        return sorted(self._fns)

    # -- dispatch ----------------------------------------------------------

    def _fail(self, name: str, call_id: str | None, message: str) -> ToolResult:
        # Phrased at the model, not at a log reader. It is the one who has to fix it.
        return ToolResult(name=name, ok=False, call_id=call_id, error=message,
                          content=json.dumps({"error": message}))

    def dispatch(self, name: str, arguments: str | dict,
                 call_id: str | None = None) -> ToolResult:
        """Run one tool call. **Never raises.**"""
        if name not in self._fns:
            return self._fail(
                name, call_id,
                f"unknown tool {name!r}; available: {', '.join(self.names)}",
            )

        if isinstance(arguments, str):
            try:
                args = json.loads(arguments or "{}")
            except (ValueError, TypeError):
                return self._fail(
                    name, call_id,
                    f"arguments were not valid JSON: {str(arguments)[:120]!r}. "
                    f"Send a JSON object.",
                )
        else:
            args = dict(arguments or {})

        if not isinstance(args, dict):
            return self._fail(name, call_id,
                              f"arguments must be a JSON object, got {type(args).__name__}")

        fn = self._fns[name]
        params = inspect.signature(fn).parameters
        accepts_kwargs = any(param.kind == param.VAR_KEYWORD for param in params.values())

        unexpected = [] if accepts_kwargs else [key for key in args if key not in params]
        if unexpected:
            return self._fail(
                name, call_id,
                f"unexpected argument(s) {', '.join(sorted(unexpected))}; "
                f"{name} accepts: {', '.join(key for key in params) or 'nothing'}",
            )

        missing = [
            key for key, param in params.items()
            if param.default is inspect.Parameter.empty
            and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD)
            and key not in args
        ]
        if missing:
            return self._fail(name, call_id,
                              f"missing required argument(s): {', '.join(missing)}")

        try:
            value = fn(**args)
        except Exception as exc:
            # The tool itself failed. Still a message: the model may be able to
            # try a different service, a different spelling, or say it cannot.
            return self._fail(name, call_id,
                              f"{name} failed: {type(exc).__name__}: {exc}"[:300])

        try:
            content = value if isinstance(value, str) else json.dumps(value, default=str)
        except Exception:
            content = str(value)

        if len(content) > self.max_result_chars:
            # A tool that returns a whole table will silently eat the context the
            # answer needed. Truncate visibly so the model knows it is partial.
            content = (
                content[: self.max_result_chars]
                + f"\n...[truncated at {self.max_result_chars} chars; narrow the query]"
            )
        return ToolResult(name=name, ok=True, content=content, call_id=call_id)

    def run(self, message: Any) -> list[dict]:
        """Dispatch every tool call on an assistant message.

        Returns the messages to append — the assistant turn followed by one tool
        result per call, which is the shape every provider expects. Returns `[]`
        when the model did not call anything.
        """
        calls = getattr(message, "tool_calls", None) or []
        if not calls:
            return []
        try:
            assistant = message.model_dump()
        except Exception:
            assistant = {"role": "assistant", "content": getattr(message, "content", "")}

        out = [assistant]
        for call in calls:
            fn = getattr(call, "function", None)
            out.append(
                self.dispatch(
                    getattr(fn, "name", "") or "",
                    getattr(fn, "arguments", "") or "{}",
                    getattr(call, "id", None),
                ).as_message()
            )
        return out
