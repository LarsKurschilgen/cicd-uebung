"""FastAPI-App: Task-Manager mit Dringlichkeits-Ranking.

Endpunkte:
    GET    /health              – Health-Check (für Deployments/CI)
    POST   /tasks               – Aufgabe anlegen
    GET    /tasks               – Aufgaben auflisten (optional nach Dringlichkeit sortiert)
    GET    /tasks/{id}          – einzelne Aufgabe
    PATCH  /tasks/{id}/status   – Status ändern
    DELETE /tasks/{id}          – Aufgabe löschen
    GET    /tasks/{id}/urgency  – Dringlichkeits-Score einer Aufgabe
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from app import __version__
from app.models import Status, Task, TaskCreate
from app.scoring import sort_by_urgency, urgency_score
from app.store import TaskNotFoundError, TaskStore

app = FastAPI(title="Task-Manager", version=__version__)
store = TaskStore()


@app.get("/health")
def health() -> dict[str, str]:
    """Einfacher Health-Check – gibt Status und Version zurück."""
    return {"status": "ok", "version": __version__}


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(data: TaskCreate) -> Task:
    """Lege eine neue Aufgabe an."""
    return store.add(data)


@app.get("/tasks", response_model=list[Task])
def list_tasks(sort_by_urgency_flag: bool = Query(False, alias="sort")) -> list[Task]:
    """Liste alle Aufgaben. Mit ``?sort=true`` nach Dringlichkeit sortiert."""
    tasks = store.list()
    if sort_by_urgency_flag:
        return sort_by_urgency(tasks)
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    """Hole eine einzelne Aufgabe."""
    try:
        return store.get(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden") from None


@app.patch("/tasks/{task_id}/status", response_model=Task)
def update_status(task_id: int, status: Status) -> Task:
    """Ändere den Status einer Aufgabe."""
    try:
        return store.set_status(task_id, status)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden") from None


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    """Lösche eine Aufgabe."""
    try:
        store.delete(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden") from None


@app.get("/tasks/{task_id}/urgency")
def get_urgency(task_id: int) -> dict[str, float | int]:
    """Gib den Dringlichkeits-Score einer Aufgabe zurück."""
    try:
        task = store.get(task_id)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden") from None
    return {"task_id": task_id, "urgency": urgency_score(task)}
