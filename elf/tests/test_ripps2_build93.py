"""Build 93: Memory Files opens pictures (PNG, JPG: fitted, zoom on L2/R2, moved with the D-pad, tilted with the
right stick) and video (AVI, with RIPPS2's fork of libsmslite: full screen, START pauses, cancel or SELECT stops).

Static checks on the patched tree and on elf/libsmslite; then, with a C compiler, the picture shrinker (a big
picture read a row at a time into at most 720 x 512) run on the PC."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
media, files, mk, about = rd('src/ripps2media.c'), rd('src/ripps2files.c'), rd('Makefile'), rd('src/ripps2about.c')
fail = []

lib = elf / 'libsmslite'
if not (lib / 'src' / 'smslite.c').exists() or not (lib / 'FORK.md').exists():
    fail.append("RIPPS2's libsmslite must be in elf/libsmslite with its FORK.md")
else:
    s = (lib / 'src' / 'smslite.c').read_text(encoding='utf-8')
    if 'void smsLitePause(int on)' not in s or s.count('s_smsLitePaused') < 4:
        fail.append('the player must pause (smsLitePause): the frame held, the sound not fed')
    fork = (lib / 'FORK.md').read_text(encoding='utf-8')
    if 'Lesser General Public License' not in fork or 'Academic Free License' not in fork:
        fail.append('FORK.md must say what licence each part is under')
build = (elf / 'build.sh').read_text(encoding='utf-8')
if 'make -C "$SRC/thirdparty/libsmslite" all' not in build or 'lib/libsmslite.a' not in build:
    fail.append('build.sh must build libsmslite into lib/')
if 'ifneq ($(wildcard lib/libsmslite.a),)' not in mk or '-DRIPPS2_SMSLITE' not in mk or 'ripps2media.o' not in mk:
    fail.append('the Makefile must link libsmslite when it is built, and ripps2media.c always')
if 'ripps2OpenMedia(path);' not in files:
    fail.append('Memory Files must open pictures and video')
if 'smsLitePause(paused);' not in media or 'getKeyOn(KEY_START)' not in media or 'smsLiteStop();' not in media:
    fail.append('START must pause a video, and cancel or SELECT stop it')
if 'rmEnd();' not in media or 'rmSetMode(1);' not in media or 'bgmStart();' not in media:
    fail.append("RIPPS2's display and music must come back after a video")
if 'KEY_R2' not in media or 'KEY_L2' not in media or 'rmSetTilt(1' not in media:
    fail.append('a picture must zoom on R2 / L2 and tilt with the right stick')
if 'libsmslite: SMS by Eugene Plotnikov' not in about:
    fail.append('About must credit libsmslite')

cc = shutil.which('gcc') or shutil.which('cc')
if cc:
    m = re.search(r'typedef struct\n\{\n    int sw, sh, tw, th, cur;.*?static void shrinkFree\(view_shrink_t \*s\)\n\{.*?\n\}\n', media, re.S)
    if not m:
        fail.append('the picture shrinker must be in ripps2media.c')
    else:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / 'k.c').write_text('#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#define VIEW_MAX_W 720\n#define VIEW_MAX_H 512\n'
                                    '#define memalign(a, n) malloc(n)\n' + m.group(0) + r'''
int main(void)
{
    view_shrink_t s;
    static unsigned char row[4000 * 4];
    int y, x, bad = 0;
    // a 4000 x 3000 picture, left half white, right half black, opaque
    if (!shrinkBegin(&s, 4000, 3000)) return 9;
    for (x = 0; x < 4000; x++) { unsigned char v = x < 2000 ? 255 : 0; row[x*4] = row[x*4+1] = row[x*4+2] = v; row[x*4+3] = 255; }
    for (y = 0; y < 3000; y++) shrinkRow(&s, row, y);
    shrinkFlush(&s);
    bad |= s.tw != 682 || s.th != 512;                  // 4:3 into 720 x 512
    bad |= s.out[0] != 255 || s.out[(s.tw - 1) * 4] != 0; // the halves kept
    bad |= s.out[3] != 127;                             // the GS's alpha (0x80 scale)
    bad |= s.out[((s.th - 1) * s.tw + 10) * 4] != 255;  // the last row written
    shrinkFree(&s);
    // a small one is kept as it is
    if (!shrinkBegin(&s, 320, 200)) return 9;
    bad |= s.tw != 320 || s.th != 200;
    printf("%d %d %d\n", bad, s.tw, s.th);
    return bad;
}
''')
            r = subprocess.run([cc, str(td / 'k.c'), '-o', str(td / 'k.exe')], capture_output=True, text=True)
            if r.returncode or subprocess.run([str(td / 'k.exe')], capture_output=True).returncode:
                fail.append('the picture shrinker must keep a big picture whole in 720 x 512 ' + r.stderr[-300:])

print('\n'.join(fail) or 'build93: pictures (fit, zoom, move, tilt) and AVI video (libsmslite fork, START pause) in Memory Files OK')
sys.exit(1 if fail else 0)
