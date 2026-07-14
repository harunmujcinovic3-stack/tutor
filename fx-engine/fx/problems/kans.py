# ------------------------------------------------------------
#  problems/kans.py — binomiale kansen
# ------------------------------------------------------------

from fx import math_engine as me
from fx.steps import Step, Field, Problem, Topic, tussen
from fx.utils import nl


def _check_k(waarde, values):
    if waarde < 0 or waarde > values.get("n", 0):
        return "k moet tussen 0 en n"
    return None


def _check_n(waarde, _):
    if waarde < 1:
        return "n moet minstens 1 zijn"
    return None


def precies_k(v):
    n, p, k = int(v["n"]), v["p"], int(v["k"])
    C = me.comb(n, k)
    kans = C * (p ** k) * ((1 - p) ** (n - k))
    return [
        Step("Herken de situatie",
             ["Binomiaal: n = %d keer," % n,
              "succeskans p = %s," % nl(p),
              "precies k = %d successen." % k]),
        Step("De formule",
             ["P(X = k) =",
              "C(n,k) · p^k · (1-p)^(n-k)"]),
        Step("Combinaties tellen",
             ["C(%d,%d) = %d" % (n, k, C),
              "(aantal volgordes waarin",
              " de successen kunnen vallen)"]),
        Step("Invullen",
             ["P = %d · %s^%d · %s^%d"
              % (C, nl(p), k, nl(1 - p), n - k)]),
        Step("Uitrekenen",
             ["P(X = %d) ≈ %s" % (k, nl(kans, 4))]),
    ]


def minstens_een(v):
    n, p = int(v["n"]), v["p"]
    q = (1 - p) ** n
    kans = 1 - q
    return [
        Step("Slim omdraaien",
             ["P(minstens 1 succes) =",
              "1 - P(GEEN enkel succes)"]),
        Step("Kans op geen succes",
             ["P(geen) = (1 - p)^n",
              "P(geen) = %s^%d" % (nl(1 - p), n),
              "P(geen) ≈ %s" % nl(q, 4)]),
        Step("Complement",
             ["P(minstens 1) = 1 - %s" % nl(q, 4),
              "≈ %s" % nl(kans, 4)]),
    ]


def verwachting(v):
    n, p = int(v["n"]), v["p"]
    E = n * p
    var = n * p * (1 - p)
    sd = var ** 0.5
    return [
        Step("Verwachtingswaarde",
             ["E(X) = n · p",
              "E(X) = %d · %s = %s" % (n, nl(p), nl(E, 2))]),
        Step("Standaardafwijking",
             ["σ = √(n·p·(1-p))",
              "σ = √(%d·%s·%s)" % (n, nl(p), nl(1 - p)),
              "σ = √%s ≈ %s" % (nl(var, 3), nl(sd, 3))]),
        Step("Conclusie",
             ["Verwacht: %s successen," % nl(E, 2),
              "spreiding σ ≈ %s." % nl(sd, 3)]),
    ]


_VELDEN_NP = [
    Field("n", "n =", start=10, integer=True, check=_check_n),
    Field("p", "p =", start=0.5, step=0.05, check=tussen("p", 0, 1)),
]

TOPIC = Topic("Binomiaal", [
    Problem("Binomiaal P(X=k)",
            _VELDEN_NP + [Field("k", "k =", start=3, integer=True,
                                check=_check_k)],
            precies_k),
    Problem("Minstens 1 keer", _VELDEN_NP, minstens_een),
    Problem("E(X) en sigma", _VELDEN_NP, verwachting),
])
