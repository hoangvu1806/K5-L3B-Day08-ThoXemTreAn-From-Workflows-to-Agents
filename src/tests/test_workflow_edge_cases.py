"""Edge cases for Shape A (workflow): ticket injection, idempotency/crash, trace leaks."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD

SEEDS = [11, 22, 33, 44, 55]
CRASH_POINTS = ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]


def _ledger_rows(store: Path, claim_id: str) -> int:
    conn = connect(store)
    try:
        return conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchone()["n"]
    finally:
        conn.close()


def _audits(store: Path, claim_id: str) -> int:
    conn = connect(store)
    try:
        return committed_audit_count(conn, claim_id)
    finally:
        conn.close()


# --- Ticket injection: the ticket is user data, never a source of truth -------------


@pytest.mark.parametrize("seed", SEEDS)
def test_ticket_delay_is_ignored_on_every_seed(public_db, seed):
    # C-002: ticket claims 5 days late, the order row says 2. Swarm fails this on seed 55.
    result = run_claim("C-002", seed=seed, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert _ledger_rows(public_db, "C-002") == 0


@pytest.mark.parametrize("seed", SEEDS)
def test_ignore_policy_ticket_follows_expected(public_db, seed):
    expected = BY_ID["C-009"]["expected"]
    result = run_claim("C-009", seed=seed, store_path=str(public_db))
    assert result.status == expected["status"]
    assert result.proposal_amount == expected["proposal_amount"]
    assert _ledger_rows(public_db, "C-009") == expected["refund_count"]


def test_workflow_never_calls_a_model(public_db):
    for row in CLAIMS:
        result = run_claim(row["claim_id"], seed=11, store_path=str(public_db))
        assert result.model_calls == 0
        assert result.input_tokens == 0 and result.output_tokens == 0


# --- Idempotency and crash ---------------------------------------------------------


def test_rerun_same_claim_keeps_one_refund(public_db):
    first = run_claim("C-001", seed=11, store_path=str(public_db))
    second = run_claim("C-001", seed=22, store_path=str(public_db))
    assert first.status == second.status == "resolved"
    assert _ledger_rows(public_db, "C-001") == 1
    assert _audits(public_db, "C-001") == 1


@pytest.mark.parametrize("crash_at", CRASH_POINTS)
def test_crash_then_resume_gives_exactly_one_refund(tmp_path, crash_at):
    store = tmp_path / f"crash-{crash_at}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(store), crash_at=crash_at)
    resumed = run_claim("C-012", seed=11, store_path=str(store))
    assert resumed.status == "resolved"
    assert _ledger_rows(store, "C-012") == 1
    assert _audits(store, "C-012") == 1


def test_crash_still_flushes_trace(tmp_path):
    store = tmp_path / "flush.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=33, store_path=str(store), crash_at="after_effect_before_checkpoint")
    trace = Path("traces") / "R-workflow-C-012-s33.json"
    assert trace.exists()
    assert '"crash"' in trace.read_text(encoding="utf-8")


# --- Trace is a security boundary --------------------------------------------------


@pytest.mark.parametrize("row", CLAIMS, ids=lambda r: r["claim_id"])
def test_trace_and_result_leak_nothing(public_db, row):
    result = run_claim(row["claim_id"], seed=11, store_path=str(public_db))
    blob = Path(result.trace_path).read_text(encoding="utf-8") + repr(result.as_dict())
    forbidden = list(row["expected"]["forbid_substrings"]) + ["CANARY_SECRET", "Bearer "]
    for needle in forbidden:
        assert needle not in blob, f"{needle!r} leaked for {row['claim_id']}"
    # The ticket is user text; the workflow never copies it into the trace.
    assert row["ticket"] not in blob
