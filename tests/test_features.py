"""Grundtests für das Scoring-Modell.

Laufen ohne pytest:  python3 tests/test_features.py
Oder mit pytest:     pytest
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features import GEWICHTE, build_features, churn_score  # noqa: E402

BEISPIELKUNDE = {
    "kunde_id": "K-9999",
    "vertragsmonate": 12.0,
    "monatsumsatz": 100.0,
    "support_tickets": 5.0,
    "letzte_nutzung_tage": 30.0,
    "zahlungsverzug_tage": 10.0,
    "logins_30d": 20.0,
    "gekuendigt": 0.0,
}


def test_gewichte_summieren_auf_eins():
    """Die Beträge aller Gewichte müssen exakt 1.0 ergeben.

    Wird beim Zusammenführen zweier Modellstände gern übersehen: wenn beide
    Seiten ihre Features behalten, ist die Summe plötzlich größer als 1.
    """
    summe = sum(abs(g) for g in GEWICHTE.values())
    assert round(summe, 6) == 1.0, f"Summe der Gewichtsbeträge ist {summe}, erwartet 1.0"


def test_jedes_feature_hat_ein_gewicht():
    """build_features und GEWICHTE müssen exakt dieselben Schlüssel haben."""
    assert set(build_features(BEISPIELKUNDE)) == set(GEWICHTE)


def test_features_liegen_zwischen_null_und_eins():
    for name, wert in build_features(BEISPIELKUNDE).items():
        assert 0.0 <= wert <= 1.0, f"{name} liegt mit {wert} ausserhalb von 0..1"


def test_score_liegt_zwischen_null_und_eins():
    assert 0.0 <= churn_score(BEISPIELKUNDE) <= 1.0


def test_inaktiver_kunde_hat_hoeheren_score():
    aktiv = dict(BEISPIELKUNDE, letzte_nutzung_tage=1.0)
    inaktiv = dict(BEISPIELKUNDE, letzte_nutzung_tage=59.0)
    assert churn_score(inaktiv) > churn_score(aktiv)


if __name__ == "__main__":
    fehler = 0
    for name, funktion in sorted(globals().items()):
        if name.startswith("test_") and callable(funktion):
            try:
                funktion()
                print(f"PASS  {name}")
            except AssertionError as exc:
                fehler += 1
                print(f"FAIL  {name}: {exc}")
    print(f"\n{'Alle Tests gruen.' if not fehler else f'{fehler} Test(s) fehlgeschlagen.'}")
    sys.exit(1 if fehler else 0)
