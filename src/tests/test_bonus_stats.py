"""Tests for the B4 ablation stats (bonus/stats.py) and the pruned baseline."""

from __future__ import annotations

from pathlib import Path

import pytest

from bonus import stats
from bonus.swarm_pruned import run_claim as pruned_run
from lab8.shapes.swarm_reference import run_claim as swarm_run
from tests.conftest import CLAIMS


def _trials(spec: dict[str, list[tuple[str, int, bool]]]) -> list[dict]:
    rows = []
    for shape, cells in spec.items():
        for claim_id, seed, passed in cells:
            rows.append(
                {"shape": shape, "claim_id": claim_id, "seed": seed, "passed": passed, "cost_estimate": 10.0}
            )
    return rows


# --- bonus/stats.py ---------------------------------------------------------------


def test_bootstrap_ci_is_tight_when_every_trial_passes():
    trials = _trials({"perfect": [("C-1", s, True) for s in (11, 22, 33)]})
    ci = stats.bootstrap_pass_rate_ci(trials, "perfect", iterations=500)
    assert ci["pass_rate"] == 1.0
    assert ci["ci_low"] == 1.0 and ci["ci_high"] == 1.0


def test_bootstrap_ci_brackets_the_point_estimate():
    # Two claims: one always passes, one always fails -> point 0.5.
    trials = _trials(
        {"half": [("C-1", s, True) for s in (11, 22)] + [("C-2", s, False) for s in (11, 22)]}
    )
    ci = stats.bootstrap_pass_rate_ci(trials, "half", iterations=2000)
    assert ci["pass_rate"] == 0.5
    assert ci["ci_low"] <= 0.5 <= ci["ci_high"]
    assert ci["ci_low"] == 0.0 and ci["ci_high"] == 1.0  # resampling 2 claims gives extremes


def test_mcnemar_no_discordant_pairs_is_not_significant():
    trials = _trials(
        {
            "a": [("C-1", 11, True), ("C-2", 11, False)],
            "b": [("C-1", 11, True), ("C-2", 11, False)],
        }
    )
    m = stats.mcnemar_exact(trials, "a", "b")
    assert m["discordant"] == 0
    assert m["p_value"] == 1.0
    assert m["significant_at_0.05"] is False


def test_mcnemar_counts_direction_of_the_single_disagreement():
    trials = _trials(
        {
            "base": [("C-1", 11, False)],
            "fixed": [("C-1", 11, True)],
        }
    )
    m = stats.mcnemar_exact(trials, "base", "fixed")
    assert m["only_fixed"] == 1 and m["only_base"] == 0
    assert m["discordant"] == 1


# --- bonus/swarm_pruned.py: same decisions as swarm, no model calls ----------------


@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
def test_pruned_matches_swarm_status_but_spends_no_model_calls(public_db, seed):
    for row in CLAIMS:
        cid = row["claim_id"]
        base = swarm_run(cid, seed=seed, store_path=str(public_db))
        # Fresh store so the pruned run is not blocked by the swarm's ledger write.
        pr = pruned_run(cid, seed=seed, store_path=str(public_db))
        assert pr.model_calls == 0, f"{cid} s{seed} spent a model call"
        assert pr.status == base.status, f"{cid} s{seed}: {pr.status} != {base.status}"
