"""Einfacher In-Memory-Speicher für Aufgaben.

Bewusst ohne echte Datenbank gehalten, damit das Projekt ohne externe
Dienste läuft. Die Klasse kapselt den Zustand, sodass Tests jederzeit
einen frischen Store erzeugen können.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models import Status, Task, TaskCreate


class TaskNotFoundError(Exception):
    """Wird geworfen, wenn eine Aufgabe nicht existiert."""


class TaskStore:
    """Hält Aufgaben im Arbeitsspeicher und vergibt fortlaufende IDs."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, data: TaskCreate) -> Task:
        """Lege eine neue Aufgabe an und gib sie zurück."""
        task = Task(
            id=self._next_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            due_date=data.due_date,
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task:
        """Hole eine Aufgabe oder wirf ``TaskNotFoundError``."""
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise TaskNotFoundError(task_id) from exc

    def list(self) -> list[Task]:
        """Alle Aufgaben als Liste."""
        return list(self._tasks.values())

    def set_status(self, task_id: int, status: Status) -> Task:
        """Ändere den Status einer Aufgabe."""
        task = self.get(task_id)
        updated = task.model_copy(update={"status": status})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> None:
        """Lösche eine Aufgabe."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def clear(self) -> None:
        """Setze den Store zurück (praktisch für Tests)."""
        self._tasks.clear()
        self._next_id = 1
