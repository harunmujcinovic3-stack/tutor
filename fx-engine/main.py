# ------------------------------------------------------------
#  main.py — de "composition root" van FX ENGINE
#
#  Dit is het ENIGE bestand dat beslist welke hardware er echt
#  aan het systeem hangt. Alle toekomstige hardware-wissels
#  (Casio-toetsenmatrix, origineel LCD, toetsinjectie) zijn
#  wijzigingen in dít bestand — nergens anders.
#
#  Op de Pico:  sla de map fx/ en dit bestand op de Pico op;
#               main.py start dan automatisch bij het opstarten.
#  Op een pc:   python3 main.py  (bediening via w/s/Enter/b)
# ------------------------------------------------------------

from fx.app import App
from fx.console import ConsoleKeys
from fx.display import ConsoleDisplay
from fx.menu import MenuScreen
from fx.registry import TOPICS
from fx.wizard import Wizard


def _problem_menu(topic):
    items = [(p.naam, (lambda p=p: Wizard(p))) for p in topic.problems]
    return MenuScreen(topic.naam, items)


def _root_menu():
    items = [(t.naam, (lambda t=t: _problem_menu(t))) for t in TOPICS]
    return MenuScreen("FX Engine", items, is_root=True)


def main():
    display = ConsoleDisplay()          # later: CasioLcd()
    sources = [ConsoleKeys()]           # Thonny-shell werkt altijd

    try:
        from fx.buttons import GpioButtons
        sources.insert(0, GpioButtons())    # later: KeyMatrix()
    except ImportError:
        pass                            # geen machine-module: pc-modus

    App(display, sources, _root_menu()).run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFX ENGINE gestopt.")
