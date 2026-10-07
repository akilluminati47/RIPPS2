"""Build 92: the category bar in RIPPS2's own face on every theme, as a sidebar or anywhere a theme puts it in
its own words (category_font, category_layout, category_x/_y/_spacing, category_label_*), the page transition
(category_transition, Colors and More > Page Transition), and the Grid look (<grid>_coverless=serial in the
in-game menu's pixel font, <grid>_title under the grid) with RIPgrid using them.

Static checks on the patched tree; then, with a C compiler, the serial formatter (gridSerial) run on the PC."""
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
thm, ui, gui, dlg, opl, mk, yml = rd('src/themes.c'), rd('src/ripps2ui.c'), rd('src/gui.c'), rd('src/dialogs.c'), rd('src/opl.c'), rd('Makefile'), rd('lng_tmpl/_base.yml')
fail = []

# the category bar
if 'fntLoadFile("builtin:ripps2", lit ? 20 : 17)' not in ui or 'gTheme->catFontTheme' not in ui:
    fail.append("the category names must be in RIPPS2's own face unless a theme sets category_font=theme")
for key in ('category_font', 'category_layout', 'category_x', 'category_y', 'category_spacing', 'category_label_launch',
            'category_label_storage', 'category_label_files', 'category_transition'):
    if '"%s"' % key not in thm:
        fail.append('themes must be able to set %s' % key)
if 'catAlong(catSlot(gRipps2Category))' not in ui or 'gTheme->catColumn' not in ui:
    fail.append('the mark must follow the names down a column')
if 'catTransitionDraw();' not in ui or 'UICFG_RIPPS2_TRANSITION' not in dlg or 'ripps2_transition' not in opl:
    fail.append('Page Transition must draw, sit in Colors and More and be saved')

# the Grid look
png = elf / 'theme' / 'gfx' / 'ripps2_pixfont.png'
if not png.exists() or struct.unpack('>IIBB', png.read_bytes()[16:26])[2:] != (8, 3) or 'ripps2_pixfont' not in mk:
    fail.append("the in-game menu's pixel font must be built in (elf/theme/gfx/ripps2_pixfont.png)")
if 'textures[RIPPS2_PIXFONT].Filter = GS_FILTER_NEAREST' not in thm:
    fail.append('the pixel font must be drawn unfiltered')
for key in ('_coverless', '_title', '_title_y', '_title_font'):
    if '"%%s%s"' % key not in thm:
        fail.append('a Grid must read <name>%s' % key)
for cfg in ('misc/theme_ripgrid.cfg',):
    c = rd(cfg)
    if 'coverless=serial' not in c or 'title=1' not in c or 'font6=builtin:ripps2sleekbold' not in c:
        fail.append('%s must use the serials, the name under the grid and Sleek Bold for developer and genre' % cfg)

cc = shutil.which('gcc') or shutil.which('cc')
if cc:
    m = re.search(r'static int gridSerial\(const char \*startup, char \*out, int size\)\n\{.*?\n\}\n', thm, re.S)
    if not m:
        fail.append('gridSerial must turn a startup into its serial')
    else:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / 's.c').write_text('#include <stdio.h>\n#include <string.h>\n#include <ctype.h>\n' + m.group(0) + r'''
int main(void)
{
    char b[24];
    int bad = 0;
    bad |= !gridSerial("SLUS_204.82", b, sizeof(b)) || strcmp(b, "SLUS-20482");
    bad |= !gridSerial("sces_503.60", b, sizeof(b)) || strcmp(b, "SCES-50360");
    bad |= gridSerial("BOOT.ELF", b, sizeof(b)) != 0;
    bad |= gridSerial("DigimonWorld", b, sizeof(b)) != 0;
    bad |= gridSerial(NULL, b, sizeof(b)) != 0;
    return bad;
}
''')
            r = subprocess.run([cc, str(td / 's.c'), '-o', str(td / 's.exe')], capture_output=True, text=True)
            if r.returncode or subprocess.run([str(td / 's.exe')]).returncode:
                fail.append('gridSerial: SLUS_204.82 must read SLUS-20482, and a name that is no serial none ' + r.stderr[-200:])

print('\n'.join(fail) or 'build92: category bar (face, layout, words, transition) and the Grid look (serials, name under it) OK')
sys.exit(1 if fail else 0)
