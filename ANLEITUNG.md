# CI/CD üben – Schritt für Schritt

Diese Anleitung führt dich durch **10 aufeinander aufbauende Übungen**. Du beginnst
lokal, bringst das Projekt zu GitHub, siehst deine erste Pipeline laufen – und
arbeitest dich bis zu automatischen Docker-Builds und Releases vor.

Jede Übung hat: ein **Ziel**, die **Schritte** und einen **🎯 Aha-Moment**, an dem
das Konzept „klick" macht. Nimm dir Zeit, absichtlich Dinge kaputt zu machen – genau
daran lernt man CI/CD am meisten.

> **Faustregel für alles Folgende:** CI (Continuous Integration) heißt „bei jeder
> Änderung automatisch prüfen, ob noch alles zusammenpasst". CD (Continuous
> Delivery) heißt „aus geprüftem Code automatisch ein auslieferbares Artefakt
> bauen". Dieses Projekt macht beides sichtbar.

---

## Vorbereitung (einmalig)

Du brauchst:

- **Git** – `git --version`
- **Python 3.11 oder 3.12** – `python --version`
- Ein **GitHub-Konto**
- Optional, aber empfohlen: **Docker Desktop** für die Übungen 7–8

Richte das Projekt lokal ein:

```bash
cd Try
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest                            # sollte "24 passed" zeigen
```

Läuft das durch, kann es losgehen.

---

## Übung 1 – Alles lokal grün bekommen

**Ziel:** Verstehen, was die Pipeline später automatisch macht – indem du es einmal
von Hand machst.

**Schritte:**

```bash
ruff check .          # Linter: Stil- und Logikfehler
black --check .        # Formatierung stimmt?
mypy app               # statische Typprüfung
pytest --cov=app --cov-report=term-missing
```

Schau dir den Coverage-Report am Ende an. Die Spalte `Missing` zeigt Zeilen, die
**kein** Test durchläuft.

**🎯 Aha-Moment:** Diese vier Befehle sind *exakt* das, was gleich in der Cloud bei
jedem Push laufen wird. „CI" ist kein Zauber – es ist deine lokale Checkliste, nur
automatisch und für jeden nachvollziehbar.

---

## Übung 2 – Projekt zu GitHub bringen

**Ziel:** Das Repo pushen und die **erste Pipeline** von selbst starten sehen.

**Schritte:**

1. Lege auf GitHub ein **neues, leeres** Repository an (ohne README, ohne
   .gitignore – die haben wir schon). Nenn es z. B. `cicd-uebung`.

2. Im Projektordner:

```bash
git init
git add .
git commit -m "Initiales Übungsprojekt"
git branch -M main
git remote add origin https://github.com/<DEIN-NAME>/cicd-uebung.git
git push -u origin main
```

3. Öffne auf GitHub den Reiter **„Actions"**.

**🎯 Aha-Moment:** Ohne dass du irgendwo einen „Start"-Knopf gedrückt hast, läuft
die CI-Pipeline los. Der Auslöser steht in `.github/workflows/ci.yml` unter `on:
push`. GitHub liest diese Datei automatisch. Klick dich in den laufenden Job und sieh
zu, wie Schritt für Schritt Linting, Typen und Tests abgearbeitet werden – auf zwei
Python-Versionen gleichzeitig.

---

## Übung 3 – Eine Pipeline absichtlich rot machen

**Ziel:** Den wichtigsten CI-Effekt erleben: **Fehler werden gestoppt, bevor sie in
`main` landen.** Rot ist gut – rot heißt, das System hat dich beschützt.

**Schritte:**

1. Baue in `app/scoring.py` einen Bug ein. Ändere in `urgency_score` die Basiszeile:

```python
    base = PRIORITY_WEIGHTS[task.priority] * 5
```

zu (falscher Faktor):

```python
    base = PRIORITY_WEIGHTS[task.priority] * 50
```

2. Committen und pushen:

