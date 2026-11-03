"""Score the utility-bill extraction spike's recorded runs. The whole interface:

    uv run python use_case/evals/run.py                    # model-free, no calls
    uv run python use_case/evals/run.py --judge            # adds the LLM judge (120 calls, measured)
    uv run python use_case/evals/run.py --save-baseline    # rewrites baseline.json

The system under test is a replay: each system reads the spike's recorded
Gemini output for a bill from SPIKE_RESULTS (client repo, outside this one).
Re-running extraction lives in the client repo; this harness scores outputs.

Cases come from golden.private.jsonl (gitignored, real values), utility track.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(HERE)]

import harness as ev  # noqa: E402  (use_case/evals/harness.py: scorers)
from helpers import harness as H  # noqa: E402  (run, save, load, compare)
from helpers.nb import bootstrap  # noqa: E402

MODEL = "gemini-3.5-flash"
BASELINE = HERE / "baseline.json"
STRATEGIES = {"A": "A (single request)", "B": "B (page by page)", "C": "C (hybrid)"}


def load_cases() -> tuple[list[dict], Path]:
    private = HERE / "golden.private.jsonl"
    spike = os.getenv("SPIKE_RESULTS")
    missing = []
    if not private.exists():
        missing.append(f"{private.relative_to(ROOT)} (gitignored; holds the real labels)")
    if not spike or not Path(spike).is_dir():
        missing.append("SPIKE_RESULTS in .env, pointing at the client repo's spikes/extraction")
    if missing:
        sys.exit("Cannot run, missing:\n  - " + "\n  - ".join(missing))
    rows = [json.loads(line) for line in private.read_text().splitlines() if line.strip()]
    cases = [r for r in rows if r.get("track") == "utility"]
    if not cases:
        sys.exit(f"No utility cases in {private.name}; refusing to score an empty set.")
    return cases, Path(spike)


def systems(cases: list[dict], spike: Path) -> dict:
    truth = {c["input"]: c["output"] for c in cases}

    def echo(bill_id: str) -> str:
        return bill_id

    def oracle(bill_id: str) -> str:
        return json.dumps(truth[bill_id])

    def replay(strategy: str, run_dir: str):
        def system(bill_id: str) -> str:
            path = spike / "results" / run_dir / f"{bill_id}__{strategy}__{MODEL}.json"
            return json.dumps(json.loads(path.read_text())["bill"])

        system.__name__ = f"replay_{strategy}_{run_dir}"
        return system

    out = {"echo": echo}
    out |= {STRATEGIES[s]: replay(s, "main") for s in STRATEGIES}
    out["oracle"] = oracle
    return out


def table(rows: dict[str, dict[str, float]], cols: list[str], first: str = "System") -> str:
    lines = [f"| {first} | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    for name, vals in rows.items():
        cells = [
            f"{vals[c]:.2f}" if isinstance(vals.get(c), float) else str(vals.get(c, ""))
            for c in cols
        ]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def pass_k(spike: Path, cases: list[dict], strategy: str = "C") -> tuple[int, int]:
    """Bills fully right in both the main and the repeat run (the 5 statement bills)."""
    by_id = {c["input"]: c for c in cases}
    ids = sorted(
        p.name.split("__")[0]
        for p in (spike / "results" / "repeat2").glob(f"*__{strategy}__{MODEL}.json")
    )
    ok = 0
    for bid in ids:
        runs = [
            json.dumps(
                json.loads(
                    (spike / "results" / d / f"{bid}__{strategy}__{MODEL}.json").read_text()
                )["bill"]
            )
            for d in ("main", "repeat2")
        ]
        ok += all(ev.bill_fully_right(r, by_id[bid]) == 1.0 for r in runs)
    return ok, len(ids)


def detection(scorers: dict) -> tuple[str, int]:
    rows = [
        json.loads(line)
        for line in (HERE / "synthetic.jsonl").read_text().splitlines()
        if line.strip()
    ]
    modes: dict[str, list[dict]] = {}
    for r in rows:
        modes.setdefault(r["failure_mode"], []).append(r)
    out = {}
    for mode, rs in modes.items():
        vals = {"n": len(rs)}
        for label, f in scorers.items():
            caught = sum(
                f(json.dumps(r["corrupted"]), {"input": r["input"], "output": r["original"]}) < 1.0
                for r in rs
            )
            vals[label] = caught / len(rs)
        out[mode + (" (hard)" if rs[0]["hard"] else "")] = vals
    return table(out, ["n", *scorers], first="Failure mode"), len(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--judge", action="store_true", help="add the LLM judge column (makes model calls)"
    )
    ap.add_argument(
        "--save-baseline", action="store_true", help="rewrite baseline.json from strategy C"
    )
    args = ap.parse_args()

    cfg = bootstrap(start=HERE)
    cases, spike = load_cases()
    systems_ = systems(cases, spike)
    cols = list(ev.SCORERS)

    reports = {name: H.run(cases, f, ev.SCORERS, name=name) for name, f in systems_.items()}
    print(f"## Systems, n = {len(cases)} bills, replayed {MODEL} runs\n")
    print(table({n: r.means for n, r in reports.items()}, cols))
    for n, r in reports.items():
        if r.errors and n != "echo":
            print(f"  ⚠️ {n}: {r.errors} cases raised")

    # Headline: strategy C, the system we'd ship.
    c = reports[STRATEGIES["C"]]
    scores = [r.scores[ev.HEADLINE] for r in c.results]
    mean, lo, hi = ev.bootstrap_ci(scores)
    w_lo, w_hi = ev.wilson_ci(int(sum(scores)), len(scores))
    print(
        f"\n## Headline\n\n{ev.HEADLINE} {mean:.2f}, bootstrap 95% CI [{lo:.2f}, {hi:.2f}], "
        f"Wilson 95% CI [{w_lo:.2f}, {w_hi:.2f}], n = {len(scores)} bills"
    )

    ok, n = pass_k(spike, cases)
    print(f"pass^2 (C fully right in both runs): {ok} of {n} statement bills")

    if args.save_baseline:
        report = H.run(
            cases,
            systems_[STRATEGIES["C"]],
            ev.SCORERS,
            name="utility-C-spike",
            meta={
                "model": MODEL,
                "strategy": "C (page classifier, per-page reads, assembly with checks)",
                "bills": len(cases),
                "headline": ev.HEADLINE,
                "label": "spike bills, not held out; replayed recorded runs, not live calls",
                "ci": {"bootstrap_95": [lo, hi], "wilson_95": [w_lo, w_hi], "unit": "bill"},
            },
        )
        # Labels, outputs and bill ids carry real account numbers. Keep a hashed id and the scores.
        for r in report.results:
            r.input = "bill-" + hashlib.sha256(r.input.encode()).hexdigest()[:8]
            r.expected = r.actual = ""
        H.save(report, BASELINE)
        print(f"saved {BASELINE.relative_to(ROOT)}")
    print("\n## compare(baseline.json, this run)\n")
    if BASELINE.exists():
        print(H.compare(H.load(BASELINE), c))
    else:
        print("no baseline.json yet; run with --save-baseline")

    det, n_gen = detection(ev.SCORERS)
    print(
        f"\n## Generated failures\n\nNatural failures in 66 recorded runs: 19 (in 18 runs). Generated: {n_gen}.\n"
    )
    print(det)

    if args.judge:
        run_judge(cfg, cases, systems_)


def run_judge(cfg, cases, systems_) -> None:
    from helpers.llm import CallStats

    stats = CallStats()
    judge = ev.make_judge(cfg, stats=stats)
    view = [ev.judge_view(c) for c in cases]
    cal = judge.calibrate(view, wrong_answer='{"accounts": []}')
    print(f"\n## Judge ({judge.model or cfg.llm_model})\n\ncalibration: {cal}")
    if not cal.passed:
        print("judge failed calibration; not scoring with it")
        print(f"judge calls: {stats.calls} (measured)")
        return

    def judge_scorer(actual, case):
        return judge.score(actual, ev.judge_view(case))

    rows = {}
    for name in ("echo", STRATEGIES["C"], "oracle"):
        rep = H.run(cases, systems_[name], {"judge": judge_scorer}, name=name)
        rows[name] = {"judge": rep.means["judge"]}
    print(table(rows, ["judge"]))
    print(f"separation: echo {rows['echo']['judge']:.2f} / oracle {rows['oracle']['judge']:.2f}")

    det, _ = detection({"amounts": ev.amounts_exact, "judge": judge_scorer})
    print("\nGenerated failures, judge next to amounts_exact:\n")
    print(det)
    print(f"\njudge calls: {stats.calls} (measured), {stats}")


if __name__ == "__main__":
    main()
