"""Build 85: the 704-wide video modes in one pass, the CD player's hints in the safe area, Sony's POPS files
checked before a USB/MMCE PS1 launch, and the launch report written before every PS1 handoff.

Static checks on the patched tree."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
rm, gui, cd, vcd, sysc, st = rd('src/renderman.c'), rd('src/gui.c'), rd('src/ripps2cd.c'), rd('src/vcdsupport.c'), rd('src/system.c'), rd('src/ripps2status.c')
bdm, mmce = rd('src/bdmsupport.c'), rd('src/mmcesupport.c')
fail = []

# --- no row of the mode table uses gsKit's multi-pass hires renderer any more
rows = re.findall(r'\{\s*(GS_MODE_\w+|-1)\s*,\s*\d+\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,', rm)
if not rows:
    fail.append('mode table not found')
for mode, w, h, passes in rows:
    if passes != '1':
        fail.append('%s %sx%s still draws in %s passes (gsKit hires overruns on RIPPS2 frames)' % (mode, w, h, passes))
if 'gsGlobal->Width >= 704' not in rm:
    fail.append('the 704-wide modes must draw 16-bit, or their double buffer crowds VRAM')
if '(HIRES)' in gui:
    fail.append('the video mode list still says HIRES')

# --- the CD hints stay inside the safe area
if 'CD_HINT_ROOM 544' not in cd or '"COPY", "CLOSE"' not in cd:
    fail.append('the CD player hint row must fit 48..592, shortening COPY TO AUDIO when tight')

# --- POPS files asked about before a USB / MMCE launch writes anything
if 'int vcdConfirmPopsFiles(const char *devPrefix)' not in vcd or 'POPS_IOX.PAK' not in vcd:
    fail.append('vcdConfirmPopsFiles must look for POPS.ELF and POPS_IOX.PAK')
for name, src in (('bdmsupport', bdm), ('mmcesupport', mmce)):
    i, j = src.find('vcdConfirmPopsFiles('), src.find('vcdInstallPopstarterMc(')
    if i < 0 or j < 0 or i > j:
        fail.append('%s must check the POPS files before preparing the memory card' % name)

# --- the launch report, before each PS1 handoff
for kind in ('"POPSTARTER", popstarterElf', '"EMBER", emberElf'):
    if 'ripps2LaunchReport(%s' % kind not in sysc:
        fail.append('the %s handoff must write the launch report' % kind.split(',')[0])
if 'mc0:/RIPPS2/LAUNCH.TXT' not in st or 'crc32(' not in st:
    fail.append('ripps2LaunchReport must write mc0:/RIPPS2/LAUNCH.TXT with the ELF CRC')

print('\n'.join(fail) or 'build85: single-pass 704 modes, CD hints in the safe area, POPS files asked, launch report OK')
sys.exit(1 if fail else 0)
