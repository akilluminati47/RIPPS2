"""Build 75: 720p and 1080i are single-pass, 640-wide frames the GS magnifies; never gsKit's hires mode.
The hires mode replayed a 256 KB queue per band and crashed under RIPPS2's drawing (build 74)."""
import os, re, sys
from pathlib import Path
src = (Path(os.environ.get('RIPTOPL_DIR', '.')) / 'src/renderman.c').read_text()
fail = []
for mode, dw in (('GS_MODE_DTV_720P', 1280), ('GS_MODE_DTV_1080I', 1920)):
    m = re.search(r'\{\s*%s\s*,\s*\d+\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,' % mode, src)
    if not m:
        fail.append('%s row missing' % mode)
        continue
    w, h, passes = map(int, m.groups())
    if passes != 1:
        fail.append('%s must be one pass, is %d' % (mode, passes))
    if dw % w:
        fail.append('%s width %d must divide the display width %d (MAGH)' % (mode, w, dw))
    if mode == 'GS_MODE_DTV_1080I':
        h //= 2  # interlaced FRAME rows are halved by rmSetMode: 540 lines a field
    if w * h * 2 * 2 > 2 * 1024 * 1024:
        fail.append('%s double buffer would leave too little VRAM for textures' % mode)
if 'ChangeThreadPriority(tid, prio)' not in src:
    fail.append('the GUI priority must be put back after gsKit_hires_init_screen')
print('\n'.join(fail) or 'HD modes: single pass, magnified, priority restored OK')
sys.exit(1 if fail else 0)
