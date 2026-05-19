from __future__ import annotations

from dataclasses import dataclass

from .state import ActionIntent, DecisionCode, RiskClass, Route


@dataclass(frozen=True)
class Admission:
    route: Route
    code: DecisionCode
    requires_budget_reservation: bool
    side_effect_allowed: bool


@dataclass(frozen=True)
class BudgetPolicy:
    max_tokens_per_action: int
    require_review_for_public_side_effects: bool = True

    def classify(self, intent: ActionIntent) -> Admission:
        # Policy is intentionally pure: it does not mutate the ledger. A governor
        # that hides state transitions inside policy code is harder to audit and
        # easier to bypass.
        if intent.estimated_tokens > self.max_tokens_per_action:
            return Admission(
                route=Route.DENY,
                code=DecisionCode.PER_ACTION_LIMIT_EXCEEDED,
                requires_budget_reservation=False,
                side_effect_allowed=False,
            )

        if (
            self.require_review_for_public_side_effects
            and intent.risk == RiskClass.PUBLIC_SIDE_EFFECT
        ):
            return Admission(
                route=Route.MANUAL_REVIEW,
                code=DecisionCode.PUBLIC_SIDE_EFFECT_REQUIRES_REVIEW,
                requires_budget_reservation=True,
                side_effect_allowed=False,
            )

        return Admission(
            route=Route.EXECUTE,
            code=DecisionCode.PREFLIGHT_PASSED,
            requires_budget_reservation=True,
            side_effect_allowed=True,
        )