```bash
git add app/scoring.py
git commit -m "Experiment: Score-Faktor ändern"
git push
```

3. Geh zu **Actions** und beobachte den Lauf.

**🎯 Aha-Moment:** Der Job wird **rot**. Öffne den fehlgeschlagenen `pytest`-Schritt –
du siehst genau, welcher Test mit welchem erwarteten/tatsächlichen Wert scheitert
(`test_no_due_date_uses_only_priority`). Die Tests, die du in Übung 1 „umsonst"
laufen sahst, fangen jetzt einen echten Regressionsfehler ab.

4. Mach den Bug rückgängig, damit es weitergeht:

```bash
git revert --no-edit HEAD
git push
```

Der nächste Lauf ist wieder grün.

---

## Übung 4 – Feature über einen Pull Request + Branch-Schutz

**Ziel:** Den professionellen Arbeitsablauf üben: nicht direkt auf `main`, sondern
über einen **Branch + Pull Request**, den CI absichern muss.

**Schritte:**

1. Schütze zuerst `main`. Auf GitHub: **Settings → Branches → Add branch ruleset**
   (bzw. „Add rule"). Aktiviere **„Require status checks to pass before merging"** und
   wähle den CI-Check aus. Ab jetzt darf nichts nach `main`, das die Pipeline nicht
   besteht.

2. Neuer Branch mit einem echten Feature – ein Endpunkt, der die Anzahl offener
   Aufgaben zählt. Öffne `app/main.py` und füge hinzu:

```python
@app.get("/stats")
def stats() -> dict[str, int]:
    """Zähle Aufgaben nach Status."""
    tasks = store.list()
    return {
        "gesamt": len(tasks),
        "offen": sum(1 for t in tasks if t.status == Status.OPEN),
        "erledigt": sum(1 for t in tasks if t.status == Status.DONE),
    }
```

3. Branch, Commit, Push:

```bash
git checkout -b feature/stats-endpoint
git add app/main.py
git commit -m "Neuer /stats-Endpunkt"
git push -u origin feature/stats-endpoint
```

4. Auf GitHub erscheint ein Button **„Compare & pull request"**. Öffne den PR.

**🎯 Aha-Moment:** Im PR läuft die Pipeline automatisch für *diesen Branch* – und der
grüne Merge-Button bleibt **gesperrt**, bis die Checks durch sind. So verhindern
echte Teams, dass kaputter Code jemals in den Hauptzweig gelangt. Merge den PR erst,
wenn er grün ist, und hol dir danach lokal den Stand:

```bash
git checkout main && git pull
```

---

## Übung 5 – Das Coverage-Gate erleben

**Ziel:** Verstehen, warum „Tests laufen durch" nicht reicht – es zählt auch, *wie
viel* Code getestet ist.

**Schritte:**

1. Füge in `app/scoring.py` eine neue, **ungetestete** Funktion hinzu:

```python
def workload_label(open_count: int) -> str:
    """Grobe Einordnung der Auslastung."""
    if open_count == 0:
        return "frei"
    if open_count <= 3:
        return "entspannt"
    if open_count <= 8:
        return "voll"
    return "überlastet"
```

2. Lokal prüfen:

```bash
pytest --cov=app --cov-report=term-missing
```

**🎯 Aha-Moment:** Die Gesamt-Coverage sinkt, weil neue Zeilen ohne Test dazukamen.
In `pyproject.toml` steht `fail_under = 85`. Wenn du genug ungetesteten Code hinzufügst,
**schlägt der Test-Schritt fehl**, obwohl kein einziger Test „falsch" ist. Das ist ein
**Quality Gate**: Es zwingt dich, neue Logik auch abzudecken.

3. Schreib den fehlenden Test – häng ihn in `tests/test_scoring.py` an:

```python
class TestWorkloadLabel:
    def test_labels(self, make_task):
        from app.scoring import workload_label
        assert workload_label(0) == "frei"
        assert workload_label(2) == "entspannt"
        assert workload_label(5) == "voll"
        assert workload_label(20) == "überlastet"
```

Push den Branch, öffne einen PR, sieh die Coverage wieder steigen und den Check grün
werden.

---

## Übung 6 – Matrix-Builds & Caching bewusst wahrnehmen

**Ziel:** Zwei Profi-Techniken verstehen, die schon eingebaut sind.

**Schritte:**

1. Öffne in einem grünen Actions-Lauf die Job-Liste. Du siehst **zwei** Jobs:
   `Python 3.11` und `Python 3.12`. Das steuert der `strategy.matrix`-Block in
   `ci.yml`.

2. Experiment: Ergänze in `ci.yml` bei `python-version` den Wert `"3.10"`:

```yaml
        python-version: ["3.10", "3.11", "3.12"]
```

Push und beobachte: Der 3.10-Job **scheitert**, weil `pyproject.toml`
`requires-python = ">=3.11"` verlangt. Entferne 3.10 wieder.

3. Schau dir zwei aufeinanderfolgende Läufe an – im Schritt „Python einrichten"
   steht beim zweiten Mal „Cache restored". Das ist `cache: pip`.

**🎯 Aha-Moment:** Mit *einer* Konfigurationsdatei testest du gegen mehrere
Umgebungen gleichzeitig (Matrix) und sparst durch Caching Zeit, weil Abhängigkeiten
nicht bei jedem Lauf neu heruntergeladen werden. So skalieren echte CI-Systeme.

---

## Übung 7 – Docker-Image lokal bauen und laufen lassen

**Ziel:** Vom „läuft auf meinem Rechner" zum portablen, reproduzierbaren Artefakt.

**Schritte:** (Docker muss laufen)

```bash
docker build -t task-manager:local .
docker run --rm -p 8000:8000 task-manager:local
# In einem zweiten Terminal:
curl http://localhost:8000/health
```

Schau in die `Dockerfile`: Sie hat **zwei Stages**. Die erste installiert
Abhängigkeiten, die zweite kopiert nur das fertige Ergebnis – deshalb ist das
Endimage klein und enthält keine Build-Werkzeuge.

**🎯 Aha-Moment:** Das Image kapselt Python-Version, Abhängigkeiten und Code in *einem*
Artefakt. Es läuft auf jedem Rechner mit Docker identisch – die Grundlage jeder
modernen Auslieferung. Der `HEALTHCHECK` am Ende erlaubt Orchestrierern (wie
Kubernetes), einen kranken Container automatisch zu erkennen.

---

## Übung 8 – Continuous Delivery: Image automatisch nach GHCR pushen

**Ziel:** Der Sprung von CI zu CD. Nach jedem Merge auf `main` baut GitHub das Image
und lädt es in die **GitHub Container Registry** hoch – ohne dein Zutun.

**Schritte:**

1. Die Datei `.github/workflows/docker.yml` ist bereits dafür da. Sie braucht kein
   manuell angelegtes Secret – GitHub stellt automatisch `GITHUB_TOKEN` bereit, und
   `permissions: packages: write` erlaubt den Push.

2. Sorge dafür, dass etwas auf `main` landet (z. B. den `/stats`-PR aus Übung 4
   mergen). Öffne danach **Actions → „Docker"**.

3. Ist der Lauf grün, geh auf dein GitHub-Profil/Repo → Reiter **„Packages"**. Dort
   liegt jetzt `task-manager` mit Tags wie `main` und einem `sha-...`.

4. Kür: Das Image von überall ziehen:

```bash
docker pull ghcr.io/<DEIN-NAME>/cicd-uebung:main
```

(Ggf. vorher `docker login ghcr.io` mit einem Personal Access Token, falls das
Package privat ist.)

**🎯 Aha-Moment:** Aus einem `git merge` entsteht vollautomatisch ein
veröffentlichtes, versioniertes Container-Image. Das ist Continuous Delivery in
Reinform: Jeder Stand von `main` ist jederzeit auslieferbar.

---

## Übung 9 – Automatische Releases über Versions-Tags

**Ziel:** Semantische Versionierung und automatische Release-Notes.

**Schritte:**

```bash
git checkout main && git pull
git tag v0.1.0
git push origin v0.1.0
```

**🎯 Aha-Moment:** Der Tag `v0.1.0` löst **zwei** Workflows aus:
`release.yml` legt unter **„Releases"** automatisch einen Eintrag mit Changelog aus
deinen Commit-Nachrichten an, und `docker.yml` baut zusätzlich ein Image mit dem Tag
`0.1.0`. Ein einziger `git push` eines Tags erzeugt also Release + versioniertes
Artefakt. Probier danach einen zweiten Tag (`v0.2.0` nach ein paar Commits) und sieh,
wie das Changelog nur die *neuen* Änderungen enthält.

---

## Übung 10 – Mit Secrets & Environments arbeiten (Ausblick)

**Ziel:** Verstehen, wie sensible Werte sicher in Pipelines kommen – ohne sie je in
den Code zu schreiben.

**Schritte:**

1. Auf GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
   Lege z. B. `DEPLOY_MESSAGE` mit einem beliebigen Text an.

2. Ergänze in `ci.yml` am Ende des `steps`-Blocks einen Schritt:

```yaml
      - name: Secret benutzen (nur Demo)
        run: echo "Deploy-Hinweis Länge: ${#MSG}"
        env:
          MSG: ${{ secrets.DEPLOY_MESSAGE }}
```

Push und schau ins Log.

**🎯 Aha-Moment:** Im Log siehst du **nie** den Klartext des Secrets – GitHub
maskiert ihn automatisch (`***`). So kommen API-Keys, Zugangsdaten und Deploy-Token in
Pipelines, ohne je im Repository sichtbar zu sein. In echten Projekten hängt an einem
**Environment** (z. B. `production`) zusätzlich oft eine manuelle Freigabe, bevor ein
Deploy läuft – die Brücke von „Continuous Delivery" zu „Continuous Deployment".

---

## Bonus: Pre-commit-Hooks (Fehler abfangen, bevor CI überhaupt läuft)

```bash
pre-commit install
# ab jetzt läuft bei jedem "git commit" automatisch ruff + black
pre-commit run --all-files   # einmal alles prüfen
```

**🎯 Aha-Moment:** Dieselben Checks wie in CI laufen jetzt schon *lokal* vor jedem
Commit. Das verkürzt die Feedback-Schleife von Minuten (CI in der Cloud) auf Sekunden
(dein Rechner) – ein Muster, das gute Teams fast immer nutzen.

---

## Wenn du all das durchhast, verstehst du praktisch:

- **Continuous Integration:** automatische Prüfung bei jedem Push/PR, Matrix-Builds,
  Caching, Linting, Typprüfung, Tests, Coverage-Gates.
- **Continuous Delivery:** automatischer Docker-Build, Push in eine Registry,
  versionierte Artefakte, automatische Releases per Tag.
- **Der Übergang zu Continuous Deployment:** Secrets, Environments und
  Freigabe-Schritte.
- **Der professionelle Arbeitsablauf:** geschützter `main`-Branch, Feature-Branches,
  Pull Requests mit erzwungenen Checks, Pre-commit-Hooks.

## Ideen zum Weitermachen

- Baue einen echten **Deploy-Schritt** ein (z. B. auf Fly.io, Render oder eine
  eigene VM per SSH-Secret).
- Ergänze **Security-Scans** (`pip-audit`, Trivy fürs Docker-Image, CodeQL).
- Tausche den In-Memory-Store gegen **SQLite/PostgreSQL** und teste mit einem
  Datenbank-Service-Container in CI.
- Führe **automatische Abhängigkeits-Updates** mit Dependabot oder Renovate ein.

Viel Erfolg – und trau dich, Dinge kaputtzumachen. Genau dafür ist dieses Projekt da.
