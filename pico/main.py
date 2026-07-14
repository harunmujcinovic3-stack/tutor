# ============================================================
#  SlaagZeker StappenPico
#  Wiskunde-examentrainer voor de Raspberry Pi Pico (MicroPython)
#
#  - Genereert steeds NIEUWE opgaven (willekeurige getallen) in de
#    stijl van de toetsmatrix: sinusoïden, normale verdeling &
#    hypothesetoets, kansrekening, differentiëren, algebra.
#  - Elke keer dat je op Enter drukt (in de Thonny-shell) verschijnt
#    de VOLGENDE tussenstap van de uitwerking.
#  - Optioneel: steek een jumperdraadje tussen GP15 en GND om een
#    "volgende stap"-knop te maken. Kort verbinden = volgende stap.
#  - De onboard-LED knippert bij elke stap.
#
#  Gebruik: open dit bestand in Thonny, sla het op de Pico op als
#  main.py en druk op Run (of reset de Pico).
# ============================================================

import math
import random
import sys
import time

try:
    from machine import Pin
    import select
    MICROPY = True
except ImportError:
    MICROPY = False          # het programma werkt ook gewoon op een pc

if MICROPY:
    try:
        _led = Pin("LED", Pin.OUT)     # Pico W
    except (TypeError, ValueError):
        _led = Pin(25, Pin.OUT)        # gewone Pico
    _knop = Pin(15, Pin.IN, Pin.PULL_UP)   # jumper GP15 <-> GND = knop
    _poller = select.poll()
    _poller.register(sys.stdin, select.POLLIN)


# ------------------------------------------------------------
#  Invoer: Enter in Thonny óf de jumper-knop
# ------------------------------------------------------------

def _knipper():
    if MICROPY:
        _led.on()
        time.sleep_ms(60)
        _led.off()


def _knop_ingedrukt():
    if not MICROPY or _knop.value() == 1:
        return False
    time.sleep_ms(30)                  # dender-controle
    if _knop.value() == 1:
        return False
    while _knop.value() == 0:          # wacht tot losgelaten
        time.sleep_ms(10)
    return True


def wacht_op_stap(prompt):
    """Wacht op Enter (Thonny-shell) of op de knop (GP15->GND)."""
    if not MICROPY:
        input(prompt)
        return
    sys.stdout.write(prompt)
    while True:
        if _knop_ingedrukt():
            break
        if _poller.poll(0):
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                break
        time.sleep_ms(15)
    sys.stdout.write("\n")
    _knipper()


def lees_keuze(prompt):
    """Lees een menukeuze; de knop kiest 'w' (willekeurige opgave)."""
    if not MICROPY:
        return input(prompt).strip().lower()
    sys.stdout.write(prompt)
    buf = ""
    while True:
        if _knop_ingedrukt():
            sys.stdout.write("w\n")
            return "w"
        if _poller.poll(0):
            ch = sys.stdin.read(1)
            if ch in ("\n", "\r"):
                sys.stdout.write("\n")
                return buf.strip().lower()
            buf += ch
        time.sleep_ms(15)


# ------------------------------------------------------------
#  Rekenhulpjes en nette notatie (Nederlandse komma)
# ------------------------------------------------------------

