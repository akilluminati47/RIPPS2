"""Builds RIPPS2's two extra built-in glyph sets (build 90), Standard and White, into elf/theme/gfx as
glyph_standard_<name>.png and glyph_white_<name>.png. A theme picks one with glyph_set=standard|white
(or ripps2, or theme for its own PNGs), and Controller Settings > Hints and Glyphs > Glyph Set lets the
user pick for every theme.

Standard is the Adapt theme's glyphs (dark glossy buttons, coloured symbols). White is the Grunge
theme's (solid white, symbols cut out). Both themes are the user's own work. Their face buttons and
START / SELECT are taken as they are; everything the themes never drew (L1, R1, L2+R2, L3, R3 and the
four D-pad directions) is drawn here in each set's own style, at the same sizes as RIPPS2's glyphs
(Standard) or half again as big, like Grunge's face buttons (White).

    python elf/theme/tools/make_glyph_sets.py --standard <thm_Adapt folder> --white <thm_Grunge folder> --font <ttf>

--font is the label face (the themes' own b.ttf, Roboto Bold Condensed). Run png8.py on elf/theme/gfx
afterwards (this script already writes 8-bit PNGs, png8.py only checks them then).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx'))
sys.path.insert(0, HERE)
import png8  # noqa: E402

SS = 4
COPIED = ('cross', 'circle', 'square', 'triangle', 'start', 'select')
PILLS = ('L1', 'R1', 'L3', 'R3')
ARMS = ('up', 'down', 'left', 'right')
NAMES = COPIED + PILLS + ('L2R2',) + ARMS  # every glyph a set carries, in the order the ELF lists them


def canvas(w, h):
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def write(im, name, supersampled=True):
    """Save a glyph as an 8-bit palette PNG (png8.convert), downsampling a supersampled one first."""
    if supersampled:
        w, h = im.size
        im = im.resize((w // SS, h // SS), Image.LANCZOS)
    path = os.path.join(OUT, name + '.png')
    im.convert('RGBA').save(path)
    png8.convert(path)
    return path


def text_box(d, f, text):
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    return l, t, r, b


def fit_font(path, texts, max_w, max_h, start):
    """The largest size at which every label fits max_w x max_h (supersampled pixels)."""
    probe = ImageDraw.Draw(Image.new('L', (8, 8)))
    px = start
    while px > 6:
        f = ImageFont.truetype(path, px * SS)
        if all((lambda b: b[2] - b[0] <= max_w * SS and b[3] - b[1] <= max_h * SS)(text_box(probe, f, t)) for t in texts):
            return f
        px -= 1
    return ImageFont.truetype(path, px * SS)


def draw_label(d, f, cx, cy, text, fill):
    l, t, r, b = text_box(d, f, text)
    d.text((cx * SS - (l + r) / 2, cy * SS - (t + b) / 2), text, font=f, fill=fill)


def plus_polygon(lo, hi, a0, a1):
    return [(a0, lo), (a1, lo), (a1, a0), (hi, a0), (hi, a1), (a1, a1), (a1, hi), (a0, hi), (a0, a1), (lo, a1), (lo, a0), (a0, a0)]


def arm_box(arm, lo, hi, a0, a1):
    return {'left': (lo, a0, a0, a1), 'right': (a1, a0, hi, a1), 'up': (a0, lo, a1, a0), 'down': (a0, a1, a1, hi)}[arm]


def arrow(arm, cx, cy, k):
    return {'left': [(cx - k, cy), (cx + k * 0.8, cy - k), (cx + k * 0.8, cy + k)],
            'right': [(cx + k, cy), (cx - k * 0.8, cy - k), (cx - k * 0.8, cy + k)],
            'up': [(cx, cy - k), (cx - k, cy + k * 0.8), (cx + k, cy + k * 0.8)],
            'down': [(cx, cy + k), (cx - k, cy - k * 0.8), (cx + k, cy - k * 0.8)]}[arm]


def S(points):
    return [(x * SS, y * SS) for x, y in points]


# ---- Standard: Adapt's dark glossy plastic. The buttons are a grey disc (62,63,66) with a darker rim
# (41,42,44) and a soft highlight towards the top; labels and the pressed D-pad arm in light grey.
STD_RIM = (41, 42, 44, 255)
STD_TOP = (80, 81, 84, 255)
STD_BOT = (50, 50, 52, 255)
STD_TEXT = (214, 216, 222, 255)


def std_fill(w, h):
    """The glossy body: a vertical gradient from STD_TOP to STD_BOT, as an RGBA image (supersampled)."""
    g = Image.new('RGBA', (w * SS, h * SS))
    gd = ImageDraw.Draw(g)
    for y in range(h * SS):
        t = y / max(1, h * SS - 1)
        gd.line([(0, y), (w * SS, y)], fill=tuple(round(STD_TOP[i] + (STD_BOT[i] - STD_TOP[i]) * t) for i in range(3)) + (255,))
    return g


def std_pill(w, text, f):
    h = 32
    mask = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle((1 * SS, 3 * SS, (w - 1) * SS, 29 * SS), radius=12 * SS, fill=255)
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    im.paste(std_fill(w, h), (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1 * SS, 3 * SS, (w - 1) * SS, 29 * SS), radius=12 * SS, outline=STD_RIM, width=round(1.6 * SS))
    draw_label(d, f, w / 2, 16.2, text, STD_TEXT)
    return im


def std_dpad(arm):
    lo, hi, a0, a1 = 2.5, 29.5, 11.0, 21.0
    mask = Image.new('L', (32 * SS, 32 * SS), 0)
    ImageDraw.Draw(mask).polygon(S(plus_polygon(lo, hi, a0, a1)), fill=255)
    im = Image.new('RGBA', (32 * SS, 32 * SS), (0, 0, 0, 0))
    im.paste(std_fill(32, 32), (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.polygon(S(plus_polygon(lo, hi, a0, a1)), outline=STD_RIM, width=round(1.6 * SS))
    x0, y0, x1, y1 = arm_box(arm, lo, hi, a0, a1)
    d.polygon(S(arrow(arm, (x0 + x1) / 2, (y0 + y1) / 2, 4.3)), fill=STD_TEXT)
    return im


# ---- White: Grunge's solid white (250,250,250), symbols cut out to the background. Half again as big
# as RIPPS2's glyphs, like Grunge's 48 px face buttons; the engine draws every glyph 20 px tall anyway.
WHITE = (250, 250, 250, 255)
W_SCALE = 1.5


def white_pill(w, text, f):
    W, H = round(w * W_SCALE), 48
    im, d = canvas(W, H)
    d.rounded_rectangle((1.5 * SS, 4.5 * SS, (W - 1.5) * SS, 43.5 * SS), radius=18 * SS, fill=WHITE)
    cut = Image.new('L', im.size, 0)
    draw_label(ImageDraw.Draw(cut), f, W / 2, 24.3, text, 255)
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel('A')), 255 - np.asarray(cut))))
    return im


def white_dpad(arm):
    n = 48
    lo, hi, a0, a1 = 3.5, 44.5, 16.5, 31.5
    im, d = canvas(n, n)
    d.polygon(S(plus_polygon(lo, hi, a0, a1)), fill=(250, 250, 250, 120))  # the D-pad, the other arms dimmed
    x0, y0, x1, y1 = arm_box(arm, lo, hi, a0, a1)
    pad = 0.6
    d.rectangle(((x0 - pad) * SS, (y0 - pad) * SS, (x1 + pad) * SS, (y1 + pad) * SS), fill=WHITE)  # the pressed arm, solid
    d.rectangle((a0 * SS, a0 * SS, a1 * SS, a1 * SS), fill=(250, 250, 250, 120))
    d.polygon(S(arrow(arm, (x0 + x1) / 2, (y0 + y1) / 2, 6.0)), fill=(0, 0, 0, 0))  # its arrow cut out
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--standard', required=True, help="the Adapt theme's folder (cross.png ... select.png)")
    ap.add_argument('--white', required=True, help="the Grunge theme's folder")
    ap.add_argument('--font', required=True, help='the label face (Roboto Bold Condensed)')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    written = []
    for set_name, src in (('standard', a.standard), ('white', a.white)):
        for n in COPIED:
            written.append(write(Image.open(os.path.join(src, n + '.png')).convert('RGBA'), 'glyph_%s_%s' % (set_name, n), False))
    f_std = min(fit_font(a.font, PILLS, 33, 20, 24), fit_font(a.font, ('L2+R2',), 60, 20, 24), key=lambda f: f.size)
    for n in PILLS:
        written.append(write(std_pill(44, n, f_std), 'glyph_standard_' + n))
    written.append(write(std_pill(72, 'L2+R2', f_std), 'glyph_standard_L2R2'))
    f_white = min(fit_font(a.font, PILLS, 50, 30, 36), fit_font(a.font, ('L2+R2',), 90, 30, 36), key=lambda f: f.size)
    for n in PILLS:
        written.append(write(white_pill(44, n, f_white), 'glyph_white_' + n))
    written.append(write(white_pill(72, 'L2+R2', f_white), 'glyph_white_L2R2'))
    for arm in ARMS:
        written.append(write(std_dpad(arm), 'glyph_standard_' + arm))
        written.append(write(white_dpad(arm), 'glyph_white_' + arm))
    print('wrote', len(written), 'glyphs to', OUT)


if __name__ == '__main__':
    main()
