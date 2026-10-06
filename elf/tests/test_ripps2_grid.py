"""Build 78: the Grid theme element -- registered, drawn, and moving in two dimensions.

A Grid theme sets gTheme->grid (initGrid), the engine knows the type name, all four arrows go through
the grid in menusys.c (Left/Right one cover, Up/Down one row via menuGridStep), held arrows repeat on
every axis, and a drive change at the grid's edge needs a fresh press."""
import os, sys
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
th = (root / 'src/themes.c').read_text()
ms = (root / 'src/menusys.c').read_text()
fail = []
if '"Grid"};' not in th or 'ELEM_TYPE_GRID' not in th:
    fail.append('the engine must know the Grid element type')
if 'theme->grid = elem;' not in th or 'elem->drawElem = &drawGrid;' not in th:
    fail.append('initGrid must register the grid and its draw')
for fn, want in (('menuNavigateLeft', 'menuPrevV();'), ('menuNavigateRight', 'menuNextV();'),
                 ('menuNavigateUp', 'menuGridStep(-1);'), ('menuNavigateDown', 'menuGridStep(1);')):
    i = ms.index('static void %s()' % fn)
    if want not in ms[i:ms.index('\n}\n', i)]:
        fail.append('%s must %s on a Grid theme' % (fn, want))
g = ms[ms.index('static void menuGridStep('):ms.index('\n}\n', ms.index('static void menuGridStep('))]
if g.count('getKeyOn(') < 2:
    fail.append('a drive change at the grid edge must need a fresh press')
if '((cf && !grid) ? getKeyOn(KEY_UP) : getKey(KEY_UP))' not in ms:
    fail.append('Up/Down must repeat when held on a Grid theme')
print('\n'.join(fail) or 'grid: element, draw, two-axis navigation, edge drive change OK')
sys.exit(1 if fail else 0)
