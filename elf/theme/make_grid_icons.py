"""RIPPS2 settings grid icons: seven line-art icons and their glows in one atlas (ripps2_grid_icons.png).

Row 0: the icons, anti-aliased white strokes on transparency (tinted at draw time).
Row 1: the same icons blurred into a soft glow, drawn additively under the active tile's icon.
Cells are 64 px, the size the grid draws them at, so the GS never has to shrink a stroke (it has no
mipmaps: a 96 px icon drawn at 64 sampled unevenly and looked warped). Shapes are laid out on a 96-unit
design grid and drawn 8x supersampled, then reduced.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFilter

CELL, SS = 64, 8
DESIGN = 96.0
K = SS * CELL / DESIGN  # design units to supersampled pixels
W = 3.2  # stroke width in design units (2.1 px on screen)
OUT = sys.argv[1] if len(sys.argv) > 1 else 'ripps2_grid_icons.png'


def P(x, y):
    return (x * K, y * K)


def poly(d, pts, closed=True, w=W):
    pts = [P(*p) for p in pts]
    if closed:
        pts = pts + [pts[0]]
    d.line(pts, fill=255, width=int(w * K), joint='curve')
    # round caps on an open path's ends, and round corners where a path turns sharply
    r = w * K / 2
    ends = [pts[0], pts[-1]] if not closed else []
    for k in range(1, len(pts) - 1):
        ax, ay = pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]
        bx, by = pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        if la and lb and (ax * bx + ay * by) / (la * lb) < 0.9:
            ends.append(pts[k])
    for p in ends:
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=255)


def line(d, a, b, w=W):
    poly(d, [a, b], closed=False, w=w)


def circle(d, cx, cy, r, w=W, fill=False):
    if fill:
        d.ellipse((P(cx - r, cy - r), P(cx + r, cy + r)), fill=255)
    else:  # PIL strokes inward from the box: grow it by half a stroke so the line is centred on r
        h = w / 2
        d.ellipse((P(cx - r - h, cy - r - h), P(cx + r + h, cy + r + h)), outline=255, width=int(w * K))


def arc(d, cx, cy, r, a0, a1, w=W):
    # PIL's own arc (a true curve, evenly stroked), centred on r, with round caps
    h = w / 2
    d.arc((P(cx - r - h, cy - r - h), P(cx + r + h, cy + r + h)), a0, a1, fill=255, width=int(w * K))
    for a in (a0, a1):
        x, y = P(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        d.ellipse((x - w * K / 2, y - w * K / 2, x + w * K / 2, y + w * K / 2), fill=255)


def rrect(d, x0, y0, x1, y1, r, w=W):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(a0, a0 + 91, 10)]
    poly(d, pts, w=w)


def browser(d):  # a folder holding a little tree: the browser's own view
    poly(d, [(12, 26), (36, 26), (42, 33), (84, 33), (84, 76), (12, 76)])
    line(d, (12, 40), (84, 40), w=W * 0.7)
    line(d, (28, 48), (28, 66), w=W * 0.8)
    line(d, (28, 57), (40, 57), w=W * 0.8)
    line(d, (28, 66), (40, 66), w=W * 0.8)
    circle(d, 28, 48, 3.2, fill=True)
    circle(d, 44, 57, 3.2, fill=True)
    circle(d, 44, 66, 3.2, fill=True)
    line(d, (52, 57), (72, 57), w=W * 0.7)
    line(d, (52, 66), (66, 66), w=W * 0.7)


def editor(d):  # a page with its corner folded, lines of text and a pencil across it
    poly(d, [(18, 12), (54, 12), (68, 26), (68, 84), (18, 84)])
    poly(d, [(54, 12), (54, 26), (68, 26)], closed=False, w=W * 0.8)
    for y, x1 in ((36, 58), (46, 58), (56, 50), (66, 40)):
        line(d, (28, y), (x1, y), w=W * 0.7)
    # the pencil: a long body at 45 degrees, its tip at the end of the last line
    a = math.radians(-45)
    ux, uy = math.cos(a), math.sin(a)          # along the pencil
    nx, ny = -uy, ux                            # across it
    tip = (46, 76)
    hw = 4.2
    b0 = (tip[0] + ux * 9, tip[1] + uy * 9)
    b1 = (tip[0] + ux * 40, tip[1] + uy * 40)
    corners = [(b0[0] + nx * hw, b0[1] + ny * hw), (b1[0] + nx * hw, b1[1] + ny * hw),
               (b1[0] - nx * hw, b1[1] - ny * hw), (b0[0] - nx * hw, b0[1] - ny * hw)]
    poly(d, corners, w=W * 0.8)
    poly(d, [corners[0], tip, corners[3]], closed=False, w=W * 0.8)
    e0 = (b1[0] - ux * 6, b1[1] - uy * 6)
    line(d, (e0[0] + nx * hw, e0[1] + ny * hw), (e0[0] - nx * hw, e0[1] - ny * hw), w=W * 0.7)


def hdd(d):  # an opened drive: platter split into partitions, the head's arm, the activity light
    rrect(d, 10, 18, 86, 78, 7)
    cx, cy, r = 40, 48, 21
    circle(d, cx, cy, r)
    circle(d, cx, cy, 3.4, fill=True)
    for ang in (-100, 15, 140):  # partition boundaries
        a = math.radians(ang)
        line(d, (cx + 6 * math.cos(a), cy + 6 * math.sin(a)), (cx + (r - 2) * math.cos(a), cy + (r - 2) * math.sin(a)), w=W * 0.6)
    circle(d, 74, 30, 4.5)
    line(d, (71, 34), (54, 54), w=W * 0.9)
    circle(d, 77, 70, 2.6, fill=True)


def exploit(d):  # a PS2 memory card taking an install: the card's cut corner, its label, an arrow in
    poly(d, [(26, 10), (64, 10), (72, 18), (72, 86), (26, 86)])
    rrect(d, 33, 18, 64, 40, 3, w=W * 0.7)
    line(d, (49, 48), (49, 74))
    poly(d, [(39, 64), (49, 74), (59, 64)], closed=False)
    line(d, (36, 80), (62, 80), w=W * 0.7)


def power(d):  # the power mark: a ring open at the top, symmetric about the stroke through it
    arc(d, 48, 52, 28, -60, 240)
    line(d, (48, 12), (48, 48))


def exitb(d):  # leave the browser: a door standing open, an arrow out through it
    rrect(d, 48, 10, 84, 86, 3)                                   # the frame
    poly(d, [(48, 10), (64, 17), (64, 82), (48, 86)], w=W * 0.85)  # the door, swung open toward you
    circle(d, 59, 50, 2.6, fill=True)                             # its handle
    line(d, (40, 48), (10, 48))
    poly(d, [(22, 36), (10, 48), (22, 60)], closed=False)


def orbits(d):  # the orbit settings: two tilted rings round a core, an orb riding each
    cx, cy = 48, 48
    for tilt, (rx, ry), at in ((-28, (36, 13), 200), (28, (36, 13), 330)):
        t = math.radians(tilt)
        pts = []
        for k in range(0, 360, 6):
            a = math.radians(k)
            x, y = rx * math.cos(a), ry * math.sin(a)
            pts.append((cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t)))
        poly(d, pts, w=W * 0.8)
        a = math.radians(at)
        x, y = rx * math.cos(a), ry * math.sin(a)
        circle(d, cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t), 4.6, fill=True)
    circle(d, cx, cy, 6.0, fill=True)


# Row order is the settings grid's tile order (ripps2files.c FB_TILE_*); the HDD drawing stays at the
# end for the HDD MANAGER, now a Square action on a hard drive (build 69)
ICONS = [browser, editor, orbits, exploit, power, exitb, hdd]

atlas = Image.new('RGBA', (CELL * len(ICONS), CELL * 2), (255, 255, 255, 0))
for i, fn in enumerate(ICONS):
    big = Image.new('L', (CELL * SS, CELL * SS), 0)
    fn(ImageDraw.Draw(big))
    a = big.resize((CELL, CELL), Image.LANCZOS)
    glow = a.filter(ImageFilter.GaussianBlur(3.0))
    glow = glow.point(lambda v: min(255, int(v * 2.4)))
    for row, alpha in ((0, a), (1, glow)):
        cell = Image.new('RGBA', (CELL, CELL), (255, 255, 255, 0))
        cell.putalpha(alpha)
        atlas.paste(cell, (i * CELL, row * CELL))
atlas.save(OUT, optimize=True)
print(OUT, atlas.size)
