# FX ENGINE 🧠📟

Een professioneel opgezet embedded project voor de **Raspberry Pi Pico 2 W
(RP2350, MicroPython)** dat een Casio fx-82MS verandert in een slimme
rekenmachine: de gebruiker kiest een onderwerp, voert gegevens in en krijgt
de **volledige uitwerking stap voor stap** — zoals een docent, niet alleen
het antwoord.

```
FX ENGINE          PARABOOL           a = 2          Stap 2/5
> Parabool    →    > Top bepalen  →   b = -8    →    Invullen
  Exponentieel       Snijpunten       c = 6          x_top = -(-8)/(2·2)
  Goniometrie        ...                             x_top = 2
```

## Architectuur in één zin

**Events in → schermstack verwerkt → stappen uit → display toont.**
Geen enkele module kent meer dan zijn buren; hardware zit alleen aan de
randen.

```
 HARDWARE-RAND          KERN (hardware-vrij)              HARDWARE-RAND
┌──────────────┐   ┌──────────────────────────────────┐   ┌────────────┐
│ buttons.py   │   │            app.py                │   │ display.py │
│ (GPIO 2-5)   ├──►│   App + schermstack (state-      ├──►│ Console-   │
│ console.py   │   │   machine): Menu / Wizard /      │   │ Display    │
│ (Thonny)     │   │   StepViewer                     │   │            │
└──────────────┘   │      │              ▲            │   └────────────┘
  events           │      ▼              │            │    lijst regels
  ("key", OK)      │  problems/*.py ── steps.py       │
  ("text","3,5")   │  (solve: dict → [Step, ...])     │
                   │  math_engine.py (bouwstenen)     │
                   └──────────────────────────────────┘
```

## Bestandenstructuur

```
fx-engine/
├── main.py              composition root: bedraadt hardware aan de kern
├── tests/
│   └── test_flows.py    end-to-end test van alle flows (draait op pc)
└── fx/
    ├── app.py           App (hoofdlus) + Screen-basisklasse + schermstack
    ├── events.py        eventtaal + EventSource-interface
    ├── buttons.py       GpioButtons: debounce, auto-repeat (GP2-GP5)
    ├── console.py       ConsoleKeys: bediening via Thonny-shell/pc
    ├── display.py       Display-interface + ConsoleDisplay
    ├── menu.py          MenuScreen (herbruikbaar, scrollt zelf)
    ├── wizard.py        Wizard: velden invullen, valideren
    ├── viewer.py        StepViewer: één stap per OK
    ├── steps.py         datamodel: Step, Field, Problem, Topic
    ├── math_engine.py   herbruikbare wiskunde-bouwstenen (abc-formule…)
    ├── registry.py      dé lijst met alle onderwerpen
    ├── utils.py         notatie (2,75), woordwrap, kleine helpers
    └── problems/
        ├── parabool.py      top, snijpunten, discriminant, raaklijn
        ├── exponentieel.py  waarde na t, tijd berekenen, % → factor
        ├── goniometrie.py   SOS-CAS-TOA: zijden en hoeken
        ├── kans.py          binomiaal, complement, E(X) en σ
        └── statistiek.py    z-score, P(X > x), vuistregels 68/95
```

## Verantwoordelijkheden per module

| Module | Weet WEL van | Weet NIETS van |
|---|---|---|
| `buttons.py` | GPIO, debounce, repeat | menu's, wiskunde, display |
| `console.py` | stdin | idem |
| `display.py` | tekens op een scherm zetten | waar de tekst vandaan komt |
| `app.py` | events rondpompen, schermstack | wiskunde, hardware |
| `menu.py` / `wizard.py` / `viewer.py` | hun eigen scherm | elkaars binnenkant, hardware |
| `problems/*` | wiskunde + stappen formuleren | knoppen, schermen, volgorde van tonen |
| `math_engine.py` | gedeelde berekeningen | alles behalve wiskunde |
| `main.py` | welke hardware er echt hangt | hoe die hardware werkt |

