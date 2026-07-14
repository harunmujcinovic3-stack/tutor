# ------------------------------------------------------------
#  problems/sinusoide.py — sinusoïden
#
#  Generieke tools:
#    - D = a + b·sin(π/n·(k·t + m)) = doel algebraïsch oplossen
#      (eerste drie tijdstippen na t = 0)
#    - formule D = a + b·sin(c·(t - d)) opstellen uit een grafiek
#      (maximum, minimum, periode, tijdstip eerste maximum)
# ------------------------------------------------------------

import math

from fx.steps import Step, Field, Problem, Topic, positief
from fx.utils import nl, pi_frac


def _binnen(k, m):
    if m == 0:
        return "%st" % nl(k)
    return "%st %s %s" % (nl(k), "+" if m > 0 else "-", nl(abs(m)))


def tijdstippen(v):
    a, b, n, k, m, doel = (v["a"], v["b"], v["n"], v["k"], v["m"], v["doel"])
    w = (doel - a) / b
    binnen = _binnen(k, m)
    sinus = "sin(π/%s·(%s))" % (nl(n), binnen)
    periode = 2.0 * n / k

    stappen = [
        Step("De vergelijking",
             ["%s + %s·%s = %s" % (nl(a), nl(b), sinus, nl(doel))]),
        Step("Sinus isoleren",
             ["%s =" % sinus,
              "(%s - %s) / %s = %s" % (nl(doel), nl(a), nl(b), nl(w, 3))]),
    ]

    basis1 = math.asin(w)
    if abs(abs(w) - 1.0) < 1e-9:
        hoeken = [basis1]
        stappen.append(Step("Basisoplossing",
                            ["sin(...) = %s is de %s," %
                             (nl(w), "top" if w > 0 else "dal"),
                             "dus maar één serie:",
                             "π/%s·(%s) = %s + j·2π"
                             % (nl(n), binnen, pi_frac(basis1))]))
    else:
        basis2 = math.pi - basis1
        hoeken = [basis1, basis2]
        stappen.append(Step("Basisoplossingen (2 series)",
                            ["π/%s·(%s) = %s + j·2π" %
                             (nl(n), binnen, pi_frac(basis1)),
                             "of",
                             "π/%s·(%s) = %s + j·2π" %
                             (nl(n), binnen, pi_frac(basis2))]))

    t_starts = []
    regels = ["Deel door π/%s" % nl(n),
              "(= keer %s/π):" % nl(n)]
    for hoek in hoeken:
        rhs = hoek * n / math.pi
        t0 = (rhs - m) / k
        t_starts.append(t0)
        regels.append("%s = %s + j·%s" % (binnen, nl(rhs, 3), nl(2 * n)))
        regels.append("→ t = %s + j·%s" % (nl(t0, 3), nl(periode, 3)))
    stappen.append(Step("Naar t oplossen", regels))

    stappen.append(Step("Periode",
                        ["periode = 2π / (π·%s/%s)" % (nl(k), nl(n)),
                         "        = 2·%s/%s = %s"
                         % (nl(n), nl(k), nl(periode, 3))]))

    kandidaten = []
    for t0 in t_starts:
        for j in range(-4, 6):
            t = t0 + j * periode
            if t > 1e-9:
                kandidaten.append(t)
    kandidaten.sort()
    top3 = kandidaten[:3]
    stappen.append(Step("Eerste drie na t = 0",
                        ["t = %s" % nl(top3[0], 3),
                         "t = %s" % nl(top3[1], 3),
                         "t = %s" % nl(top3[2], 3)]))
    return stappen


def formule_uit_grafiek(v):
    mx, mn, per, tmax = v["max"], v["min"], v["per"], v["tmax"]
    a = (mx + mn) / 2.0
    b = (mx - mn) / 2.0
    c = 2.0 * math.pi / per
    d = tmax - per / 4.0
    return [
        Step("Evenwichtsstand a",
             ["a = (max + min) / 2",
              "a = (%s + %s) / 2 = %s" % (nl(mx), nl(mn), nl(a))]),
        Step("Amplitude b",
             ["b = (max - min) / 2",
              "b = (%s - %s) / 2 = %s" % (nl(mx), nl(mn), nl(b))]),
        Step("Factor c",
             ["c = 2π / periode",
              "c = 2π / %s = %s" % (nl(per), pi_frac(c))]),
        Step("Verschuiving d",
             ["De sinus gaat STIJGEND door",
              "de evenwichtsstand een kwart",
              "periode vóór het maximum:",
              "d = %s - %s/4 = %s" % (nl(tmax), nl(per), nl(d))]),
        Step("Conclusie",
             ["D = %s + %s·sin(%s·(t - %s))"
              % (nl(a), nl(b), pi_frac(c), nl(d))]),
    ]


def _check_doel(waarde, vals):
    a = vals.get("a", 0)
    b = vals.get("b", 1)
    if b == 0 or abs((waarde - a) / b) > 1:
        return "doel buiten bereik van D"
    return None


def _check_b(waarde, _):
    if waarde == 0:
        return "b mag niet 0 zijn"
    return None


def _check_min(waarde, vals):
    if waarde >= vals.get("max", 0):
        return "min moet onder max"
    return None


TOPIC = Topic("Sinusoide", [
    Problem("Los D = doel op", [
        Field("a", "a (evenwicht) =", start=3, step=0.5),
        Field("b", "b (amplitude) =", start=0.5, step=0.1, check=_check_b),
        Field("n", "n (c = π/n) =", start=18, check=positief("n")),
        Field("k", "k (bij t) =", start=4, check=positief("k")),
        Field("m", "m (+ getal) =", start=3),
        Field("doel", "doel D =", start=3.5, step=0.1, check=_check_doel),
    ], tijdstippen),
    Problem("Formule uit grafiek", [
        Field("max", "maximum =", start=3.5, step=0.5),
        Field("min", "minimum =", start=2, step=0.5, check=_check_min),
        Field("per", "periode =", start=6, check=positief("periode")),
        Field("tmax", "t v.h. 1e max =", start=4.5, step=0.5),
    ], formule_uit_grafiek),
])
