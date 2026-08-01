# Übung: Merge-Konflikt im Scoring-Modell auflösen

## Die Ausgangslage

Zwei Leute im Team haben unabhängig voneinander dasselbe Churn-Modell
erweitert — und dabei dieselben Zeilen in `features.py` angefasst.

| Wer | Branch | Neues Feature | Idee dahinter |
|---|---|---|---|
| Jonas | `main` | `zahlungs_risiko` | Zahlungsverzug in Tagen ist ein Frühindikator |
| Ayşe | `feature/nutzungsintensitaet` | `nutzungs_intensitaet` | Wer täglich einloggt, kündigt nicht |

Beide Änderungen sind für sich richtig. Beide Branches sind grün.
Trotzdem kann Git sie nicht automatisch zusammenführen: sie haben dieselbe
`GEWICHTE`-Tabelle und dieselbe `build_features`-Funktion umgebaut.

Deine Aufgabe: den Merge durchführen und das Ergebnis so auflösen, dass
**beide** Features im Modell landen und alle Tests grün sind.

---

## Schritt 0 — Ausgangszustand ansehen

```bash
cd Try
git log --oneline --graph --all
```

Du siehst zwei Commits, die auf demselben Basis-Commit sitzen.
Vorher einmal schauen, wie gut das Modell aktuell ist:

```bash
python3 score.py
```

Notier dir die **Precision@15** ganz unten. Das ist die Kennzahl, die du
gleich verbessern wirst.

Und einmal reinschauen, was die andere Seite gemacht hat:

```bash
git diff main feature/nutzungsintensitaet -- features.py
```

---

## Schritt 1 — Merge starten

```bash
git checkout main
git merge feature/nutzungsintensitaet
```

Git meldet:

```
Auto-merging features.py
CONFLICT (content): Merge conflict in features.py
Automatic merge failed; fix conflicts and then commit the result.
```

Das ist kein Fehler, sondern eine Rückfrage. Git sagt: *„Hier weiß nur
ein Mensch, was gemeint ist."* Der Merge ist jetzt **angefangen, aber nicht
abgeschlossen**. `git status` zeigt dir jederzeit, wo du stehst:

```bash
git status
```

`UU features.py` = beide Seiten haben die Datei geändert (**U**nmerged).
`tests/test_nutzungsintensitaet.py` kam dagegen sauber dazu — neue Dateien
kollidieren nicht.

> **Ausstieg jederzeit möglich:** `git merge --abort` setzt alles auf den
> Zustand vor dem Merge zurück. Nichts geht kaputt. Trau dich zu
> experimentieren.

---

## Schritt 2 — Die Konfliktmarker lesen

Öffne `features.py`. Du findest **drei** Konfliktstellen in diesem Muster:

```
<<<<<<< HEAD
    ... so steht es auf main (Jonas)
=======
    ... so steht es im Feature-Branch (Ayşe)
>>>>>>> feature/nutzungsintensitaet
```

Merkregel:

- zwischen `<<<<<<< HEAD` und `=======` steht **deine** Seite (der Branch, auf dem du gerade bist)
- zwischen `=======` und `>>>>>>>` steht die **hereinkommende** Seite

Die drei Stellen sind:

1. **`GEWICHTE`** — beide haben die Gewichte umverteilt und je ein Feature ergänzt
2. **Die Feature-Funktionen** — `zahlungs_risiko` gegen `nutzungs_intensitaet`
3. **`build_features`** — beide haben einen Eintrag ins Rückgabe-Dict gesetzt

---

## Schritt 3 — Auflösen

Stellen 2 und 3 sind einfach: **beide Seiten behalten.** Die zwei Funktionen
stören sich nicht, und beide Einträge sollen ins Dict. Marker-Zeilen
(`<<<<<<<`, `=======`, `>>>>>>>`) rauslöschen, beide Codeblöcke stehen lassen.

Stelle 1 ist die interessante — und der eigentliche Punkt der Übung.
Hier reicht „beides behalten" **nicht**. Schau dir den Docstring oben in
`features.py` an:

> Die Beträge der Gewichte müssen zusammen 1.0 ergeben.

Wenn du beide Seiten stumpf übernimmst, kommst du auf 1.15. Das Modell wäre
nicht kaputt, aber die Scores wären nicht mehr mit früheren Läufen
vergleichbar — ein Fehler, den man ohne Test wochenlang nicht bemerkt.
Genau deshalb gibt es `test_gewichte_summieren_auf_eins`.

