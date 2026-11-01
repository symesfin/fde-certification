"""Simulated conversations for agent evals — the loop, the users, the roll-up.

Tier 2: `litellm` is imported inside the two functions that need a model
(`make_llm_user`, `binary_judge`), so importing this module costs nothing and
every other function here runs with no key and no network.

Week 4's agent-eval session builds every piece of this from scratch, and that
is the lesson: a trajectory is a trace, a simulated user is just another
system, a verifier reads what the agent *did*. This module is what those
pieces become once a second notebook — or your own app's test suite — needs
them without re-teaching them.

What is here is the part that does not depend on your domain:

    Scenario, Trajectory      the shapes
    simulate(...)             one conversation, recorded as it goes
    scripted_user             deterministic: facts on request, two nudges, leave
    make_llm_user(...)        a model playing the user, same signature
    transcript_agent(...)     wrap a `run_agent(messages, tools)` loop as `agent(traj)`
    text_check, tools_ok      the programmatic checks every domain shares
    binary_judge(...)         one yes/no question to a model, negatives first
    efficiency, no_repeated_questions, used_tools, reached_goal, no_errors
    pass_k(...)               C(c,k)/C(n,k)
    capability_report(...)    trajectories -> a fingerprinted `harness.RunReport`

What is deliberately *not* here, because it is yours: the verifier that reads
your system's state (was anything paid above authority? was the ticket
routed?), the atoms your scenarios are composed from, and the broken agents
you test the harness with. A framework cannot write those either.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import comb
from typing import Callable, Mapping, Sequence

from helpers import harness

# A user can end a conversation two ways, and they mean opposite things.
SATISFIED = "__satisfied__"
GAVE_UP = None


@dataclass
class Scenario:
    """One thing a user wants, what they know, and how success is checked."""

    name: str
    capability: str                 # what this scenario probes
    goal: str                       # what the user is trying to achieve
    opening: str                    # their first message
    knows: dict = field(default_factory=dict)      # revealed only if asked
    success: list = field(default_factory=list)    # `text` check: ALL of these must be said
    must_not: list = field(default_factory=list)   # NONE of these may be said
    expected_tools: list = field(default_factory=list)  # tools a correct trajectory calls
    check: str = "text"             # text | refuse | judge
    judge_question: str = ""        # for check == "judge": asks for exactly one of two words
    judge_words: tuple = ("YES", "NO")  # (the word that passes, the word that fails)
    max_turns: int = 6


@dataclass
class Trajectory:
    """One simulated conversation, with the evidence attached."""

    scenario: Scenario
    turns: list = field(default_factory=list)       # (speaker, text)
    tool_calls: list = field(default_factory=list)  # {"tool", "arguments", "result"}
    errors: list = field(default_factory=list)
    ended_because: str = ""

    @property
    def transcript(self) -> str:
        return "\n".join(f"{who}: {text}" for who, text in self.turns)

    @property
    def agent_said(self) -> str:
        return " ".join(text for who, text in self.turns if who == "agent").lower()

    @property
    def tools_used(self) -> list:
        return [call["tool"] for call in self.tool_calls]

    @property
    def agent_turns(self) -> int:
        return sum(1 for who, _ in self.turns if who == "agent")

    @property
    def last_agent_reply(self) -> str:
        return next((text for who, text in reversed(self.turns) if who == "agent"), "")


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

def user_is_satisfied(traj: Trajectory) -> bool:
    """Has the agent said everything the goal required? A substring check --
    cheap, and wrong in one specific way: a right answer in other words fails it."""
    return bool(traj.scenario.success) and all(
        phrase.lower() in traj.agent_said for phrase in traj.scenario.success
    )


def simulate(scenario: Scenario, agent: Callable, user: Callable, max_turns: int | None = None) -> Trajectory:
    """Run one conversation to completion.

    `agent` and `user` are both callables taking the trajectory so far. That
    symmetry is deliberate: the simulated user is just another system, and it
    can be swapped for a scripted one when you want determinism.
    """
    traj = Trajectory(scenario=scenario)
    limit = max_turns or scenario.max_turns
    traj.turns.append(("user", scenario.opening))

    for _ in range(limit):
        try:
            reply = agent(traj)
        except Exception as exc:
            traj.errors.append(f"{type(exc).__name__}: {exc}")
            traj.ended_because = "agent raised"
            return traj
        traj.turns.append(("agent", reply))

        if user_is_satisfied(traj):
            traj.ended_because = "goal reached"
            return traj

        follow_up = user(traj)
        if follow_up is SATISFIED:
            traj.ended_because = "goal reached"   # the user says so, in whatever words
            return traj
        if follow_up is GAVE_UP:
            traj.ended_because = "user gave up"
            return traj
        traj.turns.append(("user", follow_up))

    traj.ended_because = "turn limit"
    return traj


def scripted_user(traj: Trajectory):
    """Deterministic: one known fact per turn, then two nudges, then leave.

    The patience matters. A user who leaves the instant their facts run out
    cannot reveal an agent that is merely slow, and slow is a real failure.
    """
    said = sum(1 for who, _ in traj.turns if who == "user") - 1
    facts = list(traj.scenario.knows.items())
    if said < len(facts):
        key, value = facts[said]
        return f"The {key} is {value}."
    if said < len(facts) + 2:
        return "Any update?"
    return GAVE_UP


USER_PROMPT = """You are role-playing a customer contacting a company's assistant.

