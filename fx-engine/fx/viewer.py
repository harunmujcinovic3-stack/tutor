# ------------------------------------------------------------
#  viewer.py — toont de uitwerking, één stap per OK-druk
#
#  De StepViewer krijgt een kant-en-klare lijst Steps en doet
#  daar zelf NIETS wiskundigs mee. Hij is puur presentatie:
#
#      OK / DOWN  = volgende stap
#      UP         = vorige stap (terugbladeren mag altijd)
#      BACK       = terug naar het menu
#      OK op de laatste stap = klaar, terug naar het menu
#
#  Lange stappen worden op woordgrenzen gevouwen naar de breedte
#  van het display — dezelfde code werkt dus straks op het smalle
#  Casio-LCD (dan worden het meerdere pagina's).
# ------------------------------------------------------------

from fx import events, utils
from fx.app import Screen


class StepViewer(Screen):
    def __init__(self, titel, stappen):
        self.titel = titel
        self.stappen = stappen
        self.index = 0

    def render(self, display):
        stap = self.stappen[self.index]
        kop = "%s  [stap %d/%d]" % (self.titel, self.index + 1,
                                    len(self.stappen))
        regels = utils.wrap(kop, display.width)
        regels.extend(utils.wrap(stap.titel, display.width))
        regels.append("")
        regels.extend(utils.wrap_alles(stap.regels, display.width))
        regels.append("")
        laatste = self.index + 1 == len(self.stappen)
        regels.append("OK=klaar" if laatste else "OK=volgende stap")
        display.show(regels)

    def handle(self, event):
        soort, waarde = event
        if soort != "key":
            return None
        if waarde == events.BACK:
            return ("pop",)
        if waarde == events.UP and self.index > 0:
            self.index -= 1
        elif waarde in (events.OK, events.DOWN):
            if self.index + 1 == len(self.stappen):
                if waarde == events.OK:
                    return ("pop",)
            else:
                self.index += 1
        return None
