"""Shape A — deterministic workflow.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Fixed Python steps, no model call. Money stays in code
(`lab8.tools.compute_compensation`), writes go through the host gate
(`lab8.durability.issue_refund`).

1. Read the claim through `get_claim_view` (not SELECT *). Unknown -> `failed`.
2. Missing order_id -> `needs_info`. No ledger write.
3. `lookup_order` scoped to the claim's principal. Not visible -> `escalated`.
4. Quote from the order row only. The ticket text is user data and is never parsed.
5. Quote 0 -> `denied`, no issue_refund call (so no `policy_denied` audit).
6. Quote > 0 -> `issue_refund(conn, claim_id, <full quote>, crash_at=...)`.
   The host checks approval and subtracts earlier refunds on the same order.
   Not ok -> `denied` (host wrote `policy_denied`), conflict -> `failed`.
7. Ok -> `resolved`.

Trace: one event per step, built only from allowlisted fields. The ticket,
principal row, phone, address, item and internal notes never reach the trace.
`InjectedCrash` is not swallowed: the trace is flushed, then the crash re-raises.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"

# Order fields allowed in the trace. lookup_order already drops PII; this keeps
# the trace stable even if that allowlist grows later.
_TRACE_ORDER_FIELDS = (
    "order_id",
    "status",
    "delay_days",
    "shipping_fee_vnd",
    "paid_vnd",
    "damage_verified",
)


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # 1. Claim view. Only ids go to the trace, never the ticket.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add(
        "get_claim_view",
        {"found": claim["found"], "has_order_id": bool(claim.get("order_id"))},
    )
    if not claim["found"]:
        return done("failed", reason="unknown_claim")

    # 2. No order id -> ask for it. Do not mine the ticket for one.
    if not claim["order_id"]:
        return done("needs_info", reason="missing_order_id")

    # 3. Order scoped to the claim's principal.
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    trace.add("lookup_order", _order_trace(order_view))
    if not order_view["visible"]:
        return done("escalated", reason=order_view["reason"])

    # 4-5. Quote from the DB row only.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    proposal = int(quote["amount_vnd"])
    trace.add(
        "compute_compensation",
        {"amount_vnd": proposal, "reason": quote["reason"], "clause_ids": list(quote["clause_ids"])},
    )
    if proposal <= 0:
        return done("denied", reason=quote["reason"])

    # 6. Host gate with the FULL quote.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add(
        "issue_refund",
        {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]},
    )
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])

    # 7. Committed or idempotent replay.
    return done("resolved", proposal)


def _order_trace(order_view: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {"visible": order_view["visible"], "reason": order_view["reason"]}
    order = order_view.get("order")
    if order:
        payload["order"] = {key: order[key] for key in _TRACE_ORDER_FIELDS if key in order}
    return payload
