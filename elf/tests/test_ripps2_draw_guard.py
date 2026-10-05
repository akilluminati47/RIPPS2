"""Build 74: every primitive renderman queues checks the draw queue's room first (gsKit bounds-checks
only in debug builds; a full queue writes past its end)."""
import os, re, sys
from pathlib import Path
src = (Path(os.environ.get('RIPTOPL_DIR', '.')) / 'src/renderman.c').read_text()
fail = []
for m in re.finditer(r'\n(?:static )?void (rm\w+)\([^)]*\)\s*\{', src):
    body = src[m.end():src.find('\n}\n', m.end())]
    if 'gsKit_prim_' in body and 'rmQueueFull()' not in body and 'rmTiltTexQuad(' not in body:
        fail.append('%s queues a primitive without rmQueueFull()' % m.group(1))
print('\n'.join(fail) or 'draw guard: every primitive checks the queue OK')
sys.exit(1 if fail else 0)
