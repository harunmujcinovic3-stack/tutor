# ------------------------------------------------------------
#  problems/parabool.py — f(x) = ax² + bx + c
#
#  Elke problemenmodule exporteert precies één naam: TOPIC.
#  De registry pikt die op; verder hoeft er nergens iets te
#  veranderen om een onderwerp toe te voegen.
# ------------------------------------------------------------

from fx import math_engine as me
from fx.steps import Step, Field, Problem, Topic, niet_nul
from fx.utils import nl


def _velden_abc():
    return [
        Field("a", "a =", start=1, check=niet_nul("a")),
        Field("b", "b =", start=0),
        Field("c", "c =", start=0),
    ]


def _intro(v):
    return Step("De functie",
                ["f(x) = " + me.poly_str(v["a"], v["b"], v["c"])])


def top(v):
    stappen, _ = me.top_stappen(v["a"], v["b"], v["c"])
    return [_intro(v)] + stappen


def snijpunten(v):
    a, b, c = v["a"], v["b"], v["c"]
    stappen = [_intro(v),
               Step("Snijpunten met de x-as",
                    ["Los op: f(x) = 0",
                     me.poly_str(a, b, c) + " = 0"])]
    abc, wortels = me.abc_formule_stappen(a, b, c)
    stappen.extend(abc)
    if len(wortels) == 2:
        stappen.append(Step("Conclusie",
                            ["Snijpunten met de x-as:",
                             "(%s, 0) en (%s, 0)"
                             % (nl(wortels[0]), nl(wortels[1]))]))
    elif len(wortels) == 1:
        stappen.append(Step("Conclusie",
                            ["De grafiek RAAKT de x-as",
                             "in (%s, 0)." % nl(wortels[0])]))
    else:
        stappen.append(Step("Conclusie",
                            ["De grafiek snijdt de",
                             "x-as niet."]))
    return stappen


def discriminant(v):
    a, b, c = v["a"], v["b"], v["c"]
    stappen = [_intro(v)]
    d_stappen, D = me.discriminant_stappen(a, b, c)
    stappen.extend(d_stappen)
    if D > 0:
        conclusie = "D > 0: TWEE snijpunten met de x-as."
    elif D == 0:
        conclusie = "D = 0: de x-as wordt GERAAKT (1 punt)."
    else:
        conclusie = "D < 0: GEEN snijpunten met de x-as."
    stappen.append(Step("Betekenis", [conclusie]))
    return stappen


def raaklijn(v):
    a, b, c, x0 = v["a"], v["b"], v["c"], v["x0"]
    rc = 2 * a * x0 + b
    y0 = me.f_waarde(a, b, c, x0)
    sn = y0 - rc * x0
    return [
        _intro(v),
        Step("Afgeleide bepalen",
             ["f'(x) = 2ax + b",
              "f'(x) = %sx %s %s"
              % (nl(2 * a), "-" if b < 0 else "+", nl(abs(b)))]),
        Step("Helling in x = " + nl(x0),
             ["rc = f'(%s)" % nl(x0),
              "rc = %s·%s %s %s = %s"
              % (nl(2 * a), nl(x0), "-" if b < 0 else "+",
                 nl(abs(b)), nl(rc))]),
        Step("Raakpunt bepalen",
             ["y = f(%s) = %s" % (nl(x0), nl(y0)),
              "Raakpunt: (%s, %s)" % (nl(x0), nl(y0))]),
        Step("Lijn opstellen",
             ["y = rc·x + n door raakpunt:",
              "%s = %s·%s + n" % (nl(y0), nl(rc), nl(x0)),
              "n = %s" % nl(sn)]),
        Step("Conclusie",
             ["Raaklijn:",
              "y = %sx %s %s"
              % (nl(rc), "-" if sn < 0 else "+", nl(abs(sn)))]),
    ]


TOPIC = Topic("Parabool", [
    Problem("Top bepalen", _velden_abc(), top),
    Problem("Snijpunten x-as", _velden_abc(), snijpunten),
    Problem("Discriminant", _velden_abc(), discriminant),
    Problem("Raaklijn", _velden_abc() + [Field("x0", "x0 =", start=1)],
            raaklijn),
])
