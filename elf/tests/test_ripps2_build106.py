"""Build 106: POWER OFF in the in-game menu, and the star and row icons of the games list (static checks; the
in-game panel itself is drawn on the host by test_ripps2_build87.py, POWER OFF page included)."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8').replace('\r\n', '\n')
fail = []


def check(ok, what):
    if not ok:
        fail.append(what)


def fn(src, sig):
    i = src.index(sig)
    return src[i:src.index('\n}\n', i) + 3]


igr = rd('ee_core/src/igrmenu.c')
themes = rd('src/themes.c')
th = rd('include/themes.h')
dia = rd('src/dialogs.c')
gui = rd('src/gui.c')
opl = rd('src/opl.c')
base = rd('lng_tmpl/_base.yml')

# 1. POWER OFF: the last choice, confirmed like EXIT GAME, not for a disc game
# build 108 put SCREENSHOT in (RESUME, EXIT GAME, SCREENSHOT, ACHIEVEMENTS, POWER OFF) and the items became ids
# build 126 put CHEATS second (RESUME, CHEATS, EXIT GAME, ...), shown only when the game has the page
check(re.search(r'#define IGRM_ITEMS_MAX 6', igr) is not None, 'the in-game menu has up to six items')
check('{"RESUME", "CHEATS", "EXIT GAME", "SCREENSHOT", "ACHIEVEMENTS", "POWER OFF"}' in igr, 'POWER OFF is the last item')
run = fn(igr, 'int IGR_MenuRun(u16 (*buttons)(void))')
check('id == IT_POWER && info.canPowerOff' in run and 'result = id == IT_EXIT ? IGR_MENU_EXIT : IGR_MENU_POWEROFF;' in run,
      'POWER OFF takes a second press, then powers off as the power button does')
check('if (armed) {' in run, 'the first press arms it')
check('info.canPowerOff = config->GameMode != DISC_MODE;' in run, 'a disc game keeps the ROM power button')
check('id == IT_ACH && info.huntCount > 0' in run, 'only ACHIEVEMENTS opens LEFT TO HUNT')
check(re.search(r'#define PH\s+126', igr) is not None and re.search(r'#define ROW_HINT\s+115', igr) is not None,
      'the panel has a row for each of five items (build 108)')

# 2. the star: left by default, the user's setting first, the row icon moved out of its way
init = fn(themes, 'static void initItemsList(')
check('itemsList->starSide = THM_STAR_LEFT;' in init, 'the star defaults to the left')
for key in ('_star"', '_highlight"', '"star_image"', '"decorator_all"', '"decorator_ps2"', '"decorator_ps1"', '"decorator_app"'):
    check(key in init, 'the list reads %s' % key)
check('elem->endElem = &endItemsList;' in init and 'freeImageTexture(list->decoKind[i]);' in themes, 'the list frees its pictures')
draw = fn(themes, 'static void drawItemsList(')
check('gRipps2StarSide > 0 ? gRipps2StarSide - 1 : itemsList->starSide' in draw, "the user's setting wins over the theme")
check('int decoRight = haveDeco && starSide == THM_STAR_LEFT;' in draw, 'a left star sends the row icon right')
check('decoRight ? posX + elem->width - DECORATOR_SIZE : posX + starCol' in draw, 'the row icon is drawn at the row end')
check('starSide == THM_STAR_LEFT ? posX : textEndX + 4' in draw and 'starSide != THM_STAR_HIDDEN' in draw, 'the star draws left, right or not at all')
check('itemsList->highlight == THM_HL_LINE' in draw and 'itemsList->highlight == THM_HL_BAR' in draw, 'the highlight is a bar, a line or none')
check('itemsList->decoKind[thmRowKind(list, ps)]' in draw and 'itemsList->decoAll' in draw, 'row icons by kind, then for all')
check('enum { THM_STAR_LEFT = 0, THM_STAR_RIGHT, THM_STAR_HIDDEN };' in th, 'the star sides')

# 3. the setting: Game Sources, under Starred Games Page Start Mode; saved
dev = dia[dia.index('{UI_ENUM, CFG_FAVMODE'):]
check(dev.index('CFG_RIPPS2_STARSIDE') < dev.index('UI_OK'), 'Starred Games Star sits under the Starred Games start mode')
check('N_("Theme"), N_("Left"), N_("Right"), N_("Hidden")' in gui, 'Theme, Left, Right, Hidden')
check(gui.count('CFG_RIPPS2_STARSIDE, &gRipps2StarSide') == 2, 'both Game Sources pages save it')
check(opl.count('"ripps2_star_side"') == 2, 'the setting loads and saves')  # build 115: and ripps2_star_side_last
check('label: HINT_RIPPS2_STARSIDE' in base, 'the row has its hint')

if fail:
    print('build 106 FAILED:')
    for f in fail:
        print(' -', f)
    sys.exit(1)
print('build 106 ok')
