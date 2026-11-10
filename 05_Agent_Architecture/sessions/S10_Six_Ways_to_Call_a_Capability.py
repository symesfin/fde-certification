# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "fastmcp>=4.1",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium", app_title="Six Ways to Call a Capability")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 10: Six Ways to Call a Capability

    ## 👋 Introduction

    There are at least six ways to let a model do something. MCP is one of
    them. They differ in latency, token cost, how they fail, who maintains them,
    and who can discover them.

    Today we put **one function behind a model six ways** using FastMCP, a
    Python framework for building MCP servers and clients:

    - a tool
    - a skill
    - a subagent
    - an MCP server
    - Code Mode
    - an HTTP API that already exists

    Then we measure all of them. Those numbers are the evidence your
    challenge's decision row asks for.

    **You will be able to:**

    - define a capability once and let FastMCP generate the schema every client sees
    - say what an MCP client does when a model asks for a tool that is not there
    - serve a skill directory, a subagent and an existing HTTP API from one framework
    - run the same server in-process, over stdio, and mounted behind a platform gateway
    - count model calls and capability calls separately, with middleware on the server
    - find the response size at which Code Mode's token bill stops growing

    **Key concepts you will see in code:** `FastMCP`, `@server.tool`, `Client`,
    `Middleware`, `SkillsDirectoryProvider`, `mount`, `CodeMode`,
    `FastMCP.from_openapi`.

    **Where you end up:** the six ways are answers to six questions, asked in a
    fixed order. Two of the answers are numbers about *your* model, and you can
    only get them by measuring.

    ## 💼 Business Case Study

    Sofia is an engineer on the platform team of a regional hospital group. Six
    product teams each want a model to call the same kind of internal lookup:
    pharmacy renewals, bed management, the IT service desk, discharge
    summaries, supplier invoices, and the on-call rota. Each team has already
    picked a different way to do it. One wrote a tool, one an MCP server, one
    is piloting Code Mode.

    The architecture review board wants **one recommendation, with numbers, by
    the end of the month**. It will not accept *"it depends."*

    | Team | Chose | Because |
    | --- | --- | --- |
    | IT service desk | a tool | it took an afternoon |
    | Pharmacy renewals | a skill | the pharmacist who owns the rules edits markdown, not Python |
    | Discharge summaries | a subagent | forty pages of notes must not end up in a clinician's conversation |
    | On-call rota | an MCP server | so other clients could find it, though none does yet |
    | Bed management | Code Mode, piloting | one question about ward capacity is forty lookups |
    | Supplier invoices | nothing at all | their lookup has been an authenticated HTTP API for years |

    So she builds the same trivial capability all six ways and measures them.
    What she brings the board is a choice with five named rejections and the
    condition that would change it.

    > **You will be asked what you rejected.** If you never built or measured an
    > alternative, you cannot answer. This session gets you a real answer.

    ## 📜 Table of Contents

    - 🏗️ By the End of the Sesh
    - ✅ Task 1: One capability, one server — and Way 1, a tool
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #1
    - ✅ Task 2: Way 2, a skill, and Way 3, a subagent
    - ✅ Task 3: Way 4, an MCP server other clients can find
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #2
    - ✅ Task 4: Way 5, Code Mode, and Way 6, an API that already exists
    - ✅ Task 5: Measure them, then grow the data
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #3
    - ✅ Task 6: The comparison, and Sofia's page for the board
    - 🧑‍🤝‍🧑 Discuss: ❓ Question #4
    - 🏭 What we Built vs. What's in Production
    - 👋 Conclusion
    - 📖 Official Documentation

    ---
    ## 🧑‍💻 Setup

    `LLM_MODEL` must be able to call tools. Every number in this notebook comes
    out of a cell you press, against **your** configured model.
    """)
    return


@app.cell
def _(mo):
    import ast
    import json
    import subprocess
    import sys
    import time
    from pathlib import Path

    import litellm
    from fastmcp import Client, FastMCP

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    print(f"✅ {CFG}")
    return (
        CFG,
        Client,
        FastMCP,
        Path,
        ast,
        json,
        litellm,
        subprocess,
        sys,
        time,
        ui,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The capability.** One function: look up who is on call for a service.
    Everything below is a different way of putting a model in front of it. We
    keep it trivial on purpose, so the task never distracts from the plumbing.
    It is the smallest thing that behaves like Sofia's pharmacy lookup and her
    bed-management query, so all six ways get compared on the same work.
    """)
    return


@app.cell
def _():
    ONCALL = {
        "atlas": {"team": "Tracking Platform", "channel": "#team-tracking", "pager": "tracking-oncall"},
        "ledger": {"team": "Revenue Systems", "channel": "#team-revenue", "pager": "revenue-oncall"},
        "warehouse gateway": {"team": "Depot Systems", "channel": "#team-depot", "pager": "depot-oncall"},
        "postgres": {"team": "Data Platform", "channel": "#team-data", "pager": "data-oncall-24x7"},
    }

    def who_is_oncall(service: str) -> dict:
        """Find which team owns a service and how to reach them."""
        key = service.strip().lower()
        for name, info in ONCALL.items():
            if key in name or name in key:
                return {"service": name, **info}
        return {"error": f"unknown service: {service}", "known": sorted(ONCALL)}

    QUESTION_1 = "Who is on call for Atlas?"
    QUESTION_4 = ("Which teams own Atlas, Ledger, Warehouse Gateway, and Postgres? "
                  "List each service with its team.")
    print(who_is_oncall("Atlas"))
    return ONCALL, QUESTION_1, QUESTION_4, who_is_oncall


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Serving it, and counting.** `oncall_server` puts the function on a
    FastMCP server. FastMCP generates the tool's schema (the JSON description
    the model reads) from the function's signature and docstring.

    - `oncall_server` takes the function as an **argument**. That lets Task 5
      swap in a lookup that returns a bigger record.
    - `CapabilityCounter` is server middleware. It counts every call that
      reaches the tool, whoever made it.
    - `Meter` counts model round trips and tokens.
    - `server_log` collects FastMCP's own log for one cell, so the cells that
      break things on purpose can show it folded away rather than under the
      table.
    """)
    return


@app.cell
def _(FastMCP, who_is_oncall):
    import logging
    from contextlib import contextmanager

    from fastmcp.server.middleware import Middleware

    @contextmanager
    def server_log():
        """Collect FastMCP's server-side log for one cell, instead of printing it under the output.

        The server logs every tool failure with a traceback. That is the right
        place for it -- but under a table, live, it is noise. Cells that make
        failures on purpose show the log in an accordion instead.
        """
        logger = logging.getLogger("fastmcp")
        lines = []

        class Collect(logging.Handler):
            def emit(self, record):
                lines.append(f"{record.levelname}: {record.getMessage()}")

        saved_handlers = logger.handlers[:]
        logger.handlers = [Collect()]
        try:
            yield lines
        finally:
            logger.handlers = saved_handlers

    class Meter:
        """Counts model round trips and the tokens they cost."""

        def __init__(self):
            self.calls = 0
            self.tokens = 0

        def track(self, response):
            self.calls += 1
            usage = getattr(response, "usage", None)
            if usage:
                self.tokens += usage.total_tokens or 0

    class CapabilityCounter(Middleware):
        """Counts the calls that reach one tool on a server, under any namespace."""

        def __init__(self, tool_name: str):
            self.tool_name = tool_name
            self.calls = 0

        async def on_call_tool(self, context, call_next):
            if context.message.name.endswith(self.tool_name):
                self.calls += 1
            return await call_next(context)

    def oncall_server(lookup=who_is_oncall, counter=None) -> FastMCP:
        """The capability as a FastMCP server. Its schema comes from `lookup`'s signature."""
        server = FastMCP("oncall", middleware=[counter] if counter else None)
        server.tool(lookup, name="who_is_oncall", description=who_is_oncall.__doc__)
        return server

    return CapabilityCounter, Meter, oncall_server, server_log


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The loop.** Decide, dispatch, answer. The model is handed whatever tools
    the MCP client lists, and every call it asks for goes back through the
    client. The loop repeats because a model may need a second round after
    seeing the first results. The cap of six rounds stops a model that keeps
    calling forever. `dispatch` never raises: every failure comes back as text
    addressed to the model. Task 1 shows why that matters.
    """)
    return


@app.cell
def _(CFG, json, litellm):
    def openai_tools(mcp_tools) -> list[dict]:
        """MCP tool listings in the shape a chat-completions API expects."""
        return [{"type": "function", "function": {
            "name": tool.name, "description": tool.description or "", "parameters": tool.input_schema,
        }} for tool in mcp_tools]

    async def dispatch(client, call) -> str:
        """Run one tool call through the MCP client. Failures are returned, never raised."""
        try:
            arguments = json.loads(call.function.arguments or "{}")
        except ValueError as error:
            return f"arguments were not a JSON object: {error}"
        result = await client.call_tool(call.function.name, arguments, raise_on_error=False)
        text = "\n".join(getattr(block, "text", "") for block in result.content)
        if result.is_error and text.startswith("Unknown tool"):  # say what is wrong AND what is right
            text += ". Available tools: " + ", ".join(tool.name for tool in await client.list_tools())
        return text

    async def run_agent(client, question: str, meter=None, first_choice: str = "auto") -> str:
        """Decide, dispatch, answer: the whole loop, over any MCP client."""
        tools = openai_tools(await client.list_tools())
        messages = [{"role": "user", "content": question}]
        for round_number in range(6):
            reply = litellm.completion(**CFG.kwargs(), messages=messages, tools=tools, timeout=600,
                                       tool_choice=first_choice if round_number == 0 else "auto")
            if meter:
                meter.track(reply)
            message = reply.choices[0].message
            if not message.tool_calls:
                return message.content
            messages.append(message.model_dump())
            for call in message.tool_calls:
                messages.append({"role": "tool", "tool_call_id": call.id, "content": await dispatch(client, call)})
        return "gave up after 6 rounds"

    return dispatch, openai_tools, run_agent


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The API that already exists.** The supplier-invoice team's on-call
    directory is an HTTP service with an OpenAPI document. Here it is a small
    Starlette app reached through an in-process transport. It stands in for a
    real service at `https://oncall.internal`. At your firm, drop the transport
    and keep the base URL. The HTTP client carries the credential, which
    matters in Task 4.
    """)
    return


