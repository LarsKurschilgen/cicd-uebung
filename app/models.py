"""Pydantic-Modelle für die Task-Manager-API.

Hier steckt bewusst etwas Validierungslogik, damit es sich lohnt,
Randfälle zu testen (leere Titel, ungültige Prioritäten usw.).
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Priority(str, Enum):
    """Priorität einer Aufgabe."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    """Bearbeitungsstatus einer Aufgabe."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    """Eingabemodell zum Anlegen einer Aufgabe."""

    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    priority: Priority = Priority.MEDIUM
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        """Ein Titel, der nur aus Leerzeichen besteht, ist nicht erlaubt."""
        if not value.strip():
            raise ValueError("Titel darf nicht leer sein")
        return value.strip()


class Task(BaseModel):
    """Vollständige Aufgabe, wie sie die API zurückgibt."""

    id: int
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: Status = Status.OPEN
    due_date: date | None = None
    created_at: datetime
