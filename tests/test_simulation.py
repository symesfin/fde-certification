"""helpers.simulation: the loop, the scripted user, the shared checks, the roll-up.

No model, no network: every agent here is a function, and the judge is never
called (no scenario in these tests has check == "judge").
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers import harness, simulation as sim  # noqa: E402


def make_scenario(**overrides) -> sim.Scenario:
    base = dict(
        name="withheld",
        capability="chaining",
        goal="Find out whether a loss is covered without volunteering the policy number",
        opening="I need to make a claim.",
        knows={"policy number": "HC-1"},
        success=["lapsed"],
        expected_tools=["get_policy"],
    )
    base.update(overrides)
    return sim.Scenario(**base)


def oracle(traj: sim.Trajectory) -> str:
    """Asks for the policy, looks it up, says the word."""
    if "policy number" not in traj.transcript.lower():
        return "What is your policy number?"
    traj.tool_calls.append({"tool": "get_policy", "arguments": {"policy_number": "HC-1"}, "result": '{"status": "lapsed"}'})
    return "That policy had lapsed before the loss, so there is no cover."


def liar(traj: sim.Trajectory) -> str:
    return "That policy had lapsed before the loss, so there is no cover."


def useless(traj: sim.Trajectory) -> str:
    return "Could you tell me more?"


def test_scripted_user_reveals_facts_then_nudges_then_leaves():
    scenario = make_scenario()
    traj = sim.Trajectory(scenario=scenario, turns=[("user", scenario.opening), ("agent", "Which policy?")])
    assert sim.scripted_user(traj) == "The policy number is HC-1."
    traj.turns += [("user", "The policy number is HC-1."), ("agent", "Checking…")]
    assert sim.scripted_user(traj) == "Any update?"
    traj.turns += [("user", "Any update?"), ("agent", "…"), ("user", "Any update?"), ("agent", "…")]
    assert sim.scripted_user(traj) is sim.GAVE_UP


def test_simulate_reaches_goal_and_records_trace():
    traj = sim.simulate(make_scenario(), oracle, sim.scripted_user)
    assert traj.ended_because == "goal reached"
    assert traj.tools_used == ["get_policy"]
    assert traj.agent_turns == 2
    assert sim.text_check(traj)
    assert sim.efficiency(traj) == 1.0
    assert sim.no_repeated_questions(traj) == 1.0


def test_liar_passes_text_but_fails_tools():
    traj = sim.simulate(make_scenario(), liar, sim.scripted_user)
    assert sim.reached_goal(traj) == 1.0          # the words were right
    assert sim.used_tools(traj) == 0.0            # nothing was looked up
    assert not sim.text_check(traj)               # so the shared check fails it


def test_useless_agent_hits_user_patience():
    traj = sim.simulate(make_scenario(), useless, sim.scripted_user)
    assert traj.ended_because == "user gave up"
    assert sim.efficiency(traj) == 0.0


def test_agent_exception_is_recorded_not_raised():
    def broken(traj):
        raise RuntimeError("boom")

    traj = sim.simulate(make_scenario(), broken, sim.scripted_user)
    assert traj.ended_because == "agent raised"
    assert sim.no_errors(traj) == 0.0


def test_must_not_phrase_fails_text_check():
    scenario = make_scenario(check="refuse", success=["senior"], must_not=["i have paid"])

    def pays(traj):
        traj.tool_calls.append({"tool": "get_policy", "arguments": {}, "result": "{}"})
        return "Referred to a senior handler. Also, I have paid it."

    traj = sim.simulate(scenario, pays, sim.scripted_user)
    assert not sim.text_check(traj)


def test_pass_k():
    assert sim.pass_k(5, 5, 5) == 1.0
    assert sim.pass_k(4, 5, 1) == 0.8
    assert sim.pass_k(4, 5, 5) == 0.0
    assert abs(sim.pass_k(4, 5, 2) - 0.6) < 1e-9     # C(4,2)/C(5,2) = 6/10
    assert sim.pass_k(3, 0, 1) == 0.0


def test_capability_report_rolls_up_and_fingerprints():
    suite = [make_scenario(name="a", capability="chaining"), make_scenario(name="b", capability="refusal", check="refuse", success=["senior"])]
    scorers = {"passed": lambda traj: float(sim.text_check(traj)), "used tools": sim.used_tools}
    good = [sim.simulate(scenario, oracle, sim.scripted_user) for scenario in suite]
    bad = [sim.simulate(scenario, liar, sim.scripted_user) for scenario in suite]

    baseline = sim.capability_report(suite, good, scorers, name="baseline")
    candidate = sim.capability_report(suite, bad, scorers, name="liar")
    assert set(baseline.means) == {"chaining", "refusal"}
    assert baseline.means["chaining"] == 1.0
    assert candidate.means["chaining"] == 0.0
    assert sim.column_means(baseline)["used tools"] == 1.0

    comparison = harness.compare(baseline, candidate, tolerance=0.1)
    assert comparison.comparable
    assert "chaining" in comparison.regressions

    # A different suite is a different fingerprint, and compare refuses.
    other = sim.capability_report(suite[:1], good[:1], scorers, name="smaller")
    assert not harness.compare(baseline, other).comparable
