"""Reine Business-Logik: Dringlichkeits-Score für Aufgaben.

Diese Funktionen haben *keine* Abhängigkeit zu FastAPI oder der Datenbank.
Genau deshalb lassen sie sich hervorragend mit Unit-Tests abdecken –
inklusive vieler Randfälle. Das ist ideales Übungsmaterial für Testing.
"""

from __future__ import annotations

from datetime import date

from app.models import Priority, Status, Task

# Grundgewichte je Priorität.
PRIORITY_WEIGHTS: dict[Priority, int] = {
    Priority.LOW: 1,
    Priority.MEDIUM: 3,
    Priority.HIGH: 6,
    Priority.CRITICAL: 10,
}


def days_until_due(due: date | None, today: date | None = None) -> int | None:
    """Anzahl Tage bis zur Fälligkeit.

    Gibt ``None`` zurück, wenn kein Fälligkeitsdatum gesetzt ist.
    Negative Werte bedeuten: die Aufgabe ist überfällig.
    """
    if due is None:
        return None
    reference = today or date.today()
    return (due - reference).days


def urgency_score(task: Task, today: date | None = None) -> float:
    """Berechne einen Dringlichkeits-Score zwischen 0 und 100.

    Der Score kombiniert die Priorität mit der Nähe zum Fälligkeitsdatum:

    * Erledigte Aufgaben haben immer Score 0.
    * Überfällige Aufgaben bekommen einen deutlichen Aufschlag.
    * Je näher die Fälligkeit, desto höher der Score.
    """
    if task.status == Status.DONE:
        return 0.0

    base = PRIORITY_WEIGHTS[task.priority] * 50  # 5..50

    remaining = days_until_due(task.due_date, today)
    if remaining is None:
        deadline_bonus = 0.0
    elif remaining < 0:
        # Überfällig: kräftiger, aber gedeckelter Aufschlag.
        deadline_bonus = min(40.0, 20.0 + abs(remaining) * 2.0)
    elif remaining == 0:
        deadline_bonus = 30.0
    elif remaining <= 3:
        deadline_bonus = 20.0
    elif remaining <= 7:
        deadline_bonus = 10.0
    else:
        deadline_bonus = 0.0

    return round(min(100.0, base + deadline_bonus), 1)


def sort_by_urgency(tasks: list[Task], today: date | None = None) -> list[Task]:
    """Sortiere Aufgaben absteigend nach Dringlichkeit (dringendste zuerst)."""
    return sorted(tasks, key=lambda t: urgency_score(t, today), reverse=True)
