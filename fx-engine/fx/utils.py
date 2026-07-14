# ------------------------------------------------------------
#  utils.py — kleine, pure hulpfuncties (geen hardware, geen I/O)
# ------------------------------------------------------------


def nl(x, dec=3):
    """Getal netjes weergeven: 3 i.p.v. 3.0, en 2,75 i.p.v. 2.75."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = ("%." + str(dec) + "f") % x
    s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def parse_getal(tekst):
    """'3,5' of '3.5' -> 3.5; geeft None bij onzin."""
    try:
        return float(tekst.replace(",", "."))
    except ValueError:
        return None


def wrap(tekst, breedte):
    """Vouwt een regel op woordgrenzen tot regels van max. `breedte`."""
    woorden = tekst.split(" ")
    regels = []
    huidig = ""
    for w in woorden:
        proef = w if not huidig else huidig + " " + w
        if len(proef) <= breedte or not huidig:
            huidig = proef
        else:
            regels.append(huidig)
            huidig = w
    if huidig:
        regels.append(huidig)
    return regels


def wrap_alles(regels, breedte):
    uit = []
    for r in regels:
        uit.extend(wrap(r, breedte))
    return uit


def ggd(a, b):
    a, b = abs(int(a)), abs(int(b))
    while b:
        a, b = b, a % b
    return a or 1


def breuk(t, n):
    """Vereenvoudigde breuk als tekst: breuk(10, 36) -> '5/18'."""
    if n < 0:
        t, n = -t, -n
    g = ggd(t, n)
    t //= g
    n //= g
    if n == 1:
        return str(t)
    return "%d/%d" % (t, n)


def pi_frac(x, dec=3):
    """Hoek als nette breuk van pi: pi_frac(pi/2) -> '1/2π'."""
    import math
    r = x / math.pi
    for d in (1, 2, 3, 4, 6, 9, 12, 18, 36):
        n = r * d
        if abs(n - round(n)) < 1e-9:
            n = int(round(n))
            if n == 0:
                return "0"
            teken = "-" if n < 0 else ""
            n = abs(n)
            g = ggd(n, d)
            n //= g
            d //= g
            if d == 1:
                return teken + ("π" if n == 1 else "%dπ" % n)
            return "%s%d/%dπ" % (teken, n, d)
    return nl(x, dec) + " rad"


def term(coef, macht_txt, eerste=False):
    """Bouwsteen voor nette formules: term(-8, 'x') -> '- 8x'."""
    if coef == 0:
        return ""
    teken = "-" if coef < 0 else ("" if eerste else "+")
    c = abs(coef)
    cijfer = "" if (c == 1 and macht_txt) else nl(c)
    los = teken if eerste and teken else (teken + " " if teken else "")
    return los + cijfer + macht_txt
