from __future__ import annotations

import json
from pathlib import Path

from lab8.db import connect
from lab8.shapes.orchestrator import run_claim


def test_handoff_and_trace_exclude_secrets_and_order_pii(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    trace = json.loads(trace_text)
    handoff = next(event["payload"] for event in trace["events"] if event["kind"] == "handoff")

    assert handoff["facts"] == {}
    assert "issue_refund" not in handoff["allowed_tools"]
    for forbidden in (
        "CANARY_SECRET_PARENT_C-001",
        "raw_headers",
        "0901000107",
        "12 Le Loi Q1",
        "CANARY_INTERNAL_O107",
        "Ao thun",
    ):
        assert forbidden not in trace_text


def test_approval_borrowed_from_another_claim_is_denied(public_db):
    conn = connect(public_db)
    try:
        conn.execute(
            "UPDATE claims SET approval_id = ? WHERE claim_id = ?",
            ("A-010", "C-001"),
        )
        conn.commit()
    finally:
        conn.close()

    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert result.committed_audit_count == 0

    conn = connect(public_db)
    try:
        audit = conn.execute(
            "SELECT details_json FROM audit_events "
            "WHERE claim_id = ? AND event_type = 'policy_denied'",
            ("C-001",),
        ).fetchone()
    finally:
        conn.close()

    assert audit is not None
    assert json.loads(audit["details_json"])["reason"] == "approval_claim_mismatch"