## Welke data stroomt er tussen de bestanden?

1. `buttons/console` → `app`: **events** — `("key", "OK")` of `("text", "3,5")`
2. `app` → actief scherm: datzelfde event; scherm → `app`: een **actie**
   (`push`/`pop`/`replace`)
3. `wizard` → `problem.solve()`: een **dict** — `{"a": 2, "b": -8, "c": 6}`
4. `problem.solve()` → `viewer`: een **lijst `Step`-objecten** (alleen tekst!)
5. elk scherm → `display.show()`: een **lijst tekstregels**

Elke pijl is een simpel datatype. Daardoor is elk onderdeel los te testen
en los te vervangen.

## Waarom dit schaalbaar is

- **Nieuw probleem** = één functie `solve(values) -> [Step]` + één
  `Problem(...)`-regel in een bestaande module. Menu, wizard, validatie en
  viewer werken er meteen mee — nul regels UI-code.
- **Nieuw onderwerp** = één bestand in `problems/` + twee regels in
  `registry.py`. Tientallen modules blijven zo overzichtelijk.
- **Casio-LCD** straks = één klasse `CasioLcd(Display)` met `show(lines)`
  (toetsinjectie of directe LCD-aansturing) en één regel in `main.py`.
  Displays geven hun eigen `width`/`rows` door; de viewer vouwt stappen
  daar automatisch op — dezelfde stappen passen dus ook op een 2-regelig
  scherm (als meerdere pagina's).
- **Casio-toetsenmatrix** straks = één klasse `KeyMatrix(EventSource)` met
  `poll()` en één regel in `main.py`. De hele kern merkt er niets van.
- **Rekenen en tonen zijn al gescheiden**: een `Step` is pure tekst. Of hij
  wordt geprint, op een LCD getypt of via wifi verstuurd (Pico 2 **W**!)
  is een presentatiekeuze.

## Aan de slag

### Op de Pico (Thonny)

1. Interpreter: *MicroPython (Raspberry Pi Pico)*.
2. Upload de **map `fx/`** en **`main.py`** naar de Pico
   (rechtsklik in Thonny's Files-paneel → *Upload to /*).
3. Run `main.py` — of reset de Pico: het menu start vanzelf.

### Knoppen (breadboard)

Vier drukknoppen, elk tussen de GPIO-pin en GND (interne pull-up, geen
weerstanden nodig):

| GPIO | Fysieke pin | Functie |
|---|---|---|
| GP2 | 4 | UP |
| GP3 | 5 | DOWN |
| GP4 | 6 | OK |
| GP5 | 7 | BACK |

GND zit o.a. op fysieke pin 3 en 8. UP/DOWN hebben auto-repeat
(ingedrukt houden = doorscrollen/snel tellen).

### Zonder Pico (demo/ontwikkelen)

```
python3 main.py
```

Bediening via het toetsenbord: `w`=UP, `s`=DOWN, kale Enter=OK, `b`=BACK,
en in de wizard typ je gewoon het getal (`-8`, `0,5`). Dit werkt op de
Pico in de Thonny-shell trouwens óók, naast de knoppen.

### Tests

```
cd fx-engine && python3 tests/test_flows.py
```

Doorloopt alle 16 problemen end-to-end (menu → wizard → alle stappen →
terug), test de validatie en controleert een paar bekende sommen.

## Roadmap naar de echte Casio

| Fase | Wat | Waar |
|---|---|---|
| 1 (nu) | breadboard-knoppen + console | `buttons.py`, `display.py` |
| 2 | originele Casio-toetsenmatrix uitlezen | nieuwe `KeyMatrix(EventSource)` |
| 3 | origineel LCD aansturen / toetsinjectie | nieuwe `CasioLcd(Display)` |
| 4 | tientallen extra wiskundemodules | nieuwe bestanden in `problems/` |

In elke fase verandert alleen de rand — nooit de kern.
