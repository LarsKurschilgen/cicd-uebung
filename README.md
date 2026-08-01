# Churn-Scoring (Übungsprojekt)

Kleines Data-Science-Beispiel: 120 Kunden eines Abo-Dienstes werden nach
Abwanderungsrisiko bewertet. Reine Standardbibliothek, nichts zu installieren.

```
data/kunden.csv          120 Kunden, 7 Merkmale + Label "gekuendigt"
features.py              Feature Engineering + Gewichte des Scoring-Modells
score.py                 lädt Daten, erzeugt Risiko-Ranking, misst Precision@15
tests/test_features.py   Tests für Gewichte, Wertebereiche, Monotonie
```

## Ausführen

```bash
python3 score.py                  # Risiko-Ranking
python3 tests/test_features.py    # Tests (auch mit pytest lauffähig)
```

## Warum dieses Repo existiert

Es ist die Übungsvorlage für **Merge-Konflikte**. Zwei Branches haben
unabhängig voneinander dasselbe Scoring-Modell erweitert:

| Branch | Änderung |
|---|---|
| `main` | Feature `zahlungs_risiko` (Zahlungsverzug in Tagen) |
| `feature/nutzungsintensitaet` | Feature `nutzungs_intensitaet` (Logins der letzten 30 Tage) |

Beide haben dafür dieselben Stellen in `features.py` angefasst. Der Merge
kracht — und genau das sollst du auflösen.

Die Schritt-für-Schritt-Anleitung steht in **ANLEITUNG.md**.
