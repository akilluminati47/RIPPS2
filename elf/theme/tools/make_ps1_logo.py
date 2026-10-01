"""Rasterizes the PlayStation logo SVG the user supplied into elf/theme/gfx/ripps2_ps1logo.png, the
mark the PS1 games filter shows (L3) above the word GAMES.

    python make_ps1_logo.py <Playstation_logo_colour.svg> [height]

The SVG is four filled shapes made of absolute M / L / C / z commands inside one translated group,
so a small path flattener plus PIL covers it: drawn at 4x and downsampled for smooth edges, cropped
to the shapes, transparent around them.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx', 'ripps2_ps1logo.png'))
SS = 4  # supersampling


def flatten(d):
    """Polygons (lists of points) for a path's subpaths; cubic curves cut into 16 segments."""
    toks = re.findall(r'[MLCZmlcz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?', d)
    polys, cur, i, cmd = [], [], 0, None
    pos = (0.0, 0.0)
    while i < len(toks):
        t = toks[i]
        if t in 'MLCZmlcz':
            cmd = t
            i += 1
            if cmd in 'Zz':
                if cur:
                    polys.append(cur)
                cur = []
            continue
        if cmd == 'M':
            pos = (float(toks[i]), float(toks[i + 1]))
            i += 2
            if cur:
                polys.append(cur)
            cur = [pos]
            cmd = 'L'
        elif cmd == 'L':
            pos = (float(toks[i]), float(toks[i + 1]))
            i += 2
            cur.append(pos)
        elif cmd == 'C':
            p1 = (float(toks[i]), float(toks[i + 1]))
            p2 = (float(toks[i + 2]), float(toks[i + 3]))
            p3 = (float(toks[i + 4]), float(toks[i + 5]))
            i += 6
            p0 = pos
            for k in range(1, 17):
                s = k / 16.0
                u = 1 - s
                cur.append((u * u * u * p0[0] + 3 * u * u * s * p1[0] + 3 * u * s * s * p2[0] + s * s * s * p3[0],
                            u * u * u * p0[1] + 3 * u * u * s * p1[1] + 3 * u * s * s * p2[1] + s * s * s * p3[1]))
            pos = p3
        else:
            raise ValueError('unsupported path command %r' % cmd)
    if cur:
        polys.append(cur)
    return polys


def main():
    src = sys.argv[1]
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 112
    root = ET.parse(src).getroot()
    ns = '{http://www.w3.org/2000/svg}'
    shapes = []
    for g in root.iter(ns + 'g'):
        tx, ty = 0.0, 0.0
        m = re.match(r'translate\(([-\d.]+)[ ,]+([-\d.]+)\)', g.get('transform', ''))
        if m:
            tx, ty = float(m.group(1)), float(m.group(2))
        for p in g.iter(ns + 'path'):
            fill = re.search(r'fill:(#[0-9a-fA-F]{6})', p.get('style', '')).group(1)
            polys = [[(x + tx, y + ty) for x, y in poly] for poly in flatten(p.get('d'))]
            shapes.append((fill, polys))
    xs = [x for _, polys in shapes for poly in polys for x, _ in poly]
    ys = [y for _, polys in shapes for poly in polys for _, y in poly]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    scale = (height - 2) / (y1 - y0)
    width = int((x1 - x0) * scale) + 2
    big = Image.new('RGBA', (width * SS, height * SS), (0, 0, 0, 0))
    for fill, polys in shapes:
        rgb = tuple(int(fill[k:k + 2], 16) for k in (1, 3, 5))
        layer = Image.new('L', big.size, 0)
        draw = ImageDraw.Draw(layer)
        for poly in polys:
            pts = [((x - x0) * scale * SS + SS, (y - y0) * scale * SS + SS) for x, y in poly]
            draw.polygon(pts, fill=255)
        big.paste(Image.new('RGBA', big.size, rgb + (255,)), (0, 0), layer)
    img = big.resize((width, height), Image.LANCZOS)
    img.save(OUT)
    print('wrote %s %dx%d' % (OUT, width, height))


if __name__ == '__main__':
    main()
