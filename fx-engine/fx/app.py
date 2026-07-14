# ------------------------------------------------------------
#  app.py — de motor: een state-machine met een schermstack
#
#  De App kent geen wiskunde en geen hardware. Hij doet drie
#  dingen, in een strakke lus:
#
#    1. events ophalen bij alle EventSources (knoppen, console)
#    2. het event aan het BOVENSTE scherm op de stack geven
#    3. de actie uitvoeren die dat scherm teruggeeft en opnieuw
#       tekenen via het Display
#
#  Schermen (menu, wizard, viewer) erven van Screen en geven bij
#  handle() een actie terug:
#
#      ("push", scherm)      nieuw scherm bovenop (dieper het menu in)
#      ("pop",)              terug naar het vorige scherm (BACK)
#      ("replace", scherm)   huidig scherm vervangen (wizard -> viewer)
#      None                  alleen opnieuw tekenen
#
#  Door de stack is "terug" op elke diepte gratis en consistent.
# ------------------------------------------------------------

import time

try:
    _sleep_ms = time.sleep_ms          # MicroPython
except AttributeError:
    _sleep_ms = lambda ms: time.sleep(ms / 1000.0)


class Screen:
    def render(self, display):
        """Bouw de tekstregels en geef ze aan display.show()."""
        raise NotImplementedError

    def handle(self, event):
        """Verwerk één event; geef een actie terug (zie hierboven)."""
        return None


class App:
    def __init__(self, display, sources, root):
        self.display = display
        self.sources = sources
        self.stack = [root]

    # -- navigatie ------------------------------------------------
    def _apply(self, actie):
        if not actie:
            return
        soort = actie[0]
        if soort == "push":
            self.stack.append(actie[1])
        elif soort == "replace":
            self.stack[-1] = actie[1]
        elif soort == "pop" and len(self.stack) > 1:
            self.stack.pop()           # het rootmenu blijft altijd staan

    # -- hoofdlus -------------------------------------------------
    def _poll(self):
        for bron in self.sources:
            ev = bron.poll()
            if ev is not None:
                return ev
        return None

    def run(self):
        self.stack[-1].render(self.display)
        while True:
            ev = self._poll()
            if ev is None:
                _sleep_ms(10)
                continue
            actie = self.stack[-1].handle(ev)
            self._apply(actie)
            self.stack[-1].render(self.display)
