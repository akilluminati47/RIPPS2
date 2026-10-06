"""Every built-in theme image (elf/theme/gfx) is an 8-bit palette PNG.

RIPPS2's loader keeps those as 8-bit textures with a 32-bit palette, alpha included: a quarter of the
VRAM of an RGBA PNG and quicker to load. The make_*.py generators in elf/theme/tools write RGBA, so
after running one: python3 elf/theme/tools/png8.py elf/theme/gfx"""
import struct
import sys
from pathlib import Path

gfx = Path(__file__).resolve().parent.parent / 'theme' / 'gfx'
bad = []
for p in sorted(gfx.glob('*.png')):
    head = p.read_bytes()[:26]
    ct, bd = head[25], head[24]
    if (ct, bd) != (3, 8):
        bad.append('%s: colour type %d, %d-bit' % (p.name, ct, bd))
if not list(gfx.glob('*.png')):
    bad.append('no PNGs found in %s' % gfx)
print('\n'.join(bad + ['not 8-bit palette: run python3 elf/theme/tools/png8.py elf/theme/gfx'] if bad else
                ['built-in theme: all %d PNGs are 8-bit palette OK' % len(list(gfx.glob('*.png')))]))
sys.exit(1 if bad else 0)
