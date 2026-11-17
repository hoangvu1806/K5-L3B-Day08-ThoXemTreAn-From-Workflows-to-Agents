"""Focused tests for the single-agent boundary and host handoff."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.runtime import ToolRejected, run_react
from lab8.schemas import Budget
from lab8.shapes.single import run_claim
from tests.conftest import CLAIMS, WORLD


def _store(tmp_path: Path, name: str = "single.sqlite") -> Path:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_react_stops_at_eight_steps_and_does_not_write(tmp_path):
    conn = connect(_store(tmp_path))
    budget = Budget()
    calls = []

    def decide(_observation):
        calls.append(1)
        return {"tool": "lookup_policy", "args": {}}

    outcome = run_react(
        conn, budget, observation={"claim": {"claim_id": "C-001"}},
        decide=decide, max_steps=8, worker=True,
    )
    assert outcome["stopped"] == "step_cap"
    assert len(calls) == 8
    with pytest.raises(ToolRejected):
        from lab8.runtime import dispatch
        dispatch(conn, budget, "issue_refund", {"claim_id": "C-001"}, worker=True)
    conn.close()


def test_single_uses_structured_order_and_host_cap(tmp_path):
    result = run_claim("C-014", seed=11, store_path=str(_store(tmp_path)))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert result.refund_effects[0]["amount_vnd"] == 120000


def test_single_forwards_crash_and_retry_is_idempotent(tmp_path):
    path = _store(tmp_path)
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(path), crash_at="after_effect_before_checkpoint")
    result = run_claim("C-012", seed=11, store_path=str(path))
    assert result.status == "resolved"
    conn = connect(path)
    assert conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"] == 1
    conn.close()
