"""Gemeinsame Fixtures für alle Tests.

conftest.py wird von pytest automatisch gefunden – hier definierte
Fixtures stehen in allen Testdateien zur Verfügung, ohne Import.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app, store
from app.models import Priority, Status, Task


@pytest.fixture
def client() -> TestClient:
    """Ein FastAPI-Testclient mit frischem, leerem Store je Test."""
    store.clear()
    return TestClient(app)


@pytest.fixture
def make_task():
    """Factory-Fixture: erzeugt Task-Objekte mit sinnvollen Defaults.

    Beispiel:
        task = make_task(priority=Priority.HIGH, due_date=date(2026, 1, 1))
    """

    def _make(
        *,
        id: int = 1,
        title: str = "Beispiel",
        priority: Priority = Priority.MEDIUM,
        status: Status = Status.OPEN,
        due_date=None,
    ) -> Task:
        return Task(
            id=id,
            title=title,
            priority=priority,
            status=status,
            due_date=due_date,
            created_at=datetime.now(timezone.utc),
        )

    return _make