def nl(x, dec=2):
    """Getal netjes weergeven: 3 i.p.v. 3.0 en 2,75 i.p.v. 2.75."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    s = ("%." + str(dec) + "f") % x
    s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def ggd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def breuk(t, n):
    g = ggd(t, n)
    t //= g
    n //= g
    if n == 1:
        return str(t)
    return "%d/%d" % (t, n)


def comb(n, k):
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r


def _phi(z):
    """Standaardnormale verdelingsfunctie P(Z <= z)."""
    try:
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    except AttributeError:
        t = 1.0 / (1.0 + 0.2316419 * abs(z))
        pdf = math.exp(-z * z / 2.0) / math.sqrt(2.0 * math.pi)
        p = 1.0 - pdf * t * (0.319381530 + t * (-0.356563782 + t * (
            1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        return p if z >= 0 else 1.0 - p


# ------------------------------------------------------------
#  Opgave 1 — Sinusoïden (het golfslagbad)
# ------------------------------------------------------------

def opg_sinus():
    half = random.random() < 0.5           # sin(...) = 1/2 of sin(...) = 1
    P = random.choice([12, 36] if half else [8, 12, 20, 36])
    K = P // 2                              # c = pi/K, periode P = 2K
    a = random.choice([2.5, 3.0, 3.5])
    b = random.choice([0.4, 0.5, 0.8])
    d = random.choice([0, 1, 2, 3])
    binnen = "(t - %d)" % d if d else "t"
    formule = "D = %s + %s·sin(π/%d·%s)" % (nl(a), nl(b), K, binnen)

    if half:
        H = a + b / 2.0
        offsets = [K / 6.0, 5.0 * K / 6.0]
        w_txt = "1/2"
        basis = ("sin(...) = 1/2 geeft twee series oplossingen:\n"
                 "π/%d·%s = π/6 + k·2π   of   π/%d·%s = 5π/6 + k·2π   (k geheel)"
                 % (K, binnen, K, binnen))
        naar_t = ("Vermenigvuldig met %d/π:\n"
                  "t = %s + k·%d   of   t = %s + k·%d"
                  % (K, nl(d + K / 6.0), P, nl(d + 5.0 * K / 6.0), P))
    else:
        H = a + b
        offsets = [K / 2.0]
        w_txt = "1"
        basis = ("sin(...) = 1 geeft:\n"
                 "π/%d·%s = π/2 + k·2π   (k geheel)" % (K, binnen))
        naar_t = ("Vermenigvuldig met %d/π:\n"
                  "t = %s + k·%d" % (K, nl(d + K / 2.0), P))

    kandidaten = []
    for off in offsets:
        for k in range(-3, 4):
            t = d + off + k * P
            if t > 1e-9:
                kandidaten.append(t)
    kandidaten.sort()
    top3 = kandidaten[:3]

    stappen_a = [
        "Stel de vergelijking op:\n%s + %s·sin(π/%d·%s) = %s"
        % (nl(a), nl(b), K, binnen, nl(H)),
        "Sinus isoleren:\nsin(π/%d·%s) = (%s - %s)/%s = %s"
        % (K, binnen, nl(H), nl(a), nl(b), w_txt),
        basis,
        naar_t,
        "✓ Eerste drie tijdstippen na t = 0:\nt = %s s,  t = %s s  en  t = %s s"
        % (nl(top3[0]), nl(top3[1]), nl(top3[2])),
    ]

    # deel b: formule opstellen bij een beschreven grafiek
    a2 = random.choice([2.5, 3.0, 3.5])
    b2 = random.choice([0.5, 0.7, 1.0])
    P2 = random.choice([6, 8, 10, 12])
    d2 = random.choice([0, 1, 2, 3])
    tm = d2 + P2 / 4.0                      # tijdstip van het maximum
    M = a2 + b2
    m = a2 - b2
    stappen_b = [
        "a = evenwichtsstand = (max + min)/2 = (%s + %s)/2 = %s"
        % (nl(M), nl(m), nl(a2)),
        "b = amplitude = (max - min)/2 = (%s - %s)/2 = %s"
        % (nl(M), nl(m), nl(b2)),
        "c = 2π/periode = 2π/%d = π/%s" % (P2, nl(P2 / 2.0)),
        "d = tijdstip waarop de grafiek STIJGEND door de evenwichtsstand gaat.\n"
        "Dat is een kwart periode vóór het maximum: d = %s - %d/4 = %s"
        % (nl(tm), P2, nl(d2)),
        "✓ Mogelijke formule:\nD = %s + %s·sin(π/%s·(t - %s))"
        % (nl(a2), nl(b2), nl(P2 / 2.0), nl(d2)),
    ]

    return {
        "titel": "OPGAVE — Het golfslagbad (sinusoïden)",
        "context": [
            "In een golfslagbad is de diepte D (in meters) op een vast punt",
            "een periodieke functie van de tijd t (in seconden):",
            "",
            "    " + formule,
        ],
        "delen": [
            {"label": "a", "punten": 4,
             "vraag": "Bereken algebraïsch de eerste drie tijdstippen na "
                      "t = 0 waarop de diepte %s meter is." % nl(H),
             "stappen": stappen_a},
            {"label": "b", "punten": 6,
             "vraag": "Een ander golfslagbad heeft een maximale diepte van "
                      "%s m (voor het eerst op t = %s s) en een minimale "
                      "diepte van %s m. De periode is %d s. Bereken mogelijke "
                      "waarden voor a, b, c en d in D = a + b·sin(c·(t - d))."
                      % (nl(M), nl(tm), nl(m), P2),
             "stappen": stappen_b},
        ],
    }


# ------------------------------------------------------------
#  Opgave 2 — Normale verdeling & hypothesetoets (de fabriek)
# ------------------------------------------------------------

def opg_normaal():
    mu = random.choice([450, 500, 340])
    sig = random.choice([4, 5, 8])
    grenzen = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
    vlak = [0.044, 0.092, 0.150, 0.191, 0.191, 0.150, 0.092, 0.044]

    breedte = random.randint(2, 4)          # aantal halve-sigma-stroken
    i1 = random.randint(0, 8 - breedte)
    i2 = i1 + breedte
    k1, k2 = grenzen[i1], grenzen[i2]
    g1 = mu + k1 * sig
    g2 = mu + k2 * sig
    stroken = vlak[i1:i2]
    totaal = sum(stroken)

    def sigma_txt(k):
        if k == 0:
            return "μ"
        teken = "+" if k > 0 else "-"
        return "μ %s %sσ" % (teken, nl(abs(k)))

    stappen_a = [
        "Zet de grenzen om in σ-afstanden tot het gemiddelde:\n"
        "(%s - %d)/%d = %s  →  %s\n(%s - %d)/%d = %s  →  %s"
        % (nl(g1), mu, sig, nl(k1), sigma_txt(k1),
           nl(g2), mu, sig, nl(k2), sigma_txt(k2)),
        "Lees in de figuur de vlakdelen per halve σ af tussen %s en %s:\n%s"
        % (sigma_txt(k1), sigma_txt(k2),
           " + ".join(nl(s, 3) for s in stroken)),
        "Tel de vlakdelen op: %s" % nl(totaal, 3),
        "✓ Dus %s%% van de potten (afgerond %d%%) bevat tussen de %s en %s g."
        % (nl(totaal * 100, 1), round(totaal * 100), nl(g1), nl(g2)),
    ]

    mu2 = random.choice([100, 120])
    sig2 = random.choice([1, 2])
    sig_tot = math.sqrt(sig * sig + sig2 * sig2)
    stappen_b = [
        "Gemiddelden mag je optellen:\nμ_totaal = %d + %d = %d g"
        % (mu, mu2, mu + mu2),
        "Standaardafwijkingen mag je NIET optellen; de varianties wel:\n"
        "σ_totaal = √(σ₁² + σ₂²)",
        "✓ σ_totaal = √(%d² + %d²) = √%d ≈ %s g"
        % (sig, sig2, sig * sig + sig2 * sig2, nl(sig_tot, 2)),
    ]

    stappen_c = [
        "H₀: μ = %d  (het gemiddelde gewicht is in orde)" % mu,
        "✓ H₁: μ ≠ %d  (tweezijdige toets, want te licht én te zwaar\n"
        "is allebei afwijkend), met α = 0,05." % mu,
    ]

    n = 100
    delta = random.choice([0.5, 0.7, 0.9, 1.1, 1.3])
    xbar = mu + delta
    se = sig / math.sqrt(n)
    z = (xbar - mu) / se
    p = 2.0 * (1.0 - _phi(abs(z)))
    verwerp = p < 0.05
    stappen_d = [
        "Het gemiddelde van n = %d potten is ook normaal verdeeld, met\n"
        "σ_gem = σ/√n = %d/√%d = %s g" % (n, sig, n, nl(se, 2)),
        "Bereken de z-waarde van het gevonden gemiddelde:\n"
        "z = (%s - %d)/%s = %s" % (nl(xbar), mu, nl(se, 2), nl(z, 2)),
        "Tweezijdige overschrijdingskans:\n"
        "p = 2·P(Z ≥ %s) ≈ %s" % (nl(abs(z), 2), nl(p, 4)),
        "Vergelijk met α = 0,05:  %s ligt %s 0,05"
        % (nl(p, 4), "ONDER" if verwerp else "BOVEN"),
        "✓ Conclusie: H₀ wordt %s. Er is %s reden om aan te nemen dat\n"
        "het gemiddelde gewicht afwijkt van %d g."
        % ("verworpen" if verwerp else "niet verworpen",
           "dus" if verwerp else "geen", mu),
    ]

    return {
        "titel": "OPGAVE — De pindakaasfabriek (normale verdeling)",
        "context": [
            "Een fabriek verkoopt pindakaas in potten. Het gewicht van de",
            "pindakaas is normaal verdeeld met gemiddelde μ = %d g en" % mu,
            "standaardafwijking σ = %d g. Gebruik de vuistregel-figuur" % sig,
            "met vlakdelen per halve σ: 0,044 / 0,092 / 0,150 / 0,191.",
        ],
        "delen": [
            {"label": "a", "punten": 4,
             "vraag": "Bereken met de figuur het percentage potten met "
                      "tussen de %s en %s g pindakaas." % (nl(g1), nl(g2)),
             "stappen": stappen_a},
            {"label": "b", "punten": 3,
             "vraag": "Het gewicht van de lege potten is normaal verdeeld "
                      "met μ = %d g en σ = %d g. Bereken gemiddelde en "
                      "standaardafwijking van het totale gewicht van een "
                      "gevulde pot." % (mu2, sig2),
             "stappen": stappen_b},
            {"label": "c", "punten": 2,
             "vraag": "Men toetst met n = 100 potten of het gemiddelde echt "
                      "%d g is (α = 0,05). Formuleer H₀ en H₁." % mu,
             "stappen": stappen_c},
            {"label": "d", "punten": 5,
             "vraag": "Wat is de conclusie als het gemiddelde gewicht in de "
                      "100 potten gelijk is aan %s g?" % nl(xbar),
             "stappen": stappen_d},
        ],
    }


# ------------------------------------------------------------
#  Opgave 3 — Kansrekening (het dobbelspel)
# ------------------------------------------------------------

def opg_kans():
    regels = [
        ("even → net zoveel punten als de uitkomst; "
         "oneven → twee keer zoveel punten",
         lambda w: w if w % 2 == 0 else 2 * w),
        ("even → twee keer zoveel punten als de uitkomst; "
         "oneven → net zoveel punten",
         lambda w: 2 * w if w % 2 == 0 else w),
        ("even → net zoveel punten als de uitkomst; "
         "oneven → de uitkomst plus 3 punten",
         lambda w: w if w % 2 == 0 else w + 3),
    ]
    regel_txt, regel = random.choice(regels)

    verd = {}                                # punten -> aantal gunstige worpen
    for worp in range(1, 7):
        p = regel(worp)
        verd[p] = verd.get(p, 0) + 1
    waarden = sorted(verd.keys())

    tabel = ("x:        " + "   ".join("%3d" % x for x in waarden) + "\n" +
             "P(X = x): " + "   ".join("%3s" % breuk(verd[x], 6)
                                       for x in waarden))

    som_x = sum(x * verd[x] for x in waarden)
    stappen_a = [
        "De kansverdeling van X (aantallen gunstige worpen op 6):\n" + tabel,
        "E(X) = som van (waarde × kans):\nE(X) = " +
        " + ".join("%d·%s" % (x, breuk(verd[x], 6)) for x in waarden),
        "✓ E(X) = %s/6 = %s = %s punten per beurt"
        % (nl(som_x), breuk(som_x, 6), nl(som_x / 6.0, 2)),
    ]

    sommen = {}                              # som -> aantal geordende paren op 36
    for x in waarden:
        for y in waarden:
            sommen[x + y] = sommen.get(x + y, 0) + verd[x] * verd[y]
    kandidaat = [s for s in sommen
                 if 2 <= sommen[s] <= 8 and s not in (2 * waarden[0],)]
    doel = random.choice(kandidaat if kandidaat else list(sommen.keys()))
    paren = [(x, y) for x in waarden for y in waarden if x + y == doel]
    stappen_b = [
        "Zoek alle combinaties (punten Joe, punten Donald) met som %d:\n%s"
        % (doel, ",  ".join("(%d, %d)" % p for p in paren)),
        "Per combinatie geldt (onafhankelijke beurten):\n" +
        "\n".join("P(%d, %d) = %s · %s = %s"
                  % (x, y, breuk(verd[x], 6), breuk(verd[y], 6),
                     breuk(verd[x] * verd[y], 36)) for (x, y) in paren),
        "✓ Optellen: P(som = %d) = %s ≈ %s"
        % (doel, breuk(sommen[doel], 36), nl(sommen[doel] / 36.0, 3)),
    ]

    gelijk36 = sum(verd[x] * verd[x] for x in waarden)
    stappen_c = [
        "Gelijk aantal punten kan alleen als beiden dezelfde waarde gooien:\n" +
        "\n".join("P(beiden %d punten) = (%s)² = %s"
                  % (x, breuk(verd[x], 6), breuk(verd[x] * verd[x], 36))
                  for x in waarden),
        "Tel op: " + " + ".join(breuk(verd[x] * verd[x], 36)
                                for x in waarden) +
        " = %s" % breuk(gelijk36, 36),
        "✓ P(gelijk) = %s, en dat is precies wat aangetoond moest worden."
        % breuk(gelijk36, 36),
    ]

    meer36 = (36 - gelijk36) // 2            # symmetrie: P(J>D) = P(D>J)
    p_meer = meer36 / 36.0
    k = random.choice([3, 4, 5])
    n = 10
    kans = comb(n, k) * (p_meer ** k) * ((1 - p_meer) ** (n - k))
    stappen_d = [
        "Bepaal eerst p = P(Joe krijgt méér punten dan Donald) in één beurt.\n"
        "Vanwege symmetrie: P(meer) = P(minder), dus\n"
        "p = (1 - P(gelijk))/2 = (1 - %s)/2 = %s"
        % (breuk(gelijk36, 36), breuk(meer36, 36)),
        "Dit is een binomiale situatie:\n"
        "n = %d beurten, succeskans p = %s, precies k = %d successen"
        % (n, breuk(meer36, 36), k),
        "P(k = %d) = C(%d,%d) · p^%d · (1-p)^%d  met C(%d,%d) = %d"
        % (k, n, k, k, n - k, n, k, comb(n, k)),
        "✓ P = %d · (%s)^%d · (%s)^%d ≈ %s"
        % (comb(n, k), breuk(meer36, 36), k,
           breuk(36 - meer36, 36), n - k, nl(kans, 3)),
    ]

    return {
        "titel": "OPGAVE — Het dobbelspel (kansrekening)",
        "context": [
            "Joe en Donald spelen een spel met een gewone dobbelsteen.",
            "Bij iedere beurt werpen beide spelers één keer.",
            "Regel: " + regel_txt + ".",
            "Het aantal punten per beurt is de toevalsvariabele X.",
        ],
        "delen": [
            {"label": "a", "punten": 3,
             "vraag": "Bereken E(X), het verwachte aantal punten per beurt.",
             "stappen": stappen_a},
            {"label": "b", "punten": 4,
             "vraag": "Bereken de kans dat de som van de punten van Joe en "
                      "Donald in één beurt precies %d is." % doel,
             "stappen": stappen_b},
            {"label": "c", "punten": 3,
             "vraag": "De kans dat Joe en Donald in een beurt evenveel "
                      "punten krijgen is %s. Toon dit aan."
                      % breuk(gelijk36, 36),
             "stappen": stappen_c},
            {"label": "d", "punten": 5,
             "vraag": "Bereken de kans dat Joe in precies %d van de eerste "
                      "10 beurten meer punten krijgt dan Donald." % k,
             "stappen": stappen_d},
        ],
    }


# ------------------------------------------------------------
#  Opgave 4 — Differentiëren & optimaliseren (de pizza)
# ------------------------------------------------------------

def opg_diff():
    q = 2
    t0 = random.choice([10, 15, 20])
    r = q * t0 * t0
    p = random.choice([120, 165, 180, 220])
    d_max = p / (2.0 * q * t0)

    stappen_a = [
        "Quotiëntregel met teller = %dt en noemer = %dt² + %d:\n"
        "D' = (teller'·noemer - teller·noemer') / noemer²" % (p, q, r),
        "D' = (%d·(%dt² + %d) - %dt·%dt) / (%dt² + %d)²"
        % (p, q, r, p, 2 * q, q, r),
        "Teller vereenvoudigen:\n%d - %dt²" % (p * r, p * q),
        "D' = 0  →  %dt² = %d  →  t² = %d  →  t = %d  (t > 0)"
        % (p * q, p * r, t0 * t0, t0),
        "✓ Maximale vraag: D(%d) = %d·%d/(%d·%d + %d) = %s miljoen per dag"
        % (t0, p, t0, q, t0 * t0, r, nl(d_max, 3)),
    ]

    disc = p * p - 4 * q * r
    w = math.sqrt(disc)
    t_laat = (p + w) / (2.0 * q)
    t_vroeg = (p - w) / (2.0 * q)
    dagen = round(t_laat * 7)
    stappen_b = [
        "Los op D = 1:\n%dt/(%dt² + %d) = 1  →  %dt = %dt² + %d"
        % (p, q, r, p, q, r),
        "Op nul herleiden: %dt² - %dt + %d = 0\n"
        "abc-formule: discriminant = %d² - 4·%d·%d = %d"
        % (q, p, r, p, q, r, disc),
        "t = (%d ± √%d)/%d  →  t ≈ %s  of  t ≈ %s"
        % (p, disc, 2 * q, nl(t_vroeg, 1), nl(t_laat, 1)),
        "De vraag DAALT onder de 1 miljoen bij het late tijdstip:\n"
        "t ≈ %s weken" % nl(t_laat, 2),
        "✓ Omrekenen naar dagen: %s · 7 ≈ %d dagen na introductie"
        % (nl(t_laat, 2), dagen),
    ]

    a2 = random.choice([0.4, 0.5, 0.8])
    b2 = random.choice([0.05, 0.1, 0.2])
    t_top = 1.0 / b2
    e_max = a2 * t_top * math.exp(-1.0)
    stappen_c = [
        "E = %s·t·e^(-%st): productregel met u = %st en v = e^(-%st):\n"
        "E' = %s·e^(-%st) + %st·(-%s)·e^(-%st)"
        % (nl(a2), nl(b2), nl(a2), nl(b2), nl(a2), nl(b2), nl(a2),
           nl(b2), nl(b2)),
        "E-macht buiten haakjes halen:\nE' = %s·e^(-%st)·(1 - %st)"
        % (nl(a2), nl(b2), nl(b2)),
        "E' = 0: een e-macht is nooit 0, dus\n1 - %st = 0  →  t = %s weken"
        % (nl(b2), nl(t_top)),
        "✓ Maximale verwachte vraag:\nE(%s) = %s·%s·e^(-1) ≈ %s miljoen per dag"
        % (nl(t_top), nl(a2), nl(t_top), nl(e_max, 3)),
    ]

    return {
        "titel": "OPGAVE — Pizza! (differentiëren)",
        "context": [
            "Een pizzaverkoper introduceert een nieuwe pizza. De vraag D",
            "(miljoenen per dag) hangt af van de tijd t (weken):",
            "",
            "    D = %dt / (%dt² + %d)" % (p, q, r),
        ],
        "delen": [
            {"label": "a", "punten": 6,
             "vraag": "Gebruik de afgeleide dD/dt om algebraïsch de "
                      "maximale vraag per dag te berekenen.",
             "stappen": stappen_a},
            {"label": "b", "punten": 5,
             "vraag": "Onder de 1 miljoen per dag stopt de verkoop. Bereken "
                      "algebraïsch dat tijdstip; rond af op hele dagen.",
             "stappen": stappen_b},
            {"label": "c", "punten": 6,
             "vraag": "De opvolger heeft verwachte vraag E = %s·t·e^(-%st). "
                      "Gebruik dE/dt om algebraïsch de maximale verwachte "
                      "vraag te berekenen." % (nl(a2), nl(b2)),
             "stappen": stappen_c},
        ],
    }


# ------------------------------------------------------------
#  Opgave 5 — Algebra: snijpunten & raaklijnen
# ------------------------------------------------------------

def opg_algebra():
    pp, qq, s = random.choice([(2, 4, 6), (4, 8, 12), (8, 12, 20)])
    c = pp * qq
    w = int(round(math.sqrt(1 + 4 * s)))
    x1 = (1 + w) // 2                        # positieve oplossing
    x2 = (1 - w) // 2                        # negatieve oplossing
    stappen_a = [
        "Stel f(x) = g(x):\n(x² - %d)(x² - %d) = x³ + %d" % (pp, qq, c),
        "Haakjes uitwerken:\nx⁴ - %dx² + %d = x³ + %d" % (s, c, c),
        "Alles naar links halen:\nx⁴ - x³ - %dx² = 0" % s,
        "Ontbinden in factoren:\nx²·(x² - x - %d) = 0" % s,
        "x² = 0 → x = 0\nx² - x - %d = 0 → (x - %d)(x + %d) = 0 → "
        "x = %d of x = %d" % (s, x1, -x2, x1, x2),
        "✓ y-coördinaten via g(x) = x³ + %d:\n(0, %d),  (%d, %d)  en  (%d, %d)"
        % (c, c, x1, x1 ** 3 + c, x2, x2 ** 3 + c),
    ]

    kr = random.choice([2, 3])               # derdemachtswortel van x0
    x0 = kr ** 3
    ch = x0 * kr                              # zodat h(x0) = 0
    # h'(x0) = 1/(3·kr²) + ch/x0²  als breuk optellen
    n1, d1 = 1, 3 * kr * kr
    n2, d2 = ch, x0 * x0
    tn = n1 * d2 + n2 * d1
    td = d1 * d2
    stappen_b = [
        "Schrijf h zonder wortel en zonder breuk:\n"
        "h(x) = x^(1/3) - %d·x^(-1)" % ch,
        "Differentieer met de machtsregel:\n"
        "h'(x) = (1/3)·x^(-2/3) + %d·x^(-2)" % ch,
        "Vul x = %d in (want %d^(1/3) = %d, dus %d^(-2/3) = 1/%d):\n"
        "h'(%d) = 1/3 · 1/%d + %d/%d"
        % (x0, x0, kr, x0, kr * kr, x0, kr * kr, ch, x0 * x0),
        "Breuken optellen: %s + %s = %s"
        % (breuk(n1, d1), breuk(n2, d2), breuk(tn, td)),
        "✓ De helling van de raaklijn in H(%d, 0) is %s ≈ %s"
        % (x0, breuk(tn, td), nl(tn / td, 3)),
    ]

    pk = random.choice([2, 3])
    mk = random.choice([2, 3])
    qk = (pk * pk - pk) * mk * mk
    stappen_c = [
        "Evenwijdig aan y = -x betekent: de helling is -1, dus k'(a) = -1.",
        "Kettingregel op k(x) = √(%dx² + %d):\n"
        "k'(x) = %dx / (2·√(%dx² + %d)) = %dx/√(%dx² + %d)"
        % (pk, qk, 2 * pk, pk, qk, pk, pk, qk),
        "Stel k'(a) = -1:\n%da = -√(%da² + %d)" % (pk, pk, qk),
        "Kwadrateren: %da² = %da² + %d  →  %da² = %d  →  a² = %d"
        % (pk * pk, pk, qk, pk * pk - pk, qk, mk * mk),
        "Dus a = %d of a = -%d. De wortel is altijd positief, dus %da moet\n"
        "negatief zijn: alleen a = -%d voldoet." % (mk, mk, pk, mk),
        "✓ a = -%d" % mk,
    ]

    return {
        "titel": "OPGAVE — Snijpunten en raaklijnen (algebra)",
        "context": [
            "Gegeven zijn de functies",
            "    f(x) = (x² - %d)(x² - %d)      g(x) = x³ + %d" % (pp, qq, c),
            "    h(x) = x^(1/3) - %d/x          k(x) = √(%dx² + %d)"
            % (ch, pk, qk),
        ],
        "delen": [
            {"label": "a", "punten": 6,
             "vraag": "Bereken algebraïsch de coördinaten van de snijpunten "
                      "van de grafieken van f en g.",
             "stappen": stappen_a},
            {"label": "b", "punten": 5,
             "vraag": "Het punt H(%d, 0) ligt op de grafiek van h. Bereken "
                      "algebraïsch de helling van de raaklijn aan de grafiek "
                      "van h in punt H." % x0,
             "stappen": stappen_b},
            {"label": "c", "punten": 6,
             "vraag": "Bereken algebraïsch de waarde(n) van a waarvoor de "
                      "raaklijn aan de grafiek van k in A(a, k(a)) "
                      "evenwijdig loopt aan de lijn y = -x.",
             "stappen": stappen_c},
        ],
    }


# ------------------------------------------------------------
#  Opgave afspelen: elke Enter/knopdruk = één tussenstap
# ------------------------------------------------------------

def speel(opgave):
    print()
    print("=" * 52)
    print(" " + opgave["titel"])
    print("=" * 52)
    for regel in opgave["context"]:
        print(" " + regel)
    totaal = sum(d["punten"] for d in opgave["delen"])
    for deel in opgave["delen"]:
        print()
        print("-" * 52)
        print(" %dpt  %s)  %s" % (deel["punten"], deel["label"],
                                  deel["vraag"]))
        print("-" * 52)
        n = len(deel["stappen"])
        for i, stap in enumerate(deel["stappen"]):
            wacht_op_stap("   [Enter of knop] → stap %d/%d " % (i + 1, n))
            for r in stap.split("\n"):
                print("     " + r)
    print()
    print(" Einde opgave (%d punten). Terug naar het menu." % totaal)


# ------------------------------------------------------------
#  Toetsmatrix en menu
# ------------------------------------------------------------

MATRIX = """
 TOETSMATRIX  (domein → opgave → punten)
 ------------------------------------------------------
 1  Goniometrie / sinusoïden      golfslagbad     10 pt
 2  Normale verdeling & toetsen   pindakaas       14 pt
 3  Kansrekening & verwachting    dobbelspel      15 pt
 4  Differentiëren & extremen     pizza           17 pt
 5  Algebra / raaklijnen          functies        17 pt
 ------------------------------------------------------
 Elke opgave wordt met nieuwe getallen gegenereerd en
 algebraïsch, stap voor stap, uitgewerkt.
