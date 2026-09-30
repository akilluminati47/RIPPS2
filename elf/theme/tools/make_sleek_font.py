"""Builds RIPPS2 Sleek (elf/theme/fonts/ripps2_sleek.ttf), the UI font for hints, glyph labels,
menus and settings.

The letters take the PS2 logo's lettering as their model: one thin, even stroke, square corners,
letters built from horizontal and vertical bars on a grid, and the logo's own open forms -- the P
with no stem above its bowl, the zigzag 2 carried into the S. They are narrower than
the main font (Planet N Compact, assets/master.ttf), so a full hint bar fits the screen. The digits
are the main font's own, copied in so numbers read the same everywhere. The S is the square form:
the logo's stepped S (kept as --s-variant logo) reads as a stray stroke inside words. Metrics match
the main font, so both sit on one baseline.

Each glyph is a set of polylines on a grid 6 units tall (the cap height); every segment becomes a
stroke rectangle, extended half a stroke past its ends so the corners close square.

    python elf/theme/tools/make_sleek_font.py [--s-variant logo|square] [--preview out.png]
"""
import argparse
import math
import os
import unicodedata

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
MASTER = os.path.join(ROOT, 'assets', 'master.ttf')
OUT = os.path.normpath(os.path.join(HERE, '..', 'fonts', 'ripps2_sleek.ttf'))

UPM = 1000
CAP = 680            # the main font's cap height
ASC, DESC = 894, -182
U = CAP / 6.0        # one grid unit
STROKE = 0.7 * U     # a thin, even line, as in the logo
SB = 60              # side bearing each side

