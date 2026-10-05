"""Generates RIPPS2's outlined button glyphs and metadata badges (elf/theme/gfx/*.png).

They replace RiptOPL's built-in icons of the same names at build time (build.sh copies
elf/theme/gfx over the source tree's gfx/), so the hint bar, the drive row and the info page
badges all share the mockups' look: thin light-blue outlines on a faint navy fill, labels in
RIPPS2 Sleek Bold. Everything is drawn 4x and downsampled for clean edges.

    python elf/theme/tools/make_glyphs.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx'))
# labels in RIPPS2 Sleek Bold (make_sleek_font.py): the weight a label needs at glyph size
FONT = os.path.normpath(os.path.join(HERE, '..', 'fonts', 'ripps2_sleek_bold.ttf'))

SS = 4  # supersampling factor
LINE = (178, 198, 248, 240)   # outline
FILL = (6, 14, 44, 150)       # faint navy behind labels, keeps them readable over art
TEXT = (238, 243, 255, 255)   # labels and symbols
SUB = (160, 182, 236, 255)    # small second line on badges


FALLBACK = 'C:/Windows/Fonts/arialbd.ttf'  # only for glyphs the RIPPS2 font draws poorly ('?')


def font(px, text=''):
    if '?' in text and os.path.exists(FALLBACK):
        return ImageFont.truetype(FALLBACK, px * SS)
    return ImageFont.truetype(FONT, px * SS)


def canvas(w, h):
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def save(im, name):
    w, h = im.size
    im.resize((w // SS, h // SS), Image.LANCZOS).save(os.path.join(OUT, name + '.png'))


def centered_text(d, cx, cy, text, px, fill=TEXT, max_w=None):
    f = font(px, text)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    while max_w and (r - l) > max_w * SS and px > 6:  # shrink long labels to fit their pill
        px -= 1
        f = font(px, text)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text((cx * SS - (l + r) / 2, cy * SS - (t + b) / 2), text, font=f, fill=fill)


# One geometry for every glyph, so the families match to the eye: every outline spans y 2..30 (28 px
# tall) with the same stroke, every symbol inside a ring sits in the same 11 px box, the shoulder and
# stick pills share one width, and each family's labels share one size (the largest that fits all).
TOP, BOT = 2, 30
OUTLINE = 2.0
SYM = 2.1                  # symbol stroke
S0, S1 = 10.5, 21.5        # the symbol box inside a ring
PILL_W = 44                # L1 / R1 / L3 / R3
BADGE_W = 64


def outline_box(d, w, radius):
    d.rounded_rectangle((1.5 * SS, TOP * SS, (w - 1.5) * SS, BOT * SS), radius=radius * SS,
                        fill=FILL, outline=LINE, width=round(OUTLINE * SS))


def fit_size(texts, max_w, start=16):
    """The largest label size at which every text fits max_w: one size for a whole family."""
    probe = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    for px in range(start, 5, -1):
        if all((lambda b: b[2] - b[0])(probe.textbbox((0, 0), t, font=font(px, t))) <= max_w * SS for t in texts):
            return px
    return 6


# ---- ring buttons: the face buttons, and START / SELECT as the DualShock 2 draws them ----
def ring(name, draw_symbol):
    im, d = canvas(32, 32)
    d.ellipse((TOP * SS, TOP * SS, BOT * SS, BOT * SS), fill=FILL, outline=LINE, width=round(OUTLINE * SS))
    draw_symbol(d)
    save(im, name)


def sym_cross(d):
    w = round(SYM * SS)
    d.line((S0 * SS, S0 * SS, S1 * SS, S1 * SS), fill=TEXT, width=w)
    d.line((S1 * SS, S0 * SS, S0 * SS, S1 * SS), fill=TEXT, width=w)


def sym_circle(d):
    d.ellipse((S0 * SS, S0 * SS, S1 * SS, S1 * SS), outline=TEXT, width=round(SYM * SS))


def sym_square(d):
    d.rectangle((S0 * SS, S0 * SS, S1 * SS, S1 * SS), outline=TEXT, width=round(SYM * SS))


def sym_triangle(d):
    d.polygon([(16 * SS, (S0 - 0.5) * SS), (S1 * SS, (S1 - 1) * SS), (S0 * SS, (S1 - 1) * SS)], outline=TEXT, width=round(SYM * SS))


def sym_start(d):  # the START button: a small triangle pointing right
    d.polygon([((S0 + 1.5) * SS, S0 * SS), ((S1 + 0.5) * SS, 16 * SS), ((S0 + 1.5) * SS, S1 * SS)], outline=TEXT, width=round(SYM * SS))


def sym_select(d):  # the SELECT button: a short flat bar
    d.rounded_rectangle((S0 * SS, 13.5 * SS, S1 * SS, 18.5 * SS), radius=1.5 * SS, outline=TEXT, width=round(SYM * SS))


# ---- shoulder and stick buttons: a pill with the label ----
def label_pill(name, text, px):
    im, d = canvas(PILL_W, 32)
    outline_box(d, PILL_W, 9)
    centered_text(d, PILL_W / 2, 16.5, text, px)
    save(im, name)


# ---- the loading indicator (load0..load7): a thin glass ring with a bright arc sweeping round it,
# RIPPS2's own rather than RiptOPL's orb-like spinner ----
def loading_frames():
    for k in range(8):
        im, d = canvas(64, 64)
        box = (12 * SS, 12 * SS, 52 * SS, 52 * SS)
        d.ellipse(box, outline=(178, 198, 248, 90), width=round(2 * SS))
        start = -90 + k * 45
        d.arc(box, start - 70, start - 20, fill=(178, 198, 248, 120), width=round(3 * SS))  # the fading tail
        d.arc(box, start - 20, start + 30, fill=TEXT, width=round(4 * SS))                    # the bright head
        save(im, 'load%d' % k)


# ---- the D-pad: Left / Right beside a drive's or a formation's name (Up / Down on Coverflow, where
# the carousel has Left / Right). A plus in the outline style with the pressed arm lit, so it can never
# be read as START's ring and triangle. RIPPSettings hides them by default. ----
DPAD_LO, DPAD_HI = 2.0, 30.0   # the plus's reach
ARM0, ARM1 = 10.0, 22.0        # an arm's width


def dpad(name, arm):
    im, d = canvas(32, 32)
    lo, hi, a0, a1 = DPAD_LO, DPAD_HI, ARM0, ARM1
    plus = [(a0, lo), (a1, lo), (a1, a0), (hi, a0), (hi, a1), (a1, a1), (a1, hi), (a0, hi), (a0, a1), (lo, a1), (lo, a0), (a0, a0)]
    d.polygon([(x * SS, y * SS) for x, y in plus], fill=FILL, outline=LINE, width=round(OUTLINE * SS))
    # the pressed arm, lit out to its outline (so it still reads at 18 px), with an arrowhead pointing out
    e = OUTLINE / 2
    boxes = {'left': (lo - e, a0 - e, a0 + 1, a1 + e), 'right': (a1 - 1, a0 - e, hi + e, a1 + e),
             'up': (a0 - e, lo - e, a1 + e, a0 + 1), 'down': (a0 - e, a1 - 1, a1 + e, hi + e)}
    x0, y0, x1, y1 = boxes[arm]
    d.rounded_rectangle((x0 * SS, y0 * SS, x1 * SS, y1 * SS), radius=1.2 * SS, fill=TEXT)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = 3.0
    tips = {'left': [(cx - k, cy), (cx + k * 0.8, cy - k), (cx + k * 0.8, cy + k)],
            'right': [(cx + k, cy), (cx - k * 0.8, cy - k), (cx - k * 0.8, cy + k)],
            'up': [(cx, cy - k), (cx - k, cy + k * 0.8), (cx + k, cy + k * 0.8)],
            'down': [(cx, cy + k), (cx - k, cy - k * 0.8), (cx + k, cy - k * 0.8)]}
    d.polygon([(x * SS, y * SS) for x, y in tips[arm]], fill=(6, 14, 44, 255))
    save(im, name)


# ---- metadata badges: one label each, all at one size ----
def badge(name, text, px):
    im, d = canvas(BADGE_W, 32)
    outline_box(d, BADGE_W, 7)
    centered_text(d, BADGE_W / 2, 16.5, text, px)
    save(im, name)


# Variants of a value (a patch, GSM or a button combo) show the value alone: the caption was too small
# to read at badge size.
BADGES = {
    'APPS': 'APP', 'ELF': 'ELF', 'HDL': 'HDL', 'ISO': 'ISO', 'ZSO': 'ZSO', 'UL': 'UL',
    'CD': 'CD', 'DVD': 'DVD', 'VCD': 'VCD', 'PS1': 'PS1', 'PS2': 'PS2',
    'Vmode_ntsc': 'NTSC', 'Vmode_pal': 'PAL', 'Vmode_multi': 'MULTI',
    'Aspect_s': '4:3', 'Aspect_w': '16:9', 'Aspect_w1': '16:9', 'Aspect_w2': '16:9',
    'Scan_240p': '240p', 'Scan_240p1': '240p', 'Scan_480i': '480i', 'Scan_480p': '480p',
    'Scan_480p1': '480p', 'Scan_480p2': '480p', 'Scan_480p3': '480p', 'Scan_480p4': '480p', 'Scan_480p5': '480p',
    'Scan_576i': '576i', 'Scan_576p': '576p', 'Scan_720p': '720p',
    'Scan_1080i': '1080i', 'Scan_1080i2': '1080i', 'Scan_1080p': '1080p',
    'missing': '?',
}
PILLS = ('L1', 'R1', 'L3', 'R3')


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, sym in (('cross', sym_cross), ('circle', sym_circle), ('square', sym_square),
                      ('triangle', sym_triangle), ('start', sym_start), ('select', sym_select)):
        ring(name, sym)
    pill_px = fit_size(PILLS, PILL_W - 16)
    for n in PILLS:
        label_pill(n, n, pill_px)
    # the L2 + R2 chord (Random): one wider pill, same height, stroke and label size
    im, d = canvas(72, 32)
    outline_box(d, 72, 9)
    centered_text(d, 36, 16.5, 'L2+R2', pill_px)
    save(im, 'L2R2')
    badge_px = fit_size(set(BADGES.values()), BADGE_W - 12)
    for name, text in BADGES.items():
        badge(name, text, badge_px)
    for name, arm in (('left', 'left'), ('right', 'right'), ('ripps2_up', 'up'), ('ripps2_down', 'down')):
        dpad(name, arm)
    loading_frames()
    print('wrote', 6 + len(PILLS) + len(BADGES) + 4 + 8, 'images to', OUT, '(pill labels %dpx, badge labels %dpx)' % (pill_px, badge_px))


if __name__ == '__main__':
    main()
