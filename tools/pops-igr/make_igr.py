"""POPSTARTER's in-game reset pictures (POPS/IGR_BG.TM2, IGR_YES.TM2, IGR_NO.TM2) in RIPPS2's in-game menu look.

igrpops.c draws the pages with RIPPS2's own in-game menu renderer (RiptOPL ee_core/src/igrmenu.c, its font and colours,
at scale 2); this lays the panel over black at 400 x 260 with YES and NO where POPSTARTER puts its buttons (115, 195 and
213, 195, 74 x 34) and writes 24-bit TIM2 files the size of POPSTARTER's own.

    python make_igr.py <RiptOPL clone> <out folder>     (needs gcc, Pillow)
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SEP, BORDER = (36, 46, 88), (72, 96, 168)
YES_AT, NO_AT, PANEL_AT = (115, 195), (213, 195), (41, 5)


def tim2(im):
    """One picture, 24-bit, no CLUT, one mip level: POPSTARTER's own files' layout"""
    w, h = im.size
    px = im.convert('RGB').tobytes()
    head = struct.pack('<4sBBH8x', b'TIM2', 4, 0, 1)
    pic = struct.pack('<IIIHHBBBBHH', 48 + ((len(px) + 15) & ~15), 0, (len(px) + 15) & ~15, 48, 0, 0, 1, 0, 2, w, h)
    tw, th = (w - 1).bit_length(), (h - 1).bit_length()
    pic += struct.pack('<QQII', 1 << 20 | tw << 26 | th << 30, 0x260, 0, 0)  # GsTex0 (CT24, its size), GsTex1, as POPSTARTER's
    return head + pic + px


def main(riptopl, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; '
                                       'typedef unsigned long long u64;\n')
        shutil.copy(HERE / 'igrpops.c', td)
        exe = td / 'igrpops.exe'
        subprocess.run(['gcc', '-DIGR_MENU_HOST_TEST', '-I', str(td), '-I', str(Path(riptopl) / 'ee_core/include'),
                        '-I', str(Path(riptopl) / 'ee_core/src'), str(td / 'igrpops.c'), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], cwd=td, check=True)
        pages = {k: Image.open(td / ('pops_%s.ppm' % k)).convert('RGB') for k in ('bg', 'yes', 'no')}
    bg = Image.new('RGB', (400, 260))
    bg.paste(pages['bg'], PANEL_AT)
    d = ImageDraw.Draw(bg)
    for x, y in (YES_AT, NO_AT):
        d.rectangle([x, y, x + 73, y + 33], outline=SEP, width=2)

    def button(page, at):
        b = page.crop((at[0] - PANEL_AT[0], at[1] - PANEL_AT[1], at[0] - PANEL_AT[0] + 74, at[1] - PANEL_AT[1] + 34))
        ImageDraw.Draw(b).rectangle([0, 0, 73, 33], outline=BORDER, width=2)
        return b

    for name, im in (('IGR_BG', bg), ('IGR_YES', button(pages['yes'], YES_AT)), ('IGR_NO', button(pages['no'], NO_AT))):
        (out / (name + '.TM2')).write_bytes(tim2(im))
    print('wrote', ', '.join(sorted(os.listdir(out))))


if __name__ == '__main__':
    main(*sys.argv[1:3])
