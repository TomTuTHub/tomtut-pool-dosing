#!/usr/bin/env python3
"""Freistellen der Anlagen-Grafiken (Issue tomtut-pool-dosing-card#1).

Von jeder Anlage gibt es dasselbe Motiv zweimal: einmal auf weissem, einmal auf
grauem Hintergrund. Daraus laesst sich der Alphakanal exakt berechnen, statt den
Hintergrund zu stanzen (kein Halo, auch nicht an weichen Kanten):

    C_w = F*a + BG_w*(1-a)      (Motiv ueber weiss)
    C_g = F*a + BG_g*(1-a)      (Motiv ueber grau)
    => (1-a) = (C_w - C_g) / (BG_w - BG_g)
    => F     = (C_g - BG_g*(1-a)) / a

Aufruf (ohne Argumente, arbeitet auf static/):
    python3 tools/make_transparent.py
"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image

STATIC = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "tomtut_pool_dosing" / "static"
PAARE = (
    ("dosier_v1.png", "dosier_v2.png", "dosier_v2_transparent.png"),
    ("dosier_v3.png", "dosier_v4.png", "dosier_v4_transparent.png"),
)


def randfarbe(im: Image.Image) -> tuple[int, int, int]:
    """Hintergrundfarbe = Farbe des Bildrandes (muss eindeutig sein)."""
    w, h = im.size
    rand = {im.getpixel((x, 0)) for x in range(0, w, 7)}
    rand |= {im.getpixel((x, h - 1)) for x in range(0, w, 7)}
    rand |= {im.getpixel((0, y)) for y in range(0, h, 7)}
    rand |= {im.getpixel((w - 1, y)) for y in range(0, h, 7)}
    if len(rand) != 1:
        sys.exit(f"Rand ist nicht einfarbig ({len(rand)} Farben) - Verfahren nicht anwendbar")
    return rand.pop()


def clamp(v: float, lo: int = 0, hi: int = 255) -> int:
    return int(max(lo, min(hi, round(v))))


def nachbessern(ergebnis: Image.Image, dunkel: Image.Image, bg_dunkel) -> Image.Image:
    """Stellen reparieren, an denen sich die beiden Vorlagen im MOTIV unterscheiden.

    Das Verfahren oben setzt voraus, dass beide Vorlagen dasselbe Motiv zeigen.
    Wo das nicht stimmt (einzelne nachtraeglich retuschierte Stellen), faellt die
    Differenz nicht rein auf den Hintergrund zurueck und das Alpha wird falsch.
    Solche Pixel erkennt man daran, dass das Ergebnis, wieder ueber den grauen
    Hintergrund gelegt, nicht mehr die graue Vorlage ergibt. Dort gilt die graue
    Vorlage - sie ist das, was in der Bildvariante bisher ausgeliefert wurde.
    Echte Hintergrundpixel koennen hier nicht hineinlaufen: fuer sie ist die
    Rekonstruktion exakt.
    """
    platte = Image.new("RGB", ergebnis.size, bg_dunkel)
    platte.paste(ergebnis, (0, 0), ergebnis)
    korrigiert = 0
    daten = list(ergebnis.getdata())
    for i, (ist, soll) in enumerate(zip(platte.getdata(), dunkel.getdata())):
        if max(abs(ist[k] - soll[k]) for k in range(3)) > 2:
            daten[i] = (soll[0], soll[1], soll[2], 255)
            korrigiert += 1
    if korrigiert:
        ergebnis = ergebnis.copy()
        ergebnis.putdata(daten)
        print(f"  Motiv-Unterschiede nachgebessert: {korrigiert} Pixel (graue Vorlage gilt)")
    return ergebnis


def freistellen(pfad_weiss: pathlib.Path, pfad_grau: pathlib.Path, ziel: pathlib.Path) -> None:
    hell = Image.open(pfad_weiss).convert("RGB")
    dunkel = Image.open(pfad_grau).convert("RGB")
    if hell.size != dunkel.size:
        sys.exit(f"{pfad_weiss.name} und {pfad_grau.name} haben verschiedene Groessen")

    bg_hell = randfarbe(hell)
    bg_dunkel = randfarbe(dunkel)
    spanne = sum(bg_hell) / 3.0 - sum(bg_dunkel) / 3.0
    if spanne <= 1:
        sys.exit("Die beiden Hintergruende sind zu aehnlich - Alpha nicht bestimmbar")

    raus = bytearray()
    for cw, cg in zip(hell.getdata(), dunkel.getdata()):
        d = sum(cw[k] - cg[k] for k in range(3)) / 3.0
        eins_minus_a = max(0.0, min(1.0, d / spanne))
        a = 1.0 - eins_minus_a
        if a <= 0.002:
            raus += bytes((0, 0, 0, 0))
            continue
        raus += bytes(
            (
                clamp((cg[0] - bg_dunkel[0] * eins_minus_a) / a),
                clamp((cg[1] - bg_dunkel[1] * eins_minus_a) / a),
                clamp((cg[2] - bg_dunkel[2] * eins_minus_a) / a),
                clamp(a * 255),
            )
        )

    ergebnis = Image.frombytes("RGBA", hell.size, bytes(raus))
    ergebnis = nachbessern(ergebnis, dunkel, bg_dunkel)
    ergebnis.save(ziel, optimize=True)

    # Gegenprobe: wieder ueber die beiden bekannten Hintergruende legen
    for original, bg in ((dunkel, bg_dunkel), (hell, bg_hell)):
        platte = Image.new("RGB", hell.size, bg)
        platte.paste(ergebnis, (0, 0), ergebnis)
        abw = [
            max(abs(p[k] - q[k]) for k in range(3))
            for p, q in zip(platte.getdata(), original.getdata())
        ]
        print(
            f"  Gegenprobe ueber {bg}: max. Abweichung {max(abw)}, "
            f"Pixel mit Abweichung > 2: {sum(1 for v in abw if v > 2)}"
        )

    alpha = ergebnis.getchannel("A").histogram()
    gesamt = hell.size[0] * hell.size[1]
    print(
        f"  {ziel.name}: {ergebnis.size[0]}x{ergebnis.size[1]} RGBA, "
        f"voll transparent {100.0 * alpha[0] / gesamt:.1f} %, "
        f"voll deckend {100.0 * alpha[255] / gesamt:.1f} %"
    )


def main() -> None:
    for weiss, grau, ziel in PAARE:
        print(f"{weiss} + {grau} -> {ziel}")
        freistellen(STATIC / weiss, STATIC / grau, STATIC / ziel)


if __name__ == "__main__":
    main()
