"""Build 132: RIPFLOW's flank hints turn to INFO / OPTIONS after 4.2 s on a game, the category bar on RIPFLOW's info page
at its setting, and the RIPPS2 info page's art in full colour above the text band.

Static checks on the patched tree and elf/theme/conf_theme.cfg."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
themes, ui, menu, th, flow = rd('src/themes.c'), rd('src/ripps2ui.c'), rd('src/menusys.c'), rd('include/themes.h'), rd('misc/theme_coverflow.cfg')
conf = (elf / 'theme' / 'conf_theme.cfg').read_text(encoding='utf-8')
fail = []

if '#define FLANK_IDLE_S 4.2f' not in themes or 'flankInfoK(menu)' not in themes or 'dt / SLIDE_FADE_S' not in themes:
    fail.append('the flank hints must turn after 4.2 s on one game, over the screenshots\' fade time')
if 'SQUARE_ICON : confirm, lText = pass ? _STR_INFO : _STR_RUN' not in themes or 'TRIANGLE_ICON, _STR_OPTIONS' not in themes:
    fail.append('the flank hints turn to Square INFO and Triangle OPTIONS')
if 'flankInfo >= 0.5f && (ripps2HintToken(h->text_id, h->icon_id) == RIPPS2_HINT_INFO' not in themes:
    fail.append('INFO and OPTIONS must leave the hint row while they flank')
if 'float k = info ? 0.0f : flankInfoK(menu)' not in themes:
    fail.append('the info page keeps RUN / BACK beside the name')

if 'newT->infoCatBar = configGetInt(themeConfig, "info_catbar"' not in themes or 'int infoCatBar;' not in th:
    fail.append('info_catbar must be a theme key')
if not re.search(r'(?m)^info_catbar=1\s*$', flow):
    fail.append('RIPFLOW must keep the bar on its info page (info_catbar=1)')
if 'ripps2RenderInfoCategoryBar(' not in menu or 'gTheme->infoCatBar' not in menu:
    fail.append('menuRenderInfo must draw the bar for a theme that asks')
if 'float barA = ripps2CatBarAlpha() * catBarScale;' not in ui or 'ripps2Legacy() || ripps2SidebarOn() || k <= 0.0f' not in ui:
    fail.append('the info page bar follows Category Bar, times its fade in, never with the sidebar or a legacy theme')

if 'void ripps2DrawPanelShade(int x, int y, int w, int h, int clearPct)' not in ui or 'elem->glassClear > 0 && item != NULL' not in themes:
    fail.append('a glass with clear= leaves the art untinted above the text band')
if 'elem->glassClear = 0;' not in themes:
    fail.append('glassClear must start at 0 (elements come from malloc)')
m = re.search(r'info4:\n(?:\t[^\n]*\n)*?\tclear=(\d+)', conf.replace('\r\n', '\n'))
if not m or not 40 <= int(m.group(1)) <= 60:
    fail.append('the RIPPS2 info page glass (info4) must set clear= above the title (about 52)')

print('\n'.join(fail) or 'build132: flank INFO / OPTIONS after 4.2 s, the bar on RIPFLOW\'s info page, the RIPPS2 info art in full colour OK')
sys.exit(1 if fail else 0)
