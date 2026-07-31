# Task-Manager – Übungsprojekt für CI/CD

Ein bewusst kleines, aber vollständiges Python-Projekt, an dem du **Continuous
Integration & Continuous Delivery** mit **GitHub Actions** von A bis Z üben
kannst: Linting, Typprüfung, Tests, Coverage-Gates, Docker-Build,
Container-Registry und automatische Releases.

Das Projekt ist keine „Hello World"-Attrappe: Es gibt echte Business-Logik
(Dringlichkeits-Scoring von Aufgaben), eine FastAPI-REST-API, einen In-Memory-Store
und eine mehrschichtige Test-Suite (Unit-, API- und Integrationstests). Dadurch
lohnt es sich, Tests zu schreiben, Coverage zu messen und Pipelines scheitern und
wieder grün werden zu sehen.

## Was drin ist

```
Try/
├── app/                     Die Anwendung
│   ├── main.py              FastAPI-Endpunkte
│   ├── models.py            Pydantic-Modelle + Validierung
│   ├── scoring.py           Reine Business-Logik (ideal für Unit-Tests)
│   └── store.py             In-Memory-Datenspeicher
├── tests/                   Test-Suite (24 Tests)
│   ├── conftest.py          Gemeinsame Fixtures
│   ├── test_scoring.py      Unit-Tests
│   ├── test_api.py          API-Tests
│   └── test_integration.py  End-to-End-Ablauf
├── .github/workflows/       Die Pipelines
│   ├── ci.yml               Lint + Typen + Tests + Coverage (Matrix)
│   ├── docker.yml           Image bauen & nach GHCR pushen
│   └── release.yml          Automatische GitHub-Releases bei Tags
├── Dockerfile               Multi-Stage-Build
├── docker-compose.yml
├── pyproject.toml           Konfig für ruff/black/mypy/pytest/coverage
├── .pre-commit-config.yaml  Lokale Hooks vor dem Commit
├── Makefile                 Kurzbefehle (make test, make lint, ...)
└── ANLEITUNG.md             >>> Deine Schritt-für-Schritt-Übungen <<<
```

## Schnellstart (lokal)

Voraussetzung: Python 3.11 oder 3.12, Git, optional Docker.

```bash
# 1. Virtuelle Umgebung
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Installieren (inkl. Dev-Tools)
pip install -e ".[dev]"

# 3. Der komplette Qualitäts-Check (wie in CI)
ruff check .          # Linting
black --check .       # Formatierung
mypy app              # Typen
pytest --cov=app      # Tests + Coverage

# 4. App starten und ausprobieren
uvicorn app.main:app --reload
# -> http://localhost:8000/docs  (interaktive API-Doku)
```

Mit `make` geht es kürzer: `make install`, `make all`, `make run`.

## Und jetzt?

Öffne **`ANLEITUNG.md`**. Dort führen dich 10 aufeinander aufbauende Übungen durch
den kompletten CI/CD-Zyklus – vom ersten roten Pipeline-Lauf bis zum automatischen
Release. Jede Übung hat ein klares Ziel, konkrete Schritte und einen „Aha-Moment",
an dem du das Konzept wirklich verstehst.
