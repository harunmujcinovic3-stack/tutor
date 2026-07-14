# ------------------------------------------------------------
#  problems/helling.py — hellingen en raaklijnen (machtsregels)
#
#  Generieke tools:
#    - helling in een punt van f(x) = x^(1/3) + c/x
#      (derdemachtswortel + breuk herschrijven naar machten)
#    - raaklijn aan k(x) = √(p·x² + q) evenwijdig aan y = m·x
#      (kettingregel, kwadrateren, tekencontrole)
# ------------------------------------------------------------

import math

from fx.steps import Step, Field, Problem, Topic, positief
from fx.utils import nl, breuk


def helling_punt(v):
    c, x0 = v["c"], v["x0"]
    # f(x) = x^(1/3) + c/x  ->  f'(x) = (1/3)x^(-2/3) - c·x^(-2)
    w23 = x0 ** (2.0 / 3.0)
    helling = 1.0 / (3.0 * w23) - c / (x0 * x0)
    teken = "-" if c >= 0 else "+"

    stappen = [
        Step("De functie",
             ["f(x) = x^(1/3) %s %s/x" % ("-" if c < 0 else "+", nl(abs(c))),
              "Gevraagd: helling in x = %s." % nl(x0)]),
        Step("Herschrijven naar machten",
             ["Breuken en wortels eerst",
              "als machten schrijven:",
              "f(x) = x^(1/3) %s %s·x^(-1)"
              % ("-" if c < 0 else "+", nl(abs(c)))]),
        Step("Differentiëren (machtsregel)",
             ["f'(x) = 1/3·x^(-2/3) %s %s·x^(-2)" % (teken, nl(abs(c))),
              "(exponent naar voren,",
              " nieuwe exponent 1 lager)"]),
    ]

    kr = round(x0 ** (1.0 / 3.0))
    if abs(kr ** 3 - x0) < 1e-9 and c == int(c):
        # nette breuken mogelijk (x0 is een derdemacht)
        kr = int(kr)
        n1, d1 = 1, 3 * kr * kr
        n2, d2 = -int(c), int(x0 * x0)
        tn = n1 * d2 + n2 * d1
        td = d1 * d2
        stappen.append(Step("Invullen x = " + nl(x0),
                            ["%s^(-2/3) = 1/%s² = 1/%d" % (nl(x0), kr, kr * kr),
                             "f'(%s) = 1/3·1/%d %s %s/%d"
                             % (nl(x0), kr * kr, teken, nl(abs(c)),
                                int(x0 * x0))]))
        stappen.append(Step("Breuken optellen",
                            ["= %s %s %s" % (breuk(n1, d1),
                                             "+" if n2 >= 0 else "-",
                                             breuk(abs(n2), d2)),
                             "= %s" % breuk(tn, td)]))
        stappen.append(Step("Conclusie",
                            ["De helling in x = %s" % nl(x0),
                             "is %s (≈ %s)." % (breuk(tn, td),
                                                nl(tn / td, 3))]))
    else:
        stappen.append(Step("Invullen x = " + nl(x0),
                            ["%s^(-2/3) ≈ %s" % (nl(x0), nl(1 / w23, 4)),
                             "f'(%s) ≈ 1/3·%s %s %s"
                             % (nl(x0), nl(1 / w23, 4), teken,
                                nl(abs(c) / (x0 * x0), 4))]))
        stappen.append(Step("Conclusie",
                            ["De helling in x = %s" % nl(x0),
                             "is ≈ %s." % nl(helling, 4)]))
    return stappen


def raaklijn_evenwijdig(v):
    p, q, m = v["p"], v["q"], v["m"]
    noemer = p * p - m * m * p
    a2 = m * m * q / noemer
    a_abs = math.sqrt(a2)
    a = a_abs if m > 0 else -a_abs
    wa = int(round(a_abs)) if abs(a_abs - round(a_abs)) < 1e-9 else None

    return [
        Step("Wat betekent evenwijdig?",
             ["De lijn y = %sx heeft" % nl(m),
              "helling %s, dus zoek a met:" % nl(m),
              "k'(a) = %s" % nl(m)]),
        Step("Kettingregel",
             ["k(x) = √(%sx² + %s)" % (nl(p), nl(q)),
              "k'(x) = %sx / (2·√(%sx² + %s))" % (nl(2 * p), nl(p), nl(q)),
              "     = %sx / √(%sx² + %s)" % (nl(p), nl(p), nl(q))]),
        Step("Vergelijking opstellen",
             ["%sa / √(%sa² + %s) = %s" % (nl(p), nl(p), nl(q), nl(m)),
              "%sa = %s·√(%sa² + %s)" % (nl(p), nl(m), nl(p), nl(q))]),
        Step("Kwadrateren",
             ["%sa² = %s·(%sa² + %s)" % (nl(p * p), nl(m * m), nl(p), nl(q)),
              "%sa² = %s" % (nl(noemer), nl(m * m * q)),
              "a² = %s" % nl(a2, 3)]),
        Step("Oplossingen en controle",
             ["a = %s of a = -%s" % (nl(a_abs, 3), nl(a_abs, 3)),
              "k'(x) heeft hetzelfde teken",
              "als x, dus a moet hetzelfde",
              "teken hebben als m = %s." % nl(m)]),
        Step("Conclusie",
             ["a = %s" % (nl(a, 3) if wa is None else nl(a)),
              "(de andere kandidaat geeft",
              " helling %s, niet %s)" % (nl(-m), nl(m))]),
    ]


def _check_m(waarde, vals):
    if waarde == 0:
        return "m mag niet 0 zijn"
    p = vals.get("p", 1)
    if p * p - waarde * waarde * p <= 0:
        return "|m| te groot: geen oplossing"
    return None


TOPIC = Topic("Helling & raaklijn", [
    Problem("Helling x^(1/3)+c/x", [
        Field("c", "c =", start=-16),
        Field("x0", "x0 =", start=8, check=positief("x0")),
    ], helling_punt),
    Problem("Raaklijn // y=mx", [
        Field("p", "p =", start=3, check=positief("p")),
        Field("q", "q =", start=24, check=positief("q")),
        Field("m", "m (helling) =", start=-1, check=_check_m),
    ], raaklijn_evenwijdig),
])
