from __future__ import annotations

import json

from .graph import run_preflight
from .ledger import ReservationLedger
from .policy import BudgetPolicy
from .state import ActionIntent, RiskClass


def main() -> int:
    intent = ActionIntent(
        tool_name="publish_linkedin_post",
        purpose="publish a personal-brand technical demo",
        estimated_tokens=700,
        risk=RiskClass.PUBLIC_SIDE_EFFECT,
        idempotency_key="post-2026-05-18",
    )
    outcome = run_preflight(
        intent,
        ledger=ReservationLedger(total_budget=2_000),
        policy=BudgetPolicy(max_tokens_per_action=1_000),
    )
    print(f"route={outcome.decision.route}")
    print(f"reason={outcome.decision.reason}")
    print(f"tool_executed={outcome.tool_result.executed}")
    print("audit_event=" + json.dumps(outcome.audit_event.as_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
