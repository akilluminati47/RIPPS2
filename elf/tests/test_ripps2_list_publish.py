"""Build 74: All Games and Favorites never free a list under a reader (the info page hang)."""
import os, re, sys
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
fav = (root / 'src/favsupport.c').read_text()
mix = (root / 'src/mixsupport.c').read_text()
fail = []
body = fav[fav.index('static int favUpdateItemList('):fav.index('static int favGetItemCount(')]
if 'favArray' in body or 'favFreeArray' in body:
    fail.append('favUpdateItemList must build aside and favPublish, never touch favArray')
if body.count('favPublish(') < 2:
    fail.append('favUpdateItemList must publish on every return')
for fn in ('unsigned char mixGetFlags', 'int mixGetItemSourceMode', 'int mixGetItemSourceId', 'int mixGetItemKind', 'static int mixGetRowView'):
    i = mix.index(fn)
    b = mix[i:mix.index('\n}\n', i)]
    if 'mixLock()' not in b and 'mixRow(' not in b:
        fail.append('%s must read under mixSema' % fn)
print('\n'.join(fail) or 'list publish: Favorites swaps whole, All Games reads locked OK')
sys.exit(1 if fail else 0)
