"""Integrationstest: ein kompletter Ablauf über mehrere Endpunkte.

Simuliert einen realistischen Nutzungsfluss und prüft, dass die
Komponenten zusammenspielen (Anlegen -> Sortieren -> Abschließen).
"""

from __future__ import annotations

from datetime import date, timedelta


def test_full_workflow(client):
    # 1. Mehrere Aufgaben mit unterschiedlicher Dringlichkeit anlegen
    today = date.today()
    client.post("/tasks", json={"title": "Später mal", "priority": "low"})
    client.post(
        "/tasks",
        json={
            "title": "Morgen fällig",
            "priority": "high",
            "due_date": (today + timedelta(days=1)).isoformat(),
        },
    )
    client.post("/tasks", json={"title": "Kritisch", "priority": "critical"})

    # 2. Nach Dringlichkeit sortiert abfragen
    resp = client.get("/tasks", params={"sort": "true"})
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.json()]

    # Die "Später mal"-Aufgabe (low, kein Datum) sollte nicht ganz oben stehen
    assert titles[-1] == "Später mal"
    assert len(titles) == 3

    # 3. Eine Aufgabe abschließen und prüfen, dass ihre Dringlichkeit auf 0 fällt
    first_id = resp.json()[0]["id"]
    client.patch(f"/tasks/{first_id}/status", params={"status": "done"})
    urgency = client.get(f"/tasks/{first_id}/urgency").json()["urgency"]
    assert urgency == 0.0
