# ------------------------------------------------------------
#  events.py — de gemeenschappelijke taal van het hele systeem
#
#  Alles wat "invoer" is (knoppen op het breadboard, de Thonny-
#  shell, straks de Casio-toetsenmatrix) wordt vertaald naar
#  dezelfde events. De rest van de code weet daardoor NIETS van
#  hardware.
#
#  Een event is een tuple:
#      ("key",  UP | DOWN | OK | BACK)     navigatie
#      ("text", "3,5")                     een getypte waarde
#
#  Een EventSource is elk object met een methode poll() die
#  None (niets gebeurd) of één event teruggeeft.
# ------------------------------------------------------------

UP = "UP"
DOWN = "DOWN"
OK = "OK"
BACK = "BACK"


def key(name):
    return ("key", name)


def text(value):
    return ("text", value)


class EventSource:
    """Interface: implementaties zijn GpioButtons, ConsoleKeys en
    later de Casio-toetsenmatrix."""

    def poll(self):
        return None
