"""BIBLE's Power-on Wait race: 6000 ms (info line on) beside 0 ms, both from BIBLE's first frame, 8 s, same black cut."""
import bisect, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

D = r'B:\Emulation\PlayStation\PCSX2\ripps2-test\race_frames'
OUT = r'C:\Users\MINIPC~1\AppData\Local\Temp\claude\382675e3eda1ee02\b7d6b691-8b5a-49a2-aed2-50b5989d4fe8\scratchpad\race\out'
GIF = r'B:\Webpages - Projects\ps2-pillars\media\b139\bible-race-6000-vs-0.gif'
FONT = r'B:\Webpages - Projects\ps2-pillars\elf\theme\fonts\ripps2_sleek_bold.ttf'
BOX = (8, 52, 1292, 1026)
W, H = 480, 364
BAND, GAP = 34, 6
FPS, LEN, CUT = 20, 8.0, 6.5
RUNS = (('w6000', 631, 7.0, 'Power-on Wait: 6000 ms'), ('w0d', 612, 0.7, 'Power-on Wait: 0 ms'))

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
index = {}
for run, *_ in RUNS:
    index[run] = sorted(int(f[1:7]) for f in os.listdir(os.path.join(D, run)) if f.endswith('.bmp'))
font = ImageFont.truetype(FONT, 21)


def frame(run, logo, cutat, t):
    s = t if t < cutat else t + CUT
    want = logo + int(s * 1000)
    ms = index[run]
    i = min(bisect.bisect_right(ms, want) - 1, len(ms) - 1)
    im = Image.open(os.path.join(D, run, 'f%06d.bmp' % ms[max(i, 0)])).convert('RGB').crop(BOX)
    # PCSX2's own 'Memory Card saved' popup, top left, painted out with the same rows further along (the sky is level)
    im.paste(im.crop((370, 0, 730, 46)), (0, 0))
    return im.resize((W, H), Image.LANCZOS)


n = int(FPS * LEN)
for k in range(n):
    t = k / FPS
    im = Image.new('RGB', (W * 2 + GAP, H + BAND), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for j, (run, logo, cutat, label) in enumerate(RUNS):
        x = j * (W + GAP)
        im.paste(frame(run, logo, cutat, t), (x, 0))
        tw = d.textlength(label, font=font)
        d.text((x + (W - tw) / 2, H + 6), label, font=font, fill=(150, 190, 255))
    d.rectangle((W, 0, W + GAP - 1, H + BAND), fill=(26, 40, 80))
    im.save(os.path.join(OUT, '%04d.png' % k))
print(n, 'frames')
pal = os.path.join(OUT, 'pal.png')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(OUT, '%04d.png'), '-vf', 'palettegen=stats_mode=diff:max_colors=200', pal], check=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS), '-i', os.path.join(OUT, '%04d.png'), '-i', pal, '-lavfi', 'paletteuse=dither=sierra2_4a:diff_mode=rectangle', '-loop', '0', GIF], check=True)
print(os.path.getsize(GIF) // 1024, 'KB')
