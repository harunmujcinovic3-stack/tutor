# ------------------------------------------------------------
#  menu.py — een herbruikbaar keuzemenu
#
#  Een MenuScreen krijgt (label, maker)-paren; `maker` is een
#  functie die het VOLGENDE scherm bouwt zodra de gebruiker OK
#  drukt. Het menu weet dus niet wat erachter zit — het rootmenu,
#  het onderwerpmenu en elk toekomstig submenu zijn exact
#  dezelfde klasse.
#
#  Het menu scrollt automatisch als er meer items zijn dan het
#  display regels heeft (belangrijk voor het 2-regelige Casio-LCD).
# ------------------------------------------------------------

from fx import events
from fx.app import Screen


class MenuScreen(Screen):
    def __init__(self, titel, items, is_root=False):
        self.titel = titel
        self.items = items            # lijst van (label, maker_functie)
        self.cursor = 0
        self.is_root = is_root

    def render(self, display):
        zichtbaar = display.rows - 1                # 1 regel voor de titel
        eerste = 0
        if self.cursor >= zichtbaar:
            eerste = self.cursor - zichtbaar + 1
        regels = [self.titel.upper()]
        for i in range(eerste, min(eerste + zichtbaar, len(self.items))):
            marker = "> " if i == self.cursor else "  "
            regels.append(marker + self.items[i][0])
        display.show(regels)

    def handle(self, event):
        soort, waarde = event
        if soort != "key":
            return None
        if waarde == events.UP:
            self.cursor = (self.cursor - 1) % len(self.items)
        elif waarde == events.DOWN:
            self.cursor = (self.cursor + 1) % len(self.items)
        elif waarde == events.OK:
            maker = self.items[self.cursor][1]
            return ("push", maker())
        elif waarde == events.BACK and not self.is_root:
            return ("pop",)
        return None
