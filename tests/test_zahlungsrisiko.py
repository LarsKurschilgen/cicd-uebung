"""Tests fuer das Feature zahlungs_risiko."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features import churn_score, zahlungs_risiko  # noqa: E402

BASIS = {
    "kunde_id": "K-9999",
    "vertragsmonate": 12.0,
    "monatsumsatz": 100.0,
    "support_tickets": 5.0,
    "letzte_nutzung_tage": 30.0,
    "zahlungsverzug_tage": 10.0,
    "logins_30d": 20.0,
    "gekuendigt": 0.0,
}


def test_verzug_ist_gekappt():
    assert zahlungs_risiko(dict(BASIS, zahlungsverzug_tage=120.0)) == 1.0


def test_kein_verzug_kein_risiko():
    assert zahlungs_risiko(dict(BASIS, zahlungsverzug_tage=0.0)) == 0.0


def test_verzug_erhoeht_den_score():
    puenktlich = dict(BASIS, zahlungsverzug_tage=0.0)
    saeumig = dict(BASIS, zahlungsverzug_tage=28.0)
    assert churn_score(saeumig) > churn_score(puenktlich)


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
    sys.exit(1 if fehler else 0)
