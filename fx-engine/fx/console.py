# ------------------------------------------------------------
#  console.py — invoer via de Thonny-shell (of een pc-terminal)
#
#  Handig tijdens het ontwikkelen: je hoeft niet steeds knoppen
#  in te drukken. Werkt ALTIJD naast de fysieke knoppen; beide
#  bronnen worden door de App tegelijk uitgelezen.
#
#      w + Enter   = UP            s + Enter = DOWN
#      Enter       = OK            b + Enter = BACK
#      3,5 + Enter = getal typen (in de invoer-wizard)
#
#  Werkt op MicroPython én op een gewone pc (python3 main.py),
#  zodat je zonder Pico kunt demonstreren en testen.
# ------------------------------------------------------------

import select
import sys

from fx import events

_KEYS = {"w": events.UP, "s": events.DOWN, "": events.OK, "b": events.BACK}


class ConsoleKeys(events.EventSource):
    def __init__(self):
        self._buffer = ""
        self._poller = select.poll()
        self._poller.register(sys.stdin, select.POLLIN)

    def poll(self):
        while self._poller.poll(0):
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                line = self._buffer.strip()
                self._buffer = ""
                lower = line.lower()
                if lower in _KEYS:
                    return events.key(_KEYS[lower])
                return events.text(line)
            self._buffer += ch
        return None
