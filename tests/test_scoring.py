"""Unit-Tests für die reine Business-Logik in app/scoring.py.

Diese Tests brauchen weder Netzwerk noch Datenbank – sie sind schnell
und decken viele Randfälle ab. Beachte die Nutzung von ``today``, damit
die Tests unabhängig vom echten Kalenderdatum reproduzierbar bleiben.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.models import Priority, Status
from app.scoring import days_until_due, sort_by_urgency, urgency_score

TODAY = date(2026, 6, 1)


class TestDaysUntilDue:
    def test_none_due_date_returns_none(self):
        assert days_until_due(None, TODAY) is None

    def test_future_date_is_positive(self):
        assert days_until_due(date(2026, 6, 11), TODAY) == 10

    def test_past_date_is_negative(self):
        assert days_until_due(date(2026, 5, 22), TODAY) == -10

    def test_today_is_zero(self):
        assert days_until_due(TODAY, TODAY) == 0


class TestUrgencyScore:
    def test_done_task_is_always_zero(self, make_task):
        task = make_task(
            priority=Priority.CRITICAL,
            status=Status.DONE,
            due_date=date(2026, 5, 1),  # überfällig, aber erledigt
        )
        assert urgency_score(task, TODAY) == 0.0

    def test_no_due_date_uses_only_priority(self, make_task):
        task = make_task(priority=Priority.HIGH, due_date=None)
        # HIGH -> Gewicht 6 * 5 = 30, kein Deadline-Bonus
        assert urgency_score(task, TODAY) == 30.0

    def test_due_today_gets_bonus(self, make_task):
        task = make_task(priority=Priority.LOW, due_date=TODAY)
        # LOW -> 1 * 5 = 5, +30 (heute fällig) = 35
        assert urgency_score(task, TODAY) == 35.0

    def test_overdue_gets_capped_bonus(self, make_task):
        task = make_task(priority=Priority.MEDIUM, due_date=date(2026, 1, 1))
        # stark überfällig -> Deadline-Bonus auf 40 gedeckelt
        # MEDIUM -> 3 * 5 = 15, +40 = 55
        assert urgency_score(task, TODAY) == 55.0

    def test_score_never_exceeds_100(self, make_task):
        task = make_task(priority=Priority.CRITICAL, due_date=date(2026, 1, 1))
        # CRITICAL -> 50, +40 = 90 (bleibt unter 100, aber Deckel greift generell)
        assert urgency_score(task, TODAY) <= 100.0

    @pytest.mark.parametrize(
        ("days_ahead", "expected_bonus"),
        [
            (2, 20.0),  # <= 3 Tage
            (5, 10.0),  # <= 7 Tage
            (30, 0.0),  # weit weg
        ],
    )
    def test_deadline_bonus_tiers(self, make_task, days_ahead, expected_bonus):
        from datetime import timedelta

        task = make_task(priority=Priority.LOW, due_date=TODAY + timedelta(days=days_ahead))
        # LOW-Basis = 5
        assert urgency_score(task, TODAY) == 5.0 + expected_bonus


class TestSortByUrgency:
    def test_most_urgent_first(self, make_task):
        low = make_task(id=1, priority=Priority.LOW, due_date=None)
        critical = make_task(id=2, priority=Priority.CRITICAL, due_date=TODAY)
        medium = make_task(id=3, priority=Priority.MEDIUM, due_date=None)

        result = sort_by_urgency([low, critical, medium], TODAY)

        assert [t.id for t in result] == [2, 3, 1]

    def test_empty_list(self):
        assert sort_by_urgency([], TODAY) == []
