"""The category bar's PS2 mark (gfx/ripps2_mark.png), from the PlayStation 2 logo SVG the user supplied.

    python make_category_mark.py "<PlayStation_2_logo.svg>" [width] [weight] [lift]

The SVG's mark is drawn in thin bands, which at bar size (about 96 px across) come out barely a pixel
thick. So the three polygons are drawn large, their strokes thickened by `weight` (a fraction of the
mark's width, default 0.011), filled with the SVG's own gradient lifted toward white by `lift`
(default 0.35) so it reads on the dark sky, and only then reduced. Then run make_mark_glow.py.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx', 'ripps2_mark.png'))
SS = 12
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
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    weight = float(sys.argv[3]) if len(sys.argv) > 3 else 0.011
    lift = float(sys.argv[4]) if len(sys.argv) > 4 else 0.35
    out = sys.argv[5] if len(sys.argv) > 5 else OUT
    root = ET.parse(src).getroot()
    style = ''.join(s.text or '' for s in root.iter(NS + 'style'))
    cls_grad = dict(re.findall(r'\.(cls-\d)\s*\{\s*fill:\s*url\(#([\w-]+)\)', style))
    grads = {}
    for g in root.iter(NS + 'linearGradient'):
        stops = [(float(s.get('offset')), tuple(int(round(c + (255 - c) * lift)) for c in hex_rgb(s.get('stop-color'))))
                 for s in g.iter(NS + 'stop')]
        grads[g.get('id')] = (float(g.get('y1', '0')), float(g.get('y2', '0')), stops)
    shapes = []
    for poly in root.iter(NS + 'polygon'):
        grad = cls_grad.get(poly.get('class'))
        if grad is None:
            continue  # the TM beside the mark has no gradient: left out
        nums = [float(v) for v in re.findall(r'-?\d*\.?\d+', poly.get('points'))]
        shapes.append((grads[grad], list(zip(nums[0::2], nums[1::2]))))

    x0 = min(x for _, pts in shapes for x, _ in pts)
    y0 = min(y for _, pts in shapes for _, y in pts)
    x1 = max(x for _, pts in shapes for x, _ in pts)
    y1 = max(y for _, pts in shapes for _, y in pts)
    grow = weight * width  # px each stroke grows on each side, at final size
    pad = grow + 1.0
    scale = (width - 2 * pad) / (x1 - x0)
    height = int(round((y1 - y0) * scale + 2 * pad))
    W, H = width * SS, height * SS
    big = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for (gy1, gy2, stops), pts in shapes:
        mask = Image.new('L', (W, H), 0)
        ImageDraw.Draw(mask).polygon([((x - x0) * scale * SS + pad * SS, (y - y0) * scale * SS + pad * SS) for x, y in pts], fill=255)
        r = int(round(grow * SS))
        if r > 0:
            mask = mask.filter(ImageFilter.MaxFilter(2 * r + 1))  # thicker strokes, corners kept square
        fill = Image.new('RGBA', (W, H))
        px = fill.load()
        for row in range(H):
            y = (row / SS - pad) / scale + y0
            f = (y - gy1) / (gy2 - gy1) if gy2 != gy1 else 0.0
            c = gradient_at(stops, max(0.0, min(1.0, f))) + (255,)
            for col in range(W):
                px[col, row] = c
        big.paste(fill, (0, 0), mask)
    img = big.resize((width, height), Image.LANCZOS)
    img.save(out, optimize=True)
    print('wrote %s %dx%d' % (out, width, height))


if __name__ == '__main__':
    main()
