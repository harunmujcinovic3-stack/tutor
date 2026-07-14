# ------------------------------------------------------------
#  registry.py — de enige plek die alle onderwerpen kent
#
#  Nieuw onderwerp toevoegen = 2 regels in dít bestand:
#    1. de module importeren
#    2. toevoegen aan de lijst
#  (MicroPython kan mappen niet betrouwbaar scannen, daarom een
#  expliciete lijst — dat is op embedded ook sneller en zuiniger.)
# ------------------------------------------------------------

from fx.problems import parabool
from fx.problems import exponentieel
from fx.problems import goniometrie
from fx.problems import kans
from fx.problems import statistiek

TOPICS = [
    parabool.TOPIC,
    exponentieel.TOPIC,
    goniometrie.TOPIC,
    kans.TOPIC,
    statistiek.TOPIC,
]
