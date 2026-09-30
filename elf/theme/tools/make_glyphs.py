"""Generates RIPPS2's outlined button glyphs and metadata badges (elf/theme/gfx/*.png).

They replace RiptOPL's built-in icons of the same names at build time (build.sh copies
elf/theme/gfx over the source tree's gfx/), so the hint bar, the drive row and the info page
badges all share the mockups' look: thin light-blue outlines on a faint navy fill, labels in
RIPPS2 Sleek. Everything is drawn 4x and downsampled for clean edges.

    python elf/theme/tools/make_glyphs.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx'))
# labels in RIPPS2 Sleek (make_sleek_font.py), the font the hint text beside these glyphs uses
FONT = os.path.normpath(os.path.join(HERE, '..', 'fonts', 'ripps2_sleek.ttf'))

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
    # a touch of stroke: the Sleek letters are one thin line, which would thin out at hint size
    d.text((cx * SS - (l + r) / 2, cy * SS - (t + b) / 2), text, font=f, fill=fill, stroke_width=2, stroke_fill=fill)


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
        if all((lambda b: b[2] - b[0])(probe.textbbox((0, 0), t, font=font(px, t), stroke_width=2)) <= max_w * SS for t in texts):
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


def blank(name):
    # The drive name's prev/next arrows: the L1/R1 pills beside it already say that, so these
    # are drawn fully transparent (the MenuText element is their only user).
    im, _ = canvas(32, 32)
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
    badge_px = fit_size(set(BADGES.values()), BADGE_W - 12)
    for name, text in BADGES.items():
        badge(name, text, badge_px)
    blank('left')
    blank('right')
    print('wrote', 6 + len(PILLS) + len(BADGES) + 2, 'images to', OUT, '(pill labels %dpx, badge labels %dpx)' % (pill_px, badge_px))


if __name__ == '__main__':
    main()
