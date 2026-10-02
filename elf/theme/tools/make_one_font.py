"""RIPPS2 One (elf/theme/fonts/ripps2_one.ttf): a single glyph, a flagged 1 in the weight of the main
font, Planet N Compact (assets/master.ttf).

Planet N draws its 1 with the same glyph as its I, a rounded bar, so PS1 reads as PSI and R1 as RI.
RIPPS2 leaves the font itself as it is and has its font system take the 1 from this file instead,
wherever Planet N draws one. The bar keeps Planet N's own measures (136 units across, ends rounded
to its half width, 680 tall on a 1000 unit em), and the flag is the same stroke, down-left from the
top at about 40 degrees.

    python elf/theme/tools/make_one_font.py
"""
import math
import os

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'fonts', 'ripps2_one.ttf'))
UPM, ASC, DESC = 1000, 894, -182
R = 68.0           # half Planet N's stroke (its 1 is 136 across)
SB = 61            # its side bearing
CAPS = 16          # points round each rounded end


def capsule(pen, p, q):
    """A stroke from p to q, R wide each side, both ends round; clockwise, as TrueType wants."""
    (x0, y0), (x1, y1) = p, q
    a = math.atan2(y1 - y0, x1 - x0)
    pts = []
    # round the end at q, from one side to the other, then back along the far side round p
    for k in range(CAPS + 1):
        t = a + math.pi / 2 - math.pi * k / CAPS
        pts.append((x1 + R * math.cos(t), y1 + R * math.sin(t)))
    for k in range(CAPS + 1):
        t = a - math.pi / 2 - math.pi * k / CAPS
        pts.append((x0 + R * math.cos(t), y0 + R * math.sin(t)))
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area > 0:
        pts.reverse()
    pen.moveTo((round(pts[0][0]), round(pts[0][1])))
    for x, y in pts[1:]:
        pen.lineTo((round(x), round(y)))
    pen.closePath()


def main():
    stem_x = SB + R + 196          # the bar's centre: room on the left for the flag
    top, bottom = 680 - R, R
    flag_end = (SB + R, top - 164)  # down-left from the top of the bar
    pen = TTGlyphPen(None)
    capsule(pen, (stem_x, bottom), (stem_x, top))
    capsule(pen, (stem_x, top), flag_end)
    one = pen.glyph()
    advance = int(round(stem_x + R + SB))

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'one'])
    fb.setupCharacterMap({ord('1'): 'one'})
    fb.setupGlyf({'.notdef': TTGlyphPen(None).glyph(), 'one': one})
    fb.setupHorizontalMetrics({'.notdef': (400, 0), 'one': (advance, SB)})
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC, lineGap=0)
    fb.setupNameTable({'familyName': 'RIPPS2 One', 'styleName': 'Regular', 'uniqueFontIdentifier': 'RIPPS2 One',
                       'fullName': 'RIPPS2 One', 'psName': 'RIPPS2One-Regular', 'version': 'Version 1.0'})
    # Planet N's own vertical metrics, typo metrics in use, so the 1 sits on its baseline everywhere
    fb.setupOS2(sTypoAscender=750, sTypoDescender=-170, sTypoLineGap=0, usWinAscent=ASC, usWinDescent=-DESC,
                sCapHeight=680, sxHeight=480, fsSelection=0x00C0, version=4)
    fb.setupPost()
    fb.setupMaxp()
    fb.font.save(OUT)
    print('wrote', OUT, 'advance', advance)


if __name__ == '__main__':
    main()