@app.cell
def _(who_is_oncall):
    import httpx2
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    DIRECTORY_SPEC = {
        "openapi": "3.1.0",
        "info": {"title": "On-call directory", "version": "4.2.0"},
        "paths": {"/oncall/{service}": {"get": {
            "operationId": "who_is_oncall",
            "summary": "Find which team owns a service and how to reach them.",
            "parameters": [{"name": "service", "in": "path", "required": True, "schema": {"type": "string"}}],
            "responses": {"200": {"description": "The owning team",
                                  "content": {"application/json": {"schema": {"type": "object"}}}}},
        }}},
    }

    def directory_api(lookup=who_is_oncall) -> Starlette:
        """The HTTP API, as its owners run it."""
        async def get_oncall(request):
            record = lookup(request.path_params["service"])
            return JSONResponse(record, status_code=404 if "error" in record else 200)

        return Starlette(routes=[Route("/oncall/{service}", get_oncall)])

    def directory_client(lookup=who_is_oncall, token: str = "issued-to-the-caller", requests_seen=None):
        """The caller's HTTP client, and the credential on it."""
        async def record_request(request):
            if requests_seen is not None:
                requests_seen.append({"url": str(request.url), "authorization": request.headers.get("authorization")})

        return httpx2.AsyncClient(transport=httpx2.ASGITransport(app=directory_api(lookup)),
                                  base_url="https://oncall.internal", headers={"Authorization": f"Bearer {token}"},
                                  event_hooks={"request": [record_request]})

    return DIRECTORY_SPEC, directory_client


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Where code runs, and where skills live.** Code Mode needs somewhere to run
    the program a model writes.

    - `NotASandbox` is the smallest thing that will: restricted builtins and an
      `exec`. Task 4 explains why it is named that way.
    - `CODE_MODE_BRIEF` is the description the model reads for `execute`, the
      one tool Code Mode leaves it.
    - `SKILLS_DIR` is the skill directory next to this notebook.
    """)
    return


@app.cell
def _(Path, ast, mo):
    from fastmcp.experimental.transforms.code_mode import CodeMode
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    SAFE_BUILTINS = {
        "len": len, "sorted": sorted, "list": list, "dict": dict, "set": set,
        "str": str, "int": int, "float": float, "bool": bool, "print": print,
        "sum": sum, "any": any, "all": all, "range": range, "enumerate": enumerate,
        "zip": zip, "min": min, "max": max,
    }

    class NotASandbox:
        """Runs a model's program as the body of an async function. Restricted builtins; no isolation."""

        async def run(self, code: str, *, inputs=None, external_functions=None):
            if "\n" not in code and "\\n" in code:  # one line of literal \n escapes, a small-model habit
                try:
                    ast.parse(code)
                except SyntaxError:
                    code = code.replace("\\n", "\n")  # it cannot run as sent; undo that one mistake
            try:
                program = ast.parse(code)  # a top-level `return` parses; it is wrapped below
            except SyntaxError as error:  # a failure is a message, here too
                raise ValueError(f"your code does not parse: {error.msg} (line {error.lineno})") from None
            wrapper = ast.AsyncFunctionDef(
                name="program", body=program.body or [ast.Pass()], decorator_list=[], type_params=[],
                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]))
            module = ast.fix_missing_locations(ast.Module(body=[wrapper], type_ignores=[]))
            namespace = {"__builtins__": SAFE_BUILTINS, **(external_functions or {})}
            exec(compile(module, "<model>", "exec"), namespace)
            answer = await namespace["program"]()
            if answer is None:
                raise ValueError("your code returned nothing; end it with a return statement")
            return answer

    CODE_MODE_BRIEF = (
        "Run Python to answer the question. The code is the body of an async function: top-level "
        "statements, `await call_tool(tool_name, params)` for each lookup, and a final `return`. Whatever "
        "you return is sent back to you in full, so return only the fields the question asks for, never a "
        "whole record. No imports, no def. Example:\n"
        'answer = {}\nfor name in ["a", "b"]:\n    record = await call_tool("some_tool", {"key": name})\n'
        '    answer[name] = record["field"]  # keep the field, drop the record\nreturn answer\n\n'
        "Tools: who_is_oncall(service: str) -> dict with keys service, team, channel, pager."
    )
    SKILLS_DIR = Path(mo.notebook_dir()) / "skills"
    return (
        CODE_MODE_BRIEF,
        CodeMode,
        NotASandbox,
        SKILLS_DIR,
        SkillsDirectoryProvider,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🏗️ By the End of the Sesh

    Here is the whole job in one cell:

    - the capability, defined once
    - served five of the six ways
    - mounted behind one platform server that any MCP client can discover
    - one four-service question, asked two ways, with the counter running

    Each task below unrolls one part of it.
    """)
    return


@app.cell
def _(mo):
    sesh_button = mo.ui.run_button(label="Serve it five ways and ask one question two ways")
    sesh_button
    return (sesh_button,)


@app.cell
async def _(
    CODE_MODE_BRIEF,
    CapabilityCounter,
    Client,
    CodeMode,
    DIRECTORY_SPEC,
    FastMCP,
    Meter,
    NotASandbox,
    QUESTION_4,
    SKILLS_DIR,
    SkillsDirectoryProvider,
    directory_client,
    mo,
    run_agent,
    sesh_button,
    ui,
    who_is_oncall,
):
    mo.stop(not sesh_button.value, mo.md("*Click above: one question, asked two ways, about four model calls.*"))

    sesh_counter = CapabilityCounter("who_is_oncall")
    oncall = FastMCP("oncall", middleware=[sesh_counter])
    oncall.tool(who_is_oncall)                                       # Way 1: the schema comes from the signature
    oncall.add_provider(SkillsDirectoryProvider(roots=SKILLS_DIR))   # Way 2: a directory a pharmacist edits, served
    bed_management = FastMCP("bed-management", transforms=[CodeMode(
        sandbox_provider=NotASandbox(), discovery_tools=[], execute_description=CODE_MODE_BRIEF)])
    bed_management.mount(oncall)                                     # Way 5: the same tool, behind one `execute`
    directory = FastMCP.from_openapi(DIRECTORY_SPEC, client=directory_client())  # Way 6: an API that already exists
    platform = FastMCP("platform")                                   # Way 4: one server any MCP client can discover
    platform.mount(oncall, namespace="oncall")
    platform.mount(directory, namespace="directory")

    async with Client(platform) as sesh_client:
        sesh_discovered = [tool.name for tool in await sesh_client.list_tools()]
        sesh_discovered += [str(resource.uri) for resource in await sesh_client.list_resources()]
    sesh_rows = []
    for sesh_way, sesh_server, sesh_choice in [("Tool", oncall, "auto"), ("Code Mode", bed_management, "required")]:
        sesh_meter, sesh_counter.calls = Meter(), 0
        async with Client(sesh_server) as sesh_client:
            sesh_answer = await run_agent(sesh_client, QUESTION_4, sesh_meter, first_choice=sesh_choice)
        sesh_rows.append({"way": sesh_way, "model calls": sesh_meter.calls, "capability calls": sesh_counter.calls,
                          "tokens": sesh_meter.tokens, "answer": str(sesh_answer)[:90].replace("\n", " ")})

    mo.vstack([
        mo.md("**`platform` advertises:** " + ", ".join(f"`{name}`" for name in sesh_discovered)),
        ui.table(sesh_rows, title="Four lookups, two ways, one counter on the server"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 1: One capability, one server — and Way 1, a tool

    The model is given a schema, decides to call it, and your code runs it.
    This is the baseline every other way is measured against. It is what the
    service-desk team built in an afternoon.

    > **🖼️ Diagram placeholder:** `who_is_oncall` registered once on a FastMCP
    > server; arrows from it to the generated JSON schema (what the model reads)
    > and to the function that runs (what the server dispatches). The model
    > sits on the far side of a `Client`, which carries `list_tools` out and
    > `call_tool` back. Drop it in at
    > `data/diagrams/S10_Six_Ways_to_Call_a_Capability_task1.png`.

    **The schema comes from the function.** Nobody wrote the JSON below.
    FastMCP read the signature and docstring of `who_is_oncall` and generated
    it. The description the model chooses by and the function that runs are
    one registration, so they cannot drift apart.
    """)
    return


