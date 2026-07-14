# ------------------------------------------------------------
#  problems/extremen.py — extremen berekenen met de afgeleide
#
#  Generieke tools voor twee veelvoorkomende functietypes:
#    - gebroken functie   D = p·t / (q·t² + r)     (quotiëntregel)
#    - e-macht product    E = a·t·e^(-b·t)          (productregel)
#  plus het oplossen van D = doel (abc-formule).
# ------------------------------------------------------------

import math

from fx import math_engine as me
from fx.steps import Step, Field, Problem, Topic, positief
from fx.utils import nl


def _breuk_str(p, q, r):
    return "%st / (%st² + %s)" % (nl(p), nl(q), nl(r))


def max_gebroken(v):
    p, q, r = v["p"], v["q"], v["r"]
    t2 = r / q
    t_top = math.sqrt(t2)
    top = p * t_top / (q * t2 + r)          # = p·t*/(2r)
    return [
        Step("De functie",
             ["D = " + _breuk_str(p, q, r),
              "Zoek het maximum met D'."]),
        Step("Quotiëntregel",
             ["teller u = %st, noemer v = %st² + %s" % (nl(p), nl(q), nl(r)),
              "D' = (u'·v - u·v') / v²",
              "D' = (%s·(%st² + %s) - %st·%st) / (%st² + %s)²"
              % (nl(p), nl(q), nl(r), nl(p), nl(2 * q), nl(q), nl(r))]),
        Step("Teller vereenvoudigen",
             ["%s·%s - %s·%s·t² = %s(%s - %st²)"
              % (nl(p), nl(r), nl(p), nl(q), nl(p), nl(r), nl(q)),
              "Alleen de teller kan 0 worden."]),
        Step("D' = 0 oplossen",
             ["%s - %st² = 0" % (nl(r), nl(q)),
              "t² = %s / %s = %s" % (nl(r), nl(q), nl(t2)),
              "t = %s   (t > 0)" % nl(t_top, 3)]),
        Step("Maximum uitrekenen",
             ["D(%s) = %s·%s / (%s·%s + %s)"
              % (nl(t_top, 3), nl(p), nl(t_top, 3), nl(q), nl(t2), nl(r)),
              "D(%s) = %s" % (nl(t_top, 3), nl(top, 3))]),
        Step("Conclusie",
             ["Maximale waarde ≈ %s" % nl(top, 3),
              "bij t = %s." % nl(t_top, 3),
              "(voor en na het maximum is",
              " D' > 0 resp. D' < 0)"]),
    ]


def oplossen_gebroken(v):
    p, q, r, doel = v["p"], v["q"], v["r"], v["doel"]
    A, B, C = q * doel, -p, r * doel
    stappen = [
        Step("De vergelijking",
             ["%s = %s" % (_breuk_str(p, q, r), nl(doel)),
              "Vermenigvuldig met de noemer:",
              "%st = %s·(%st² + %s)" % (nl(p), nl(doel), nl(q), nl(r))]),
        Step("Op nul herleiden",
             ["%st² - %st + %s = 0" % (nl(A), nl(p), nl(C)),
              "Dit is kwadratisch in t:",
              "a = %s, b = %s, c = %s" % (nl(A), nl(B), nl(C))]),
    ]
    abc, wortels = me.abc_formule_stappen(A, B, C)
    stappen.extend(abc)
    if len(wortels) == 2:
        stappen.append(Step("Conclusie",
                            ["Stijgend DOOR %s op t ≈ %s;"
                             % (nl(doel), nl(wortels[0], 2)),
                             "dalend ONDER %s op t ≈ %s."
                             % (nl(doel), nl(wortels[1], 2))]))
    elif len(wortels) == 1:
        stappen.append(Step("Conclusie",
                            ["De waarde %s wordt precies" % nl(doel),
                             "één keer bereikt: t ≈ %s." % nl(wortels[0], 2)]))
    else:
        stappen.append(Step("Conclusie",
                            ["De waarde %s wordt nooit" % nl(doel),
                             "bereikt (ligt boven het maximum)."]))
    return stappen


def max_e_product(v):
    a, b = v["a"], v["b"]
    t_top = 1.0 / b
    top = a * t_top * math.exp(-1.0)
    return [
        Step("De functie",
             ["E = %s·t·e^(-%st)" % (nl(a), nl(b)),
              "Zoek het maximum met E'."]),
        Step("Productregel",
             ["u = %st,  v = e^(-%st)" % (nl(a), nl(b)),
              "E' = u'·v + u·v'",
              "E' = %s·e^(-%st) + %st·(-%s)·e^(-%st)"
              % (nl(a), nl(b), nl(a), nl(b), nl(b))]),
        Step("E-macht buiten haakjes",
             ["E' = %s·e^(-%st)·(1 - %st)" % (nl(a), nl(b), nl(b))]),
        Step("E' = 0 oplossen",
             ["Een e-macht is NOOIT 0, dus:",
              "1 - %st = 0" % nl(b),
              "t = 1 / %s = %s" % (nl(b), nl(t_top))]),
        Step("Maximum uitrekenen",
             ["E(%s) = %s·%s·e^(-1)" % (nl(t_top), nl(a), nl(t_top)),
              "E(%s) = %s·e^(-1) ≈ %s"
              % (nl(t_top), nl(a * t_top), nl(top, 3))]),
        Step("Conclusie",
             ["Maximale waarde ≈ %s" % nl(top, 3),
              "bij t = %s." % nl(t_top)]),
    ]


def _check_doel(waarde, vals):
    if waarde <= 0:
        return "doel moet > 0 zijn"
    return None


TOPIC = Topic("Extremen (afgeleide)", [
    Problem("Max p·t/(q·t²+r)", [
        Field("p", "p =", start=10, check=positief("p")),
        Field("q", "q =", start=1, check=positief("q")),
        Field("r", "r =", start=25, check=positief("r")),
    ], max_gebroken),
    Problem("Los pt/(qt²+r)=doel op", [
        Field("p", "p =", start=10, check=positief("p")),
        Field("q", "q =", start=1, check=positief("q")),
        Field("r", "r =", start=25, check=positief("r")),
        Field("doel", "doel =", start=0.5, step=0.1, check=_check_doel),
    ], oplossen_gebroken),
    Problem("Max a·t·e^(-bt)", [
        Field("a", "a =", start=0.4, step=0.1, check=positief("a")),
        Field("b", "b =", start=0.05, step=0.01, check=positief("b")),
    ], max_e_product),
])
