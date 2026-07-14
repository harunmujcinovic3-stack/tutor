# ------------------------------------------------------------
#  math_engine.py — herbruikbare wiskundige bouwstenen
#
#  Problemen componeren hun uitwerking uit deze bouwstenen. De
#  abc-formule wordt bijvoorbeeld gebruikt door "Snijpunten",
#  "Discriminant" én toekomstige modules — de stappen worden hier
#  één keer goed opgeschreven.
#
#  Elke bouwsteen geeft (stappen, resultaat) terug:
#  pure functies, geen I/O, geen hardware.
# ------------------------------------------------------------

import math

from fx.steps import Step
from fx.utils import nl, term


def poly_str(a, b, c):
    """f(x) = 2x² - 8x + 6 (netjes met tekens en zonder 1x)."""
    delen = [term(a, "x²", eerste=True), term(b, "x"), term(c, "")]
    s = " ".join(d for d in delen if d)
    return s if s else "0"


def f_waarde(a, b, c, x):
    return a * x * x + b * x + c


def discriminant_stappen(a, b, c):
    """Stappen voor D = b2 - 4ac; geeft ([Step], D) terug."""
    D = b * b - 4 * a * c
    stappen = [
        Step("Discriminant opstellen",
             ["D = b² - 4ac",
              "met a = %s, b = %s, c = %s" % (nl(a), nl(b), nl(c))]),
        Step("Invullen",
             ["D = (%s)² - 4·%s·%s" % (nl(b), nl(a), nl(c)),
              "D = %s - %s" % (nl(b * b), nl(4 * a * c)),
              "D = %s" % nl(D)]),
    ]
    return stappen, D


def abc_formule_stappen(a, b, c):
    """Volledige abc-formule; geeft ([Step], [oplossingen]) terug."""
    stappen, D = discriminant_stappen(a, b, c)
    if D < 0:
        stappen.append(Step("Conclusie",
                            ["D < 0, dus er zijn",
                             "GEEN oplossingen."]))
        return stappen, []
    if D == 0:
        x = -b / (2.0 * a)
        stappen.append(Step("Een oplossing (D = 0)",
                            ["x = -b / (2a)",
                             "x = %s / %s" % (nl(-b), nl(2 * a)),
                             "x = %s" % nl(x)]))
        return stappen, [x]
    w = math.sqrt(D)
    x1 = (-b - w) / (2.0 * a)
    x2 = (-b + w) / (2.0 * a)
    stappen.append(Step("abc-formule",
                        ["x = (-b ± √D) / (2a)",
                         "x = (%s ± √%s) / %s"
                         % (nl(-b), nl(D), nl(2 * a)),
                         "√D = √%s = %s" % (nl(D), nl(w))]))
    stappen.append(Step("Twee oplossingen",
                        ["x1 = (%s - %s)/%s = %s"
                         % (nl(-b), nl(w), nl(2 * a), nl(x1)),
                         "x2 = (%s + %s)/%s = %s"
                         % (nl(-b), nl(w), nl(2 * a), nl(x2))]))
    return stappen, sorted([x1, x2])


def top_stappen(a, b, c):
    """Top van de parabool; geeft ([Step], (xt, yt)) terug."""
    xt = -b / (2.0 * a)
    yt = f_waarde(a, b, c, xt)
    stappen = [
        Step("Gebruik de formule",
             ["x_top = -b / (2a)",
              "met a = %s en b = %s" % (nl(a), nl(b))]),
        Step("Invullen",
             ["x_top = -(%s) / (2 * %s)" % (nl(b), nl(a)),
              "x_top = %s / %s" % (nl(-b), nl(2 * a)),
              "x_top = %s" % nl(xt)]),
        Step("x_top invullen in f",
             ["f(%s) = %s" % (nl(xt), poly_str(a, b, c).replace("x", "(%s)" % nl(xt))),
              "f(%s) = %s" % (nl(xt), nl(yt))]),
        Step("Conclusie",
             ["De top is (%s, %s)." % (nl(xt), nl(yt)),
              "a %s 0, dus een %s." %
              (">" if a > 0 else "<",
               "dalparabool (minimum)" if a > 0 else
               "bergparabool (maximum)")]),
    ]
    return stappen, (xt, yt)


def comb(n, k):
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r


def phi(z):
    """Standaardnormale verdelingsfunctie P(Z <= z)."""
    try:
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    except AttributeError:
        t = 1.0 / (1.0 + 0.2316419 * abs(z))
        pdf = math.exp(-z * z / 2.0) / math.sqrt(2.0 * math.pi)
        p = 1.0 - pdf * t * (0.319381530 + t * (-0.356563782 + t * (
            1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        return p if z >= 0 else 1.0 - p
