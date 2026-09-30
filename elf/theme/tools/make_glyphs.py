"""Generates RIPPS2's outlined button glyphs and metadata badges (elf/theme/gfx/*.png).

They replace RiptOPL's built-in icons of the same names at build time (build.sh copies
elf/theme/gfx over the source tree's gfx/), so the hint bar, the drive row and the info page
badges all share the mockups' look: thin light-blue outlines on a faint navy fill, labels in
the RIPPS2 font. Everything is drawn 4x and downsampled for clean edges.

    python elf/theme/tools/make_glyphs.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx'))
FONT = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'assets', 'master.ttf'))

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


def pill(d, w, h, radius, stroke=2.0, inset=1.5):
    s, i = stroke * SS, inset * SS
    d.rounded_rectangle((i, i, w * SS - i, h * SS - i), radius=radius * SS, fill=FILL, outline=LINE, width=round(s))


# ---- face buttons: a ring with the symbol inside ----
def face(name, draw_symbol):
    im, d = canvas(32, 32)
    d.ellipse((2 * SS, 2 * SS, 30 * SS, 30 * SS), fill=FILL, outline=LINE, width=2 * SS)
    draw_symbol(d)
    save(im, name)


def sym_cross(d):
    w = round(2.2 * SS)
    d.line((11 * SS, 11 * SS, 21 * SS, 21 * SS), fill=TEXT, width=w)
    d.line((21 * SS, 11 * SS, 11 * SS, 21 * SS), fill=TEXT, width=w)


def sym_circle(d):
    d.ellipse((10.5 * SS, 10.5 * SS, 21.5 * SS, 21.5 * SS), outline=TEXT, width=round(2.2 * SS))


def sym_square(d):
    d.rectangle((11 * SS, 11 * SS, 21 * SS, 21 * SS), outline=TEXT, width=round(2.2 * SS))


def sym_triangle(d):
    pts = [(16 * SS, 9.5 * SS), (22.5 * SS, 20.5 * SS), (9.5 * SS, 20.5 * SS)]
    d.polygon(pts, outline=TEXT, width=round(2.2 * SS))


# ---- shoulder / system buttons: a pill with the label ----
def label_pill(name, text, w, px):
    im, d = canvas(w, 32)
    pill(d, w, 32, 10)
    centered_text(d, w / 2, 16.5, text, px, max_w=w - 14)
    save(im, name)


def blank(name):
    # The drive name's prev/next arrows: the L1/R1 pills beside it already say that, so these
    # are drawn fully transparent (the MenuText element is their only user).
    im, _ = canvas(32, 32)
    save(im, name)


# ---- metadata badges (64x32): a label, optionally with a caption or button symbols ----
def badge(name, text, sub=None, symbols=None):
    im, d = canvas(64, 32)
    pill(d, 64, 32, 7)
    if sub is None and symbols is None:
        centered_text(d, 32, 16.5, text, 15, max_w=52)
    else:
        centered_text(d, 32, 12, text, 13, max_w=52)
        if sub:
            centered_text(d, 32, 24.5, sub, 7, SUB, max_w=52)
        if symbols:
            for k, s in enumerate(symbols):
                cx, cy, r = 27 + 10 * k, 24.5, 3.4
                box = ((cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS)
                if s == 'triangle':
                    d.polygon([(cx * SS, (cy - r) * SS), ((cx + r) * SS, (cy + r * 0.8) * SS), ((cx - r) * SS, (cy + r * 0.8) * SS)], outline=SUB, width=SS)
                elif s == 'circle':
                    d.ellipse(box, outline=SUB, width=SS)
                elif s == 'cross':
                    d.line((box[0], box[1], box[2], box[3]), fill=SUB, width=SS)
                    d.line((box[2], box[1], box[0], box[3]), fill=SUB, width=SS)
    save(im, name)


BADGES = {
    'APPS': ('APP',), 'ELF': ('ELF',), 'HDL': ('HDL',), 'ISO': ('ISO',), 'ZSO': ('ZSO',), 'UL': ('UL',),
    'CD': ('CD',), 'DVD': ('DVD',), 'VCD': ('VCD',), 'PS1': ('PS1',), 'PS2': ('PS2',),
    'Vmode_ntsc': ('NTSC',), 'Vmode_pal': ('PAL',), 'Vmode_multi': ('MULTI',),
    'Aspect_s': ('4:3',), 'Aspect_w': ('16:9',), 'Aspect_w1': ('16:9', 'PS2RD'), 'Aspect_w2': ('16:9', 'HEX ISO'),
    'Scan_240p': ('240p',), 'Scan_240p1': ('240p', 'HEX ISO'), 'Scan_480i': ('480i',), 'Scan_480p': ('480p',),
    'Scan_480p1': ('480p', None, ('triangle', 'cross')), 'Scan_480p2': ('480p', None, ('circle', 'cross')),
    'Scan_480p3': ('480p', 'GSM'), 'Scan_480p4': ('480p', 'PS2RD'), 'Scan_480p5': ('480p', 'HEX ISO'),
    'Scan_576i': ('576i',), 'Scan_576p': ('576p', 'GSM'), 'Scan_720p': ('720p', 'GSM'),
    'Scan_1080i': ('1080i',), 'Scan_1080i2': ('1080i', 'GSM'), 'Scan_1080p': ('1080p', 'GSM'),
    'missing': ('?',),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    face('cross', sym_cross)
    face('circle', sym_circle)
    face('square', sym_square)
    face('triangle', sym_triangle)
    label_pill('select', 'SELECT', 76, 12)
    label_pill('start', 'START', 68, 12)
    for n in ('L1', 'R1', 'L3', 'R3'):
        label_pill(n, n, 48, 15)
    blank('left')
    blank('right')
    for name, spec in BADGES.items():
        badge(name, *spec)
    print('wrote', 16 + len(BADGES), 'images to', OUT)


if __name__ == '__main__':
    main()
