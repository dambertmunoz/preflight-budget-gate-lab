from __future__ import annotations

from dataclasses import dataclass, field, replace

from .state import ActionIntent, BudgetReservation, ReservationStatus


@dataclass
class ReservationLedger:
    total_budget: int
    _active: dict[str, BudgetReservation] = field(default_factory=dict)
    _released: dict[str, BudgetReservation] = field(default_factory=dict)

    @property
    def available(self) -> int:
        return self.total_budget - sum(r.tokens for r in self._active.values())

    def get(self, reservation_id: str) -> BudgetReservation | None:
        return self._active.get(reservation_id) or self._released.get(reservation_id)

    def can_reserve(self, tokens: int) -> bool:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        return tokens <= self.available

    def reserve(self, intent: ActionIntent) -> BudgetReservation | None:
        existing = self._active.get(intent.idempotency_key)
        if existing is not None:
            if existing.intent_fingerprint != intent.fingerprint:
                return None
            return existing
        if not self.can_reserve(intent.estimated_tokens):
            return None
        reservation = BudgetReservation(
            reservation_id=intent.idempotency_key,
            tokens=intent.estimated_tokens,
            intent_fingerprint=intent.fingerprint,
            status=ReservationStatus.HELD,
        )
        self._active[intent.idempotency_key] = reservation
        return reservation

    def has_idempotency_conflict(self, intent: ActionIntent) -> bool:
        existing = self._active.get(intent.idempotency_key)
        return existing is not None and existing.intent_fingerprint != intent.fingerprint

    def commit(self, reservation: BudgetReservation) -> BudgetReservation:
        committed = replace(reservation, status=ReservationStatus.COMMITTED)
        self._active[reservation.reservation_id] = committed
        return committed

    def release(self, reservation: BudgetReservation | None) -> BudgetReservation | None:
        if reservation is None:
            return None
        released = replace(reservation, status=ReservationStatus.RELEASED)
        self._active.pop(reservation.reservation_id, None)
        self._released[reservation.reservation_id] = released
        return released

    # Alias used in architecture discussions: release is the safer domain word,
    # rollback is the familiar failure-path word.
    rollback = release
