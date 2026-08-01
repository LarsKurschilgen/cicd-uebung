"""Feature Engineering für das Churn-Scoring.

Jede Feature-Funktion bekommt einen Kunden (dict) und gibt einen Wert
zwischen 0.0 und 1.0 zurück. Der Churn-Score ist die gewichtete Summe.

WICHTIG: Die Beträge der Gewichte müssen zusammen 1.0 ergeben.
Sonst sind Scores zwischen zwei Modellständen nicht mehr vergleichbar.
Genau das prüft tests/test_features.py.
"""

# --- Gewichte des Scoring-Modells -------------------------------------
# Negativ = wirkt schützend (senkt das Churn-Risiko)
# Positiv = wirkt treibend (erhöht das Churn-Risiko)
GEWICHTE = {
    "vertragsalter": -0.15,
    "umsatz_risiko": 0.30,
    "ticket_last": 0.20,
    "inaktivitaet": 0.15,
    "nutzungs_intensitaet": -0.20,
}


# --- Feature-Funktionen -----------------------------------------------
def vertragsalter(kunde):
    """Lange Vertragslaufzeit = gewachsene Bindung. Kappung bei 36 Monaten."""
    return min(kunde["vertragsmonate"] / 36.0, 1.0)


def umsatz_risiko(kunde):
    """Kleine Monatsumsätze churnen leichter. Kappung bei 200 EUR."""
    return 1.0 - min(kunde["monatsumsatz"] / 200.0, 1.0)


def ticket_last(kunde):
    """Viele Support-Tickets = Frust. Kappung bei 10 Tickets."""
    return min(kunde["support_tickets"] / 10.0, 1.0)


def inaktivitaet(kunde):
    """Tage seit letzter Nutzung. Kappung bei 60 Tagen."""
    return min(kunde["letzte_nutzung_tage"] / 60.0, 1.0)


def nutzungs_intensitaet(kunde):
    """Logins der letzten 30 Tage. Kappung bei 40 Logins.

    Wer den Dienst taeglich nutzt, kuendigt praktisch nie. Das Feature
    wirkt deshalb mit negativem Gewicht.
    """
    return min(kunde["logins_30d"] / 40.0, 1.0)


# --- Zusammenbau -------------------------------------------------------
def build_features(kunde):
    """Baut den Feature-Vektor für einen Kunden."""
    return {
        "vertragsalter": vertragsalter(kunde),
        "umsatz_risiko": umsatz_risiko(kunde),
        "ticket_last": ticket_last(kunde),
        "inaktivitaet": inaktivitaet(kunde),
        "nutzungs_intensitaet": nutzungs_intensitaet(kunde),
    }


def churn_score(kunde):
    """Gewichtete Summe der Features, normiert auf 0..1."""
    features = build_features(kunde)
    roh = sum(GEWICHTE[name] * wert for name, wert in features.items())
    negativ_anteil = sum(-g for g in GEWICHTE.values() if g < 0)
    return (roh + negativ_anteil) / sum(abs(g) for g in GEWICHTE.values())
