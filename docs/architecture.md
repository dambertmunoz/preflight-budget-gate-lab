# Architecture note: preflight budget gates for agent tools

Author: [Dambert Muñoz](https://dambertmunoz.com/)  
LinkedIn: [Dambert Muñoz](https://www.linkedin.com/in/dambert-m-4b772397/)

## The architecture problem

A lot of agent systems treat cost governance as a dashboard problem:

```text
tool call -> tokens spent -> logs emitted -> dashboard updated
```

That is useful for reporting, but it is too late for governance. If the tool already ran, the system may have already spent budget, mutated state, published content, triggered an external process, or exposed sensitive context.

For tool-using agents, the useful control point is before execution:

```text
intent -> admission decision -> reservation -> execution boundary -> commit/release
```

## System shape

```text
┌─────────┐
│ Planner │
└────┬────┘
     │ emits typed ActionIntent
     ▼
┌────────────────┐
│ BudgetPolicy   │  pure deterministic decision
└────┬───────────┘
     │
     ├── deny ───────────────▶ no reservation, no tool call
     │
     ▼
┌────────────────────┐
│ ReservationLedger  │  reserve budget before side effects
└────┬───────────────┘
     │
     ├── manual_review ──────▶ hold reservation, no tool call
     │
     ▼
┌──────────┐
│ Executor │  may run only with side_effect_allowed=True
└────┬─────┘
     │
     ├── success ────────────▶ commit reservation
     └── pre-commit failure ─▶ release reservation
```

## Main contracts

### `ActionIntent`

The planner cannot ask for a vague tool call. It must provide a typed operation shape:

- `tool_name`
- `purpose`
- `estimated_tokens`
- `risk`
- `idempotency_key`

That means the governor is evaluating an explicit intent, not reverse-engineering a tool call after the fact.

### `BudgetPolicy`

The policy is deliberately pure. It classifies the intent and returns an admission decision, but it does not mutate the ledger.

That separation matters because hidden state transitions inside policy code make governance harder to audit and easier to bypass.

### `ReservationLedger`

The ledger owns budget lifecycle:

- `HELD`: budget has been reserved before execution;
- `COMMITTED`: tool succeeded and the budget is consumed;
- `RELEASED`: execution failed before the commit boundary.

The ledger also rejects idempotency-key conflicts. Reusing the same key with a different tool shape is not a safe replay; it is an operational ambiguity.

### `AuditEvent`

Every route emits a stable audit event:

- route;
- decision code;
- reservation id/status;
- side-effect permission;
- whether a tool executed.

The point is not pretty logging. The point is that an operator can later answer: “Why was this allowed, blocked, or held for review?”

## Critical invariants

1. No side-effecting tool executes without an explicit `EXECUTE` route.
2. `EXECUTE` requires `side_effect_allowed=True`.
3. Execution requires a held reservation.
4. Commit happens only after successful execution.
5. Public side effects are routed to manual review by default.
6. Denials do not run tools.
7. Pre-commit failures release their reservation.

## Why this is Staff/Architect-level and not just a toy demo

The implementation is intentionally small, but the boundary is real:

- policy is separated from ledger mutation;
- lifecycle states are explicit;
- decisions use stable enums rather than free-form strings;
- tests validate invariants, not only examples;
- public side effects are blocked before the tool call;
- idempotency conflicts are modeled instead of hand-waved.

The missing production pieces are intentionally excluded: durable storage, approval workflows, distributed locking, per-team budgets, and pricing integrations. Those are important, but they are not the architectural primitive. The primitive is admission control before side effects.