# polylines per glyph, x in grid units from 0 to the glyph's width, y from 0 (baseline) to 6 (cap)
GLYPHS = {
    'A': [[(0, 0), (0, 6), (4, 6), (4, 0)], [(0, 3), (4, 3)]],
    'B': [[(0, 0), (0, 6), (3.2, 6), (3.2, 3), (0, 3)], [(3.2, 3), (4, 3), (4, 0), (0, 0)]],
    'C': [[(4, 6), (0, 6), (0, 0), (4, 0)]],
    'D': [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 1), (3, 0), (0, 0)]],
    'E': [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3.2, 3)]],
    'F': [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3.2, 3)]],
    'G': [[(4, 6), (0, 6), (0, 0), (4, 0), (4, 3), (2.2, 3)]],
    'H': [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    'I': [[(0, 0), (0, 6)]],
    'J': [[(4, 6), (4, 0), (0, 0), (0, 1.8)]],
    'K': [[(0, 0), (0, 6)], [(0, 3), (1.2, 3)], [(4, 6), (1.2, 3), (4, 0)]],
    'L': [[(0, 6), (0, 0), (3.6, 0)]],
    'M': [[(0, 0), (0, 6), (5, 6), (5, 0)], [(2.5, 6), (2.5, 2.2)]],
    'N': [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    'O': [[(0, 0), (0, 6), (4, 6), (4, 0), (0, 0)]],
    'P': [[(0, 6), (4, 6), (4, 3), (0, 3)], [(0, 3), (0, 0)]],                  # the logo's P
    'Q': [[(0, 0), (0, 6), (4, 6), (4, 0), (0, 0)], [(2.8, 1.2), (4.6, -0.6)]],
    'R': [[(0, 6), (4, 6), (4, 3), (0, 3)], [(0, 3), (0, 0)], [(1.8, 3), (4, 0)]],
    'S_logo': [[(4, 6), (2, 6), (2, 0), (0, 0)]],                               # the logo's stepped S
    'S_square': [[(4, 6), (0, 6), (0, 3), (4, 3), (4, 0), (0, 0)]],             # the logo's 2, mirrored
    'T': [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    'U': [[(0, 6), (0, 0), (4, 0), (4, 6)]],
    'V': [[(0, 6), (2, 0), (4, 6)]],
    'W': [[(0, 6), (0, 0), (5, 0), (5, 6)], [(2.5, 0), (2.5, 3.8)]],
    'X': [[(0, 6), (4, 0)], [(0, 0), (4, 6)]],
    'Y': [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]],
    'Z': [[(0, 6), (4, 6), (0, 0), (4, 0)]],
    ':': [[(0, 0), (0, 0.01)], [(0, 3.6), (0, 3.61)]],
    '.': [[(0, 0), (0, 0.01)]],
    ',': [[(0, 0.2), (0, -1.0)]],
    ';': [[(0, 3.6), (0, 3.61)], [(0, 0.2), (0, -1.0)]],
    "'": [[(0, 6), (0, 4.4)]],
    '"': [[(0, 6), (0, 4.4)], [(1.2, 6), (1.2, 4.4)]],
    '-': [[(0, 3), (2.6, 3)]],
    '_': [[(0, -0.8), (4, -0.8)]],
    '+': [[(0, 3), (3.2, 3)], [(1.6, 1.4), (1.6, 4.6)]],
    '=': [[(0, 2), (3.2, 2)], [(0, 4), (3.2, 4)]],
    '/': [[(0, 0), (3, 6)]],
    '\\': [[(0, 6), (3, 0)]],
    '(': [[(1.4, 6.6), (0, 6.6), (0, -0.6), (1.4, -0.6)]],
    ')': [[(0, 6.6), (1.4, 6.6), (1.4, -0.6), (0, -0.6)]],
    '[': [[(1.4, 6.6), (0, 6.6), (0, -0.6), (1.4, -0.6)]],
    ']': [[(0, 6.6), (1.4, 6.6), (1.4, -0.6), (0, -0.6)]],
    '<': [[(3, 5.4), (0, 3), (3, 0.6)]],
    '>': [[(0, 5.4), (3, 3), (0, 0.6)]],
    '!': [[(0, 6), (0, 1.8)], [(0, 0), (0, 0.01)]],
    '?': [[(0, 6), (4, 6), (4, 3), (2, 3), (2, 1.8)], [(2, 0), (2, 0.01)]],
    '&': [[(4, 0), (0, 0), (0, 3), (3, 3)], [(1, 3), (1, 6), (3.2, 6), (3.2, 4.4)], [(3, 3), (4, 3)]],
    '%': [[(0, 0), (4, 6)], [(0, 6), (0.8, 6), (0.8, 5.2), (0, 5.2), (0, 6)], [(3.2, 0.8), (4, 0.8), (4, 0), (3.2, 0), (3.2, 0.8)]],
    '#': [[(1.2, 0), (1.2, 6)], [(2.8, 0), (2.8, 6)], [(0, 2), (4, 2)], [(0, 4), (4, 4)]],
    '*': [[(0, 4.5), (2.4, 4.5)], [(1.2, 3.3), (1.2, 5.7)]],
    '@': [[(3, 2), (1.4, 2), (1.4, 4), (3, 4), (3, 1.2), (4, 1.2), (4, 6), (0, 6), (0, 0), (4, 0)]],
    '|': [[(0, -0.6), (0, 6.6)]],
    '~': [[(0, 3), (1, 3.8), (2, 3), (3, 3.8)]],
}
MASTER_DIGITS = '0123456789'  # numbers are the main font's own


def stroke_rect(p, q, half):
    """The four corners of a stroke from p to q, extended half a stroke past each end."""
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        dx, dy, length = 1.0, 0.0, 1.0
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    ax, ay = x0 - ux * half, y0 - uy * half
    bx, by = x1 + ux * half, y1 + uy * half
    pts = [(ax + nx * half, ay + ny * half), (bx + nx * half, by + ny * half),
           (bx - nx * half, by - ny * half), (ax - nx * half, ay - ny * half)]
    # TrueType outer contours run clockwise (negative signed area with y up)
    area = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))
    return pts if area < 0 else pts[::-1]


