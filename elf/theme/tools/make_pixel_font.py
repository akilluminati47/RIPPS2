"""Builds RIPPS2's pixel font atlas (build 92): elf/theme/gfx/ripps2_pixfont.png, the in-game menu's own 5x7
font (ee_core/src/igrmenu.c, igrmFont: ASCII 32..95) as a texture, so the front end can write in it too (the
Grid's coverless cases show a game's serial in it). 64 glyphs in 6 x 8 cells, 16 a row: 96 x 32, white on
clear, an 8-bit palette PNG. Drawn unfiltered, it stays sharp at any whole scale.

    python elf/theme/tools/make_pixel_font.py <RiptOPL tree>    (reads ee_core/src/igrmenu.c there)
"""
import os
import re
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx', 'ripps2_pixfont.png'))
sys.path.insert(0, HERE)
import png8  # noqa: E402


def main():
    src = open(os.path.join(sys.argv[1], 'ee_core', 'src', 'igrmenu.c'), encoding='utf-8').read()
    table = src[src.index('igrmFont[67][7] = {'):]
    rows = re.findall(r'\{((?:\s*0x[0-9a-fA-F]{2}\s*,?){7})\}', table)[:64]
    assert len(rows) == 64, len(rows)
    im = Image.new('RGBA', (96, 32), (0, 0, 0, 0))
    for g, row in enumerate(rows):
        bits = [int(b, 16) for b in re.findall(r'0x[0-9a-fA-F]{2}', row)]
        ox, oy = (g % 16) * 6, (g // 16) * 8
        for y, b in enumerate(bits):
            for x in range(5):
                if b & (0x10 >> x): # bit 4 is the left column
                    im.putpixel((ox + x, oy + y), (255, 255, 255, 255))
    im.save(OUT)
    png8.convert(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
