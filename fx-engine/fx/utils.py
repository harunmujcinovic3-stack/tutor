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


def term(coef, macht_txt, eerste=False):
    """Bouwsteen voor nette formules: term(-8, 'x') -> '- 8x'."""
    if coef == 0:
        return ""
    teken = "-" if coef < 0 else ("" if eerste else "+")
    c = abs(coef)
    cijfer = "" if (c == 1 and macht_txt) else nl(c)
    los = teken if eerste and teken else (teken + " " if teken else "")
    return los + cijfer + macht_txt
