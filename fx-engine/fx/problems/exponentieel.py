# ------------------------------------------------------------
#  problems/exponentieel.py — N = b · g^t
# ------------------------------------------------------------

import math

from fx.steps import Step, Field, Problem, Topic, positief
from fx.utils import nl


def waarde_na_t(v):
    b, g, t = v["b"], v["g"], v["t"]
    N = b * (g ** t)
    return [
        Step("Het model",
             ["N = b · g^t",
              "b = %s (beginwaarde)" % nl(b),
              "g = %s (groeifactor)" % nl(g)]),
        Step("Invullen",
             ["N = %s · %s^%s" % (nl(b), nl(g), nl(t)),
              "%s^%s = %s" % (nl(g), nl(t), nl(g ** t, 4))]),
        Step("Uitrekenen",
             ["N = %s · %s" % (nl(b), nl(g ** t, 4)),
              "N ≈ %s" % nl(N, 2)]),
        Step("Conclusie",
             ["Na t = %s is de" % nl(t),
              "hoeveelheid ≈ %s." % nl(N, 2)]),
    ]


def tijd_bij_doel(v):
    b, g, N = v["b"], v["g"], v["doel"]
    t = math.log(N / b) / math.log(g)
    return [
        Step("De vergelijking",
             ["Los op: b · g^t = N",
              "%s · %s^t = %s" % (nl(b), nl(g), nl(N))]),
        Step("Deel door b",
             ["%s^t = %s / %s" % (nl(g), nl(N), nl(b)),
              "%s^t = %s" % (nl(g), nl(N / b, 4))]),
        Step("Logaritme nemen",
             ["t = log(%s) / log(%s)" % (nl(N / b, 4), nl(g)),
              "(want g^t = w geeft",
              " t = log(w)/log(g))"]),
        Step("Uitrekenen",
             ["t ≈ %s / %s" % (nl(math.log10(N / b), 4),
                               nl(math.log10(g), 4)),
              "t ≈ %s" % nl(t, 2)]),
        Step("Conclusie",
             ["Na t ≈ %s tijdseenheden" % nl(t, 2),
              "is de hoeveelheid %s." % nl(N)]),
    ]


def percentage_naar_factor(v):
    p = v["p"]
    g = 1 + p / 100.0
    soort = "groei" if p >= 0 else "afname"
    return [
        Step("Regel",
             ["groeifactor",
              "g = 1 + p/100"]),
        Step("Invullen",
             ["p = %s%% (%s)" % (nl(p), soort),
              "g = 1 + %s/100" % nl(p),
              "g = %s" % nl(g, 4)]),
        Step("Conclusie",
             ["%s%% per tijdseenheid" % nl(p),
              "hoort bij g = %s." % nl(g, 4)]),
    ]


def _check_g(waarde, _):
    if waarde <= 0:
        return "g moet > 0 zijn"
    if waarde == 1:
        return "g = 1 is geen groei"
    return None


def _check_doel(waarde, values):
    if waarde <= 0:
        return "doel moet > 0 zijn"
    return None


TOPIC = Topic("Exponentieel", [
    Problem("Waarde na tijd t", [
        Field("b", "b (begin) =", start=100, check=positief("b")),
        Field("g", "g (factor) =", start=1.05, step=0.01, check=_check_g),
        Field("t", "t =", start=5),
    ], waarde_na_t),
    Problem("Tijd berekenen", [
        Field("b", "b (begin) =", start=100, check=positief("b")),
        Field("g", "g (factor) =", start=1.05, step=0.01, check=_check_g),
        Field("doel", "doel N =", start=200, check=_check_doel),
    ], tijd_bij_doel),
    Problem("% naar factor", [
        Field("p", "p (%) =", start=5, step=0.5),
    ], percentage_naar_factor),
])