Your goal: {goal}

Things you know, and will say ONLY if asked directly:
{knows}

Rules:
- Stay in character. You are a customer who needs something, not an assistant.
- Never volunteer what you know unless asked for it specifically.
- Keep replies to one or two sentences.
- If the assistant has answered your goal, reply exactly: DONE
- If it is going in circles and you have lost patience, reply exactly: GIVE UP

The conversation so far:
{transcript}

Your next message:"""


def make_llm_user(llm_kwargs: Mapping, *, prompt: str = USER_PROMPT, on_token: Callable | None = None, timeout: int = 600) -> Callable:
    """A model playing the user, as a drop-in for `scripted_user`.

    `llm_kwargs` is what the rest of the notebook passes to `litellm.completion`
    (`CFG.kwargs()`). `on_token(traj, partial)` fires as the reply streams in;
    the harness that scores a hundred conversations passes nothing and pays
    nothing for the display.
    """

    def user(traj: Trajectory):
        from litellm import completion  # tier 2: imported at the call site

        known = "\n".join(f"- {key}: {value}" for key, value in traj.scenario.knows.items()) or "- nothing"
        messages = [{"role": "user", "content": prompt.format(goal=traj.scenario.goal, knows=known, transcript=traj.transcript)}]
        if on_token is None:
            reply = (completion(**llm_kwargs, timeout=timeout, messages=messages).choices[0].message.content or "").strip()
        else:
            reply = ""
            for chunk in completion(**llm_kwargs, timeout=timeout, messages=messages, stream=True):
                reply += getattr(chunk.choices[0].delta, "content", None) or ""
                on_token(traj, reply)
            reply = reply.strip()
        if "GIVE UP" in reply.upper():
            return GAVE_UP
        if "DONE" in reply.upper():
            return SATISFIED
        return reply

    return user


def transcript_agent(system_prompt: str, run_agent: Callable, tools=None) -> Callable:
    """Wrap a `run_agent(messages, tools=...) -> (reply, calls)` loop as `agent(traj)`.

    The whole transcript goes in as alternating user/assistant messages, one
    reply comes out, and the tool calls are recorded onto the trajectory.
    `tools=[]` is the same agent with its tools unwired.
    """

    def agent(traj: Trajectory) -> str:
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": "user" if who == "user" else "assistant", "content": text} for who, text in traj.turns
        ]
        reply, calls = run_agent(messages, tools=tools)
        traj.tool_calls.extend(calls)
        return reply

    return agent


# ---------------------------------------------------------------------------
# Scorers: (traj) -> 0..1, or nan for "not this scorer's job"
# ---------------------------------------------------------------------------

def tools_ok(traj: Trajectory) -> bool:
    return all(tool in traj.tools_used for tool in traj.scenario.expected_tools)


def said_all(traj: Trajectory, phrases: Sequence[str]) -> bool:
    return all(phrase.lower() in traj.agent_said for phrase in phrases)


def said_any(traj: Trajectory, phrases: Sequence[str]) -> bool:
    return any(phrase.lower() in traj.agent_said for phrase in phrases)


def text_check(traj: Trajectory) -> bool:
    """The programmatic check every domain shares: expected tools called, every
    success phrase said, no forbidden phrase said. Your own verifier adds the
    assertion about *state* that only your system can answer."""
    scenario = traj.scenario
    return tools_ok(traj) and said_all(traj, scenario.success) and not said_any(traj, scenario.must_not)


def binary_judge(traj: Trajectory, llm_kwargs: Mapping, *, timeout: int = 600, max_tokens: int = 20) -> float:
    """One yes/no question to a model. Classifiers hold; graders drift.

    The scenario's `judge_question` must ask for exactly one of the two words
    in `judge_words`. The failing word is checked first, so a reply like
    "FAILED -- not helpful" cannot pass on the word "helpful".
    """
    scenario = traj.scenario
    if scenario.check != "judge":
        return float("nan")
    from litellm import completion  # tier 2: imported at the call site

    pass_word, fail_word = (word.upper() for word in scenario.judge_words)
    prompt = (
        f"{scenario.judge_question}\n\nConversation:\n{traj.transcript}\n\nTools the assistant called: "
        f"{', '.join(traj.tools_used) or 'none'}\n\nOne word:"
    )
    verdict = (completion(**llm_kwargs, timeout=timeout, messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens).choices[0].message.content or "").upper()
    if fail_word in verdict:
        return 0.0
    return float(pass_word in verdict)


def reached_goal(traj: Trajectory) -> float:
    return float(traj.ended_because == "goal reached")


def used_tools(traj: Trajectory) -> float:
    """Did it look before it spoke? The scorer a guessing agent fails."""
    return float(tools_ok(traj))


def efficiency(traj: Trajectory) -> float:
    """1.0 for a two-turn resolution, decaying after. Getting there in eleven turns is not getting there."""
    return 0.0 if traj.ended_because != "goal reached" else min(1.0, 2 / max(traj.agent_turns, 1))


def no_repeated_questions(traj: Trajectory) -> float:
    """Did it ask for the same thing twice? Invisible in final-answer scoring."""
    stop = {"the", "a", "is", "what", "your", "you", "can", "please"}
    asks = [frozenset(text.lower().split()) - stop for who, text in traj.turns if who == "agent" and "?" in text]
    for index, ask in enumerate(asks):
        for other_ask in asks[index + 1:]:
            if ask and len(ask & other_ask) / len(ask | other_ask) > 0.6:
                return 0.0
    return 1.0


def no_errors(traj: Trajectory) -> float:
    return float(not traj.errors)


def pass_k(successes: int, trials: int, k: int) -> float:
    """The chance that k independent attempts ALL succeed, from c successes in n
    trials: C(c,k)/C(n,k). pass^1 is the ordinary success rate."""
    if trials <= 0 or k <= 0 or k > trials:
        return 0.0
    return comb(successes, k) / comb(trials, k) if successes >= k else 0.0


# ---------------------------------------------------------------------------
# The roll-up: trajectories -> a report the harness can save and compare
# ---------------------------------------------------------------------------

def capability_report(
    suite: Sequence[Scenario],
    trajectories: Sequence[Trajectory],
    scorers: Mapping[str, Callable],
    *,
    name: str,
    passed_key: str = "passed",
    capabilities: Sequence[str] | None = None,
) -> harness.RunReport:
    """Score every trajectory, roll `passed_key` up per capability, and return a
    `harness.RunReport` whose fingerprint covers the scenarios and capabilities --
    so `harness.compare` refuses to compare it against a different suite."""
    names = list(capabilities) if capabilities else sorted({scenario.capability for scenario in suite})
    results = []
    for index, (scenario, trajectory) in enumerate(zip(suite, trajectories)):
        scores = {}
        for label, scorer in scorers.items():
            value = float(scorer(trajectory))
            scores[label] = value if value == value else 0.0  # nan -> 0, so means stay finite
        results.append(harness.Result(
            index=index, input=scenario.opening[:2000], expected=scenario.capability,
            actual=trajectory.transcript[:2000], scores=scores,
        ))
    per_capability = {
        capability: sum(result.scores[passed_key] for result, scenario in zip(results, suite) if scenario.capability == capability)
        / max(1, sum(1 for scenario in suite if scenario.capability == capability))
        for capability in names
    }
    cases = [{"input": scenario.opening, "output": scenario.capability} for scenario in suite]
    return harness.RunReport(
        name=name,
        fingerprint=harness.fingerprint(cases, {capability: None for capability in names}),
        n=len(suite), means=per_capability, results=results,
        meta={"scorers": list(scorers), "rolled_up": passed_key},
    )


def column_means(report: harness.RunReport) -> dict:
    """Mean of every scorer column across the report's results -- the per-scorer
    view next to the per-capability one."""
    if not report.results:
        return {}
    labels = list(report.results[0].scores)
    return {label: sum(result.scores.get(label, 0.0) for result in report.results) / len(report.results) for label in labels}
