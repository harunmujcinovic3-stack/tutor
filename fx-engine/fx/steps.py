# ------------------------------------------------------------
#  steps.py — het datamodel dat door het hele systeem stroomt
#
#  Dit is het hart van de scheiding tussen REKENEN en TONEN:
#
#    wizard verzamelt        engine rekent           viewer toont
#    ----------------        --------------          ------------
#    {"a": 2, "b": -8,  -->  Problem.solve()   -->   [Step, Step,
#     "c": 6}                                         Step, ...]
#
#  Een Step bevat ALLEEN tekst (titel + regels). Geen enkele
#  aanname over het scherm. De viewer bepaalt hoe een stap wordt
#  weergegeven; straks kan hetzelfde Step-object op het Casio-LCD
#  worden getypt.
# ------------------------------------------------------------


class Step:
    """Eén uitwerkingsstap, zoals een docent hem op het bord zet."""

    def __init__(self, titel, regels):
        self.titel = titel
        self.regels = list(regels)


class Field:
    """Eén invoerveld van de wizard.

    key     naam in de parameter-dict (bijv. "a")
    label   wat de gebruiker ziet (bijv. "a =")
    start   beginwaarde van de editor
    step    stapgrootte van UP/DOWN
    integer True = alleen gehele getallen
    check   optioneel: fn(waarde, eerdere_waarden) -> foutmelding of None
    """

    def __init__(self, key, label, start=0, step=1, integer=False, check=None):
        self.key = key
        self.label = label
        self.start = start
        self.step = step
        self.integer = integer
        self.check = check


class Problem:
    """Eén oplosbaar probleem binnen een onderwerp.

    solve is een functie: dict met veldwaarden -> lijst van Steps.
    Het probleem weet niets van knoppen of schermen.
    """

    def __init__(self, naam, fields, solve):
        self.naam = naam
        self.fields = fields
        self.solve = solve


class Topic:
    """Een menu-onderwerp (Parabool, Kans, ...) met zijn problemen."""

    def __init__(self, naam, problems):
        self.naam = naam
        self.problems = problems


# veelgebruikte veld-controles ---------------------------------

def niet_nul(key):
    def check(waarde, _):
        if waarde == 0:
            return key + " mag niet 0 zijn"
        return None
    return check


def positief(key):
    def check(waarde, _):
        if waarde <= 0:
            return key + " moet > 0 zijn"
        return None
    return check


def tussen(key, lo, hi):
    def check(waarde, _):
        if waarde < lo or waarde > hi:
            return "%s moet tussen %s en %s" % (key, lo, hi)
        return None
    return check
