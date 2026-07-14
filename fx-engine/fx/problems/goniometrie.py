# ------------------------------------------------------------
#  problems/goniometrie.py — rechthoekige driehoeken (SOS CAS TOA)
#  Hoeken in graden.
# ------------------------------------------------------------

import math

from fx.steps import Step, Field, Problem, Topic, positief, tussen
from fx.utils import nl


def overstaand_met_tan(v):
    A, aanl = v["A"], v["aanl"]
    o = aanl * math.tan(math.radians(A))
    return [
        Step("Kies de juiste regel",
             ["Bekend: hoek en AANLIGGENDE",
              "Gezocht: OVERSTAANDE",
              "→ TOA: tan(A) = o / a"]),
        Step("Formule omschrijven",
             ["o = a · tan(A)"]),
        Step("Invullen",
             ["o = %s · tan(%s°)" % (nl(aanl), nl(A)),
              "tan(%s°) ≈ %s" % (nl(A), nl(math.tan(math.radians(A)), 4))]),
        Step("Uitrekenen",
             ["o ≈ %s · %s" % (nl(aanl), nl(math.tan(math.radians(A)), 4)),
              "o ≈ %s" % nl(o, 2)]),
        Step("Conclusie",
             ["De overstaande zijde is",
              "≈ %s (zelfde eenheid" % nl(o, 2),
              "als de aanliggende)."]),
    ]


def schuine_met_sin(v):
    A, o = v["A"], v["over"]
    s = o / math.sin(math.radians(A))
    return [
        Step("Kies de juiste regel",
             ["Bekend: hoek en OVERSTAANDE",
              "Gezocht: SCHUINE zijde",
              "→ SOS: sin(A) = o / s"]),
        Step("Formule omschrijven",
             ["s = o / sin(A)"]),
        Step("Invullen",
             ["s = %s / sin(%s°)" % (nl(o), nl(A)),
              "sin(%s°) ≈ %s" % (nl(A), nl(math.sin(math.radians(A)), 4))]),
        Step("Uitrekenen",
             ["s ≈ %s / %s" % (nl(o), nl(math.sin(math.radians(A)), 4)),
              "s ≈ %s" % nl(s, 2)]),
    ]


def hoek_berekenen(v):
    o, aanl = v["over"], v["aanl"]
    A = math.degrees(math.atan(o / aanl))
    return [
        Step("Kies de juiste regel",
             ["Bekend: OVERSTAANDE en",
              "AANLIGGENDE zijde",
              "→ TOA: tan(A) = o / a"]),
        Step("Invullen",
             ["tan(A) = %s / %s" % (nl(o), nl(aanl)),
              "tan(A) = %s" % nl(o / aanl, 4)]),
        Step("Inverse tangens",
             ["A = tan⁻¹(%s)" % nl(o / aanl, 4),
              "A ≈ %s°" % nl(A, 1)]),
        Step("Conclusie",
             ["De hoek is ≈ %s°." % nl(A, 1)]),
    ]


TOPIC = Topic("Goniometrie", [
    Problem("Zijde met tan", [
        Field("A", "hoek A (°) =", start=30, check=tussen("A", 1, 89)),
        Field("aanl", "aanliggend =", start=5, check=positief("aanliggend")),
    ], overstaand_met_tan),
    Problem("Schuine met sin", [
        Field("A", "hoek A (°) =", start=30, check=tussen("A", 1, 89)),
        Field("over", "overstaand =", start=5, check=positief("overstaand")),
    ], schuine_met_sin),
    Problem("Hoek berekenen", [
        Field("over", "overstaand =", start=3, check=positief("overstaand")),
        Field("aanl", "aanliggend =", start=4, check=positief("aanliggend")),
    ], hoek_berekenen),
])
