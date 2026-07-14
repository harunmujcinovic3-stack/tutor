# ------------------------------------------------------------
#  wizard.py — verzamelt de invoer, veld voor veld
#
#  De wizard toont steeds één Field van het gekozen Problem:
#
#      a = 2
#
#  Waarde aanpassen kan op twee manieren tegelijk:
#    - UP/DOWN (± stapgrootte van het veld, met auto-repeat)
#    - een getal typen in de shell (event ("text", "3,5"))
#
#  OK bevestigt het veld (na validatie), BACK gaat een veld
#  terug (of verlaat de wizard bij het eerste veld).
#
#  Zodra alle velden gevuld zijn roept de wizard ALLEEN MAAR
#  problem.solve(values) aan en vervangt zichzelf door een
#  StepViewer met het resultaat. De wizard rekent zelf niets uit
#  — dat is de kern van de scheiding rekenen/tonen.
# ------------------------------------------------------------

from fx import events, utils
from fx.app import Screen
from fx.steps import Step
from fx.viewer import StepViewer


class Wizard(Screen):
    def __init__(self, problem):
        self.problem = problem
        self.index = 0
        self.values = {}
        self.huidig = problem.fields[0].start
        self.fout = None

    # -- helpers ---------------------------------------------------
    def _field(self):
        return self.problem.fields[self.index]

    def _laad_veld(self):
        f = self._field()
        self.huidig = self.values.get(f.key, f.start)
        self.fout = None

    def _klaar(self):
        try:
            stappen = self.problem.solve(dict(self.values))
        except Exception as e:                    # vangnet: nooit crashen
            stappen = [Step("Fout in berekening",
                            ["Er ging iets mis:", str(e),
                             "Controleer de invoer."])]
        return ("replace", StepViewer(self.problem.naam, stappen))

    # -- Screen-interface -------------------------------------------
    def render(self, display):
        f = self._field()
        regels = [self.problem.naam.upper(),
                  "Invoer %d/%d" % (self.index + 1, len(self.problem.fields)),
                  "",
                  "  %s %s" % (f.label, utils.nl(self.huidig))]
        if self.fout:
            regels.append("! " + self.fout)
        regels.append("")
        regels.extend(utils.wrap("UP/DOWN of typ getal, OK=verder",
                                 display.width))
        display.show(regels)

    def handle(self, event):
        soort, waarde = event
        f = self._field()

        if soort == "text":
            getal = utils.parse_getal(waarde)
            if getal is None:
                self.fout = "geen geldig getal"
            else:
                self.huidig = round(getal) if f.integer else getal
                self.fout = None
            return None

        if waarde == events.UP:
            self.huidig += 1 if f.integer else f.step
        elif waarde == events.DOWN:
            self.huidig -= 1 if f.integer else f.step
        elif waarde == events.BACK:
            if self.index == 0:
                return ("pop",)
            self.index -= 1
            self._laad_veld()
        elif waarde == events.OK:
            if f.check:
                self.fout = f.check(self.huidig, self.values)
                if self.fout:
                    return None
            self.values[f.key] = self.huidig
            if self.index + 1 == len(self.problem.fields):
                return self._klaar()
            self.index += 1
            self._laad_veld()
        return None