@app.cell
async def _(Client, json, mo, oncall_server, openai_tools):
    async with Client(oncall_server()) as schema_client:
        listed_tools = await schema_client.list_tools()
        atlas_result = await schema_client.call_tool("who_is_oncall", {"service": "Atlas"})

    mo.vstack([
        mo.md("**What every MCP client is told:**"),
        mo.md(f"```json\n{json.dumps(openai_tools(listed_tools), indent=2)}\n```"),
        mo.md(f"**Called through the client:** `{atlas_result.data}`"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `call_with_tool` is Way 1 for the measurement: a server built around the
    capability, an in-memory client, and the loop from Setup. It costs **two
    model calls minimum**: one to decide, one to answer. That is the cost floor
    for every tool-based architecture. It is also why latency-sensitive systems
    sometimes skip tools and just do retrieval.

    The loop does not assume one question means one tool call. Ask about four
    services and a current model may emit all four requests in a single
    turn. Task 5 measures whether yours does. That answer changes the
    arithmetic.
    """)
    return


@app.cell
def _(Client, oncall_server, run_agent, who_is_oncall):
    async def call_with_tool(question: str, lookup=who_is_oncall, meter=None, counter=None) -> dict:
        """Way 1: the capability as a tool on a FastMCP server, called through an in-memory client."""
        async with Client(oncall_server(lookup, counter)) as tool_client:
            return {"answer": await run_agent(tool_client, question, meter)}

    return (call_with_tool,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### When the model gets it wrong

    A hand-written schema and the dispatcher it describes live in different
    places, and they drift apart. Someone renames a function. Someone adds a
    tool to the schema before implementing it. FastMCP removes that drift for
    its own server.

    It cannot stop a model from asking for a tool that is not there. Maybe a
    client still holds a tool list from before the service desk renamed
    `lookup_team`. Maybe the model invents a name.

    A loop with no name check would run a *different* function and answer
    confidently from the result. The MCP client cannot do that, because the
    server dispatches by name. The cell below sets up:

    - a stale tool list that still advertises `lookup_team`
    - one server that has only `who_is_oncall`
    - three model calls: the bad request, then the model's next move after
      it is told what went wrong. First in FastMCP's words, then in words that
      also name the tools that exist.
    """)
    return


@app.cell
def _(mo, openai_tools):
    from types import SimpleNamespace

    STALE_TOOLS = openai_tools([SimpleNamespace(
        name="lookup_team", description="Look up the team that owns a service. Preferred over who_is_oncall.",
        input_schema={"type": "object", "properties": {"service": {"type": "string"}}, "required": ["service"]},
    )]) + openai_tools([SimpleNamespace(
        name="who_is_oncall", description="Find which team owns a service and how to reach them.",
        input_schema={"type": "object", "properties": {"service": {"type": "string"}}, "required": ["service"]},
    )])

    drift_button = mo.ui.run_button(label="Ask a model for a tool that does not exist")
    drift_button
    return STALE_TOOLS, SimpleNamespace, drift_button


@app.cell
async def _(
    CFG,
    Client,
    STALE_TOOLS,
    dispatch,
    drift_button,
    json,
    litellm,
    mo,
    oncall_server,
    ui,
    who_is_oncall,
):
    mo.stop(not drift_button.value, mo.md("*Click above: three model calls — the bad request, and two recoveries.*"))

    asked = [{"role": "user", "content": "Who owns Atlas?"}]
    mo.output.replace(mo.md("**1 of 3** — asking the model, with the stale tool list…"))
    first_message = litellm.completion(**CFG.kwargs(), messages=asked, tools=STALE_TOOLS,
                                       timeout=600).choices[0].message
    first_calls = first_message.tool_calls or []
    mo.stop(not first_calls, mo.md("The model answered without calling a tool. Press again."))

    told = {}  # what the model hears back, per tool call: FastMCP's own message, then dispatch's
    async with Client(oncall_server()) as drift_client:
        for drift_call in first_calls:
            bare = await drift_client.call_tool(drift_call.function.name,
                                                json.loads(drift_call.function.arguments or "{}"), raise_on_error=False)
            told[drift_call.id] = (bare.content[0].text, await dispatch(drift_client, drift_call))

    drift_rows = [
        {"step": "model asked for", "value": ", ".join(call.function.name for call in first_calls)},
        {"step": "a loop with no name check would run who_is_oncall and return",
         "value": str(who_is_oncall(**json.loads(first_calls[0].function.arguments or "{}")))},
    ]
    for version, told_label in [(0, "FastMCP's message, as is"), (1, "the same, naming the tools that exist")]:
        mo.output.replace(mo.md(f"**{version + 2} of 3** — the model is told: {told_label}…"))
        told_messages = asked + [first_message.model_dump()] + [
            {"role": "tool", "tool_call_id": call_id, "content": pair[version]} for call_id, pair in told.items()]
        reply_message = litellm.completion(**CFG.kwargs(), messages=told_messages, tools=STALE_TOOLS,
                                           timeout=600).choices[0].message
        next_move = ", ".join(call.function.name for call in (reply_message.tool_calls or [])) \
            or f"answers: {(reply_message.content or '').strip()[:90]}"
        drift_rows.append({"step": f"told: {list(told.values())[0][version]}", "value": f"next move: {next_move}"})

    ui.table(drift_rows, title="Same failure, addressed to the party who can fix it")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A crash shows up in your logs. A wrong function shows up in a customer's
    transcript, if you ever see it. The rule that prevents both:

    > **A tool failure is a message, not an exception.**

    If your code raises, the request dies and the model never hears about it.
    **The model is the only party who can fix a bad tool call**, so the error
    has to be addressed to it, and addressed well.

    Read the last two rows. `Unknown tool: 'lookup_team'` says what is wrong,
    and a small model told only that tends to apologise and give up. Name the
    tools that exist and it usually calls the right one on the next turn.
    `dispatch` adds that line after FastMCP's message. It is the cheapest fix
    in this notebook!

    The cell below puts five failures through a FastMCP client with no model
    involved, so you can read exactly what the model would be handed. The
    server logs each one with a traceback, which is where an exception
    belongs; that log is folded under the table. The model gets the one line
    in the table.
    """)
    return


@app.cell
async def _(
    Client,
    FastMCP,
    SimpleNamespace,
    dispatch,
    mo,
    server_log,
    ui,
    who_is_oncall,
):
    from fastmcp.server.middleware.response_limiting import ResponseLimitingMiddleware

    failure_server = FastMCP("failures", middleware=[ResponseLimitingMiddleware(max_size=300)])
    failure_server.tool(who_is_oncall)

    @failure_server.tool
    def page_oncall(service: str) -> str:
        """Page the on-call engineer for a service."""
        raise ConnectionError("pager gateway refused the connection")

    @failure_server.tool
    def full_rota(service: str) -> str:
        """Every shift on the rota for a service."""
        return "\n".join(f"shift {index}: eng-{index:02d}" for index in range(500))

    def model_call(name: str, arguments: str):
        """A tool call shaped the way a chat-completions reply delivers one."""
        return SimpleNamespace(function=SimpleNamespace(name=name, arguments=arguments))

    FAILURES = [
        ("Unknown tool name", model_call("lookup_team", '{"service": "Atlas"}')),
        ("Malformed JSON arguments", model_call("who_is_oncall", '{"service": "Atl')),
        ("Unexpected argument", model_call("who_is_oncall", '{"svc": "Atlas"}')),
        ("The tool itself raises", model_call("page_oncall", '{"service": "Atlas"}')),
        ("A result larger than the limit", model_call("full_rota", '{"service": "Atlas"}')),
    ]
    failure_rows = []
    with server_log() as failure_log:
        async with Client(failure_server) as failure_client:
            for failure_name, failing_call in FAILURES:
                handed_back = " ".join((await dispatch(failure_client, failing_call)).split())  # one line per row
                shown = handed_back if len(handed_back) < 160 else f"{handed_back[:70]} … {handed_back[-70:]}"
                failure_rows.append({"failure": failure_name, "what the model is handed": shown})
    mo.vstack([
        ui.table(failure_rows, title="Five failures, each returned as a message"),
        mo.accordion({"📚 The server's log for those five — where the tracebacks went":
                      mo.md("```text\n" + "\n".join(failure_log) + "\n```")}),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Here is how a naive loop and FastMCP compare.** Carry this into your own
    app whichever of the six you pick, because every one of them dispatches
    something eventually.

    | | Naive loop | FastMCP client and server |
    | --- | --- | --- |
    | Unknown tool name | runs the wrong function, silently | `Unknown tool: 'lookup_team'` from the server, and the tools that exist from `dispatch` |
    | Malformed JSON arguments | `ValueError`, request dies | never reaches the client; the loop's `dispatch` returns a message |
    | Unexpected argument | `TypeError`, request dies | a validation message naming the missing and unexpected parameters |
    | The tool itself raises | request dies | `Error calling tool 'page_oncall': …`, and the model can try again |
    | A result larger than the context | silently eats the answer's room | `ResponseLimitingMiddleware` truncates, and *says* it did |

    Three of those rows are partly your code:

    - naming the tools that exist
    - the JSON parse, which happens before the client sees anything
    - the response limit, which is middleware you have to add

    In production, set `mask_error_details=True` on the server so the
    "tool itself raises" row stops leaking internals to whoever is on the
    other end.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #1

    Look at the endpoint on your own app — or whatever sits between a model's
    tool request and your code. In one to three sentences: what does it do
    today when the model asks for a tool name it does not have, or sends
    arguments that do not parse — and which of the five rows in the table
    above would a user of your app meet first?

    **Answer:**

    ---
    ## ✅ Task 2: Way 2, a skill, and Way 3, a subagent

    **A skill** is a directory on disk with instructions in it. The agent reads
    the instructions, then runs the script.

    The difference from a tool is *where the knowledge lives*. A tool's schema
    is in your code. A skill's instructions are a file a domain expert can edit
    without touching Python. That matters when the person who knows the
    escalation policy is not an engineer. The pharmacy team chose a skill. The
    renewal rules change every time the formulary does, and the pharmacist who
    owns them does not open pull requests.

    > **🖼️ Diagram placeholder:** left, the `skills/oncall-lookup/` directory
    > (`SKILL.md`, `run.py`) served by `SkillsDirectoryProvider` as
    > `skill://` resources: only the description is listed up front, the body
    > is read once the skill is chosen, and `run.py` runs as a subprocess.
    > Right, a subagent: a tool whose body is a second model call with its own
    > prompt, returning three lines to the caller. Drop it in at
    > `data/diagrams/S10_Six_Ways_to_Call_a_Capability_task2.png`.

    `SkillsDirectoryProvider` serves the skill directory next to this notebook
    as MCP resources. A client listing them sees a name and a description,
    nothing else. The body is one `read_resource` away, loaded only once the
    skill is chosen. That is called **progressive disclosure**, and it is why a
    hundred skills cost almost nothing until one is used.
    """)
    return


@app.cell
async def _(Client, FastMCP, SKILLS_DIR, SkillsDirectoryProvider, mo, ui):
    pharmacy = FastMCP("pharmacy")
    pharmacy.add_provider(SkillsDirectoryProvider(roots=SKILLS_DIR))
    async with Client(pharmacy) as skill_client:
        skill_listing = await skill_client.list_resources()
        SKILL_BODY = (await skill_client.read_resource("skill://oncall-lookup/SKILL.md"))[0].text

    mo.vstack([
        ui.table([{"resource": str(resource.uri), "listed up front": resource.description}
                  for resource in skill_listing], title="What a client sees before choosing the skill"),
        mo.md(f"**What it reads once it has chosen:**\n\n```markdown\n{SKILL_BODY}\n```"),
    ])
    return (SKILL_BODY,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Skills exist for content like the escalation paragraph. It is policy, it
    changes without a deploy, and the person who owns it is not an engineer.

    The skill's instructions say to run `run.py`, so the agent runs it as a
    subprocess. First it has to decide *which* services to look up. It asks
    the model for that decision with a schema. A schema *constrains
    generation* to the shape you want, so the model cannot ramble.
    """)
    return


@app.cell
def _(CFG, SKILLS_DIR, SKILL_BODY, json, litellm, mo, subprocess, sys, time):
    def run_skill(service: str) -> dict:
        """Invoke the skill's script the way an agent would: as a subprocess."""
        finished = subprocess.run([sys.executable, str(SKILLS_DIR / "oncall-lookup" / "run.py"), service],
                                  capture_output=True, text=True, timeout=30)
        return json.loads(finished.stdout) if finished.returncode == 0 else {"error": finished.stderr[:120]}

    PLAN_SCHEMA = [{"type": "function", "function": {
        "name": "lookup_services", "description": "Look up on-call information for one or more services.",
        "parameters": {"type": "object", "required": ["services"], "properties": {"services": {
            "type": "array", "items": {"type": "string"}, "description": "Every service named in the question."}}},
    }}]

    async def call_with_skill(question: str, lookup=None, meter=None, counter=None) -> dict:
        """Way 2: decide which services, run the script per service, answer with the skill's policy in view.

        `lookup` and `counter` are unused, and that is the finding: the capability runs in a
        subprocess, so no counter on any server sees it. Neither will your tracing.
        """
        plan = litellm.completion(**CFG.kwargs(), timeout=600, tools=PLAN_SCHEMA, tool_choice="required",
                                  messages=[{"role": "user", "content": question}])
        if meter:
            meter.track(plan)
        plan_calls = plan.choices[0].message.tool_calls or []
        try:
            services = json.loads(plan_calls[0].function.arguments)["services"]
        except (IndexError, KeyError, ValueError, TypeError):
            services = [question]
        results = [json.dumps(run_skill(str(service))) for service in services]
        final = litellm.completion(**CFG.without_server_tools(CFG.kwargs()), timeout=600, messages=[
            {"role": "system", "content": SKILL_BODY},
            {"role": "user", "content": f"{question}\n\nLookup results:\n" + "\n".join(results)}])
        if meter:
            meter.track(final)
        return {"answer": final.choices[0].message.content}

    spawn_started = time.perf_counter()
    spawned = [run_skill(name) for name in ("Atlas", "Ledger", "Warehouse Gateway", "Postgres")]
    mo.md(f"`run_skill('Ledger')` → `{spawned[1]}`  \nFour subprocess spawns took "
          f"**{1000 * (time.perf_counter() - spawn_started):.0f} ms**. If a skill-based path is slow, "
          "look somewhere other than the process boundary first.")
    return (call_with_skill,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **A subagent.** Hand the job to a second model call with its own
    instructions and its own context, and take back only the answer.

    The reason to do this is **context hygiene**. The subagent can read fifty
    documents and return three lines, and the parent conversation never
    carries the rest. The discharge-summary team chose a subagent. Their parent
    conversation is a clinician's, and forty pages of notes must not end up in
    it.

    Served from FastMCP, a subagent is **a tool whose body is a model call**.
    MCP once let a server borrow the client's model for this, a feature called
    "sampling". The protocol has deprecated it, and FastMCP's own advice is to
    call an LLM directly from your tool. That is what `ask_oncall_desk` does.
    """)
    return


@app.cell
def _(CFG, Client, FastMCP, ONCALL, json, litellm):
    def oncall_desk_server(meter=None) -> FastMCP:
        """The discharge-summary team's pattern: a specialist behind one tool."""
        desk = FastMCP("oncall-desk")

        @desk.tool
        def ask_oncall_desk(question: str) -> str:
            """Ask the on-call desk a question in plain words; get back only the answer."""
            reply = litellm.completion(**CFG.without_server_tools(CFG.kwargs()), timeout=600, messages=[
                {"role": "system", "content":
                 "You answer on-call questions from this table and nothing else. Name the team and the "
                 f"channel for each service asked about. If a service is not listed, say so.\n\n{json.dumps(ONCALL, indent=2)}"},
                {"role": "user", "content": question},
            ])
            if meter:
                meter.track(reply)
            return reply.choices[0].message.content

        return desk

    async def call_with_subagent(question: str, lookup=None, meter=None, counter=None) -> dict:
        """Way 3: hand the whole question over and take back only the answer."""
        async with Client(oncall_desk_server(meter)) as desk_client:
            desk_result = await desk_client.call_tool("ask_oncall_desk", {"question": question})
        return {"answer": desk_result.data}

    return call_with_subagent, oncall_desk_server


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The caller never sees the table. For four services that buys nothing. For
    a fifty-page policy document, it keeps those fifty pages out of every
    later turn.

    It has a cost too. The subagent never calls the function. The data is in
    its prompt, so it recites instead of looking anything up. That is cheap,
    and it makes a subagent the wrong shape for anything that has to be
    *current*.

    > **For a full subagent setup, look at `deepagents`**, built on LangGraph.
    > It gives you:
    >
    > - `SubAgent`, a named specialist with its own prompt and tools
    > - `SubAgentMiddleware`, so a parent can spawn them
    > - a todo list, so a long job has state
    > - a virtual filesystem, so a subagent can hand back a *file* instead of
    >   a paragraph
    >
    > The cell above has neither of the last two. `deepagents` earns its
    > dependencies when you have several specialists, long-running work, and
    > something to hand between them.

    ---
    ## ✅ Task 3: Way 4, an MCP server other clients can find

    The capability becomes a **separate process** speaking a standard protocol
    over stdio (the process's standard input and output). Any MCP-aware client
    can then discover and call it: Claude Code, Claude Desktop, or your app.

    **You write it once, and software you did not write can find it.** The
    cost is a process boundary, a handshake, and a deployment to own. The
    on-call rota team chose this. When Sofia asked which client outside their
    codebase discovers it today, the answer was "none yet". Question #2 asks
    you the same thing.

    > **🖼️ Diagram placeholder:** the same server three ways: in-process
    > (`Client(server)`), in its own process over stdio
    > (`oncall_fastmcp_server.py`), and mounted with two other teams' servers
    > behind one `platform` server, where Claude Code and the ops console both
    > connect. Drop it in at
    > `data/diagrams/S10_Six_Ways_to_Call_a_Capability_task3.png`.

    Everything so far used an in-memory client: the same protocol, with no
    process boundary. `oncall_fastmcp_server.py`, next to this notebook, is the
    same server as its own program. The cell starts it as a subprocess, the way
    Claude Code would, and times the difference.
    """)
    return


@app.cell
async def _(Client, Path, mo, oncall_server, time, ui):
    from fastmcp.client import PythonStdioTransport

    SERVER_FILE = Path(mo.notebook_dir()) / "oncall_fastmcp_server.py"
    boundary_rows = []
    for boundary_name, boundary_target in [("in-memory", oncall_server()),
                                           ("stdio subprocess", PythonStdioTransport(SERVER_FILE, keep_alive=False))]:
        connect_started = time.perf_counter()
        async with Client(boundary_target) as boundary_client:
            connected = time.perf_counter()
            boundary_result = await boundary_client.call_tool("who_is_oncall", {"service": "Postgres"})
            called = time.perf_counter()
        boundary_rows.append({"client": boundary_name, "start + handshake (ms)": round(1000 * (connected - connect_started)),
                              "one call (ms)": round(1000 * (called - connected), 1), "result": str(boundary_result.data)})

    mo.vstack([
        mo.md(f"```python\n{SERVER_FILE.read_text(encoding='utf-8')}\n```"),
        ui.table(boundary_rows, title="The same server, either side of a process boundary"),
        mo.md("To use it from Claude Code, add a `.mcp.json` at the repository root. `uv run` picks the "
              "interpreter that has `fastmcp`; a bare `python` often is not it:\n\n```json\n"
              '{\n  "mcpServers": {\n    "oncall": {\n      "command": "uv",\n      "args": ["run", "--group", '
              '"week5", "python", "05_Agent_Architecture/sessions/oncall_fastmcp_server.py"]\n    }\n  }\n}\n```'),
    ])
    return PythonStdioTransport, SERVER_FILE


@app.cell
def _(Client, PythonStdioTransport, SERVER_FILE, run_agent, who_is_oncall):
    class CountingClient:
        """Counts `call_tool` on the client side. The server's own counter is in another process."""

        def __init__(self, client, counter):
            self.client, self.counter = client, counter

        async def list_tools(self):
            return await self.client.list_tools()

        async def call_tool(self, name, *args, **kwargs):
            if self.counter and name.endswith(self.counter.tool_name):
                self.counter.calls += 1
            return await self.client.call_tool(name, *args, **kwargs)

    async def call_with_mcp(question: str, lookup=who_is_oncall, meter=None, counter=None) -> dict:
        """Way 4 for the measurement: the same server in its own process, over stdio; the loop is Way 1's.

        `lookup` is unused: the subprocess runs its own copy of the capability.
        """
        async with Client(PythonStdioTransport(SERVER_FILE, keep_alive=False)) as stdio_client:
            return {"answer": await run_agent(CountingClient(stdio_client, counter), question, meter)}

    return (call_with_mcp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Over stdio, an MCP tool call costs the same two model round trips as Way 1.
    On top of that you pay, once, to start a process and complete a handshake.
    **What MCP changes is who can reach you.** Task 5 measures it anyway, so
    you can see that for yourself: Way 1's numbers, plus the start-up cost,
    and one wrinkle — the counter has to move to the client, because the
    server's middleware is in a process this notebook cannot see into.

    `mount` shows what it does change. Sofia's platform team can put several
    teams' servers behind one, each under a namespace, and give every client in
    the hospital one thing to point at:
    """)
    return


@app.cell
async def _(
    Client,
    DIRECTORY_SPEC,
    FastMCP,
    directory_client,
    oncall_desk_server,
    oncall_server,
    ui,
):
    gateway = FastMCP("platform")
    gateway.mount(oncall_server(), namespace="oncall")
    gateway.mount(FastMCP.from_openapi(DIRECTORY_SPEC, client=directory_client()), namespace="supplier")
    gateway.mount(oncall_desk_server(), namespace="discharge")

    async with Client(gateway) as gateway_client:
        gateway_tools = await gateway_client.list_tools()
    ui.table([{"tool": tool.name, "description": (tool.description or "")[:80]} for tool in gateway_tools],
             title="One endpoint, three teams' capabilities")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🏢 In the enterprise:** an MCP server is a *service*. It has a
    > lifecycle, a health check, an owner, and, over HTTP, authentication. A
    > tool in your own process needs none of that. So the decision is whether a
    > client you did not write needs to discover this capability: Claude Code,
    > another team's agent, an ops console. Discovery is the only thing the
    > process boundary buys. If your app is the only caller, you have taken on
    > a deployment target and a lifecycle problem for nothing.

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #2

    In one to three sentences: who, *outside your codebase*, would need to
    discover your capability in the next year — name the client, not a
    category — and if the honest answer is nobody, what does an MCP server buy
    you that a tool does not?

    **Answer:**

    ---
    ## ✅ Task 4: Way 5, Code Mode, and Way 6, an API that already exists

    Two more ways, and the two the room will ask about most. The table is the
    short version; the cells below it are the long one, with the detail folded
    away.

    | | What it is | Why Sofia's teams want it | What you take on | The number to remember |
    | --- | --- | --- | --- | --- |
    | **Code Mode** | The model gets one tool, `execute`, and writes a program against your functions. Only the program's `return` comes back | One ward-capacity question is forty lookups | You are running code a model wrote: a real sandbox and a security review come first | The tool loop's tokens grow with your data; Code Mode's stay flat. It costs *more* at small records, and wins once records are bigger than its overhead |
    | **UTCP** | Describe the HTTP API that already exists; `from_openapi` generates the tools from its OpenAPI document. Nothing new is deployed | The supplier lookup has been an authenticated API for years | The *caller* holds the credential — does that token get through whatever SSO sits in front of the API? | The same two model calls as a tool. The row to read is the `Authorization` header on the request the client made |

    **Code Mode.** Stop giving the model tools. Give it a **Python namespace**
    and let it write code against it.

    In a tool loop, every intermediate result travels back through the model.
    In Code Mode, the model writes a program that loops, filters, and combines
    results, and only the answer comes back. The bed-management team is
    piloting this because one question about ward capacity is forty lookups.
    Their pilot is also why the board's security member is on the call.

    > **🖼️ Diagram placeholder:** the model sees one tool, `execute`. Its
    > program runs in a sandbox and calls `call_tool("who_is_oncall", …)` four
    > times against the mounted server; the four records stay inside the
    > sandbox, and only the `return` value crosses back to the model. Beside
    > it, Way 6: the model's call goes through a server generated from an
    > OpenAPI document straight to the existing API, credential on the
    > caller's HTTP client. Drop it in at
    > `data/diagrams/S10_Six_Ways_to_Call_a_Capability_task4.png`.

    FastMCP's `CodeMode` is a *transform*. Put it on a server and every tool
    behind it disappears from the listing, replaced by one tool, `execute`.
    The cell below shows the model's view, then runs two programs by hand with
    no model involved. One returns only what the question needs. The other
    forgets to return.
    """)
    return


@app.cell
async def _(
    CODE_MODE_BRIEF,
    Client,
    CodeMode,
    FastMCP,
    NotASandbox,
    mo,
    oncall_server,
    run_agent,
    server_log,
    who_is_oncall,
):
    def code_mode_server(lookup=who_is_oncall, counter=None) -> FastMCP:
        """Way 5: the on-call server mounted behind one `execute` tool."""
        bed = FastMCP("bed-management", transforms=[CodeMode(
            sandbox_provider=NotASandbox(), discovery_tools=[], execute_description=CODE_MODE_BRIEF)])
        bed.mount(oncall_server(lookup, counter))
        return bed

    async def call_with_code_mode(question: str, lookup=who_is_oncall, meter=None, counter=None) -> dict:
        """The model must write a program on its first turn; the loop is otherwise Way 1's."""
        async with Client(code_mode_server(lookup, counter)) as code_client:
            return {"answer": await run_agent(code_client, question, meter, first_choice="required")}

    BY_HAND = ('teams = []\nfor name in ["Atlas", "Postgres"]:\n'
               '    record = await call_tool("who_is_oncall", {"service": name})\n'
               '    teams.append(record["team"])\nreturn teams')
    with server_log() as by_hand_log:
        async with Client(code_mode_server()) as by_hand_client:
            code_listing = [tool.name for tool in await by_hand_client.list_tools()]
            returned = await by_hand_client.call_tool("execute", {"code": BY_HAND})
            forgot = await by_hand_client.call_tool("execute", {"code": BY_HAND.rsplit("\n", 1)[0]}, raise_on_error=False)

    mo.vstack([
        mo.md(f"**Tools the model sees:** `{code_listing}`\n\n```python\n{BY_HAND}\n```\n\n"
              f"→ `{returned.content[0].text}`\n\n**Without the last line:** `{forgot.content[0].text}`"),
        mo.accordion({"📚 The server's log for the program that forgot to return":
                      mo.md("```text\n" + "\n".join(by_hand_log) + "\n```")}),
    ])
    return (call_with_code_mode,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The second program is why `NotASandbox` refuses a `None`. Hand a model an
    empty result and it may make the answer up. This is Task 1's rule applied
    to a program: a failure is a message. What the runner is, what it is not,
    and the one mistake it repairs are in the fold below.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion({"📚 Go deeper: what `NotASandbox` repairs, why it is not a sandbox, and the security review": mo.md(r"""
    There is one mistake `NotASandbox` repairs instead of reporting. A small
    reasoning model sometimes sends its program as a single line full of
    literal `\n` escapes. Told only "unexpected character after line
    continuation", it sends the same line again until the loop gives up. Told
    what is wrong, it recovers only sometimes. A program in that shape cannot
    run as sent, so the runner restores the line breaks and parses again. It
    does this only when the program fails to parse, so a program that parses
    is never touched.

    > **`NotASandbox` is not a sandbox, and FastMCP says so first.** The
    > `SandboxProvider` interface it implements is documented with a warning:
    > implementations **must** run the code in isolation, never with plain
    > `exec()`. Restricted builtins make an escape harder, not impossible.
    > That namespace has no `import`, no file access, and no network. A
    > determined input can still find a way out of a Python `exec`.
    >
    > **It also cannot be interrupted.** Nothing above limits *time*. A model
    > that emits `while True:` hangs this cell until you restart the kernel,
    > and a Python thread cannot be killed. FastMCP's default provider runs the
    > code in `pydantic-monty` (the `fastmcp[code-mode]` extra) with a
    > 30-second and 100 MB limit out of the box. A real timeout needs real
    > isolation, so you get both from the same place.

    > **🏢 In the enterprise:** Code Mode means running code a model wrote.
    > Expect that to need a security review before it is an architecture
    > decision. Can you run untrusted code in a subprocess, a container, or a
    > WASM runtime with no filesystem and no egress, and get that approved? If
    > not, the token savings Task 5 measures go in your decision log as the
    > reason you *would* switch once the sandbox exists. Rejecting Code Mode
    > for a security reason is a fine answer. Say so plainly.
    """)})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Way 6, UTCP.** The idea behind the Universal Tool Calling Protocol: **if
    the capability is already an HTTP API, call it.** A description says how,
    and the client makes the request itself. There is no wrapper server, no
    second deployment, and no lifecycle to own.

    That describes many enterprise capabilities. The service exists, it has an
    owner, and it has been in production for years. The only thing missing is
    a description a model can read. The supplier-invoice team's lookup has
    been an authenticated HTTP API for years, which is why they have built
    nothing at all.

    In FastMCP the description is the API's own **OpenAPI document**, the
    machine-readable spec many HTTP APIs already publish.
    `FastMCP.from_openapi` reads it and generates the tools in the caller's
    process, around the caller's HTTP client. Nothing is written by hand and
    nothing new is deployed.
    """)
    return


@app.cell
async def _(
    Client,
    DIRECTORY_SPEC,
    FastMCP,
    directory_client,
    mo,
    run_agent,
    ui,
    who_is_oncall,
):
    async def call_with_utcp(question: str, lookup=who_is_oncall, meter=None, counter=None) -> dict:
        """Way 6: tools generated from the API's OpenAPI document; the loop is Way 1's."""
        described = FastMCP.from_openapi(DIRECTORY_SPEC, client=directory_client(lookup), name="supplier")
        if counter:
            described.add_middleware(counter)
        async with Client(described) as described_client:
            return {"answer": await run_agent(described_client, question, meter)}

    requests_seen = []
    async with Client(FastMCP.from_openapi(DIRECTORY_SPEC, client=directory_client(requests_seen=requests_seen))) as api_client:
        api_tool = (await api_client.list_tools())[0]
        api_result = await api_client.call_tool("who_is_oncall", {"service": "Warehouse Gateway"})

    mo.vstack([
        mo.md(f"**Generated from the document:** `{api_tool.name}` — {api_tool.description}"),
        ui.table(requests_seen, title="The request the caller's client actually made"),
        mo.md(f"**Result:** `{api_result.content[0].text}`"),
    ])
    return (call_with_utcp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read the URL. `Warehouse Gateway` went out as `Warehouse%20Gateway`,
    encoded by the generated client, so you did not have to remember to write
    that code. Read the second column. The credential is on the **caller's**
    HTTP client.

    - **What you get:** every HTTP service your firm already runs becomes
      callable without building anything.
    - **What you take on:** the client makes the request, so the client holds
      the credential. If SSO sits in front of that endpoint, have that
      conversation before you promise a date.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion({"📚 Go deeper: the API that already exists, in the enterprise": mo.md(r"""
    > **🏢 In the enterprise:** many capabilities at work already exist as an
    > authenticated HTTP API with an owner and years of production behind it.
    > A description makes it callable. A hand-built MCP server rebuilds it as a
    > second service that forwards calls. So the decision is who holds the
    > credential. With a description, the *client* makes the request, and it
    > needs a token that gets through whatever SSO sits in front of that API.
    > Have that conversation with the platform team before you promise a
    > delivery date.
    """)})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## ✅ Task 5: Measure them, then grow the data

    Six implementations, two questions, one counter. Watch two numbers:
    **how many times the capability actually ran**, and how much of that work
    had to travel through the model.

    > **🖼️ Diagram placeholder:** five lanes, one per way, each showing model
    > calls as boxes on the model side and capability calls as ticks on the
    > server side; the counter middleware sits on the server, so the skill's
    > subprocess and the subagent's prompt are outside its view. Drop it in at
    > `data/diagrams/S10_Six_Ways_to_Call_a_Capability_task5.png`.
    """)
    return


@app.cell
def _(
    CapabilityCounter,
    Meter,
    call_with_code_mode,
    call_with_mcp,
    call_with_skill,
    call_with_subagent,
    call_with_tool,
    call_with_utcp,
    time,
    who_is_oncall,
):
    WAYS = [
        ("Tool", call_with_tool),
        ("MCP (stdio)", call_with_mcp),
        ("Skill", call_with_skill),
        ("Subagent", call_with_subagent),
        ("Code Mode", call_with_code_mode),
        ("UTCP", call_with_utcp),
    ]
    PLAIN = str.maketrans("", "", "*|#`-")  # the answer column, readable on a projector

    async def measure(way_fn, question: str, lookup=who_is_oncall) -> dict:
        """Run one way, counting model calls on the meter and capability calls on the server."""
        meter, counter = Meter(), CapabilityCounter("who_is_oncall")
        started = time.perf_counter()
        result = await way_fn(question, lookup, meter, counter)
        return {
            "model calls": meter.calls,
            "capability calls": counter.calls,
            "seconds": round(time.perf_counter() - started, 1),
            "tokens": meter.tokens,
            "answer": " ".join(str(result.get("answer")).translate(PLAIN).split())[:70],
        }

    return WAYS, measure


@app.cell
def _(QUESTION_1, QUESTION_4, mo):
    run_compare = mo.ui.run_button(label="Measure six architectures on both questions")
    mo.vstack([mo.md(f"**One lookup:** _{QUESTION_1}_\n\n**Four lookups:** _{QUESTION_4}_"), run_compare])
    return (run_compare,)


@app.cell
async def _(QUESTION_1, QUESTION_4, WAYS, measure, mo, run_compare, ui):
    mo.stop(not run_compare.value, mo.md("Press to run. **About twenty-two model calls.** "
                                         "Your numbers will differ from anyone else's — that is the point."))

    RESULTS = {}
    for lookup_label, question_text in [("1 lookup", QUESTION_1), ("4 lookups", QUESTION_4)]:
        for way_name, way_fn in ui.track(WAYS, label=f"Measuring — {lookup_label}"):
            RESULTS[(lookup_label, way_name)] = {"way": way_name, **await measure(way_fn, question_text)}

    mo.vstack([
        ui.table([RESULTS[(label, name)] for name, _ in WAYS], title=f"**{label}**")
        for label in ("1 lookup", "4 lookups")
    ])
    return (RESULTS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Read the `4 lookups` table before you read anything else

    **The `capability calls` column is the same number for every architecture
    that reaches the server at all.** Four lookups means four invocations,
    whether the model asked for them one at a time, all at once, or wrote a
    loop. The work is the same. What changes is how much of it crossed the
    model boundary.

    Three things to check against your own output:

    **1. How many tool calls did the model make in a single turn?** If `Tool`
    cost you 2 model calls for 4 lookups, your model emits parallel tool calls.
    The common rule of thumb, *"N tools means N+1 round trips"*, does not
    apply to it. It is 2 either way. This depends on your model and your
    server's tool-call parser, so measure it on yours.

    **2. `Subagent` shows `capability calls` of 0.** It never called the
    function. The table is in its prompt and it is reciting. Cheap, and stale
    the moment the data changes.

    **3. `Skill` also shows 0, for the opposite reason.** It ran the lookup four
    times, in a subprocess, where no counter on any server can see. That is the
    cost of putting a capability on the other side of a process boundary.

    **4. `MCP (stdio)` matches `Tool` on both counts and costs a little more
    time** — the process start and the handshake, once. Its capability calls
    are counted on the *client*, because the server's middleware is in a
    process this notebook cannot see into: the same blind spot the skill has,
    handled by moving the counter to the side you do run. You will meet it
    again with every MCP server you did not write.

    Now the sweep. The token column already separates the ways. Is that gap
    fixed, or does it grow? Same four lookups. The only change is how much data
    each lookup returns: a bare record, then one with a rota attached, then one
    with a full rota. Nothing else moves.
    """)
    return


@app.cell
def _(mo):
    run_scale = mo.ui.run_button(label="Sweep three payload sizes × two architectures")
    run_scale
    return (run_scale,)


@app.cell
async def _(
    QUESTION_4,
    call_with_code_mode,
    call_with_tool,
    json,
    measure,
    mo,
    run_scale,
    ui,
    who_is_oncall,
):
    mo.stop(not run_scale.value, mo.md("Press to run. **About twenty-four model calls**: the tool loop "
                                       "once per size, Code Mode three times."))

    def with_rota(shifts: int):
        """The same lookup, returning a realistically sized record."""
        def lookup(service: str) -> dict:
            record = dict(who_is_oncall(service))
            if "error" in record:
                return record
            record["rota"] = [
                {"engineer": f"eng-{index:02d}", "shift": f"2026-08-{index + 1:02d}T09:00Z",
                 "phone": f"+1-555-01{index:02d}", "backup": f"eng-{index + 50:02d}"}
                for index in range(shifts)
            ]
            return record
        return lookup

    scale_rows = []
    for shift_count in ui.track([0, 8, 24], label="Growing the payload"):
        sized_lookup = with_rota(shift_count)
        # Code Mode three times: what it costs depends on the program the model writes each time.
        code_mode_runs = sorted([(await measure(call_with_code_mode, QUESTION_4, sized_lookup))["tokens"]
                                 for _ in range(3)])
        scale_rows.append({"record size": f"{len(json.dumps(sized_lookup('atlas')))} B",
                           "Tool": (await measure(call_with_tool, QUESTION_4, sized_lookup))["tokens"],
                           "Code Mode": code_mode_runs[1], "Code Mode, worst of 3": code_mode_runs[-1]})

    peak_tokens = max(max(row["Tool"], row["Code Mode"]) for row in scale_rows) or 1
    ui.table(
        [{"record size": row["record size"],
          "Tool": row["Tool"], "": "█" * max(int(40 * row["Tool"] / peak_tokens), 1),
          "Code Mode (median of 3)": row["Code Mode"], " ": "█" * max(int(40 * row["Code Mode"] / peak_tokens), 1),
          "Code Mode, worst of 3": row["Code Mode, worst of 3"]}
         for row in scale_rows],
        title="Tokens for the same four lookups, as each result grows",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The tool loop scales with your data. Code Mode stays flat!**

    Every result a tool returns is read back into the conversation. The
    context carries all four records whether the answer needed one field or
    all of them. In Code Mode, the four records live inside the sandbox while
    the program runs and never go into a message. Only the `return` value
    comes back.

    Read the first row as carefully as the last. With a bare record, Code Mode
    can cost *more* than the tool loop. Its description and the program it
    writes are a fixed price, paid before any data moves. You only come out
    ahead once your records are bigger than that overhead.

    Parallel tool calls already cut the round trips. Code Mode's advantage is
    that **the intermediate data never enters the context at all**, and real
    capabilities return a lot of intermediate data. Four dictionary lookups is
    the smallest possible demonstration. Swap in a search API, a database
    query, or a document fetch and the slope gets steeper.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion({"📚 Go deeper: the worst-of-3 column, and why the tool description is part of the architecture": mo.md(r"""
    The flat line depends on the *program* the model writes. A program that
    returns whole records sends them straight back into the context, and that
    run costs more than the tool loop it was meant to beat. `CODE_MODE_BRIEF`
    prevents this. The sentence that does it explains *why*: whatever you
    return is sent back to you in full. Drafts of the brief that said what to
    return, but not why, got whole records back now and then.

    So Code Mode moves cost into code a model writes on every request. Judge
    it by the worst run, and treat the tool description as part of the
    architecture.
    """)})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #3

    The sweep above grew a record from 118 bytes to 2.5 KB. In one to three
    sentences: roughly how many bytes does *your* endpoint really return per
    call — the retrieved passages with their sources, the whole record — and
    how many calls does one request need? Put those two numbers on the slope
    above and say which architecture's token bill you are actually paying.

    **Answer:**

    ---
    ## ✅ Task 6: The comparison, and Sofia's page for the board

    This is Sofia's page for the board. The table covers what no counter
    reports: the judgement you form by building all six.

    > **🖼️ Diagram placeholder:** the six ordering questions as a vertical
    > decision path, each "yes" exiting sideways to its way (UTCP, MCP, Code
    > Mode, skill, subagent), "otherwise" at the bottom landing on a tool; the
    > six teams placed where Sofia's recommendation puts them. Drop it in at
    > `data/diagrams/S10_Six_Ways_to_Call_a_Capability_task6.png`.

    | | Tool | Skill | Subagent | MCP | Code Mode | UTCP |
    | --- | --- | --- | --- | --- | --- | --- |
    | **Tokens as results grow** | scales | scales | n/a | scales | **flat** | scales |
    | **Extra process** | no | subprocess | no | **yes** | sandbox | no |
    | **Discoverable by other clients** | no | no | no | **yes** | no | **yes** |
    | **Editable by a non-engineer** | no | **yes** | prompt only | no | no | manifest |
    | **Keeps parent context clean** | no | no | **yes** | no | **yes** | no |
    | **Blast radius if it misbehaves** | low | medium | low | low | **high** | medium |
    | **Auth story** | in-process | in-process | in-process | server holds it | in-process | **client holds it** |
    | **You maintain** | a function | a directory | a prompt | **a service** | **a sandbox** | a manifest |

    The measured half appears below once Task 5 has run. Until you press
    Task 5's button, it stays greyed out.
    """)
    return


@app.cell
def _(RESULTS, ui):
    # The measured half, from your run rather than transcribed by hand.
    ui.table(
        [{"": metric} | {
            way: RESULTS[(question_label, way)][key]
            for way in ("Tool", "MCP (stdio)", "Skill", "Subagent", "Code Mode", "UTCP")
        } for metric, question_label, key in (
            ("Model calls (1 lookup)", "1 lookup", "model calls"),
            ("Model calls (4 lookups)", "4 lookups", "model calls"),
            ("Capability calls (4 lookups)", "4 lookups", "capability calls"),
            ("Tokens (4 lookups)", "4 lookups", "tokens"),
        )],
        title="Measured — MCP is Tool's arithmetic plus a process, and now you can see it",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Choosing, in the order the questions actually matter

    1. **Does it already exist as an HTTP API?** UTCP. You describe it instead
       of building it. Otherwise you would build a service that forwards calls.
       Settle who holds the credential first.
    2. **Does anything outside your codebase need to discover this?** MCP.
       Discovery is what the process boundary buys, and the only thing.
    3. **Does one request need several calls, or calls that return a lot?** Code
       Mode. The intermediate data stays out of the context.
    4. **Does the knowledge change more often than the code?** A skill. A
       domain expert can edit policy in markdown. A constant in Python needs
       an engineer and a deploy.
    5. **Does the work read a lot to produce a little?** A subagent, for the
       context it saves.
    6. **Otherwise: a tool.** It is the boring answer, and it is usually right.

    > **Don't reach for MCP just because it is the one people have heard
    > of.** MCP earns its cost when a client you did not
    > write needs to discover your capability. If your app is the only caller,
    > you have taken on a deployment target and a lifecycle problem for nothing.

    Sofia walks the list for each team:

    - **Supplier invoices:** already an API, so UTCP, plus a conversation about
      who holds the credential.
    - **On-call rota:** the one capability three teams and Claude Code all
      want, so MCP, owned by platform.
    - **Bed management:** Code Mode, *only once* the sandbox passes security
      review. Task 5's token slope is the number that justifies the review.
    - **Pharmacy:** keeps its skill.
    - **Discharge summaries:** keep their subagent.
    - **IT service desk:** keeps its tool, because a tool was right.

    Six teams, six answers, one ordering. The board gets the six questions and
    the numbers, and no "it depends"!

    ---
    ### 🧑‍🤝‍🧑 Discuss: ❓ Question #4

    Walk the six questions above for *your* endpoint. In one to three
    sentences: which one is the first "yes" that is not "otherwise", what way
    does that select as the alternative worth building, and what is the
    condition — a second client, a response size, a call count, a review
    passing — under which you would switch to it?

    **Answer:**

    ---
    ## 🏗️ By the End of the Sesh

    The code from the start, now that every line has been unrolled. The
    capability, the counter, the loop, the API and the sandbox are defined in
    the cells above it.

    ```python
    sesh_counter = CapabilityCounter("who_is_oncall")
    oncall = FastMCP("oncall", middleware=[sesh_counter])
    oncall.tool(who_is_oncall)                                       # Way 1: the schema comes from the signature
    oncall.add_provider(SkillsDirectoryProvider(roots=SKILLS_DIR))   # Way 2: a directory a pharmacist edits, served
    bed_management = FastMCP("bed-management", transforms=[CodeMode(
        sandbox_provider=NotASandbox(), discovery_tools=[], execute_description=CODE_MODE_BRIEF)])
    bed_management.mount(oncall)                                     # Way 5: the same tool, behind one `execute`
    directory = FastMCP.from_openapi(DIRECTORY_SPEC, client=directory_client())  # Way 6: an API that already exists
    platform = FastMCP("platform")                                   # Way 4: one server any MCP client can discover
    platform.mount(oncall, namespace="oncall")
    platform.mount(directory, namespace="directory")

    async with Client(platform) as sesh_client:
        sesh_discovered = [tool.name for tool in await sesh_client.list_tools()]
        sesh_discovered += [str(resource.uri) for resource in await sesh_client.list_resources()]
    sesh_rows = []
    for sesh_way, sesh_server, sesh_choice in [("Tool", oncall, "auto"), ("Code Mode", bed_management, "required")]:
        sesh_meter, sesh_counter.calls = Meter(), 0
        async with Client(sesh_server) as sesh_client:
            sesh_answer = await run_agent(sesh_client, QUESTION_4, sesh_meter, first_choice=sesh_choice)
        sesh_rows.append({"way": sesh_way, "model calls": sesh_meter.calls, "capability calls": sesh_counter.calls,
                          "tokens": sesh_meter.tokens, "answer": str(sesh_answer)[:90].replace("\n", " ")})
    ```

    - `oncall.tool(who_is_oncall)` is Task 1: the schema is generated, and a
      name the server does not have comes back as a message.
    - `SkillsDirectoryProvider` is Task 2's skill. Task 2's subagent is the one
      way left out of this block. It is a tool too, so on `oncall` the model
      would be offered it beside `who_is_oncall` and the measurement would blur.
    - `platform.mount(...)` is Task 3: one server for every client you did not
      write.
    - `CodeMode` and `from_openapi` are Task 4. `sesh_counter` and `Meter` are
      Task 5, where the stdio server from Task 3 joins the chart, and the
      comparison they feed is Task 6.

    ---
    ## 🏭 What we Built vs. What's in Production

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Tool schema | Generated from the signature by FastMCP | The same, with the docstring reviewed like any API |
    | Dispatch | Every failure returned as a message | The same, plus `mask_error_details=True` so internals stay on the server |
    | Skill | A directory served as `skill://` resources | Skills in a repo with review, so policy changes are audited |
    | Subagent | A tool whose body is a model call | Its own evals — a harness applies to a subagent too |
    | MCP server | In-memory, stdio, and one `mount` | Over HTTP (`server.run(transport="http")`) with auth, health checks, and a deployment somebody owns |
    | Code Mode | `CodeMode` with `NotASandbox` | `fastmcp[code-mode]`'s Monty provider, or a container — no filesystem, no egress, a hard timeout |
    | UTCP | `from_openapi` over an in-process stand-in | The real base URL, a credential from your identity provider, retries per route |
    | Measurement | Middleware counters, pressed once | The same middleware in production, per request, on a dashboard |

    The numbers only stay useful if you keep collecting them as the data
    grows. A counter on every request also answers the next team's question
    without another month of building six things.

    ---
    ## 👋 Conclusion

    You put one function behind a model six ways with FastMCP and measured
    where the differences really are:

    - A generated schema removed one class of failure, and an MCP client
      turned the rest into messages.
    - Parallel tool calls removed most of the round-trip cost.
    - The subagent's zero capability calls was recitation. The skill's zero
      was a process boundary the counter could not see through.
    - MCP changed who can reach you. The arithmetic stayed the same.
    - Code Mode kept intermediate data out of the context. It pays a fixed
      overhead and wins once records grow.

    The six ordering questions let you fill in the comparison table without
    a preference.

    To point this at your own app, swap `who_is_oncall` for your capability in
    `oncall_server`. Take the `call_with_*` that the ordering picked, and run
    `measure` over both at the response size your endpoint really returns.
    The number that comes out is the *why* column of your decision.

    Now build 🏗️, ship 🚢, and share 📤
    [this week's challenge](../challenge/README.md).

    ---
    ## 📖 Official Documentation

    | Tool | Used here for | Docs |
    | --- | --- | --- |
    | FastMCP tools | `FastMCP`, `server.tool`, the schema generated from a signature | [gofastmcp.com — tools](https://gofastmcp.com/servers/tools) |
    | FastMCP client | `Client`, in-memory and over stdio | [gofastmcp.com — client](https://gofastmcp.com/clients/client) |
    | FastMCP middleware | `Middleware` for the counter, `ResponseLimitingMiddleware` | [gofastmcp.com — middleware](https://gofastmcp.com/servers/middleware) |
    | FastMCP composition | `mount` with a namespace | [gofastmcp.com — composition](https://gofastmcp.com/servers/composition) |
    | FastMCP skills | `SkillsDirectoryProvider` | [gofastmcp.com — skills](https://gofastmcp.com/servers/providers/skills) |
    | FastMCP Code Mode | `CodeMode`, `SandboxProvider` | [gofastmcp.com — Code Mode](https://gofastmcp.com/servers/transforms/code-mode) |
    | FastMCP OpenAPI | `FastMCP.from_openapi` | [gofastmcp.com — OpenAPI](https://gofastmcp.com/integrations/openapi) |
    | LiteLLM | `completion(tools=...)` — every model call | [docs.litellm.ai — function calling](https://docs.litellm.ai/docs/completion/function_call) |
    | MCP | the protocol every client and server here speaks | [modelcontextprotocol.io](https://modelcontextprotocol.io/docs/getting-started/intro) |
    | UTCP | the idea behind Way 6: describe the API, call it directly | [utcp.io](https://www.utcp.io/) |
    """)
    return


if __name__ == "__main__":
    app.run()
