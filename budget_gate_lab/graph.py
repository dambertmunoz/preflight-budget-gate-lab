from __future__ import annotations

from .ledger import ReservationLedger
from .policy import BudgetPolicy
from .state import (
    ActionIntent,
    AuditEvent,
    Decision,
    DecisionCode,
    PreflightResult,
    ReservationStatus,
    Route,
    ToolResult,
)


def _audit(intent: ActionIntent, decision: Decision, result: ToolResult) -> AuditEvent:
    reservation = decision.reservation
    return AuditEvent(
        intent_key=intent.idempotency_key,
        route=decision.route,
        decision_code=decision.code,
        reservation_id=reservation.reservation_id if reservation else None,
        reservation_status=reservation.status if reservation else None,
        side_effect_allowed=decision.side_effect_allowed,
        tool_executed=result.executed,
    )


def _blocked(intent: ActionIntent, decision: Decision) -> PreflightResult:
    result = ToolResult(executed=False, message=f"blocked:{decision.reason}")
    return PreflightResult(
        decision=decision,
        tool_result=result,
        audit_event=_audit(intent, decision, result),
    )


def _execute_tool(intent: ActionIntent, decision: Decision) -> ToolResult:
    if decision.route != Route.EXECUTE:
        return ToolResult(executed=False, message=f"blocked:{decision.reason}")
    if not decision.side_effect_allowed:
        return ToolResult(executed=False, message="blocked:side_effect_not_allowed")
    if decision.reservation is None:
        return ToolResult(executed=False, message="blocked:missing_budget_reservation")
    if decision.reservation.status != ReservationStatus.HELD:
        return ToolResult(executed=False, message="blocked:reservation_not_held")

    return ToolResult(
        executed=True,
        message=f"executed:{intent.tool_name}:{intent.idempotency_key}",
    )


def run_preflight(
    intent: ActionIntent,
    *,
    ledger: ReservationLedger,
    policy: BudgetPolicy,
    simulate_tool_failure: bool = False,
) -> PreflightResult:
    admission = policy.classify(intent)

    if admission.route == Route.DENY:
        return _blocked(
            intent,
            Decision(route=admission.route, code=admission.code),
        )

    if ledger.has_idempotency_conflict(intent):
        return _blocked(
            intent,
            Decision(route=Route.DENY, code=DecisionCode.IDEMPOTENCY_CONFLICT),
        )

    reservation = ledger.reserve(intent) if admission.requires_budget_reservation else None
    if reservation is None and admission.requires_budget_reservation:
        return _blocked(
            intent,
            Decision(route=Route.DENY, code=DecisionCode.INSUFFICIENT_BUDGET),
        )

    if admission.route == Route.MANUAL_REVIEW:
        # The reservation is intentionally held while approval is pending. A real
        # system would attach TTL/expiry; the primitive demonstrated here is the
        # pre-side-effect hold, not durable workflow infrastructure.
        return _blocked(
            intent,
            Decision(
                route=Route.MANUAL_REVIEW,
                code=admission.code,
                reservation=reservation,
                side_effect_allowed=False,
            ),
        )

    executable = Decision(
        route=Route.EXECUTE,
        code=admission.code,
        reservation=reservation,
        side_effect_allowed=admission.side_effect_allowed,
    )

    if simulate_tool_failure:
        released = ledger.release(reservation)
        failed = Decision(
            route=Route.DENY,
            code=DecisionCode.EXECUTION_FAILED_ROLLED_BACK,
            reservation=released,
            side_effect_allowed=False,
        )
        result = ToolResult(executed=False, message="rolled_back_before_commit")
        return PreflightResult(
            decision=failed,
            tool_result=result,
            audit_event=_audit(intent, failed, result),
        )

    result = _execute_tool(intent, executable)
    if result.executed:
        committed = ledger.commit(reservation) if reservation else None
        executable = Decision(
            route=Route.EXECUTE,
            code=admission.code,
            reservation=committed,
            side_effect_allowed=True,
        )
        result = ToolResult(
            executed=True,
            message=f"executed:{intent.tool_name}:{intent.idempotency_key}",
        )

    return PreflightResult(
        decision=executable,
        tool_result=result,
        audit_event=_audit(intent, executable, result),
    )
