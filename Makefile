# Praktische Kurzbefehle. Aufruf z. B.:  make test
# (Unter Windows ohne "make" die Befehle einfach direkt aus der rechten Spalte tippen.)

.PHONY: install lint format typecheck test cov run docker-build docker-run all

install:            ## Abhängigkeiten inkl. Dev-Tools installieren
	pip install -e ".[dev]"

lint:               ## Ruff-Linter ausführen
	ruff check .

format:             ## Code mit Black + Ruff formatieren
	black .
	ruff check --fix .

typecheck:          ## Statische Typprüfung mit mypy
	mypy app

test:               ## Tests ausführen
	pytest

cov:                ## Tests mit Coverage-Report (bricht ab unter 85 %)
	pytest --cov=app --cov-report=term-missing --cov-report=xml

run:                ## App lokal starten -> http://localhost:8000/docs
	uvicorn app.main:app --reload

docker-build:       ## Docker-Image bauen
	docker build -t task-manager:local .

docker-run:         ## Container starten -> http://localhost:8000
	docker run --rm -p 8000:8000 task-manager:local

all: lint typecheck cov  ## Der komplette Qualitäts-Check wie in CI
