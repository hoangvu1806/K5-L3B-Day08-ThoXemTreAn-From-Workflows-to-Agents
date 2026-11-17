"""Shape B: a bounded ReAct reader followed by the host-only refund gate."""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        budget = Budget()
        trace = Trace(make_run_id("single", claim_id, seed))
        claim: dict = {}
        order: dict = {}

        def decide(observation: dict) -> dict:
            nonlocal claim, order
            last_tool = observation.get("last_tool")
            result = observation.get("last_result") or {}
            # Charge each decision without putting customer data in the prompt.
            complete(budget, seed=seed, purpose="decide", prompt=f"single:{last_tool or 'start'}")

            if last_tool is None:
                trace.add("read", {"tool": "get_claim_view"})
                return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

            if last_tool == "get_claim_view":
                if not result.get("found"):
                    trace.add("decision", {"status": "failed", "reason": "unknown_claim"})
                    return {"final": {"status": "failed", "reason": "unknown_claim", "proposal": 0}}
                claim = result
                if not claim.get("order_id"):
                    trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
                    return {"final": {"status": "needs_info", "reason": "missing_order_id", "proposal": 0}}
                trace.add("read", {"tool": "lookup_order"})
                return {
                    "tool": "lookup_order",
                    "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
                }

            if last_tool == "lookup_order":
                if not result.get("visible"):
                    reason = result.get("reason", "order_not_visible")
                    trace.add("decision", {"status": "escalated", "reason": reason})
                    return {"final": {"status": "escalated", "reason": reason, "proposal": 0}}
                order = result["order"]
                trace.add("read", {"tool": "lookup_refund_history"})
                return {
                    "tool": "lookup_refund_history",
                    "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
                }

            if last_tool == "lookup_refund_history":
                trace.add("refund_history", {"refunded_vnd": result.get("refunded_vnd", 0)})
                trace.add("read", {"tool": "compute_compensation"})
                return {"tool": "compute_compensation", "args": {"order": order}}

            if last_tool == "compute_compensation":
                proposal = int(result["amount_vnd"])
                trace.add("quote", {"amount_vnd": proposal, "reason": result.get("reason")})
                return {"final": {"status": "quoted", "reason": result.get("reason"), "proposal": proposal}}

            trace.add("decision", {"status": "failed", "reason": "unexpected_tool"})
            return {"final": {"status": "failed", "reason": "unexpected_tool", "proposal": 0}}

        reacted = run_react(
            conn,
            budget,
            observation={"claim": {"claim_id": claim_id}},
            decide=decide,
            max_steps=8,
            worker=True,
        )
        final = reacted["final"]
        proposal = int(final.get("proposal", 0))
        if reacted["stopped"] == "step_cap":
            trace.add("decision", {"status": "failed", "reason": "step_cap"})
            return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                          status="failed", proposal_amount=0, budget=budget,
                          trace=trace, error_reason="step_cap")

        if final["status"] != "quoted" or proposal <= 0:
            status = "denied" if final["status"] == "quoted" else final["status"]
            return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                          status=status, proposal_amount=0, budget=budget,
                          trace=trace, error_reason=final.get("reason"))

        # Flush before a possible injected crash; only the host writes money.
        trace.add("host_call", {"tool": "issue_refund", "proposal_amount": proposal})
        trace.write()
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        status = "resolved" if outcome["ok"] else "failed" if outcome["conflict"] else "denied"
        trace.add("host_result", {"status": status, "reason": outcome["reason"]})
        return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=proposal, budget=budget,
                      trace=trace, error_reason=None if outcome["ok"] else outcome["reason"])
    finally:
        conn.close()
