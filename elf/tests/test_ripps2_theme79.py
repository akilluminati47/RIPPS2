"""Build 79: SELECT hold-to-cycle themes, the Grid's art (no stock disc/case, fade-in, title tiles,
breathing glow), and clear glass keys.

The SELECT block in menusys.c is compiled on the host with a fake pad and clock and played through:
a tap refreshes on release, a 4.2 s hold cycles the theme once and never refreshes, a hold kept going
does not cycle again, and a release just short of 4.2 s is still a refresh."""
import os, re, subprocess, sys, tempfile
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
th = (root / 'src/themes.c').read_text()
ms = (root / 'src/menusys.c').read_text()
fail = []

# --- SELECT: tap = refresh on release, 4.2 s hold = one theme step, no refresh
i = ms.index('{', ms.index('// RIPPS2 build 79: SELECT'))
depth, j = 0, i
while True:
    depth += {'{': 1, '}': -1}.get(ms[j], 0)
    j += 1
    if depth == 0:
        break
block = ms[i:j]
harness = r'''
#include <stdio.h>
typedef long clock_t;
#define CLOCKS_PER_SEC 1000
#define KEY_SELECT 1
static clock_t now; static int down, was, refreshes, cycles, viewPending;
static clock_t clock(void) { return now; }
static int getKeyOn(int k) { return down && !was; }
static int getKeyPressed(int k) { return down; }
static void guiCycleTheme(void) { cycles++; }
struct item { void (*refresh)(struct item *); };
static void doRefresh(struct item *it) { refreshes++; }
static struct item it = { doRefresh };
static struct { struct item *item; } sel = { &it }, *selected_item = &sel;
static void frame(void) { BLOCK was = down; now += 20; }
static void hold(int ms) { down = 1; for (int t = 0; t < ms; t += 20) frame(); down = 0; frame(); frame(); }
int main(void) {
    hold(200);  printf("%d %d\n", refreshes, cycles);
    hold(4300); printf("%d %d\n", refreshes, cycles);
    hold(9000); printf("%d %d\n", refreshes, cycles);
    hold(4100); printf("%d %d\n", refreshes, cycles);
    return 0;
}
'''.replace('BLOCK', block)
with tempfile.TemporaryDirectory() as d:
    c, exe = Path(d) / 's.c', Path(d) / 's'
    c.write_text(harness)
    r = subprocess.run(['cc', '-std=c99', '-o', str(exe), str(c)], capture_output=True, text=True)
    if r.returncode:
        fail.append('the SELECT block must compile on its own: ' + r.stderr[:400])
    else:
        got = subprocess.run([str(exe)], capture_output=True, text=True).stdout.split('\n')[:4]
        want = ['1 0', '1 1', '1 2', '2 2']
        if got != want:
            fail.append('SELECT tap/hold: want refreshes,cycles %s, got %s' % (want, got))
if ms.count('getKeyOn(KEY_SELECT)') != 1:
    fail.append('the old press-to-refresh SELECT branch must be gone')

# --- Grid: real art only, fading in; a glass title tile when there is none; a breathing glow
g = th[th.index('static void drawGridCover('):th.index('static void drawGridGlow(')]
if 'COVER_DEFAULT' in g:
    fail.append('the Grid must not fall back to the stock disc/case art')
if 'gridFadeIn(' not in g or 'fntRenderString(' not in g or 'ripps2DrawPanelFlat(' not in g:
    fail.append('Grid covers must fade in, and art-less games get a glass tile with the name')
glow = th[th.index('static void drawGridGlow('):th.index('static void drawGrid(')]
if 'sinf(' not in glow or 'rmSetBlendAdditive(1)' not in glow:
    fail.append('the Grid selection must breathe (a pulsing additive glow)')

# --- glass keys and the morph picking a framed panel over a frosted backdrop layer
for key in ('"%s_tint"', '"%s_tint_color"', '"%s_frame"', '"%s_widecrop"'):
    if key not in th:
        fail.append('theme key %s must be read' % key)
p = th[th.index('int thmGetPanelRect('):]
p = p[:p.index('\n}\n')]
if 'glassFrame' not in p:
    fail.append('the page morph must skip frameless backdrop panels')
if re.search(r'thmFrostFor\([^)]*\)', th) and '&fade' not in th:
    fail.append('the frost must ease in with the art under it')

print('\n'.join(fail) or 'theme79: SELECT tap/hold, grid art/tiles/glow, glass keys, morph panel OK')
sys.exit(1 if fail else 0)
