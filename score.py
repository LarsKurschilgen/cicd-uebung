"""Churn-Scoring: Kunden laden, bewerten, Risiko-Ranking ausgeben.

Aufruf:  python3 score.py
Nur Standardbibliothek, keine Installation nötig.
"""

import csv
import os

from features import build_features, churn_score

DATEI = os.path.join(os.path.dirname(__file__), "data", "kunden.csv")
TOP_N = 15

NUMERISCH = (
    "vertragsmonate",
    "monatsumsatz",
    "support_tickets",
    "letzte_nutzung_tage",
    "zahlungsverzug_tage",
    "logins_30d",
    "gekuendigt",
)


def lade_kunden(pfad=DATEI):
    """Liest die CSV und wandelt alle Zahlenspalten in float um."""
    with open(pfad, newline="", encoding="utf-8") as f:
        kunden = list(csv.DictReader(f))
    for kunde in kunden:
        for spalte in NUMERISCH:
            kunde[spalte] = float(kunde[spalte])
    return kunden


def ranking(kunden):
    """Sortiert Kunden nach Churn-Score, absteigend."""
    bewertet = [(churn_score(k), k) for k in kunden]
    return sorted(bewertet, key=lambda paar: paar[0], reverse=True)


def precision_at_k(rangliste, k):
    """Anteil tatsächlich gekündigter Kunden unter den Top-k Risikofällen."""
    top = rangliste[:k]
    treffer = sum(1 for _, kunde in top if kunde["gekuendigt"] == 1.0)
    return treffer / k


def balken(wert, breite=20):
    return "#" * round(wert * breite)


def main():
    kunden = lade_kunden()
    rangliste = ranking(kunden)
    features = sorted(build_features(kunden[0]))

    print(f"Kunden geladen: {len(kunden)}")
    print(f"Features im Modell ({len(features)}): {', '.join(features)}")
    print()
    print(f"--- Top {TOP_N} Abwanderungsrisiko ---")
    print(f"{'Kunde':<9}{'Score':>7}  {'':<20} gekündigt")
    for score, kunde in rangliste[:TOP_N]:
        markierung = "ja" if kunde["gekuendigt"] == 1.0 else "-"
        print(f"{kunde['kunde_id']:<9}{score:>7.3f}  {balken(score):<20} {markierung}")

    print()
    basisrate = sum(k["gekuendigt"] for k in kunden) / len(kunden)
    print(f"Precision@{TOP_N}: {precision_at_k(rangliste, TOP_N):.1%}")
    print(f"Basisrate:      {basisrate:.1%}")


if __name__ == "__main__":
    main()