def draw_polylines(polys):
    pen = TTGlyphPen(None)
    xs = [x for poly in polys for x, _ in poly]
    width_units = max(xs) - min(xs) if xs else 0
    ox = SB + STROKE / 2 - min(xs) * U
    half = STROKE / 2
    for poly in polys:
        pts = [(ox + x * U, y * U) for x, y in poly]
        for p, q in zip(pts, pts[1:]):
            corners = stroke_rect(p, q, half)
            pen.moveTo((round(corners[0][0]), round(corners[0][1])))
            for c in corners[1:]:
                pen.lineTo((round(c[0]), round(c[1])))
            pen.closePath()
    advance = round(width_units * U + STROKE + 2 * SB)
    return pen.glyph(), advance


def build(s_variant):
    master = TTFont(MASTER)
    mcmap = master.getBestCmap()
    mglyphs = master.getGlyphSet()

    order = ['.notdef', 'space']
    glyf, hmtx, cmap = {}, {}, {}

    empty = TTGlyphPen(None).glyph()
    glyf['.notdef'], hmtx['.notdef'] = empty, (400, 0)
    glyf['space'], hmtx['space'] = empty, (round(2.6 * U), 0)
    cmap[0x20] = 'space'
    cmap[0xA0] = 'space'

    defs = dict(GLYPHS)
    defs['S'] = defs.pop('S_logo') if s_variant == 'logo' else defs.pop('S_square')
    defs.pop('S_logo', None)
    defs.pop('S_square', None)
    for ch in MASTER_DIGITS:
        defs.pop(ch, None)

    for ch, polys in defs.items():
        name = 'g%04X' % ord(ch)
        glyph, adv = draw_polylines(polys)
        glyf[name], hmtx[name] = glyph, (adv, 0)
        order.append(name)
        cmap[ord(ch)] = name
        if ch.isalpha():
            cmap[ord(ch.lower())] = name  # all capitals, as in the logo

    for ch in MASTER_DIGITS:  # the main font's own digits, outlines copied across
        src = mcmap[ord(ch)]
        pen = TTGlyphPen(None)
        mglyphs[src].draw(pen)
        name = 'digit' + ch
        glyf[name], hmtx[name] = pen.glyph(), (master['hmtx'][src][0], 0)
        order.append(name)
        cmap[ord(ch)] = name

    # accented Latin letters fall back to their base letter, so other languages stay readable
    for cp in range(0xC0, 0x250):
        base = unicodedata.normalize('NFD', chr(cp))[0]
        if cp not in cmap and base.upper() in defs and base.isalpha():
            cmap[cp] = cmap[ord(base.upper())]

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC, lineGap=9)
    fb.setupNameTable({'familyName': 'RIPPS2 Sleek', 'styleName': 'Regular',
                       'uniqueFontIdentifier': 'RIPPS2 Sleek Regular', 'fullName': 'RIPPS2 Sleek',
                       'psName': 'RIPPS2Sleek-Regular', 'version': 'Version 1.0'})
    fb.setupOS2(sTypoAscender=750, sTypoDescender=-170, sTypoLineGap=0, usWinAscent=ASC, usWinDescent=-DESC,
                sCapHeight=CAP, sxHeight=CAP)
    fb.setupPost()
    fb.setupMaxp()
    return fb.font


def preview(font_path, out):
    from PIL import Image, ImageDraw, ImageFont
    lines = ['MENU RUN INFO OPTIONS REFRESH FAVORITE PS1', 'SETTINGS GAME SOURCES START DEVICE BACK SELECT',
             'ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789', 'VIDEO MODE AUTO  H-POS 0  16:9 480P  4/8']
    im = Image.new('RGB', (1000, 30 + 2 * 44 * len(lines)), (12, 20, 60))
    d = ImageDraw.Draw(im)
    y = 10
    for size in (26, 13):
        f = ImageFont.truetype(font_path, size)
        for line in lines:
            d.text((14, y), line, font=f, fill=(232, 240, 255))
            y += size + 12
    im.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s-variant', choices=('logo', 'square'), default='square')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--preview')
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    build(a.s_variant).save(a.out)
    print('wrote', a.out)
    if a.preview:
        preview(a.out, a.preview)


if __name__ == '__main__':
    main()
