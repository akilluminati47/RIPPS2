"""Build 90: the theme engine's hint and glyph keys (hints_hide, hints_order, hints_labels, hints_layout,
hints_spacing, glyph_set), Controller Settings > Hints and Glyphs (each row starting on Theme, the user's choice
winning), the Hint Order page, and the Standard and White glyph sets built in.

Static checks on the patched tree and on elf/theme/gfx; then, with a C compiler, ripps2hints.c built on the PC
against stand-ins for the theme (the declarations come from the real include/ripps2.h)."""
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
pillars = Path(__file__).resolve().parents[1]  # elf/
rd = lambda p: (root / p).read_text(encoding='utf-8')
thm, gui, mk, dia, opl, hints, hdr = (rd('src/themes.c'), rd('src/gui.c'), rd('Makefile'), rd('src/dialogs.c'), rd('src/opl.c'),
                                      rd('src/ripps2hints.c'), rd('include/ripps2.h'))
fail = []

GLYPHS = ('cross', 'circle', 'square', 'triangle', 'start', 'select', 'L1', 'R1', 'L2R2', 'L3', 'R3', 'up', 'down', 'left', 'right')

# the glyph sets: built in, every glyph present and 8-bit
if 'ripps2hints.o' not in mk:
    fail.append('ripps2hints.c must be built')
for s in ('standard', 'white'):
    for n in GLYPHS:
        name = 'glyph_%s_%s' % (s, n)
        if name not in mk:
            fail.append('%s must be embedded (PNG_ASSETS)' % name)
        png = pillars / 'theme' / 'gfx' / (name + '.png')
        if not png.exists():
            fail.append('elf/theme/gfx/%s.png is missing' % name)
        elif struct.unpack('>IIBB', png.read_bytes()[16:26])[2:] != (8, 3):
            fail.append('%s.png must be an 8-bit palette PNG' % name)
if 'thmGlyphSetLoad(newT, ripps2GlyphSetFor(newT->glyphSetDef), 0)' not in thm or 'thmGlyphSetRefresh();' not in gui:
    fail.append('the glyph set in effect must load with the theme and when it changes')
if 'RIPPS2_DPAD_UP], RIPPS2_DPAD_UP, themePath' not in thm:
    fail.append('the D-pad glyphs must load with the theme')

# the theme keys
for key in ('hints_hide', 'hints_order', 'hints_labels', 'hints_layout', 'hints_spacing', 'glyph_set'):
    if '"%s"' % key not in thm:
        fail.append('themes must be able to set %s' % key)
for call in ('ripps2HintShown(', 'ripps2HintRank(', 'ripps2HintColumn()', 'ripps2HintLabels()'):
    if call not in thm[thm.index('static void drawHintText('):]:
        fail.append('the hint bar must follow %s' % call)

# the page, and the settings it saves
if 'RIPPS2_HINTS_BUTTON' not in dia or 'ripps2ShowHintsConfig()' not in gui:
    fail.append('Controller Settings must open Hints and Glyphs')
if 'struct UIItem diaHintOrder[]' not in dia or dia.count('UICFG_RIPPS2_HINT_SLOT') != 8:
    fail.append('Hint Order must offer all eight places')
for v in ('pickLayout[] = {"Theme"', 'pickLabels[] = {"Theme"', 'pickShow[] = {"Theme"', 'pickGlyphs[] = {"Theme", "RIPPS2", "Standard", "White"'):
    if v not in hints:
        fail.append('every Hints and Glyphs row must start on Theme: %s' % v)
for key in ('ripps2_hint_layout', 'ripps2_hint_labels', 'ripps2_hint_menu', 'ripps2_hint_refresh', 'ripps2_hint_star',
            'ripps2_hint_view', 'ripps2_glyph_set', 'ripps2_hint_order'):
    if hints.count('"%s"' % key) < 1:
        fail.append('the setting %s must be saved' % key)
if 'ripps2HintsLoadConfig(configOPL)' not in opl or 'ripps2HintsSaveConfig(configOPL)' not in opl:
    fail.append('Hints and Glyphs must load and save with the settings')

HOST_H = r'''
#include "ripps2_b90.h"
#define START_ICON 1
#define SQUARE_ICON 2
#define TRIANGLE_ICON 3
#define SELECT_ICON 4
#define R3_ICON 5
#define L3_ICON 6
#define CROSS_ICON 7
#define _STR_RIPPS2_SOURCE 900
typedef struct { int hintsHide, hintsOrder[8], hintsOrderCount, hintsLabelsDef, hintsColumnDef, hintsSpacing, glyphSetDef; } theme_t;
extern theme_t *gTheme;
'''

