"""Build 78: frosted glass reads 8-bit palette textures through the PNG loader's swizzled palette.

Builds a 640x480 T8 texture the way src/textures.c stores one (palette entries 8-15 and 16-23 of every
32 swapped, alpha 0..0x80), runs the real ripps2MakeFrost (src/ripps2ui.c) on the host, and checks the
80x60 result against a Python box average of the same picture (within a few levels, for the 3x3 soften
and the sampling step)."""
import os, random, re, subprocess, sys, tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
src = (root / 'src/ripps2ui.c').read_text()
code = src[src.index('#define FROST_W 80'):src.index('void ripps2DrawFrost(')]
random.seed(7)
W, H = 640, 480
pal = [(random.randrange(256), random.randrange(256), random.randrange(256)) for _ in range(256)]
# a picture with structure: four colour quadrants with noise
pix = bytearray()
for y in range(H):
    for x in range(W):
        q = (x >= W // 2) + 2 * (y >= H // 2)
        pix.append((q * 64 + 8 + random.randrange(8)) & 0xFF)  # entries the loader swizzles
swz = list(range(256))
for i in range(256):
    if (i & 0x18) == 8:
        swz[i], swz[i + 8] = i + 8, i
clut = bytearray()
for i in range(256):
    r, g, b = pal[swz[i]]
    clut += bytes([r, g, b, 0x80])
c = '''#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <malloc.h>
#define GS_PSM_CT32 0
#define GS_PSM_CT24 1
#define GS_PSM_T8 0x13
#define GS_PSM_T4 0x14
#define GS_FILTER_LINEAR 1
typedef struct { int Width, Height, PSM, Filter; void *Mem, *Clut; } GSTEXTURE;
''' + code + '''
int main(int argc, char **argv) {
    static unsigned char pix[640 * 480], clut[1024];
    FILE *f = fopen(argv[1], "rb"); fread(pix, 1, sizeof(pix), f); fread(clut, 1, sizeof(clut), f); fclose(f);
    GSTEXTURE s = {640, 480, GS_PSM_T8, 0, pix, clut}, d;
    if (!ripps2MakeFrost(&s, &d)) return 1;
    fwrite(d.Mem, 1, 80 * 60 * 4, stdout);
    return 0;
}
'''
with tempfile.TemporaryDirectory() as t:
    Path(t, 'in.bin').write_bytes(bytes(pix) + bytes(clut))
    Path(t, 'f.c').write_text(c)
    r = subprocess.run(['gcc', '-O1', '-o', t + '/f', t + '/f.c'], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)
    out = subprocess.run([t + '/f', t + '/in.bin'], capture_output=True).stdout
fail = []
if len(out) != 80 * 60 * 4:
    fail.append('ripps2MakeFrost failed')
else:
    worst = 0
    for qy, qx in ((15, 20), (15, 60), (45, 20), (45, 60)):  # quadrant centres, away from the edges
        o = out[(qy * 80 + qx) * 4:(qy * 80 + qx) * 4 + 3]
        y0, x0 = qy * 8, qx * 8
        ref = [0, 0, 0]
        for yy in range(y0, y0 + 8):
            for xx in range(x0, x0 + 8):
                col = pal[pix[yy * W + xx]]
                ref = [a + b for a, b in zip(ref, col)]
        ref = [v / 64 for v in ref]
        worst = max(worst, max(abs(a - b) for a, b in zip(o, ref)))
    if worst > 40:
        fail.append('frost differs from the picture by %d levels: palette order or sampling is wrong' % worst)
print('\n'.join(fail) or 'frost: T8 palette read through the swizzle, 80x60 soft copy OK')
sys.exit(1 if fail else 0)
