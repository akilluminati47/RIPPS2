"""Rasterizes the PS2 mark from the PlayStation 2 logo SVG the user supplied into
elf/theme/gfx/ripps2_ps2logo.png, the mark the PS2 games filter shows (L3) above the word GAMES.

    python make_ps2_logo.py "<PlayStation_2_logo.svg>" [width]

Only the three gradient polygons that draw the mark are used (group g3, classes cls-1..cls-3); the
wordmark under it and the TM beside it are left out. Each polygon is filled with its own vertical
linear gradient (userSpaceOnUse, y1 at the bottom), drawn at 4x and downsampled.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx', 'ripps2_ps2logo.png'))
SS = 4
NS = '{http://www.w3.org/2000/svg}'


def hex_rgb(h):
    return tuple(int(h[k:k + 2], 16) for k in (1, 3, 5))


def gradient_at(stops, f):
    if f <= stops[0][0]:
        return stops[0][1]
    for (o0, c0), (o1, c1) in zip(stops, stops[1:]):
        if f <= o1:
            t = 0.0 if o1 == o0 else (f - o0) / (o1 - o0)
            return tuple(int(round(a + (b - a) * t)) for a, b in zip(c0, c1))
    return stops[-1][1]


def main():
    src = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 384
    root = ET.parse(src).getroot()
    style = ''.join(s.text or '' for s in root.iter(NS + 'style'))
    cls_grad = dict(re.findall(r'\.(cls-\d)\s*\{\s*fill:\s*url\(#([\w-]+)\)', style))
    grads = {}
    for g in root.iter(NS + 'linearGradient'):
        y1 = float(g.get('y1', '0'))
        y2 = float(g.get('y2', '0'))
        stops = [(float(s.get('offset')), hex_rgb(s.get('stop-color'))) for s in g.iter(NS + 'stop')]
        grads[g.get('id')] = (y1, y2, stops)

    shapes = []
    for poly in root.iter(NS + 'polygon'):
        grad = cls_grad.get(poly.get('class'))
        if grad is None:
            continue  # the TM mark has no gradient: left out
        nums = [float(v) for v in re.findall(r'-?\d*\.?\d+', poly.get('points'))]
        shapes.append((grads[grad], list(zip(nums[0::2], nums[1::2]))))

    x0 = min(x for _, pts in shapes for x, _ in pts)
    y0 = min(y for _, pts in shapes for _, y in pts)
    x1 = max(x for _, pts in shapes for x, _ in pts)
    y1 = max(y for _, pts in shapes for _, y in pts)
    scale = (width - 2) / (x1 - x0)
    height = int((y1 - y0) * scale) + 2
    big = Image.new('RGBA', (width * SS, height * SS), (0, 0, 0, 0))
    for (gy1, gy2, stops), pts in shapes:
        mask = Image.new('L', big.size, 0)
        ImageDraw.Draw(mask).polygon([((x - x0) * scale * SS + SS, (y - y0) * scale * SS + SS) for x, y in pts], fill=255)
        fill = Image.new('RGBA', big.size)
        px = fill.load()
        for row in range(big.size[1]):
            y = (row - SS) / (scale * SS) + y0
            f = (y - gy1) / (gy2 - gy1) if gy2 != gy1 else 0.0
            c = gradient_at(stops, max(0.0, min(1.0, f))) + (255,)
            for col in range(big.size[0]):
                px[col, row] = c
        big.paste(fill, (0, 0), mask)
    img = big.resize((width, height), Image.LANCZOS)
    img.save(OUT)
    print('wrote %s %dx%d' % (OUT, width, height))


if __name__ == '__main__':
    main()
