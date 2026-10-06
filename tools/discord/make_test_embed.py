"""RIPPS2 "Test me" posts for the testers' Discord.

Builds, for build N:
  test-me-N.png    the banner: "Test me | Build N" in RIPPS2 Sleek over the pillars, with the RIPPS2 mark
  ripps2-icon.png  the RIPPS2 mark (the dead elf: an elf's blue hat in a pool of blood), as the post's author icon
  post-N.json      the webhook payload: the banner first, then what is new and what to test

    python make_test_embed.py --build 70 --notes notes.md [--release URL] [--attach FILE ...] [--out DIR] [--post]

--attach adds files to the post as downloads (build 73: RIPPS2.elf itself, so testers get the build
from the post).

notes.md holds the post's words:
    # <one-line pitch>
    ## <section title>            (a section of what is new: up to 6)
    - <bullet>
    ## Test list                  (the numbered list of what testers should try on real hardware)
    - <one test per bullet>
    ## Report                     (how to report)
    <text>

--post sends it to the webhook named by the RIPPS2_DISCORD_WEBHOOK environment variable. The URL is a
credential: it is never written to a file here, and this script never prints it.
"""
import argparse
import json
import math
import os
import random
import sys
import urllib.request
import uuid

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', '..', 'elf', 'theme', 'fonts')
BLUE = 0x3C6EF0  # the embed's side bar: RIPPS2 blue


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


# The RIPPS2 mark: the dead elf in its blue hat (media/deadelf, rendered by media/deadelf/scene.html)
MARK = os.path.join(HERE, '..', '..', 'media', 'deadelf', 'ripps2-deadelf-bluehat.png')