Du musst also **fachlich entscheiden**: alle sechs Features behalten und die
Gewichte so neu verteilen, dass die Beträge wieder 1.0 ergeben. Zum Beispiel:

```python
GEWICHTE = {
    "vertragsalter": -0.12,
    "umsatz_risiko": 0.25,
    "ticket_last": 0.18,
    "inaktivitaet": 0.15,
    "zahlungs_risiko": 0.15,
    "nutzungs_intensitaet": -0.15,
}
```

Das ist ein Vorschlag, keine Musterlösung. Jede Verteilung, die auf 1.0 kommt
und beide neuen Features nennenswert gewichtet, ist eine gültige Antwort.
Probier ruhig eigene Werte und schau, was mit der Precision passiert.

---

## Schritt 4 — Prüfen

Erst: sind wirklich alle Marker weg?

```bash
grep -n "<<<<<<<\|=======\|>>>>>>>" features.py
```

Keine Ausgabe = sauber. (Ein vergessener Marker ist der häufigste Anfängerfehler —
der Code ist dann kein gültiges Python mehr.)

Dann alle Tests:

```bash
python3 tests/test_features.py
python3 tests/test_zahlungsrisiko.py
python3 tests/test_nutzungsintensitaet.py
```

Oder auf einen Schlag, falls du pytest hast:

```bash
pytest
```

Und der Lohn der Mühe:

```bash
python3 score.py
```

Mit beiden Features zusammen sollte die Precision@15 deutlich über den
86,7 % vom Anfang liegen — die zusammengeführte Version schafft rund 93 %.
Das ist die Pointe: der Merge war nicht bloß Buchhaltung, sondern hat das
Modell tatsächlich besser gemacht.

---

## Schritt 5 — Merge abschließen

```bash
git add features.py
git commit
```

Git hat die Commit-Nachricht schon vorbereitet („Merge branch …"). Ergänze
gern eine Zeile dazu, **wie** du die Gewichte aufgelöst hast — genau danach
sucht in sechs Monaten jemand.

Fertig:

```bash
git log --oneline --graph
```

Du siehst jetzt einen Merge-Commit mit zwei Elternteilen — die Stelle, an der
die beiden Entwicklungslinien wieder zusammenlaufen.

---

## Wieder von vorn anfangen

Wenn der Merge schon abgeschlossen ist:

```bash
git checkout main
git reset --hard HEAD~1     # macht den Merge-Commit rückgängig
```

Wenn du mittendrin steckst, reicht `git merge --abort`.

Zur Kontrolle: `git log --oneline` auf `main` sollte danach mit
„Uebungsanleitung fuer den Merge-Konflikt" beginnen, und `git status`
sauber sein. Dann kannst du bei Schritt 1 wieder einsteigen.

---

## Spickzettel

| Befehl | Wofür |
|---|---|
| `git status` | Wo stehe ich? Welche Dateien sind noch offen? |
| `git diff` | Was genau kollidiert? |
| `git merge --abort` | Merge abbrechen, alles zurück auf Anfang |
| `git checkout --ours features.py` | Konflikt komplett zugunsten von main lösen |
| `git checkout --theirs features.py` | Konflikt komplett zugunsten des Feature-Branch lösen |
| `git add <datei>` | Datei als aufgelöst markieren |
| `git commit` | Merge abschließen |
| `git log --oneline --graph --all` | Verlauf als Baum |

`--ours` / `--theirs` sind praktisch, wenn eine Seite eindeutig gewinnt.
Hier taugen sie nicht: du brauchst beide Seiten und obendrein etwas Drittes,
das in keinem der Branches steht.

---

## Die eigentliche Lehre

Ein Merge-Konflikt ist keine technische Panne. Er ist die Stelle, an der Git
merkt, dass zwei Leute dieselbe Frage unterschiedlich beantwortet haben, und
zugibt, dass es die richtige Antwort nicht kennt. In der Data Science trifft
das besonders oft die Stellen, an denen Fachwissen steckt: Gewichte,
Schwellenwerte, Hyperparameter.

Deswegen der Merkzettel für den Alltag: Wenn beim Auflösen die Antwort nicht
„links", „rechts" oder „beides" lautet, sondern etwas Drittes — dann war es
nie ein Git-Problem. Dann war es eine inhaltliche Entscheidung, die noch
niemand getroffen hatte.
