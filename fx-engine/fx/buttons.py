# ------------------------------------------------------------
#  buttons.py — vier fysieke knoppen op het breadboard
#
#  GP2 = UP, GP3 = DOWN, GP4 = OK, GP5 = BACK
#  Elke knop zit tussen de GPIO-pin en GND; we gebruiken de
#  interne pull-up, dus ingedrukt = 0. Geen weerstanden nodig.
#
#  Verantwoordelijkheden:
#    - debounce (dendervrij maken)
#    - auto-repeat op UP/DOWN (ingedrukt houden = doorscrollen)
#    - vertalen naar events; verder niets
#
#  Dit bestand is het ENIGE dat van de knop-hardware afweet.
#  Straks vervangt een KeyMatrix-klasse met dezelfde poll()-
#  interface dit bestand, zonder dat de rest verandert.
# ------------------------------------------------------------

import time
from machine import Pin

from fx import events

_DEBOUNCE_MS = 25       # minimale tijd dat een niveau stabiel moet zijn
_REPEAT_START_MS = 450  # vasthouden: eerste herhaling na ...
_REPEAT_MS = 130        # ... en daarna elke ...

DEFAULT_PINS = {2: events.UP, 3: events.DOWN, 4: events.OK, 5: events.BACK}


class _Button:
    def __init__(self, gpio, name):
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
        self.name = name
        self.stable = 1                   # laatst bevestigde niveau (1 = los)
        self.last_change = time.ticks_ms()
        self.pressed_at = 0
        self.last_repeat = 0

    def poll(self):
        """Geeft de knopnaam terug bij indrukken (en bij auto-repeat)."""
        now = time.ticks_ms()
        level = self.pin.value()
        if level != self.stable:
            if time.ticks_diff(now, self.last_change) >= _DEBOUNCE_MS:
                self.stable = level
                self.last_change = now
                if level == 0:            # zojuist ingedrukt
                    self.pressed_at = now
                    self.last_repeat = now
                    return self.name
        else:
            self.last_change = now
            if self.stable == 0 and self.name in (events.UP, events.DOWN):
                held = time.ticks_diff(now, self.pressed_at)
                since = time.ticks_diff(now, self.last_repeat)
                if held >= _REPEAT_START_MS and since >= _REPEAT_MS:
                    self.last_repeat = now
                    return self.name
        return None


class GpioButtons(events.EventSource):
    def __init__(self, pins=None):
        pins = pins or DEFAULT_PINS
        self.buttons = [_Button(gpio, name) for gpio, name in pins.items()]

    def poll(self):
        for b in self.buttons:
            name = b.poll()
            if name is not None:
                return events.key(name)
        return None
