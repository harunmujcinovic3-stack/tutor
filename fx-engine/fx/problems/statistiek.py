# ------------------------------------------------------------
#  problems/statistiek.py — normale verdeling
# ------------------------------------------------------------

import math

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


# vlakdelen per halve sigma, van -2σ tot +2σ (vuistregel-figuur)
_VLAK = [0.044, 0.092, 0.150, 0.191, 0.191, 0.150, 0.092, 0.044]


def _sigma_afstand(g, mu, sigma):
    return (g - mu) / float(sigma)


def _check_grens(key):
    def check(waarde, vals):
        k = _sigma_afstand(waarde, vals.get("mu", 0), vals.get("sigma", 1))
        if abs(k * 2 - round(k * 2)) > 1e-9:
            return key + ": moet heel aantal halve σ van μ"
        if k < -2 or k > 2:
            return key + ": tussen μ-2σ en μ+2σ"
        if key == "g2" and waarde <= vals.get("g1", waarde - 1):
            return "g2 moet boven g1"
        return None
    return check


def pct_tussen(v):
    mu, sigma, g1, g2 = v["mu"], v["sigma"], v["g1"], v["g2"]
    k1 = _sigma_afstand(g1, mu, sigma)
    k2 = _sigma_afstand(g2, mu, sigma)
    i1 = int(round((k1 + 2) * 2))
    i2 = int(round((k2 + 2) * 2))
    stroken = _VLAK[i1:i2]
    som = sum(stroken)

    def afstand_txt(k):
        if k == 0:
            return "μ"
        return "μ %s %sσ" % ("+" if k > 0 else "-", nl(abs(k)))

    return [
        Step("Grenzen in σ-afstanden",
             ["(%s - %s)/%s = %s" % (nl(g1), nl(mu), nl(sigma), nl(k1)),
              "→ %s" % afstand_txt(k1),
              "(%s - %s)/%s = %s" % (nl(g2), nl(mu), nl(sigma), nl(k2)),
              "→ %s" % afstand_txt(k2)]),
        Step("Vlakdelen aflezen",
             ["Per halve σ tussen",
              "%s en %s:" % (afstand_txt(k1), afstand_txt(k2)),
              " + ".join(nl(s, 3) for s in stroken)]),
        Step("Optellen",
             ["som = %s" % nl(som, 3)]),
        Step("Conclusie",
             ["%s%% van de waarden ligt" % nl(som * 100, 1),
              "tussen %s en %s." % (nl(g1), nl(g2))]),
    ]


def som_verdelingen(v):
    mu1, s1, mu2, s2 = v["mu1"], v["s1"], v["mu2"], v["s2"]
    kw = s1 * s1 + s2 * s2
    st = math.sqrt(kw)
    return [
        Step("Gemiddelden optellen",
             ["μ_totaal = μ1 + μ2",
              "μ_totaal = %s + %s = %s" % (nl(mu1), nl(mu2), nl(mu1 + mu2))]),
        Step("Let op bij σ!",
             ["σ's mag je NIET optellen.",
              "Wel de varianties (σ²):",
              "σ_tot = √(σ1² + σ2²)"]),
        Step("Invullen",
             ["σ_tot = √(%s² + %s²)" % (nl(s1), nl(s2)),
              "σ_tot = √(%s + %s) = √%s"
              % (nl(s1 * s1), nl(s2 * s2), nl(kw))]),
        Step("Conclusie",
             ["gemiddelde: %s" % nl(mu1 + mu2),
              "σ: √%s ≈ %s" % (nl(kw), nl(st, 4))]),
    ]


def hypothesetoets(v):
    mu, sigma, n, gem = v["mu"], v["sigma"], int(v["n"]), v["gem"]
    se = sigma / math.sqrt(n)
    boven = gem >= mu
    grens = mu + 1.96 * se if boven else mu - 1.96 * se
    verwerp = gem > grens if boven else gem < grens
    kant = "rechter" if boven else "linker"
    return [
        Step("Hypothesen (tweezijdig)",
             ["H0: μ = %s" % nl(mu),
              "H1: μ ≠ %s" % nl(mu),
              "α = 0,05"]),
        Step("σ van het gemiddelde",
             ["Gemiddelde van n = %d is ook" % n,
              "normaal verdeeld, met",
              "σ_gem = σ/√n = %s/√%d = %s"
              % (nl(sigma), n, nl(se, 3))]),
        Step("Grenswaarde (%skant)" % kant,
             ["Uitkomst %s ligt %s μ, dus" % (nl(gem), "boven" if boven
                                              else "onder"),
              "vergelijk met de %sgrens:" % kant,
              "gr = %s %s 1,96·%s = %s"
              % (nl(mu), "+" if boven else "-", nl(se, 3), nl(grens, 3))]),
        Step("Vergelijken",
             ["%s ligt %s %s"
              % (nl(gem), ("BOVEN" if verwerp else "onder") if boven else
                 ("ONDER" if verwerp else "boven"), nl(grens, 3))]),
        Step("Conclusie",
             ["H0 wordt %s." % ("VERWORPEN" if verwerp else
                                "NIET verworpen"),
              "Er is %s reden om aan het" % ("dus" if verwerp else "geen"),
              "gemiddelde %s te twijfelen." % nl(mu)]),
    ]


_VELDEN_MS = [
    Field("mu", "gemiddelde =", start=100),
    Field("sigma", "sigma =", start=15, check=positief("sigma")),
]


def _check_n(waarde, _):
    if waarde < 2:
        return "n moet minstens 2 zijn"
    return None


TOPIC = Topic("Normaal & toetsen", [
    Problem("Z-score", _VELDEN_MS + [Field("x", "x =", start=115)], z_score),
    Problem("Kans P(X > x)", _VELDEN_MS + [Field("x", "x =", start=115)],
            kans_boven),
    Problem("Vuistregels 68/95", _VELDEN_MS, vuistregels),
    Problem("% tussen 2 grenzen", [
        Field("mu", "gemiddelde =", start=100),
        Field("sigma", "sigma =", start=8, check=positief("sigma")),
        Field("g1", "ondergrens =", start=84, check=_check_grens("g1")),
        Field("g2", "bovengrens =", start=104, check=_check_grens("g2")),
    ], pct_tussen),
    Problem("Som 2 verdelingen", [
        Field("mu1", "gemiddelde 1 =", start=450),
        Field("s1", "sigma 1 =", start=4, check=positief("sigma 1")),
        Field("mu2", "gemiddelde 2 =", start=100),
        Field("s2", "sigma 2 =", start=1, check=positief("sigma 2")),
    ], som_verdelingen),
    Problem("Hypothesetoets", [
        Field("mu", "μ volgens H0 =", start=450),
        Field("sigma", "sigma =", start=4, check=positief("sigma")),
        Field("n", "n (steekproef) =", start=100, integer=True,
              check=_check_n),
        Field("gem", "gevonden gem. =", start=450.7, step=0.1),
    ], hypothesetoets),
])
