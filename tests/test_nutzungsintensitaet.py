"""Tests fuer das Feature nutzungs_intensitaet."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features import churn_score, nutzungs_intensitaet  # noqa: E402

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


def test_intensitaet_ist_gekappt():
    assert nutzungs_intensitaet(dict(BASIS, logins_30d=90.0)) == 1.0


def test_intensitaet_bei_null_logins():
    assert nutzungs_intensitaet(dict(BASIS, logins_30d=0.0)) == 0.0


def test_viele_logins_senken_den_score():
    wenig = dict(BASIS, logins_30d=2.0)
    viel = dict(BASIS, logins_30d=38.0)
    assert churn_score(viel) < churn_score(wenig)


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
