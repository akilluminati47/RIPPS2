"""ripps2BibleSky in Python: the sky triplet of a Color Theme (src/ripps2ui.c), and the lab cards for the stills."""
import math, os
SKY = ((0x01, 0x02, 0x09), (0x0B, 0x19, 0x4C), (0x02, 0x04, 0x10))
L = (0.213, 0.715, 0.072)


def matrix(hue, sat):
    r = hue * 3.14159265 / 180
    c, s = math.cos(r), math.sin(r)
    h = (0.213 + c * 0.787 - s * 0.213, 0.715 - c * 0.715 - s * 0.715, 0.072 - c * 0.072 + s * 0.928,
         0.213 - c * 0.213 + s * 0.143, 0.715 + c * 0.285 + s * 0.140, 0.072 - c * 0.072 - s * 0.283,
         0.213 - c * 0.213 - s * 0.787, 0.715 - c * 0.715 + s * 0.715, 0.072 + c * 0.928 + s * 0.072)
    m = [0.0] * 9
    for i in range(3):
        for j in range(3):
            m[i * 3 + j] = sum(((sat if i == k else 0.0) + L[k] * (1.0 - sat)) * h[k * 3 + j] for k in range(3))
    return m


def tint(hue, sat, lift):
    if hue == 0 and sat == 1 and lift == 0:
        return ','.join('%02X%02X%02X' % s for s in SKY)
    m = matrix(hue, sat)
    out = []
    for px in SKY:
        d = max(px) - min(px)
        o = [min(255.0, max(0.0, m[i * 3] * px[0] + m[i * 3 + 1] * px[1] + m[i * 3 + 2] * px[2] + lift * d)) for i in range(3)]
        out.append('%02X%02X%02X' % tuple(int(v + 0.5) for v in o))
    return ','.join(out)


THEMES = {'blood': (130.0, 1.8, 0.0), 'ectoplasm': (250.0, 1.2, 0.0), 'ripps2': (0.0, 1.0, 0.0)}
R = r'C:\Users\MINIPC~1\AppData\Local\Temp\claude\382675e3eda1ee02\b7d6b691-8b5a-49a2-aed2-50b5989d4fe8\scratchpad\race'
for name, t in THEMES.items():
    sky = tint(*t)
    print(name, sky)
    auto = '$CREDITS' if name == 'ripps2' else '$OSDSYS'
    d = os.path.join(R, 'still_' + name, 'SYS-CONF')
    os.makedirs(d, exist_ok=True)
    ini = ['KEY_READ_WAIT_TIME = 9000', 'OSDHISTORY_READ = 0', 'EJECT_TRAY = 0', 'LOGO_DISPLAY = 2', 'BIBLE_GLYPHS = 1', 'BIBLE_INFO = 0',
           'VIDEO_MODE = 1080I', 'BIBLE_WIDESCREEN = AUTO', 'BIBLE_BACKGROUND = SKY', 'BIBLE_COLOR = ' + sky, 'NAME_AUTO = Credits',
           'LK_AUTO_E1 = ' + auto, 'NAME_SQUARE = Credits', 'LK_SQUARE_E1 = $CREDITS', '']
    if name == 'ripps2':
        ini[0] = 'KEY_READ_WAIT_TIME = 0'
    open(os.path.join(d, 'PS2BBL.INI'), 'w', newline='').write('\r\n'.join(ini))
