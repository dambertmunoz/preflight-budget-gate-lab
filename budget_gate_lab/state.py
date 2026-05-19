from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RiskClass(StrEnum):
    READ_ONLY = "read_only"
    WRITES_INTERNAL = "writes_internal"
    PUBLIC_SIDE_EFFECT = "public_side_effect"


class Route(StrEnum):
    EXECUTE = "execute"
    MANUAL_REVIEW = "manual_review"
    DENY = "deny"


class DecisionCode(StrEnum):
    PREFLIGHT_PASSED = "preflight_passed"
    INSUFFICIENT_BUDGET = "insufficient_budget"
    PER_ACTION_LIMIT_EXCEEDED = "estimated_tokens_exceed_per_action_limit"
    PUBLIC_SIDE_EFFECT_REQUIRES_REVIEW = "public_side_effect_requires_manual_review"
    IDEMPOTENCY_CONFLICT = "idempotency_key_conflicts_with_existing_intent"
    EXECUTION_FAILED_ROLLED_BACK = "execution_failed_reservation_rolled_back"


class ReservationStatus(StrEnum):
    HELD = "held"
    COMMITTED = "committed"
    RELEASED = "released"


@dataclass(frozen=True)
class ActionIntent:
    tool_name: str
    purpose: str
    estimated_tokens: int
    risk: RiskClass
    idempotency_key: str

    def __post_init__(self) -> None:
        if not self.tool_name.strip():
            raise ValueError("tool_name is required")
        if not self.purpose.strip():
            raise ValueError("purpose is required")
        if self.estimated_tokens <= 0:
            raise ValueError("estimated_tokens must be positive")
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key is required")

    @property
    def fingerprint(self) -> str:
        # Stable enough for the demo: an idempotency key is only safe if replayed
        # with the same operation shape, not merely the same string.
        return "|".join(
            [
                self.tool_name.strip(),
                self.purpose.strip(),
                str(self.estimated_tokens),
                self.risk.value,
            ]
        )


@dataclass(frozen=True)
class BudgetReservation:
    reservation_id: str
    tokens: int
    intent_fingerprint: str
    status: ReservationStatus = ReservationStatus.HELD


@dataclass(frozen=True)
class Decision:
    route: Route
    code: DecisionCode
    reservation: BudgetReservation | None = None
    side_effect_allowed: bool = False

    @property
    def reason(self) -> str:
        return self.code.value


@dataclass(frozen=True)
class ToolResult:
    executed: bool
    message: str


@dataclass(frozen=True)
class AuditEvent:
    intent_key: str
    route: Route
    decision_code: DecisionCode
    reservation_id: str | None
    reservation_status: ReservationStatus | None
    side_effect_allowed: bool
    tool_executed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "intent_key": self.intent_key,
            "route": self.route.value,
            "decision_code": self.decision_code.value,
            "reservation_id": self.reservation_id,
            "reservation_status": (
                self.reservation_status.value if self.reservation_status else None
            ),
            "side_effect_allowed": self.side_effect_allowed,
            "tool_executed": self.tool_executed,
        }


@dataclass(frozen=True)
class PreflightResult:
    decision: Decision
    tool_result: ToolResult
    audit_event: AuditEvent

    def __iter__(self):
        # Backward-compatible ergonomics for small demos/tests:
        # decision, result = run_preflight(...)
        yield self.decision
        yield self.tool_result