"""

OPGAVEN = {
    "1": opg_sinus,
    "2": opg_normaal,
    "3": opg_kans,
    "4": opg_diff,
    "5": opg_algebra,
}


def toon_menu():
    print()
    print("┌──────────────────────────────────────────────┐")
    print("│  SlaagZeker StappenPico — kies een domein     │")
    print("├──────────────────────────────────────────────┤")
    print("│  1  Sinusoïden (golfslagbad)                  │")
    print("│  2  Normale verdeling & hypothesetoets        │")
    print("│  3  Kansrekening & verwachtingswaarde         │")
    print("│  4  Differentiëren & optimaliseren            │")
    print("│  5  Algebra: snijpunten & raaklijnen          │")
    print("│  w  Willekeurige opgave (of druk op de knop)  │")
    print("│  m  Toon de toetsmatrix                       │")
    print("│  q  Stoppen                                   │")
    print("└──────────────────────────────────────────────┘")


def main():
    print()
    print("**************************************************")
    print("*  SlaagZeker StappenPico                        *")
    print("*  Examentraining wiskunde, stap voor stap       *")
    print("*  Enter (of knop op GP15) = volgende tussenstap *")
    print("**************************************************")
    while True:
        toon_menu()
        keuze = lees_keuze(" Keuze: ")
        if MICROPY:
            random.seed(time.ticks_us())     # echte variatie per keuze
        if keuze == "q":
            print(" Tot de volgende keer — succes met leren!")
            break
        if keuze == "m":
            print(MATRIX)
            continue
        if keuze == "w":
            keuze = random.choice(list(OPGAVEN.keys()))
        maker = OPGAVEN.get(keuze)
        if maker is None:
            print(" Ongeldige keuze, probeer opnieuw.")
            continue
        speel(maker())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Gestopt.")
