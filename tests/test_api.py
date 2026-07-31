"""API-Tests über den FastAPI-TestClient.

Diese Tests prüfen HTTP-Verhalten: Statuscodes, JSON-Antworten,
Validierung und Fehlerfälle. Sie sind etwas "schwerer" als reine
Unit-Tests, aber immer noch schnell (kein echter Server nötig).
"""

from __future__ import annotations


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_create_task_returns_201(client):
    resp = client.post("/tasks", json={"title": "Steuererklärung", "priority": "high"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["title"] == "Steuererklärung"
    assert body["priority"] == "high"
    assert body["status"] == "open"


def test_create_task_rejects_blank_title(client):
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 422  # Pydantic-Validierungsfehler


def test_create_task_rejects_invalid_priority(client):
    resp = client.post("/tasks", json={"title": "Test", "priority": "urgent"})
    assert resp.status_code == 422


def test_get_missing_task_returns_404(client):
    resp = client.get("/tasks/999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Aufgabe nicht gefunden"


def test_list_tasks_empty(client):
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_status(client):
    created = client.post("/tasks", json={"title": "Aufräumen"}).json()
    resp = client.patch(f"/tasks/{created['id']}/status", params={"status": "done"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Wegwerfen"}).json()
    resp = client.delete(f"/tasks/{created['id']}")
    assert resp.status_code == 204
    # danach nicht mehr auffindbar
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_urgency_endpoint(client):
    created = client.post("/tasks", json={"title": "Wichtig", "priority": "critical"}).json()
    resp = client.get(f"/tasks/{created['id']}/urgency")
    assert resp.status_code == 200
    assert resp.json()["urgency"] > 0
