# ------------------------------------------------------------
#  problems/verdeling.py — een eigen kansverdeling (tabel)
#
#  De gebruiker voert zijn eigen kansverdelingstabel in:
#  vier waarden x1..x4 met kansen als TELLERS OP 36
#  (dus 1/3 = 12, 1/6 = 6; samen precies 36).
#  Daardoor rekent alles exact met breuken, zoals op papier.
#
#  Tools: E(X), P(som van 2 spelers = s), P(beiden gelijk),
#  en binomiaal: P(speler 1 wint precies k van de n beurten).
# ------------------------------------------------------------

from fx import math_engine as me
from fx.steps import Step, Field, Problem, Topic
from fx.utils import nl, breuk


def _tabel(v):
    xs = [int(v["x1"]), int(v["x2"]), int(v["x3"]), int(v["x4"])]
    ts = [int(v["t1"]), int(v["t2"]), int(v["t3"]), int(v["t4"])]
    paren = [(x, t) for x, t in zip(xs, ts) if t > 0]
    return paren


def _tabel_stap(paren):
    return Step("De kansverdeling",
                ["x:    " + "  ".join("%4d" % x for x, _ in paren),
                 "P(x): " + "  ".join("%4s" % breuk(t, 36)
                                      for _, t in paren)])


def verwachting(v):
    paren = _tabel(v)
    som = sum(x * t for x, t in paren)
    return [
        _tabel_stap(paren),
        Step("Formule",
             ["E(X) = som van",
              "(waarde × kans)"]),
        Step("Invullen",
             ["E(X) = " + " + ".join("%d·%s" % (x, breuk(t, 36))
                                     for x, t in paren)]),
        Step("Uitrekenen",
             ["E(X) = %s" % breuk(som, 36),
              "     = %s" % nl(som / 36.0, 3)]),
    ]


def som_kans(v):
    paren = _tabel(v)
    s = int(v["s"])
    combi = [(x1, x2, t1 * t2)
             for x1, t1 in paren for x2, t2 in paren if x1 + x2 == s]
    totaal = sum(t for _, _, t in combi)
    regels = []
    for x1, x2, t in combi:
        regels.append("(%d, %d): kans %s" % (x1, x2, breuk(t, 1296)))
    stappen = [
        _tabel_stap(paren),
        Step("Combinaties met som %d" % s,
             ["(speler 1, speler 2):"] + (regels or ["geen enkele!"])),
    ]
    if combi:
        stappen.append(Step("Optellen",
                            ["P(som = %d) =" % s,
                             " + ".join(breuk(t, 1296) for _, _, t in combi),
                             "= %s ≈ %s" % (breuk(totaal, 1296),
                                            nl(totaal / 1296.0, 4))]))
    else:
        stappen.append(Step("Conclusie",
                            ["Som %d is onmogelijk:" % s,
                             "P = 0"]))
    return stappen


def gelijk(v):
    paren = _tabel(v)
    som = sum(t * t for x, t in paren)
    return [
        _tabel_stap(paren),
        Step("Wanneer gelijk?",
             ["Alleen als beide spelers",
              "dezelfde waarde krijgen."]),
        Step("Per waarde",
             ["P(beiden %d) = (%s)² = %s" % (x, breuk(t, 36),
                                             breuk(t * t, 1296))
              for x, t in paren]),
        Step("Optellen",
             ["P(gelijk) =",
              " + ".join(breuk(t * t, 1296) for _, t in paren),
              "= %s" % breuk(som, 1296)]),
    ]


def meer_binomiaal(v):
    paren = _tabel(v)
    n, k = int(v["n"]), int(v["k"])
    gelijk36 = sum(t * t for _, t in paren)          # op 1296
    meer = (1296 - gelijk36) // 2                     # op 1296
    p = meer / 1296.0
    C = me.comb(n, k)
    kans = C * (p ** k) * ((1 - p) ** (n - k))
    return [
        _tabel_stap(paren),
        Step("Kans op 'meer' per beurt",
             ["P(gelijk) = %s" % breuk(gelijk36, 1296),
              "Symmetrie: P(meer) = P(minder)",
              "p = (1 - %s)/2 = %s"
              % (breuk(gelijk36, 1296), breuk(meer, 1296))]),
        Step("Binomiale situatie",
             ["n = %d beurten," % n,
              "succeskans p = %s," % breuk(meer, 1296),
              "precies k = %d successen." % k]),
        Step("Formule",
             ["P = C(n,k)·p^k·(1-p)^(n-k)",
              "C(%d,%d) = %d" % (n, k, C)]),
        Step("Uitrekenen",
             ["P = %d·(%s)^%d·(%s)^%d" % (C, breuk(meer, 1296), k,
                                          breuk(1296 - meer, 1296), n - k),
              "P ≈ %s" % nl(kans, 4)]),
    ]


def _check_teller(key, laatste=False):
    def check(waarde, vals):
        if waarde < 0 or waarde != int(waarde):
            return key + ": geheel getal >= 0"
        if laatste:
            som = (vals.get("t1", 0) + vals.get("t2", 0) +
                   vals.get("t3", 0) + waarde)
            if som != 36:
                return "kansen samen %s/36, moet 36/36" % nl(som)
        return None
    return check


def _velden_tabel():
    return [
        Field("x1", "waarde x1 =", start=2, integer=True),
        Field("x2", "waarde x2 =", start=4, integer=True),
        Field("x3", "waarde x3 =", start=6, integer=True),
        Field("x4", "waarde x4 =", start=10, integer=True),
        Field("t1", "P(x1)·36 =", start=12, integer=True,
              check=_check_teller("t1")),
        Field("t2", "P(x2)·36 =", start=6, integer=True,
              check=_check_teller("t2")),
        Field("t3", "P(x3)·36 =", start=12, integer=True,
              check=_check_teller("t3")),
        Field("t4", "P(x4)·36 =", start=6, integer=True,
              check=_check_teller("t4", laatste=True)),
    ]


def _check_n(waarde, _):
    if waarde < 1:
        return "n moet minstens 1 zijn"
    return None


def _check_k(waarde, vals):
    if waarde < 0 or waarde > vals.get("n", 0):
        return "k moet tussen 0 en n"
    return None


TOPIC = Topic("Kansverdeling", [
    Problem("E(X) berekenen", _velden_tabel(), verwachting),
    Problem("P(som 2 spelers = s)",
            _velden_tabel() + [Field("s", "som s =", start=8, integer=True)],
            som_kans),
    Problem("P(beiden gelijk)", _velden_tabel(), gelijk),
    Problem("P(k v.d. n keer meer)",
            _velden_tabel() + [
                Field("n", "n (beurten) =", start=10, integer=True,
                      check=_check_n),
                Field("k", "k (successen) =", start=4, integer=True,
                      check=_check_k)],
            meer_binomiaal),
])
