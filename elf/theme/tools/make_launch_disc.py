"""Draws RIPPS2's launch disc (build 91): elf/theme/gfx/ripps2_disc.png, the disc that pops in (or spins
up) in the middle of the screen as a game launches, when a theme sets launch_disc=pop|spin and the game
has no disc art (ICO) of its own. A theme can ship its own as launch_disc.png.

A dark blue DVD face with a rainbow sheen in two uneven sweeps (so a spin reads as a spin), a clear
centre hole, a silver hub and a bright outer rim. Drawn 4x and downsampled, then made an 8-bit palette
PNG (png8).

    python elf/theme/tools/make_launch_disc.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', 'gfx', 'ripps2_disc.png'))
sys.path.insert(0, HERE)
import png8  # noqa: E402

N, SS = 128, 4


def main():
    n = N * SS
    y, x = np.mgrid[0:n, 0:n].astype(np.float64)
    c = (n - 1) / 2.0
    dx, dy = x - c, y - c
    r = np.hypot(dx, dy) / (n / 2.0)  # 0 at the centre, 1 at the edge
    a = np.arctan2(dy, dx)

    # the face: deep blue, a touch lighter outwards
    rgb = np.zeros((n, n, 3))
    rgb[..., 0] = 10 + 14 * r
    rgb[..., 1] = 18 + 26 * r
    rgb[..., 2] = 52 + 60 * r
    # the sheen: two sweeps of different width and strength, coloured round the hue wheel by angle
    sweep = 0.85 * np.maximum(0, np.cos(a - 0.6)) ** 6 + 0.45 * np.maximum(0, np.cos(a - 3.9)) ** 14
    sweep *= np.clip((r - 0.30) / 0.15, 0, 1)
    hue = (a / (2 * math.pi) * 3.0 + r * 0.8) % 1.0
    rain = np.stack([0.5 + 0.5 * np.cos(2 * math.pi * (hue - k / 3.0)) for k in range(3)], -1)
    rgb += sweep[..., None] * (rain * 150 + 70)
    # fine grooves: a faint ring pattern
    rgb *= (0.94 + 0.06 * np.cos(r * 220))[..., None]
    # the hub: silver ring, then the clear hole
    hub = (r > 0.17) & (r < 0.30)
    shade = 150 + 60 * np.cos(a * 2 + 0.6)
    rgb[hub] = np.stack([shade, shade, shade + 12], -1)[hub]
    alpha = np.where(r <= 1.0, 255.0, 0.0)
    alpha[r < 0.12] = 0.0
    rgb[(r >= 0.12) & (r < 0.17)] = [60, 70, 96]  # the clear plastic round the hole
    alpha[(r >= 0.12) & (r < 0.17)] = 150
    # the outer rim, bright
    rim = (r > 0.955) & (r <= 1.0)
    rgb[rim] = [205, 215, 240]
    img = np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)
    im = Image.fromarray(img, 'RGBA').resize((N, N), Image.LANCZOS)
    im.save(OUT)
    png8.convert(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
