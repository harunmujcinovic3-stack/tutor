# SlaagZeker StappenPico 🧮

Verander je Raspberry Pi Pico in een **stap-voor-stap examentrainer** voor
wiskunde. De Pico genereert steeds nieuwe opgaven in de stijl van het
examenprogramma (zie de toetsmatrix hieronder) en werkt ze **algebraïsch**
uit — maar geeft per keer maar **één tussenstap** prijs. Druk op Enter (of
op je zelfgemaakte knop) voor de volgende stap.

## Wat heb je nodig?

- Raspberry Pi Pico (of Pico W) met MicroPython-firmware
- Micro-USB-kabel
- [Thonny](https://thonny.org)
- Optioneel: 1 jumperkabeltje (voor de "volgende stap"-knop)

## Installatie (Thonny)

1. Sluit de Pico via USB aan en kies rechtsonder in Thonny de interpreter
   **MicroPython (Raspberry Pi Pico)**. Geen MicroPython op de Pico? Houd
   BOOTSEL ingedrukt tijdens het aansluiten en laat Thonny de firmware
   installeren (*Tools → Options → Interpreter → Install or update*).
2. Open `main.py` uit deze map in Thonny.
3. *File → Save as… → Raspberry Pi Pico* en sla het op als **`main.py`**.
4. Druk op **Run** (groene knop). Het menu verschijnt in de Thonny-shell.
5. Kies een domein (1–5), lees de vraag en druk op **Enter** voor elke
   volgende tussenstap.

Omdat het bestand `main.py` heet, start de trainer voortaan ook vanzelf
zodra de Pico stroom krijgt.

> Tip: de code draait óók gewoon op je laptop (`python3 main.py`), handig
> om te demonstreren als de Pico even niet meewerkt tijdens de hackathon.

## De jumper-knop (optioneel maar leuk)

Steek een jumperkabeltje in **GP15** (pin 20) en tik met het andere
uiteinde kort tegen een **GND**-pin (bijvoorbeeld pin 18, er tussenin zit
er altijd één in de buurt). Elke tik = volgende tussenstap, en in het menu
kiest de knop een willekeurige opgave. De onboard-LED knippert bij elke
stap als bevestiging.

```
 Pico (bovenaanzicht, USB boven)
 ┌──────────────┐
 │ ...          │
 │ pin 18  GND ●│──┐
 │ pin 19 GP14 ●│  │  jumperkabel: even
 │ pin 20 GP15 ●│──┘  aantikken = volgende stap
 │ ...          │
 └──────────────┘
```

Er is geen weerstand nodig: de code gebruikt de interne pull-up van GP15.

## Toetsmatrix

| # | Domein | Opgave | Punten |
|---|--------|--------|--------|
| 1 | Goniometrie / sinusoïden | Het golfslagbad | 10 |
| 2 | Normale verdeling & hypothesetoetsen | De pindakaasfabriek | 14 |
| 3 | Kansrekening & verwachtingswaarde | Het dobbelspel | 15 |
| 4 | Differentiëren & optimaliseren | Pizza! | 17 |
| 5 | Algebra: snijpunten & raaklijnen | Functies | 17 |

Elke opgave bestaat uit meerdere delen (a, b, c, …) met puntenaantallen
zoals op een echte toets. De getallen worden per keer opnieuw geloot, dus
je kunt eindeloos oefenen — de *aanpak* blijft hetzelfde, de antwoorden
niet.

## Hoe het werkt

- `main.py` is één zelfstandig MicroPython-bestand, geen extra libraries.
- Elke opgave-generator loot parameters die gegarandeerd "mooi" uitkomen
  (gehele oplossingen, nette breuken) zodat de algebraïsche stappen
  kloppen zoals je ze op papier zou schrijven.
- De stappenteller wacht op Enter via de seriële shell **of** op een
  puls op GP15 — allebei tegelijk actief.
- Zonder `machine`-module (op een pc) valt de code automatisch terug op
  gewone `input()`.
