# ------------------------------------------------------------
#  tests/test_flows.py — end-to-end test van alle flows (op pc)
#
#  Draait met:  python3 tests/test_flows.py   (vanuit fx-engine/)
#
#  Simuleert knop- en tekst-events en controleert dat:
#   - het menu navigeert en terugkeert
#   - ELKE wizard van ELK probleem volledig doorlopen kan worden
#   - de stappenviewer alle stappen toont en netjes terugkeert
#   - validatie foute invoer tegenhoudt
#   - een paar bekende sommen het juiste antwoord geven
# ------------------------------------------------------------

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fx import events
from fx.app import App
from fx.display import Display
from fx.menu import MenuScreen
from fx.registry import TOPICS
from fx.wizard import Wizard
from fx.viewer import StepViewer


class FakeDisplay(Display):
    width = 32
    rows = 12

    def __init__(self):
        self.frames = []

    def show(self, lines):
        self.frames.append(list(lines))

    @property
    def laatste(self):
        return "\n".join(self.frames[-1])


def maak_app():
    from main import _root_menu
    d = FakeDisplay()
    app = App(d, [], _root_menu())
    app.stack[-1].render(d)
    return app, d


def stuur(app, d, ev):
    app._apply(app.stack[-1].handle(ev))
    app.stack[-1].render(d)


def kies(app, d, index):
    """Zet de cursor op `index` en druk OK."""
    scherm = app.stack[-1]
    assert isinstance(scherm, MenuScreen), d.laatste
    while scherm.cursor != index:
        stuur(app, d, events.key(events.DOWN))
    stuur(app, d, events.key(events.OK))


def vul_in(app, d, waarden):
    for w in waarden:
        stuur(app, d, events.text(str(w)))
        stuur(app, d, events.key(events.OK))


def doorloop_viewer(app, d):
    viewer = app.stack[-1]
    assert isinstance(viewer, StepViewer), d.laatste
    n = len(viewer.stappen)
    assert n >= 3, "te weinig stappen: " + d.laatste
    for _ in range(n):
        assert "stap" in d.laatste
        stuur(app, d, events.key(events.OK))
    assert isinstance(app.stack[-1], MenuScreen), d.laatste
    return n


STANDAARD = {                       # veilige invoer per veldnaam
    "a": 2, "b": -8, "c": 6, "x0": 1, "g": 1.05, "t": 5, "doel": 200,
    "p": 0.5, "n": 10, "k": 3, "A": 30, "aanl": 5, "over": 3,
    "mu": 100, "sigma": 15, "x": 115,
}
STANDAARD_EXPONENTIEEL = dict(STANDAARD, b=100, p=5)


def test_alle_problemen():
    totaal = 0
    for ti, topic in enumerate(TOPICS):
        for pi, prob in enumerate(topic.problems):
            app, d = maak_app()
            kies(app, d, ti)            # onderwerp
            kies(app, d, pi)            # probleem
            assert isinstance(app.stack[-1], Wizard), d.laatste
            basis = (STANDAARD_EXPONENTIEEL
                     if topic.naam == "Exponentieel" else STANDAARD)
            vul_in(app, d, [basis[f.key] for f in prob.fields])
            totaal += doorloop_viewer(app, d)
            # BACK vanaf probleemmenu -> onderwerpmenu -> root
            stuur(app, d, events.key(events.BACK))
            assert len(app.stack) == 1
    print("alle %d problemen doorlopen, %d stappen getoond"
          % (sum(len(t.problems) for t in TOPICS), totaal))


def test_validatie():
    app, d = maak_app()
    kies(app, d, 0)                     # Parabool
    kies(app, d, 0)                     # Top bepalen
    stuur(app, d, events.text("0"))
    stuur(app, d, events.key(events.OK))
    assert "mag niet 0" in d.laatste    # blijft staan met foutmelding
    assert isinstance(app.stack[-1], Wizard)
    stuur(app, d, events.text("2"))
    stuur(app, d, events.key(events.OK))
    assert "2/3" in d.laatste           # door naar veld b
    print("validatie ok")


def test_bekende_sommen():
    # top van 2x² - 8x + 6 is (2, -2)
    app, d = maak_app()
    kies(app, d, 0)
    kies(app, d, 0)
    vul_in(app, d, [2, -8, 6])
    alles = ""
    viewer = app.stack[-1]
    for stap in viewer.stappen:
        alles += stap.titel + " " + " ".join(stap.regels) + "\n"
    assert "x_top = 2" in alles, alles
    assert "(2, -2)" in alles, alles

    # snijpunten van x² - 5x + 6 zijn x=2 en x=3
    app, d = maak_app()
    kies(app, d, 0)
    kies(app, d, 1)
    vul_in(app, d, [1, -5, 6])
    alles = " ".join(" ".join(s.regels) for s in app.stack[-1].stappen)
    assert "(2, 0) en (3, 0)" in alles, alles

    # binomiaal n=10, p=0.5, k=3: C=120, P≈0.1172
    app, d = maak_app()
    kies(app, d, 3)
    kies(app, d, 0)
    vul_in(app, d, [10, "0,5", 3])
    alles = " ".join(" ".join(s.regels) for s in app.stack[-1].stappen)
    assert "C(10,3) = 120" in alles, alles
    assert "0,1172" in alles, alles
    print("bekende sommen kloppen")


def test_terugbladeren():
    app, d = maak_app()
    kies(app, d, 0)
    kies(app, d, 2)                     # Discriminant
    vul_in(app, d, [1, 2, 5])           # D = 4 - 20 = -16
    viewer = app.stack[-1]
    stuur(app, d, events.key(events.OK))
    assert viewer.index == 1
    stuur(app, d, events.key(events.UP))
    assert viewer.index == 0
    stuur(app, d, events.key(events.BACK))
    assert isinstance(app.stack[-1], MenuScreen)
    print("terugbladeren ok")


if __name__ == "__main__":
    test_alle_problemen()
    test_validatie()
    test_bekende_sommen()
    test_terugbladeren()
    print("ALLE TESTS GESLAAGD")