MAIN = r'''
#include <stdio.h>
#include <string.h>
#include "ripps2hints_host.h"
theme_t th, *gTheme = &th;
static int bad = 0;
#define CHECK(c) do { if (!(c)) { printf("FAILED: %s (line %d)\n", #c, __LINE__); bad = 1; } } while (0)
int main(void)
{
    int o[8], n;
    n = ripps2HintParse("star, view,source", o, 8);
    CHECK(n == 3 && o[0] == RIPPS2_HINT_STAR && o[1] == RIPPS2_HINT_VIEW && o[2] == RIPPS2_HINT_SOURCE);
    n = ripps2HintParse("START,select,r3,l3,cross,square,triangle,menu", o, 8);
    CHECK(n == 7 && o[0] == RIPPS2_HINT_MENU && o[1] == RIPPS2_HINT_REFRESH && o[4] == RIPPS2_HINT_RUN && o[6] == RIPPS2_HINT_OPTIONS);
    n = ripps2HintParse("bogus,,run", o, 8);
    CHECK(n == 1 && o[0] == RIPPS2_HINT_RUN);

    memset(&th, 0, sizeof(th));
    th.hintsLabelsDef = th.hintsColumnDef = -1;
    th.hintsHide = 1 << RIPPS2_HINT_STAR;
    CHECK(!ripps2HintShown(RIPPS2_HINT_STAR) && ripps2HintShown(RIPPS2_HINT_VIEW));
    gRipps2HintPick[RIPPS2_HINT_STAR] = RIPPS2_PICK_SHOWN;  // the user wins over hints_hide
    gRipps2HintPick[RIPPS2_HINT_VIEW] = RIPPS2_PICK_HIDDEN;
    CHECK(ripps2HintShown(RIPPS2_HINT_STAR) && !ripps2HintShown(RIPPS2_HINT_VIEW));

    th.hintsOrderCount = ripps2HintParse("run,info", th.hintsOrder, 8);
    CHECK(ripps2HintRank(RIPPS2_HINT_RUN) == 0 && ripps2HintRank(RIPPS2_HINT_INFO) == 1 && ripps2HintRank(RIPPS2_HINT_MENU) == RIPPS2_HINT_COUNT);
    strcpy(gRipps2HintOrder, "refresh,menu"); // the user's order replaces the theme's
    CHECK(ripps2HintRank(RIPPS2_HINT_REFRESH) == 0 && ripps2HintRank(RIPPS2_HINT_MENU) == 1 && ripps2HintRank(RIPPS2_HINT_RUN) == RIPPS2_HINT_COUNT);
    gRipps2HintOrder[0] = '\0';
    CHECK(ripps2HintRank(RIPPS2_HINT_RUN) == 0);

    CHECK(ripps2HintLabels() == 1);
    th.hintsLabelsDef = 0;
    CHECK(ripps2HintLabels() == 0);
    gRipps2HintLabels = 1;
    CHECK(ripps2HintLabels() == 1);
    gRipps2HintLabels = 2;
    CHECK(ripps2HintLabels() == 0);

    CHECK(ripps2HintColumn() == 0);
    th.hintsColumnDef = 1;
    CHECK(ripps2HintColumn() == 1);
    gRipps2HintLayout = 1;
    CHECK(ripps2HintColumn() == 0);
    gRipps2HintLayout = 2;
    th.hintsColumnDef = 0;
    CHECK(ripps2HintColumn() == 1);

    CHECK(ripps2GlyphSetParse("White") == RIPPS2_GLYPHSET_WHITE && ripps2GlyphSetParse("standard") == RIPPS2_GLYPHSET_STANDARD);
    CHECK(ripps2GlyphSetParse("nope") == RIPPS2_GLYPHSET_THEME && ripps2GlyphSetParse(NULL) == RIPPS2_GLYPHSET_THEME);
    CHECK(ripps2GlyphSetFor(RIPPS2_GLYPHSET_STANDARD) == RIPPS2_GLYPHSET_STANDARD);
    gRipps2GlyphSet = RIPPS2_GLYPHSET_RIPPS2;
    CHECK(ripps2GlyphSetFor(RIPPS2_GLYPHSET_STANDARD) == RIPPS2_GLYPHSET_RIPPS2);

    CHECK(ripps2HintToken(_STR_RIPPS2_SOURCE, CROSS_ICON) == RIPPS2_HINT_SOURCE);
    CHECK(ripps2HintToken(1, L3_ICON) == RIPPS2_HINT_VIEW && ripps2HintToken(1, CROSS_ICON) == RIPPS2_HINT_RUN);
    CHECK(ripps2HintToken(1, START_ICON) == RIPPS2_HINT_MENU && ripps2HintToken(1, SELECT_ICON) == RIPPS2_HINT_REFRESH);
    return bad;
}
'''

cc = shutil.which('gcc') or shutil.which('cc')
if cc and not fail:
    m = re.search(r'// RIPPS2 build 90: Controller Settings > Hints and Glyphs.*?int ripps2ShowHintsConfig\(void\);[^\n]*\n', hdr, re.S)
    if not m:
        fail.append('include/ripps2.h must declare the build 90 hint functions')
    else:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / 'ripps2_b90.h').write_text(m.group(0))
            (td / 'ripps2hints_host.h').write_text(HOST_H)
            (td / 'm.c').write_text(MAIN)
            exe = td / 'm.exe'
            r = subprocess.run([cc, '-DRIPPS2_HINTS_HOST_TEST', '-I', str(td), str(td / 'm.c'), str(root / 'src/ripps2hints.c'), '-o', str(exe)],
                               capture_output=True, text=True)
            if r.returncode:
                fail.append('ripps2hints.c must build on the PC: ' + r.stderr[-600:])
            else:
                r = subprocess.run([str(exe)], capture_output=True, text=True)
                if r.returncode:
                    fail.append('the hint rules: ' + r.stdout.strip())

print('\n'.join(fail) or 'build90: hint keys, Hints and Glyphs (Theme first, the user wins), Hint Order, Standard and White glyph sets OK')
sys.exit(1 if fail else 0)