def icon(size=256):
    """The RIPPS2 mark: the dead elf (assets/ripps2-deadelf.png, rendered in three.js by
    media/deadelf/scene.html), on a dark rounded tile so it reads on Discord's light and dark themes."""
    mark = Image.open(MARK).convert('RGBA')
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.18), fill=(10, 6, 12, 255))
    inner = int(size * 0.92)
    im.alpha_composite(mark.resize((inner, inner), Image.LANCZOS), ((size - inner) // 2, (size - inner) // 2))
    return im


def mark(box):
    """The dead elf alone, with its own transparency, trimmed to what it draws and fitted into a
    box x box square: the banner puts it straight onto the night sky, no tile behind it. Scaled
    premultiplied, so the edges keep their colour instead of a dark fringe."""
    m = Image.open(MARK).convert('RGBA')
    m = m.crop(m.getchannel('A').getbbox())
    k = box / max(m.size)
    m = m.convert('RGBa').resize((max(1, round(m.width * k)), max(1, round(m.height * k))), Image.LANCZOS).convert('RGBA')
    out = Image.new('RGBA', (box, box), (0, 0, 0, 0))
    out.alpha_composite(m, ((box - m.width) // 2, (box - m.height) // 2))
    return out


def banner(build, w=1280, h=480):
    """Dark PS2 night, the pillars field low in the frame, and the words."""
    im = Image.new('RGB', (w, h), (2, 6, 20))
    px = im.load()
    for y in range(h):  # the sky: deep at the top, a blue haze at the horizon
        t = y / h
        c = (int(2 + 10 * t ** 2.2), int(5 + 28 * t ** 2.2), int(18 + 90 * t ** 2.4))
        for x in range(w):
            px[x, y] = c
    glow = Image.new('RGB', (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w * 0.18, h * 0.55, w * 0.82, h * 1.25), fill=(20, 60, 160))
    im = Image.blend(im, Image.eval(glow.filter(ImageFilter.GaussianBlur(90)), lambda v: v), 0.45)
    d = ImageDraw.Draw(im, 'RGBA')
    rnd = random.Random(build)
    for _ in range(140):  # stars
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.6)
        a = rnd.randint(40, 160)
        d.point((x, y), fill=(200, 215, 255, a))
    # the pillars: a floor grid to the horizon, then towers in perspective rows (far ones dim), the
    # tallest in the middle like the RIPPS2 field, every top kept below the words
    horizon, cx = h * 0.56, w / 2
    for k in range(-14, 15):  # floor lines running to the vanishing point
        d.line((cx + k * 18, horizon, cx + k * 210, h), fill=(40, 80, 190, 70), width=1)
    for r in range(1, 9):
        y = horizon + (h - horizon) * (r / 8.0) ** 1.8
        d.line((0, y, w, y), fill=(40, 80, 190, 60), width=1)
    towers = []
    for row in range(7):
        z = 1.0 + row * 0.6
        for col in range(-12, 13):
            hgt = (0.45 + rnd.random() * 0.55) * (0.25 + 0.75 * math.exp(-(col * col) / 30.0))
            towers.append((z, col, hgt))
    towers.sort(key=lambda t: -t[0])
    for z, col, hgt in towers:
        sc = 120 / z
        x = cx + col * sc * 0.95
        base = horizon + 140 / z - 20
        tw = sc * 0.6
        top = max(h * 0.44, base - hgt * sc * 1.55)
        fade = max(0.25, 1.15 - z * 0.22)
        edge = (int(70 * fade + 20), int(120 * fade + 20), int(235 * fade + 20), int(255 * fade))
        d.rectangle((x - tw / 2, top, x + tw / 2, base), fill=(12, 30, 90, int(215 * fade)))
        d.rectangle((x - tw / 2, top, x + tw / 2, base), outline=edge, width=2 if z < 2 else 1)
        for f in (0.33, 0.66):
            yy = top + (base - top) * f
            d.line((x - tw / 2, yy, x + tw / 2, yy), fill=(70, 120, 235, int(90 * fade)), width=1)
        d.rectangle((x - tw / 2, top, x + tw / 2, top + 3), fill=(170, 205, 255, int(255 * fade)))
    # a dark band behind the words so they read on any phone
    shade = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, w, h * 0.5), fill=(1, 4, 14, 150))
    im = Image.alpha_composite(im.convert('RGBA'), shade.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(im)
    im.alpha_composite(mark(140), (66, 56))
    big = font('ripps2_sleek_case.ttf', 104)
    small = font('ripps2_sleek_case.ttf', 40)
    title = 'Test me'
    d.text((232, 58), title, font=big, fill=(245, 248, 255))
    tw = d.textlength(title, font=big)
    d.text((232 + tw + 34, 58), '|', font=big, fill=(90, 140, 255))
    d.text((232 + tw + 34 + d.textlength('|', font=big) + 34, 58), 'Build %d' % build, font=big, fill=(160, 195, 255))
    d.text((236, 178), 'RIPPS2 alpha  /  real PS2 hardware wanted', font=small, fill=(150, 165, 205))
    return im.convert('RGB')


def parse_notes(path):
    pitch, sections, cur = '', [], None
    for raw in open(path, encoding='utf-8').read().splitlines():
        line = raw.rstrip()
        if line.startswith('# '):
            pitch = line[2:].strip()
        elif line.startswith('## '):
            cur = [line[3:].strip(), []]
            sections.append(cur)
        elif cur is not None and line.strip():
            cur[1].append(line.strip())
    return pitch, sections


def payload(build, notes, release):
    pitch, sections = parse_notes(notes)
    news, tests, report = [], [], ''
    for title, lines in sections:
        if title.lower() == 'test list':
            tests = [l[2:] if l.startswith('- ') else l for l in lines]
        elif title.lower() == 'report':
            report = '\n'.join(lines)
        else:
            news.append((title, lines))
    head = {
        'color': BLUE,
        'author': {'name': 'RIPPS2', 'icon_url': 'attachment://ripps2-icon.png'},
        'title': 'Test me | Build %d' % build,
        'description': pitch + ('\n\n**Kill it:** %s\nThe ELF killer, but ELF-sufficient, never ELF-destructive: your other ELFs stay safe on the [shelf](https://akilluminati47.github.io/RIPPS2/).' % release
                                if release else ''),
        'image': {'url': 'attachment://test-me-%d.png' % build},
    }
    if release:
        head['url'] = release
    body = {'color': BLUE, 'fields': []}
    for title, lines in news[:6]:
        body['fields'].append({'name': title, 'value': '\n'.join(lines)[:1024], 'inline': False})
    # the test list as numbered lines, split across fields of up to 1024 characters
    chunk, start, n = '', 1, 1
    for t in tests:
        line = '`%2d` %s\n' % (n, t)
        if len(chunk) + len(line) > 1000:
            body['fields'].append({'name': 'What to test on your PS2 (%d to %d)' % (start, n - 1), 'value': chunk, 'inline': False})
            chunk, start = '', n
        chunk += line
        n += 1
    if chunk:
        body['fields'].append({'name': 'What to test on your PS2' + (' (%d to %d)' % (start, n - 1) if start > 1 else ''), 'value': chunk, 'inline': False})
    if report:
        body['fields'].append({'name': 'Tell us', 'value': report[:1024], 'inline': False})
    body['footer'] = {'text': 'RIPPS2 build %d  |  alpha: keep your usual loader close by' % build, 'icon_url': 'attachment://ripps2-icon.png'}
    return {'content': '', 'embeds': [head, body], 'allowed_mentions': {'parse': []},
            'attachments': [{'id': 0, 'filename': 'test-me-%d.png' % build}, {'id': 1, 'filename': 'ripps2-icon.png'}]}


def post(data, files, extra=()):
    url = os.environ.get('RIPPS2_DISCORD_WEBHOOK', '')
    if not url.startswith('https://discord.com/api/webhooks/'):
        sys.exit('RIPPS2_DISCORD_WEBHOOK is not set to a Discord webhook URL')
    boundary = uuid.uuid4().hex
    parts = [('--%s\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n' % boundary).encode() +
             json.dumps(data).encode() + b'\r\n']
    for i, path in enumerate(list(files) + list(extra)):
        kind = 'image/png' if i < len(files) else 'application/octet-stream'
        parts.append(('--%s\r\nContent-Disposition: form-data; name="files[%d]"; filename="%s"\r\nContent-Type: %s\r\n\r\n'
                      % (boundary, i, os.path.basename(path), kind)).encode() + open(path, 'rb').read() + b'\r\n')
    parts.append(('--%s--\r\n' % boundary).encode())
    req = urllib.request.Request(url + '?wait=true', data=b''.join(parts), method='POST',
                                 headers={'Content-Type': 'multipart/form-data; boundary=%s' % boundary, 'User-Agent': 'RIPPS2-test-post'})
    with urllib.request.urlopen(req) as r:
        msg = json.loads(r.read().decode())
    print('posted, message id', msg.get('id'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', type=int, required=True)
    ap.add_argument('--notes', required=True)
    ap.add_argument('--release', default='')
    ap.add_argument('--out', default='.')
    ap.add_argument('--post', action='store_true')
    ap.add_argument('--attach', action='append', default=[])
    ap.add_argument('--readme', action='store_true', help="also write the banner to media/ripps2-test-me.png (the README's header)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bn, ic = os.path.join(a.out, 'test-me-%d.png' % a.build), os.path.join(a.out, 'ripps2-icon.png')
    banner(a.build).save(bn, optimize=True)
    if a.readme:
        banner(a.build).save(os.path.join(HERE, '..', '..', 'media', 'ripps2-test-me.png'), optimize=True)
    icon().save(ic, optimize=True)
    data = payload(a.build, a.notes, a.release)
    jp = os.path.join(a.out, 'post-%d.json' % a.build)
    json.dump(data, open(jp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    size = sum(len(json.dumps(e)) for e in data['embeds'])
    print(bn, ic, jp, 'embed text about %d of 6000 characters' % size)
    for f in a.attach:
        data['attachments'].append({'id': len(data['attachments']), 'filename': os.path.basename(f)})
    if a.post:
        post(data, [bn, ic], a.attach)


if __name__ == '__main__':
    main()
