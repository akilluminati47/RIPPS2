"""akilluminati47's signature, written on by hand over a release clip (the user, 11/03: "write akilluminati47 with this
font like its written by hand animated over the gif we make").

The name is set in Rock Salt and revealed glyph by glyph, left to right, each glyph's time in proportion to its width,
behind a soft slanted pen edge, then held to the end. It is written as a PNG sequence with alpha and laid over the clip
with ffmpeg before the GIF is made, so the GIF keeps one palette for both.

    python tools/dev/signature.py <in.mp4> <out.mp4> [--font RockSalt-Regular.ttf] [--start 0.6] [--write 1.8]
"""
import argparse
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

NAME = 'akilluminati47'
FONT = r'B:\Webpages - Projects\.gears\eday-assets\fonts\RockSalt-Regular.ttf'


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                          '-of', 'csv=p=0', path], capture_output=True, text=True, check=True).stdout.strip().split(',')
    num, den = out[2].split('/')
    return int(out[0]), int(out[1]), float(num) / float(den)


def ink(width, height, font_path):
    """the whole name, white with a dark edge, on a transparent canvas the size of the clip; and each glyph's x span"""
    size = max(18, int(height * 0.075))
    font = ImageFont.truetype(font_path, size)
    pad = 6
    w = int(font.getlength(NAME)) + pad * 4
    bbox = font.getbbox(NAME)
    h = bbox[3] + pad * 4
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((pad * 2, pad), NAME, font=font, fill=(255, 255, 255, 255), stroke_width=max(2, size // 14), stroke_fill=(10, 10, 14, 230))
    shadow = layer.split()[3].filter(ImageFilter.GaussianBlur(3)).point(lambda a: a * 0.55)
    under = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    under.putalpha(shadow)
    sign = Image.alpha_composite(under, layer)
    spans, x = [], pad * 2
    for i in range(len(NAME)):
        x1 = pad * 2 + font.getlength(NAME[:i + 1])
        spans.append((x, x1))
        x = x1
    # a hand's slant: a few degrees up to the right, then set in the lower right corner
    sign = sign.rotate(4, resample=Image.BICUBIC, expand=True)
    return sign, spans, w, h


def reveal_mask(size, spans, frac, src_w, src_h):
    """the written part of the name at frac (0..1): glyphs left to right, each in time with its width, a soft slanted edge"""
    total = spans[-1][1] - spans[0][0]
    edge = spans[0][0] + frac * total
    m = Image.new('L', (src_w, src_h), 0)
    d = ImageDraw.Draw(m)
    slant = src_h * 0.35
    d.polygon([(0, 0), (edge + slant, 0), (edge - slant, src_h), (0, src_h)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(2.5))
    return m.rotate(4, resample=Image.BICUBIC, expand=True).resize(size)


def frames(width, height, fps, start, write, length, font_path, folder):
    sign, spans, sw, sh = ink(width, height, font_path)
    margin = int(width * 0.03)
    # above the menu's button hints along the bottom
    pos = (width - sign.width - margin, height - sign.height - int(height * 0.12))
    n = int(round(length * fps))
    blank = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for i in range(n):
        t = i / fps
        frac = 0.0 if t < start else min(1.0, (t - start) / write)
        # ease out: the hand slows at the end of the name
        frac = 1 - (1 - frac) ** 1.6 if frac < 1 else 1.0
        frame = blank.copy()
        if frac > 0:
            part = sign.copy()
            a = ImageChops.multiply(part.split()[3], reveal_mask(sign.size, spans, frac, sw, sh))
            part.putalpha(a)
            frame.alpha_composite(part, pos)
        frame.save(os.path.join(folder, 'sig%05d.png' % i))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--font', default=FONT)
    ap.add_argument('--start', type=float, default=0.6)
    ap.add_argument('--write', type=float, default=1.8)
    a = ap.parse_args()
    width, height, fps = probe(a.src)
    length = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', a.src],
                                  capture_output=True, text=True, check=True).stdout.strip())
    folder = tempfile.mkdtemp(prefix='sig')
    try:
        frames(width, height, fps, a.start, a.write, length, a.font, folder)
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', a.src, '-framerate', '%g' % fps, '-i', os.path.join(folder, 'sig%05d.png'),
               '-filter_complex', '[0:v][1:v]overlay=0:0:eof_action=repeat:format=auto,format=yuv420p[v]', '-map', '[v]']
        cmd += ['-map', '0:a?', '-c:a', 'copy', '-c:v', 'libx264', '-crf', '20', a.dst]
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    print('signed', a.dst)


if __name__ == '__main__':
    main()
