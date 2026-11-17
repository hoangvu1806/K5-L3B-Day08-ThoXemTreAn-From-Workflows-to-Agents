"""Stats for the B4 ablation. Standard library only.

Two tools that do not assume a ground-truth oracle beyond pass/fail:

- bootstrap_pass_rate_ci: resample CLAIMS (not trials) with replacement to get a
  95%% CI for a shape's pass rate. Resampling by claim keeps the 5 seeds of one
  claim together, so the CI reflects claim-level, not trial-level, uncertainty.
- mcnemar_exact: paired test between two shapes on the same (claim, seed) cells.
  Uses the exact binomial on the discordant pairs, so it is valid for the few
  disagreements a 70-trial corpus produces.

Run as a module to turn a benchmark trials file into reports/bonus_stats.json:

    python -m bonus.stats --benchmark reports/bonus_ablation.json \
        --baseline swarm --out reports/bonus_stats.json
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from math import comb
from pathlib import Path
from typing import Any


def _by_claim(trials: list[dict], shape: str) -> dict[str, list[bool]]:
    """claim_id -> list of pass flags across seeds, for one shape."""
    out: dict[str, list[bool]] = defaultdict(list)
    for t in trials:
        if t["shape"] == shape:
            out[t["claim_id"]].append(bool(t["passed"]))
    return dict(out)


def bootstrap_pass_rate_ci(
    trials: list[dict], shape: str, *, iterations: int = 10000, seed: int = 20261117
) -> dict[str, float]:
    by_claim = _by_claim(trials, shape)
    claims = list(by_claim)
    point = _pass_rate(by_claim, claims)
    rng = random.Random(seed)
    samples = []
    for _ in range(iterations):
        drawn = [claims[rng.randrange(len(claims))] for _ in claims]
        samples.append(_pass_rate(by_claim, drawn))
    samples.sort()
    lo = samples[int(0.025 * len(samples))]
    hi = samples[int(0.975 * len(samples)) - 1]
    return {"pass_rate": point, "ci_low": lo, "ci_high": hi, "iterations": iterations}


def _pass_rate(by_claim: dict[str, list[bool]], claims: list[str]) -> float:
    passed = total = 0
    for c in claims:
        flags = by_claim[c]
        passed += sum(1 for f in flags if f)
        total += len(flags)
    return passed / total if total else 0.0


def mcnemar_exact(trials: list[dict], shape_a: str, shape_b: str) -> dict[str, Any]:
    """Exact McNemar on paired (claim, seed) cells where exactly one shape passes."""
    a = {(t["claim_id"], t["seed"]): bool(t["passed"]) for t in trials if t["shape"] == shape_a}
    b = {(t["claim_id"], t["seed"]): bool(t["passed"]) for t in trials if t["shape"] == shape_b}
    cells = sorted(set(a) & set(b))
    only_a = sum(1 for k in cells if a[k] and not b[k])  # a passes, b fails
    only_b = sum(1 for k in cells if b[k] and not a[k])  # b passes, a fails
    n = only_a + only_b
    k = min(only_a, only_b)
    # Two-sided exact binomial p-value with p=0.5 on the discordant pairs.
    p = 1.0 if n == 0 else min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / (2 ** n))
    return {
        "pairs": len(cells),
        "only_%s" % shape_a: only_a,
        "only_%s" % shape_b: only_b,
        "discordant": n,
        "p_value": round(p, 6),
        "significant_at_0.05": p < 0.05,
    }


def _shape_summary(trials: list[dict], shape: str) -> dict[str, Any]:
    flags = [bool(t["passed"]) for t in trials if t["shape"] == shape]
    costs = [float(t["cost_estimate"]) for t in trials if t["shape"] == shape]
    successes = sum(flags)
    return {
        "trials": len(flags),
        "successes": successes,
        "pass_rate": successes / len(flags) if flags else 0.0,
        "cost_per_success_vnd": round(sum(costs) / successes, 4) if successes else None,
        **bootstrap_pass_rate_ci(trials, shape),
    }


def analyze(trials: list[dict], baseline: str) -> dict[str, Any]:
    shapes = sorted({t["shape"] for t in trials})
    report: dict[str, Any] = {
        "note": "simulated cost; MockLLM; resampling by claim. Not an API bill.",
        "by_shape": {s: _shape_summary(trials, s) for s in shapes},
        "mcnemar_vs_%s" % baseline: {
            s: mcnemar_exact(trials, baseline, s) for s in shapes if s != baseline
        },
    }
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="B4 stats over a benchmark trials file")
    ap.add_argument("--benchmark", required=True)
    ap.add_argument("--baseline", default="swarm")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.benchmark).read_text(encoding="utf-8"))
    trials = data["trials"]
    report = analyze(trials, args.baseline)
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for shape, s in report["by_shape"].items():
        print(
            f"{shape:28} pass {s['pass_rate']:.3f}  CI[{s['ci_low']:.3f},{s['ci_high']:.3f}]"
            f"  cost/success {s['cost_per_success_vnd']}"
        )
    for shape, m in report["mcnemar_vs_%s" % args.baseline].items():
        print(f"McNemar {args.baseline} vs {shape:20} discordant={m['discordant']} p={m['p_value']}")


if __name__ == "__main__":
    main()
