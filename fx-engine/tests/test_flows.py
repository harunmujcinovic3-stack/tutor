# ------------------------------------------------------------
#  tests/test_flows.py — end-to-end test van alle flows (op pc)
#
#  Draait met:  python3 tests/test_flows.py   (vanuit fx-engine/)
#
#  Simuleert knop- en tekst-events en controleert dat:
#   - het menu navigeert en terugkeert
#   - ELKE wizard van ELK probleem volledig doorlopen kan worden
#     (met de standaardwaarden, dus die moeten geldig zijn)
#   - de stappenviewer alle stappen toont en netjes terugkeert
#   - validatie foute invoer tegenhoudt
#   - bekende sommen uit het curriculum het juiste antwoord geven
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
from fx.problems import (parabool, extremen, helling, sinusoide,
                         exponentieel, verdeling, statistiek)


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
        if w is not None:
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


def alles(stappen):
    return " | ".join(s.titel + " :: " + " ".join(s.regels) for s in stappen)


def test_alle_problemen():
    """Doorloop elk probleem met zijn standaardwaarden (alleen OK)."""
    totaal = 0
    aantal = 0
    for ti, topic in enumerate(TOPICS):
        for pi, prob in enumerate(topic.problems):
            app, d = maak_app()
            kies(app, d, ti)            # onderwerp
            kies(app, d, pi)            # probleem
            assert isinstance(app.stack[-1], Wizard), d.laatste
            vul_in(app, d, [None] * len(prob.fields))
            totaal += doorloop_viewer(app, d)
            aantal += 1
            stuur(app, d, events.key(events.BACK))
            assert len(app.stack) == 1
    print("alle %d problemen doorlopen, %d stappen getoond"
          % (aantal, totaal))


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
    assert "2/" in d.laatste            # door naar veld b
    print("validatie ok")


def test_curriculum_sommen():
    # parabool: top van 2x² - 8x + 6 is (2, -2)
    s = alles(parabool.top({"a": 2, "b": -8, "c": 6}))
    assert "x_top = 2" in s and "(2, -2)" in s, s

    # snijpunten van x² - 5x + 6 met de x-as: x=2 en x=3
    s = alles(parabool.snijpunten({"a": 1, "b": -5, "c": 6}))
    assert "(2, 0) en (3, 0)" in s, s

    # snijden met g: x² = x geeft (0,0) en (1,1)
    s = alles(parabool.snijden_met_g(
        {"a": 1, "b": 0, "c": 0, "d": 0, "e": 1, "h": 0}))
    assert "(0, 0)" in s and "(1, 1)" in s, s

    # extremen: max van 165t/(2t²+450) is 2,75 bij t=15
    s = alles(extremen.max_gebroken({"p": 165, "q": 2, "r": 450}))
    assert "t = 15" in s and "2,75" in s, s

    # oplossen 165t/(2t²+450) = 1: dalend onder 1 op t ≈ 79,68
    s = alles(extremen.oplossen_gebroken(
        {"p": 165, "q": 2, "r": 450, "doel": 1}))
    assert "79,68" in s, s

    # max van 0,4t·e^(-0,05t) is ≈ 2,943 bij t=20
    s = alles(extremen.max_e_product({"a": 0.4, "b": 0.05}))
    assert "t = 1 / 0,05 = 20" in s and "2,943" in s, s

    # helling van x^(1/3) - 16/x in x=8 is 1/3
    s = alles(helling.helling_punt({"c": -16, "x0": 8}))
    assert "1/3 (≈ 0,333)" in s, s

    # raaklijn aan √(3x²+24) evenwijdig aan y=-x: a = -2
    s = alles(helling.raaklijn_evenwijdig({"p": 3, "q": 24, "m": -1}))
    assert "Conclusie :: a = -2" in s, s

    # sinusoïde: 3 + 0,5·sin(π/18·(4t+3)) = 3,5 → t = 1,5 / 10,5 / 19,5
    s = alles(sinusoide.tijdstippen(
        {"a": 3, "b": 0.5, "n": 18, "k": 4, "m": 3, "doel": 3.5}))
    assert "1/2π" in s, s
    assert "t = 1,5" in s and "t = 10,5" in s and "t = 19,5" in s, s

    # formule uit grafiek: max 3,5, min 2, periode 6, 1e max op 4,5
    s = alles(sinusoide.formule_uit_grafiek(
        {"max": 3.5, "min": 2, "per": 6, "tmax": 4.5}))
    assert "2,75" in s and "0,75" in s and "1/3π" in s, s
    assert "sin(1/3π·(t - 3))" in s, s

    # exponentieel: 2,5·1,5^t = 100 → t ≈ 9,1
    s = alles(exponentieel.tijd_bij_doel({"b": 2.5, "g": 1.5, "doel": 100}))
    assert "t ≈ 9,1" in s, s

    # logistisch: 200/(1+4e^(-0,15t)) = 100 → t ≈ 9,242
    s = alles(exponentieel.logistisch_tijd(
        {"L": 200, "A": 4, "r": 0.15, "doel": 100}))
    assert "9,242" in s, s

    # kansverdeling (dobbelspel): E(X)=5, P(som=8)=1/4,
    # P(gelijk)=5/18, P(4 v.d. 10 meer) ≈ 0,2428 met p=13/36
    tabel = {"x1": 2, "x2": 4, "x3": 6, "x4": 10,
             "t1": 12, "t2": 6, "t3": 12, "t4": 6}
    s = alles(verdeling.verwachting(tabel))
    assert "E(X) = 5" in s, s
    s = alles(verdeling.som_kans(dict(tabel, s=8)))
    assert "= 1/4" in s, s
    s = alles(verdeling.gelijk(tabel))
    assert "= 5/18" in s, s
    s = alles(verdeling.meer_binomiaal(dict(tabel, n=10, k=4)))
    assert "13/36" in s and "0,2428" in s, s

    # normaal: tussen μ-2σ en μ+0,5σ ligt 66,8%
    s = alles(statistiek.pct_tussen(
        {"mu": 450, "sigma": 4, "g1": 442, "g2": 452}))
    assert "66,8%" in s, s

    # som van verdelingen: 450+100=550, σ=√17
    s = alles(statistiek.som_verdelingen(
        {"mu1": 450, "s1": 4, "mu2": 100, "s2": 1}))
    assert "550" in s and "√17" in s, s

    # hypothesetoets: grens 450,784 → 450,7 → H0 niet verworpen
    s = alles(statistiek.hypothesetoets(
        {"mu": 450, "sigma": 4, "n": 100, "gem": 450.7}))
    assert "450,784" in s and "NIET verworpen" in s, s
    # en een uitkomst buiten de grens wordt wél verworpen
    s = alles(statistiek.hypothesetoets(
        {"mu": 450, "sigma": 4, "n": 100, "gem": 451.2}))
    assert "VERWORPEN" in s, s

    print("curriculum-sommen kloppen")


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
    test_curriculum_sommen()
    test_terugbladeren()
    print("ALLE TESTS GESLAAGD")
