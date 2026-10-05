"""Builds 74-75: the AUDIO folder search order, drive search only on the IO worker; BIBLE on the HDD
falls back to __common; the QUIETBOOT marker follows the boot sound setting."""
import os, re, sys
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
snd = (root / 'src/sound.c').read_text()
boot = (root / 'src/ripps2boot.c').read_text()
opl = (root / 'src/opl.c').read_text()
fail = []
fn = snd[snd.index('int ripps2AudioBase('):snd.index('\n}\n', snd.index('int ripps2AudioBase('))]
if fn.index('oplGetRipps2Dir(base') > fn.index('if (searchDrives)'):
    fail.append('AUDIO beside RIPPS2 must be tried before any drive')
calls1 = [m.start() for m in re.finditer(r'ripps2AudioBase\([^;]*, 1\)', snd)]
for pos in calls1:
    owner = snd.rfind('\nstatic void ', 0, pos)
    if 'audioLateWork' not in snd[owner:owner + 40]:
        fail.append('only the IO worker (audioLateWork, deferredAudioInit) may search drives for AUDIO')
if 'ripps2AudioBase(dir, sizeof(dir), 1)' not in opl:
    fail.append('deferredAudioInit must search the drives once')
if not re.search(r'parts\[\] = \{"__sysconf", "__common"\}', boot):
    fail.append('BIBLE on the HDD must try __sysconf, then __common')
if 'ripps2QuietBootMark(gEnableSFX && gEnableBootSND)' not in opl:
    fail.append('each settings save must keep QUIETBOOT in step with the boot sound')
print('\n'.join(fail) or 'AUDIO order, BIBLE HDD fallback, QUIETBOOT OK')
sys.exit(1 if fail else 0)
