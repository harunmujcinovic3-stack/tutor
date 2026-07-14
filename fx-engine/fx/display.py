# ------------------------------------------------------------
#  display.py — alles wat het systeem ooit LAAT ZIEN loopt hierdoor
#
#  Schermen (menu, wizard, stappenviewer) bouwen een lijst met
#  tekstregels en roepen display.show(regels) aan. Ze printen
#  NOOIT zelf. Daardoor is de overstap naar het originele Casio-
#  LCD straks één nieuwe klasse:
#
#      class CasioLcd(Display):
#          width, rows = 12, 2
#          def show(self, lines): ...  # toetsinjectie / LCD-driver
#
#  ... en één regel in main.py. Verder verandert er niets.
#
#  width/rows zijn onderdeel van het contract: schermen vragen
#  het display hoe groot het is en passen hun lay-out daarop aan.
#  Zo werkt dezelfde code op een brede console én op een smal
#  2-regelig LCD (de viewer verdeelt lange stappen dan over
#  meerdere pagina's).
# ------------------------------------------------------------


class Display:
    width = 24   # tekens per regel
    rows = 8     # zichtbare regels tegelijk

    def show(self, lines):
        raise NotImplementedError


class ConsoleDisplay(Display):
    """Voorlopige weergave via de seriële console / Thonny-shell."""

    def __init__(self, width=32, rows=10):
        self.width = width
        self.rows = rows

    def show(self, lines):
        rand = "+" + "-" * (self.width + 2) + "+"
        print()
        print(rand)
        for line in lines[: self.rows]:
            print("| " + line[: self.width].ljust(self.width) + " |")
        print(rand)
