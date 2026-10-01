"""RIPPS2 settings grid icons: six line-art icons and their glows in one atlas (ripps2_grid_icons.png).

Row 0: the icons, anti-aliased white strokes on transparency (tinted at draw time).
Row 1: the same icons blurred into a soft glow, drawn additively under the active tile's icon.
Cells are 96 px, drawn 4x supersampled and reduced, so the strokes stay smooth when the PS2 scales them.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFilter

CELL, SS = 96, 4
W = 3.2  # stroke width in cell pixels
OUT = sys.argv[1] if len(sys.argv) > 1 else 'ripps2_grid_icons.png'


def P(x, y):
    return (x * SS, y * SS)


def poly(d, pts, closed=True, w=W):
    pts = [P(*p) for p in pts]
    if closed:
        pts = pts + [pts[0]]
    d.line(pts, fill=255, width=int(w * SS), joint='curve')
    # round caps on an open path's ends, and round corners where a path turns sharply
    r = w * SS / 2
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
    box = (P(cx - r, cy - r), P(cx + r, cy + r))
    if fill:
        d.ellipse(box, fill=255)
    else:
        d.ellipse(box, outline=255, width=int(w * SS))


def arc(d, cx, cy, r, a0, a1, w=W):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
           for a in [a0 + (a1 - a0) * i / 48 for i in range(49)]]
    poly(d, pts, closed=False, w=w)


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


def power(d):  # the power mark
    arc(d, 48, 51, 27, -55, 235)
    line(d, (48, 14), (48, 46))


def exitb(d):  # out of the panel, back to the orbs: an arrow leaving a frame toward an orb on its orbit
    poly(d, [(50, 16), (82, 16), (82, 80), (50, 80)], closed=False)
    line(d, (70, 48), (38, 48))
    poly(d, [(48, 38), (37, 48), (48, 58)], closed=False)
    circle(d, 17, 48, 4.2, fill=True)
    # the orbit, a thin tilted ellipse round the orb
    pts = []
    c, s_ = math.cos(math.radians(-24)), math.sin(math.radians(-24))
    for i in range(72):
        t = 2 * math.pi * i / 72
        x, y = 14 * math.cos(t), 5.5 * math.sin(t)
        pts.append((17 + x * c - y * s_, 48 + x * s_ + y * c))
    poly(d, pts, w=W * 0.55)


ICONS = [browser, editor, hdd, exploit, power, exitb]

atlas = Image.new('RGBA', (CELL * len(ICONS), CELL * 2), (255, 255, 255, 0))
for i, fn in enumerate(ICONS):
    big = Image.new('L', (CELL * SS, CELL * SS), 0)
    fn(ImageDraw.Draw(big))
    a = big.resize((CELL, CELL), Image.LANCZOS)
    glow = a.filter(ImageFilter.GaussianBlur(4.5))
    glow = glow.point(lambda v: min(255, int(v * 2.4)))
    for row, alpha in ((0, a), (1, glow)):
        cell = Image.new('RGBA', (CELL, CELL), (255, 255, 255, 0))
        cell.putalpha(alpha)
        atlas.paste(cell, (i * CELL, row * CELL))
atlas.save(OUT, optimize=True)
print(OUT, atlas.size)
