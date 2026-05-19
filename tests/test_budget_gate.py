from __future__ import annotations

from budget_gate_lab.graph import run_preflight
from budget_gate_lab.ledger import ReservationLedger
from budget_gate_lab.policy import BudgetPolicy
from budget_gate_lab.state import (
    ActionIntent,
    DecisionCode,
    ReservationStatus,
    RiskClass,
    Route,
)


def _policy() -> BudgetPolicy:
    return BudgetPolicy(max_tokens_per_action=1_000)


def _intent(
    *,
    key: str = "intent-1",
    tool: str = "read_docs",
    tokens: int = 400,
    risk: RiskClass = RiskClass.READ_ONLY,
    purpose: str = "summarize architecture docs",
) -> ActionIntent:
    return ActionIntent(
        tool_name=tool,
        purpose=purpose,
        estimated_tokens=tokens,
        risk=risk,
        idempotency_key=key,
    )


def test_safe_read_only_action_executes_after_budget_reservation():
    ledger = ReservationLedger(total_budget=2_000)
    outcome = run_preflight(_intent(), ledger=ledger, policy=_policy())

    assert outcome.decision.route == Route.EXECUTE
    assert outcome.decision.code == DecisionCode.PREFLIGHT_PASSED
    assert outcome.decision.side_effect_allowed is True
    assert outcome.decision.reservation is not None
    assert outcome.decision.reservation.status == ReservationStatus.COMMITTED
    assert outcome.tool_result.executed is True
    assert outcome.audit_event.as_dict() == {
        "intent_key": "intent-1",
        "route": "execute",
        "decision_code": "preflight_passed",
        "reservation_id": "intent-1",
        "reservation_status": "committed",
        "side_effect_allowed": True,
        "tool_executed": True,
    }
    assert ledger.available == 1_600


def test_public_side_effect_routes_to_manual_review_before_tool_executes():
    ledger = ReservationLedger(total_budget=2_000)
    outcome = run_preflight(
        _intent(
            key="publish-1",
            tool="publish_linkedin_post",
            purpose="publish public post",
            tokens=500,
            risk=RiskClass.PUBLIC_SIDE_EFFECT,
        ),
        ledger=ledger,
        policy=_policy(),
    )

    assert outcome.decision.route == Route.MANUAL_REVIEW
    assert outcome.decision.code == DecisionCode.PUBLIC_SIDE_EFFECT_REQUIRES_REVIEW
    assert outcome.decision.side_effect_allowed is False
    assert outcome.decision.reservation is not None
    assert outcome.decision.reservation.status == ReservationStatus.HELD
    assert outcome.tool_result.executed is False
    assert outcome.tool_result.message.startswith("blocked:")
    assert ledger.available == 1_500  # held while approval is pending


def test_insufficient_budget_denies_without_reservation_or_execution():
    ledger = ReservationLedger(total_budget=300)
    outcome = run_preflight(
        _intent(key="research-1", tool="long_research", tokens=800),
        ledger=ledger,
        policy=_policy(),
    )

    assert outcome.decision.route == Route.DENY
    assert outcome.decision.code == DecisionCode.INSUFFICIENT_BUDGET
    assert outcome.decision.reservation is None
    assert outcome.tool_result.executed is False
    assert ledger.available == 300


def test_per_action_limit_denies_before_touching_ledger():
    ledger = ReservationLedger(total_budget=5_000)
    outcome = run_preflight(
        _intent(key="too-large", tokens=1_500),
        ledger=ledger,
        policy=_policy(),
    )

    assert outcome.decision.route == Route.DENY
    assert outcome.decision.code == DecisionCode.PER_ACTION_LIMIT_EXCEEDED
    assert outcome.decision.reservation is None
    assert outcome.tool_result.executed is False
    assert ledger.available == 5_000


def test_execution_failure_releases_reservation_before_commit_boundary():
    ledger = ReservationLedger(total_budget=2_000)
    outcome = run_preflight(
        _intent(
            key="write-1",
            tool="write_internal_record",
            purpose="store generated artifact",
            tokens=600,
            risk=RiskClass.WRITES_INTERNAL,
        ),
        ledger=ledger,
        policy=_policy(),
        simulate_tool_failure=True,
    )

    assert outcome.decision.route == Route.DENY
    assert outcome.decision.code == DecisionCode.EXECUTION_FAILED_ROLLED_BACK
    assert outcome.decision.reservation is not None
    assert outcome.decision.reservation.status == ReservationStatus.RELEASED
    assert outcome.tool_result.executed is False
    assert ledger.available == 2_000
    assert ledger.get("write-1") is not None
    assert ledger.get("write-1").status == ReservationStatus.RELEASED  # type: ignore[union-attr]


def test_multiple_committed_actions_consume_shared_budget():
    ledger = ReservationLedger(total_budget=1_000)

    first = run_preflight(_intent(key="a", tokens=400), ledger=ledger, policy=_policy())
    second = run_preflight(_intent(key="b", tokens=400), ledger=ledger, policy=_policy())
    third = run_preflight(_intent(key="c", tokens=300), ledger=ledger, policy=_policy())

    assert first.decision.route == Route.EXECUTE
    assert second.decision.route == Route.EXECUTE
    assert third.decision.route == Route.DENY
    assert third.decision.code == DecisionCode.INSUFFICIENT_BUDGET
    assert third.tool_result.executed is False
    assert ledger.available == 200


def test_same_idempotency_key_with_same_intent_is_a_safe_replay():
    ledger = ReservationLedger(total_budget=2_000)
    intent = _intent(key="same-key", tokens=400)

    first = run_preflight(intent, ledger=ledger, policy=_policy())
    replay = run_preflight(intent, ledger=ledger, policy=_policy())

    assert first.decision.route == Route.EXECUTE
    assert replay.decision.route == Route.EXECUTE
    assert replay.decision.reservation is not None
    assert replay.decision.reservation.reservation_id == "same-key"
    assert ledger.available == 1_600


def test_reusing_idempotency_key_with_different_intent_is_denied():
    ledger = ReservationLedger(total_budget=2_000)
    run_preflight(_intent(key="conflict", tokens=400), ledger=ledger, policy=_policy())

    outcome = run_preflight(
        _intent(key="conflict", tool="different_tool", tokens=500),
        ledger=ledger,
        policy=_policy(),
    )

    assert outcome.decision.route == Route.DENY
    assert outcome.decision.code == DecisionCode.IDEMPOTENCY_CONFLICT
    assert outcome.decision.side_effect_allowed is False
    assert outcome.tool_result.executed is False
    assert ledger.available == 1_600


def test_only_execute_route_can_execute_tools():
    cases = [
        _intent(key="safe", risk=RiskClass.READ_ONLY),
        _intent(key="review", risk=RiskClass.PUBLIC_SIDE_EFFECT),
        _intent(key="deny", tokens=2_000),
    ]

    for intent in cases:
        outcome = run_preflight(
            intent,
            ledger=ReservationLedger(total_budget=2_000),
            policy=_policy(),
        )
        if outcome.decision.route == Route.EXECUTE:
            assert outcome.decision.side_effect_allowed is True
            assert outcome.tool_result.executed is True
        else:
            assert outcome.decision.side_effect_allowed is False
            assert outcome.tool_result.executed is False
