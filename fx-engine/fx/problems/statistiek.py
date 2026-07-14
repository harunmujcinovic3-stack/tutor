# ------------------------------------------------------------
#  problems/statistiek.py — normale verdeling
# ------------------------------------------------------------

from fx import math_engine as me
from fx.steps import Step, Field, Problem, Topic, positief
from fx.utils import nl


def z_score(v):
    x, mu, sigma = v["x"], v["mu"], v["sigma"]
    z = (x - mu) / sigma
    ligging = "boven" if z > 0 else "onder"
    return [
        Step("De formule",
             ["z = (x - μ) / σ",
              "z meet: hoeveel σ ligt",
              "x van het gemiddelde?"]),
        Step("Invullen",
             ["z = (%s - %s) / %s" % (nl(x), nl(mu), nl(sigma)),
              "z = %s / %s" % (nl(x - mu), nl(sigma))]),
        Step("Uitrekenen",
             ["z ≈ %s" % nl(z, 3)]),
        Step("Betekenis",
             ["x ligt %s σ %s" % (nl(abs(z), 2), ligging),
              "het gemiddelde." +
              (" Dat is uitzonderlijk!" if abs(z) > 2 else "")]),
    ]


def kans_boven(v):
    x, mu, sigma = v["x"], v["mu"], v["sigma"]
    z = (x - mu) / sigma
    kans = 1 - me.phi(z)
    return [
        Step("Eerst de z-score",
             ["z = (x - μ) / σ",
              "z = (%s - %s) / %s = %s"
              % (nl(x), nl(mu), nl(sigma), nl(z, 3))]),
        Step("Kans opzoeken",
             ["P(X > %s) = P(Z > %s)" % (nl(x), nl(z, 3)),
              "= 1 - P(Z ≤ %s)" % nl(z, 3),
              "= 1 - %s" % nl(me.phi(z), 4)]),
        Step("Conclusie",
             ["P(X > %s) ≈ %s" % (nl(x), nl(kans, 4)),
              "≈ %s%%" % nl(kans * 100, 1)]),
    ]


def vuistregels(v):
    mu, sigma = v["mu"], v["sigma"]
    return [
        Step("Vuistregel 68%",
             ["68% ligt tussen μ-σ en μ+σ:",
              "tussen %s en %s" % (nl(mu - sigma), nl(mu + sigma))]),
        Step("Vuistregel 95%",
             ["95% ligt tussen μ-2σ en μ+2σ:",
              "tussen %s en %s" % (nl(mu - 2 * sigma), nl(mu + 2 * sigma))]),
        Step("Uitzonderlijk",
             ["Buiten μ ± 2σ ligt maar 5%:",
              "onder %s of boven %s" % (nl(mu - 2 * sigma),
                                        nl(mu + 2 * sigma)),
              "→ zulke waarden zijn bijzonder."]),
    ]


_VELDEN_MS = [
    Field("mu", "gemiddelde =", start=100),
    Field("sigma", "sigma =", start=15, check=positief("sigma")),
]

TOPIC = Topic("Statistiek", [
    Problem("Z-score", _VELDEN_MS + [Field("x", "x =", start=115)], z_score),
    Problem("Kans P(X > x)", _VELDEN_MS + [Field("x", "x =", start=115)],
            kans_boven),
    Problem("Vuistregels 68/95", _VELDEN_MS, vuistregels),
])
