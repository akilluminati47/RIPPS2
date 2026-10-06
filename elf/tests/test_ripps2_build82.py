"""Build 82: HD text at its true width, US spellings on screen, and RIPgrid's back covers, flip and page slide.

Static checks on the patched tree. The HD check works the font scale out of the mode table the way
fntsys.c does (height scale x PAR) and asks for the 16:9 width every picture in RIPPS2 uses: three
quarters of the frame's own x scale."""
import os, re, sys
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
rm, th, ui, lng = rd('src/renderman.c'), rd('src/themes.c'), rd('src/ripps2ui.c'), rd('lng_tmpl/_base.yml')
about, files = rd('src/ripps2about.c'), rd('src/ripps2files.c')
fail = []

# --- HD: a glyph's width scale must be 0.75 of the frame's x scale (fntsys: ws = hs * PAR)
for mode, frame in (('GS_MODE_DTV_720P', False), ('GS_MODE_DTV_1080I', True)):
    m = re.search(r'\{\s*%s\s*,\s*\d+\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*\d+\s*,\s*\d+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*(\d+)\s*,\s*(\d+)\s*\}' % mode, rm)
    if not m:
        fail.append('%s row not found' % mode)
        continue
    w, h, par1, par2 = map(int, m.groups())
    if frame:
        h //= 2  # interlaced FRAME rows draw half the lines a field
    par = par2 / par1 * (2 if frame else 1)
    ws, want = h / 480 * par, 0.75 * w / 640
    if abs(ws - want) > 0.01:
        fail.append('%s text width scale %.3f, wants %.3f (PAR %d/%d upside down?)' % (mode, ws, want, par2, par1))

# --- US spellings on screen
for text, where in (('Update cancelled.', lng), ('colour depth', lng), ('MIT licence', about), ('behaviour reference', about), ('"CENTRE"', files)):
    if text in where:
        fail.append('UK spelling on screen: %s' % text)

# --- RIPgrid: back covers, the 2 s flip that stays, a page slide
if '"COV2"' not in th or 'gridBackFor(elem)' not in th:
    fail.append('the grid must keep its own back cover (COV2) cache')
if 'FLIP_HOLD_S 2.0f' not in th or 'ripps2StickSide()' not in th or 'gridFlips[k].target = !gridFlips[k].target;' not in th:
    fail.append('a 2 s hold of the right stick must turn the chosen case over, and again turn it back')
if 'ripps2TiltBeginTurn(' not in th or 'int ripps2StickSide(void)' not in ui:
    fail.append('the flip must draw through the tilt with a turn of its own')
dg = th[th.index('static void drawGrid(struct menu_list'):]
dg = dg[:dg.index('\n}\n')]
if 'int page = (cur / cols) / rows * rows;' not in dg or 'gridSlideFrom' not in dg or 'powf(1.0f - t, 3.0f)' not in dg:
    fail.append('the grid must move by whole pages, sliding as RIPFLOW does')
if 'selBack = gridBackTexture(elem, src, item, 1);' not in dg:
    fail.append('the chosen game\'s back cover must be asked for as soon as its front is in')
ig = th[th.index('static void initGrid('):]
ig = ig[:ig.index('\n}\n')]
if 'int slots = 2 * cols * rows;' not in ig or 'elem->endElem = &endGrid;' not in ig:
    fail.append('the grid needs two pages of cover slots and its own end')

print('\n'.join(fail) or 'build82: HD text width, US spellings, RIPgrid back covers, flip and slide OK')
sys.exit(1 if fail else 0)
