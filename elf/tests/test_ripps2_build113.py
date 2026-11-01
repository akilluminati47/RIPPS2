"""Build 113: the category sidebar (the user, 10/22). The three categories as glyphs down the theme's side bar
(category_layout=sidebar, or column; Colors and More > Category Layout overrides), Adapt's bar by default; Left on a
list (the cancel button on Launch Disc and Memory Files) focuses them, Up / Down opens each one's drawer with its name
first, Cross enters it and Cross on an item goes there; the game is let go and the hints are the sidebar's.

Static checks on the patched tree."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
side, ui, themes, menusys, opl = rd('src/ripps2side.c'), rd('src/ripps2ui.c'), rd('src/themes.c'), rd('src/menusys.c'), rd('src/opl.c')
th, tx, mk = rd('include/themes.h'), rd('src/textures.c'), rd('Makefile')
fail = []


def need(text, items, where):
    for s, why in items:
        if s not in text:
            fail.append('%s: %s' % (where, why))


need(themes, (('newT->catSidebar = newT->catColumn || !strcasecmp(v, "sidebar");', 'category_layout=sidebar, and column means it too'),
              ('newT->sbW = 26;', "the bar Adapt draws, by default (26 wide)"),
              ('newT->sbBar = !strcasecmp(v, "never") ? 0 : !strcasecmp(v, "pages") ? 1 : 2;', 'sidebar_bar=never|pages|always'),
              ('configGetColor(themeConfig, "sidebar_color", newT->sbColor);', 'sidebar_color'),
              ('if (ps == item && !ripps2SidebarFocused()) {', 'no chosen game while the sidebar has the focus'),
              ('hint = &sbSelect;', "the sidebar's own hints (Select, Back) while it has the focus"),
              ('thmLoadResource(&newT->textures[RIPPS2_SIDEBAR_ICONS], RIPPS2_SIDEBAR_ICONS,', 'the glyph atlas is loaded')), 'themes.c')
need(ui, (('    if (ripps2SidebarOn()) { // build 113: the glyphs down the side bar instead of the words (ripps2side.c)\n        ripps2SidebarRender();\n        return;\n    }', 'the words give way to the sidebar'),
          ('int ripps2CatSlot(int cat)', "the sidebar follows Category Order")), 'ripps2ui.c')
if ui.count('if (ripps2SidebarFocused()) { // build 113: the category sidebar has the pad while it has the focus') != 2:
    fail.append('ripps2ui.c: Launch Disc and Memory Files hand the pad to a focused sidebar')
need(menusys, (('    if (ripps2SidebarFocused()) { // RIPPS2 build 113: the category sidebar has the pad while it has the focus\n        ripps2SidebarInput();\n        return;\n    }', 'Storage hands the pad to a focused sidebar'),
               ('ripps2SidebarOpen(0); // RIPPS2 build 113: Left on a list goes to the category sidebar', 'Left on a list opens it'),
               # build 126 (the user, 10/31): the drawer of the page in use, shown or hidden
               ('ripps2SidebarOpen(1); // build 113: the Storage drawer, its sources', 'the cancel button opens the Storage drawer'),
               ('int menuSourceCount(void)', 'the drawer lists the visible sources'), ('void menuSourceSelect(int i)', 'and goes to one')), 'menusys.c')
need(side, (('if (gRipps2CatLayout == 1)\n        return 0;\n    if (gRipps2CatLayout == 2)\n        return 1;', 'Category Layout overrides the theme'),
            ('fntLoadFile("builtin:ripflowbold"', "the drawer's names in Roboto Condensed Bold (the user's pick)"),
            ('return 1 + (cat == RIPPS2_CAT_STORAGE ? menuSourceCount() : 0);', "a drawer's name is its first item"),
            ('menuSourceSelect(sbItem - 1);\n            ripps2SetCategory(cat);', 'Cross on an item goes there (the source, then the page)')), 'ripps2side.c')
# the first lab pass (10/22): each drawer by its own glyph, frosted like Adapt's bar, the frame kept in the list,
# the two HDD pages told apart
need(side, (('top = sbGlyphY(slot) - SB_ROW / 2', "a drawer's name beside its glyph"),
            ('int floor = gTheme->usedHeight - 56; // clear of the hints', 'the list kept above the hints'),
            ('        thmDrawMainFrost(x0, 0, right - x0, gTheme->usedHeight);', 'the frosted backdrop under the drawer on Storage'),
            ('int fy = (int)sbTween(&sbFrameTw, (float)sbGlyphY(sbGlyph));', "the glyph keeps its frame while its drawer has the pad (build 115: sliding)"),
            ('snprintf(out, size, "%s (%s)", name, icon == HDD_BD_ICON ? "exFAT" : "APA");', 'HDD Games (exFAT) and HDD Games (APA)'),
            ('right = x0 + w > 320 ? 320 : x0 + w;', 'the drawer as wide as its longest name (the second lab pass)')), 'ripps2side.c')
need(themes, (('int thmDrawMainFrost(int x, int y, int w, int h)', 'the frost a blur panel draws, for the drawer'),), 'themes.c')
if 'ALIGN_RIGHT' in side:
    fail.append('ripps2side.c: fntRenderString reads no ALIGN_RIGHT (the 112 hotfix): measure instead')
need(opl, (('gRipps2CatLayout = value; // build 113', 'Category Layout is read'), ('configSetInt(configOPL, "ripps2_catlayout", gRipps2CatLayout);', 'and kept')), 'opl.c')
need(th, (('int catSidebar;', 'the theme asks for the sidebar'),), 'themes.h')
need(tx, (('{RIPPS2_SIDEBAR_ICONS, "ripps2_sidebar_icons", &ripps2_sidebar_icons_png},', 'the atlas in the texture table'),), 'textures.c')
need(mk, (('ripps2side.o', 'the sidebar is built'), ('PNG_ASSETS += ripps2_sidebar_icons', 'its atlas too')), 'Makefile')
atlas = Path(__file__).resolve().parents[1] / 'theme' / 'gfx' / 'ripps2_sidebar_icons.png'
if not atlas.exists():
    fail.append('elf/theme/gfx/ripps2_sidebar_icons.png (make_sidebar_icons.py)')

# Colors and More > Category Layout (Theme, Across the Top, Sidebar), with the other category rows; Cancel puts it back
need(rd('src/dialogs.c'), (('{UI_ENUM, UICFG_RIPPS2_CATLAYOUT, 1, 1, _STR_HINT_RIPPS2_CATEGORY_LAYOUT, 0, 0, {.intvalue = {0, 0}}},', 'the Category Layout row'),), 'dialogs.c')
gui = rd('src/gui.c')
need(gui, (('static const char *guiRipps2LayoutNames[] = {N_("Theme"), N_("Across the Top"), N_("Sidebar"), N_("Menu"), NULL};', 'its choices (build 115: Menu too)'),
           ('        gRipps2CatLayout = v; // build 113', 'it is read as it changes (the page behind shows it)'),
           # build 114 (the settings audit): the category rows are Layout's; Back there puts them back, a change is saved
           ('        gRipps2CatLayout = keepCat[4];', 'Cancel puts it back'),
           ('gRipps2CatLayout != keepCat[4]', 'a change is saved')), 'gui.c')
need(rd('lng_tmpl/_base.yml'), (('- label: RIPPS2_CATEGORY_LAYOUT\n  string: Category Layout\n', 'its label'),), '_base.yml')
# The legacy key (the user): a theme made for OPL shows Storage alone, Launch Disc and Memory Files in the START menu.
# Build 115 (the user, 10/26): category_layout alone says it (row, sidebar or menu); a disk theme that says neither row
# nor sidebar is menu; build 113's categories=three still reads as row where category_layout is not set
need(themes, (('                newT->catLegacy = !strcasecmp(v, "menu");', 'category_layout=menu asks for Storage alone'),
              ('            newT->catLegacy = 1;\n            if (configGetStr(themeConfig, "categories", &v) && v != NULL && !strcasecmp(v, "three"))\n                newT->catLegacy = 0;',
               'unset is menu; categories=three is still the bar'),
              ('if (themePath == NULL)\n            newT->catLegacy = 0;', 'the built-in looks keep the three')), 'themes.c')
if 'ripps2Keys[]' in themes:
    fail.append('themes.c: build 115 dropped the guess from RIPPS2 keys (a theme says category_layout)')
need(ui, (('    if (ripps2Legacy()) // build 113: a legacy theme has no bar', 'a legacy theme has no category bar'),
          ('    if (ripps2Legacy()) { // build 113: no bar to step along', 'L1 / R1 go back to Storage from the other two')), 'ripps2ui.c')
if ui.count('if (ripps2Legacy() && getKeyOn(gSelectButton == KEY_CIRCLE ? KEY_CROSS : KEY_CIRCLE)) {') != 2:
    fail.append('ripps2ui.c: the cancel button takes a legacy theme from Launch Disc and Memory Files back to Storage')
need(menusys, (('submenuAppendItem(&mainMenu, -1, (char *)_t("Launch Disc"), MENU_RIPPS2_LAUNCH, -1);', 'LAUNCH DISC in the START menu'),
               ('submenuAppendItem(&mainMenu, -1, (char *)_t("Memory Files"), MENU_RIPPS2_MEMORY, -1);', 'and MEMORY FILES'),
               ('if (mainMenuLegacy != ripps2Legacy())', 'the START menu follows a theme change'),
               ('if (ripps2PageButtons() == 1 || ripps2Legacy())', 'L1 / R1 turn the pages on a legacy theme, as in OPL')), 'menusys.c')
need(side, (('    if (ripps2Legacy())\n        return 0; // a legacy theme has no categories to show', 'no sidebar on a legacy theme'),), 'ripps2side.c')

# The settings moves (the user agreed 10/22): Hints and Glyphs on Interface with D-pad Glyphs and Button Hints in it,
# Show Recents beside the Starred Games rows on Game Sources
dia = rd('src/dialogs.c')
def table(name):
    s = dia[dia.index('struct UIItem %s[] = {' % name):]
    return s[:s.index('{UI_TERMINATOR}')]
if 'RIPPS2_HINTS_BUTTON' not in table('diaUIConfig') or 'RIPPS2_HINTS_BUTTON' in table('diaControllerConfig'):
    fail.append('dialogs.c: Hints and Glyphs belongs on Interface now, not Controller Settings')
hg = table('diaHintsConfig')
if 'UICFG_RIPPS2_GLYPHS' not in hg or 'UICFG_RIPPS2_HINTS,' not in hg:
    fail.append('dialogs.c: D-pad Glyphs and Button Hints are Hints and Glyphs rows')
if 'UICFG_RIPPS2_RECENTS' not in table('diaDeviceConfig'):
    fail.append('dialogs.c: Show Recents sits with the Starred Games rows on Game Sources')
if gui.count('if (ret == RIPPS2_HINTS_BUTTON) {') + gui.count('if (result == RIPPS2_HINTS_BUTTON) {') != 2:
    fail.append('gui.c: both Interface pages open Hints and Glyphs')
if gui.count('guiRipps2RecentsRead(') != 3:
    fail.append('gui.c: both Game Sources pages read Show Recents')
hints = rd('src/ripps2hints.c')
need(hints, (('guiRipps2HintRowsRead(diaHintsConfig);', 'Hints and Glyphs reads the two rows'), ('guiRipps2HintRowsSet(diaHintsConfig);', 'and shows them'),
             ('gRipps2UserSet = keepUserSet;', 'Back puts them back')), 'ripps2hints.c')

# Part 2: Language on Interface only; GSM Defaults on Game Launching only; the In-Game Menu page (IGR Path in it) under
# Game Launching; the read-ahead caches on Game Launching; prefix paths and HDD Spindown on Game Sources; Video Mode in
# Interface's Display section; Game Sources > Cache (Fast Cache, Cache Game List (HDD APA), Automatic Refresh)
general, launch, ui_t, disp, adv, igr, dev = (table(n) for n in ('diaConfig', 'diaLaunchConfig', 'diaUIConfig', 'diaDisplayConfig',
                                                                'diaAdvancedConfig', 'diaIgrConfig', 'diaDeviceConfig'))
for gone, where, text in (('UICFG_LANG', 'General', general), ('GENERAL_GSM_DEFAULTS_BUTTON', 'General', general),
                          ('RIPPS2_IGR_BUTTON', 'General', general), ('CFG_EXITTO', 'General', general),
                          ('DISPLAY_GSM_DEFAULTS_BUTTON', 'Display', disp), ('UICFG_VMODE', 'Interface', ui_t),
                          ('UICFG_AUTOREFRESH', 'Interface', ui_t), ('CFG_BDMPREFIX', 'Advanced', adv), ('CFG_BDMCACHE', 'Advanced', adv),
                          ('CFG_HDDGAMELISTCACHE', 'Advanced', adv)):
    if gone in text:
        fail.append('dialogs.c: %s is still on %s (the settings moves)' % (gone, where))
for want, where, text in (('UICFG_LANG', 'Interface', ui_t), ('LAUNCH_GSM_DEFAULTS_BUTTON', 'Game Launching', launch),
                          ('RIPPS2_IGR_BUTTON', 'Game Launching', launch), ('CFG_EXITTO', 'In-Game Menu', igr),
                          ('CFG_BDMCACHE', 'Game Launching', launch), ('CFG_SMBCACHE', 'Game Launching', launch),
                          ('CFG_BDMPREFIX', 'Game Sources', dev), ('CFG_HDDSPINDOWN', 'Game Sources', dev),
                          ('RIPPS2_CACHE_BUTTON', 'Game Sources', dev), ('UICFG_VMODE', 'Display', disp), ('CFG_DEBUG', 'Advanced', adv)):
    if want not in text:
        fail.append('dialogs.c: %s belongs on %s' % (want, where))
cache = table('diaCacheConfig')
for want in ('CFG_RIPPS2_FASTCACHE', 'CFG_HDDGAMELISTCACHE', 'UICFG_AUTOREFRESH'):
    if want not in cache:
        fail.append('dialogs.c: Game Sources > Cache needs %s' % want)
need(gui, (('ret = diaExecuteDialog(diaDisplayConfig, -1, 1, &guiSettingsDisplayUpdater);', "Video Mode shows on the Display section (build 114: Interface's Screen page)"),
           ('if (lock != bootLockWas)\n        ripps2BootLockApply(lock);', 'BOOT LOCK is set when its page closes (build 116: EXIT follows the lock, the IGR Path is no longer filled in)'),
           ('static int guiShowCacheConfig(void)', 'the Cache page (build 115: says whether a setting changed, for STATUS)'), ('guiSaveAdvancedSettings(ui); // build 113: the read-ahead caches', 'Game Launching keeps the caches')), 'gui.c')
if gui.count('        guiShowCacheConfig();') != 2:  # build 115: guiShowCacheSettings (STATUS) calls it too
    fail.append('gui.c: both Game Sources pages open the Cache page')
need(rd('src/ripps2shot.c'), (('guiExitPathBegin(diaIgrConfig);', 'the In-Game Menu page shows IGR Path'), ('guiExitPathEnd();', 'and keeps it')), 'ripps2shot.c')
sb = rd('src/supportbase.c')
need(sb, (('    if (!gRipps2FastCache)\n        return 0;', 'Fast Cache off reads the source first'),
          ('if (!readOk || !gEnableWrite || !gRipps2FastCache || gamecount > SB_SNAP_MAX)', 'and keeps no list')), 'supportbase.c')
need(opl, (('configSetInt(configOPL, "ripps2_fastcache", gRipps2FastCache);', 'Fast Cache is kept'),), 'opl.c')

# RIPDISC's SELECT hold (the user's note): notches that fill, not a squiggly line, and clear of HOLD
disc = rd('src/ripps2disc.c')
need(disc, (('#define RD_NOTCHES 12', 'the hold fills notches'),
            ('float fill = p * RD_NOTCHES - i; // 1: lit, 0..1: filling, below 0: still to come', 'the one filling fades in'),
            ('hx = x + w / 2 - (RD_RING_W + 6 + ripps2HintWidth(hold)) / 2;', 'the ring has its own room in the hint (build 117: in the box flush with the bar)'),
            ('ripps2HintText(hx + RD_RING_W + 6, y + 90, hold, rdAlpha(RD_SOFT, ia));', 'HOLD starts after the ring (build 114: on the launch guard frame)')), 'ripps2disc.c')
if 'rmDrawLine(cx + (int)(r * cosf(a0))' in disc:
    fail.append('ripps2disc.c: the old 1 px ring is still drawn')

# The trim (the user: "nuetrino and bible stay ... cut the other fat"; "keep credits in the repo as we are still
# utilizing the pointers"): Ember and POPSTARTER found and launched, no longer carried; their credits stay
repo = Path(__file__).resolve().parents[2]
for gone, where, text in (('ember_elf.o', 'Makefile', mk), ('popstarter_elf.o', 'Makefile', mk),
                          ('ember_elf_gz', 'ripps2ember.c', rd('src/ripps2ember.c')), ('popstarter_elf_bin', 'ripps2ember.c', rd('src/ripps2ember.c')),
                          ('ripps2EmberInstall', 'ripps2.h', rd('include/ripps2.h')), ('ripps2PopstarterInstall', 'ripps2.h', rd('include/ripps2.h')),
                          ('ACT_EMBER_INSTALL', 'ripps2status.c', rd('src/ripps2status.c')), ('ACT_POPS_INSTALL', 'ripps2status.c', rd('src/ripps2status.c')),
                          ('hddInstallBundledPopstarter', 'hddsupport.c', rd('src/hddsupport.c')),
                          ('ember/ember.elf', 'elf/build.sh', (repo / 'elf/build.sh').read_text(encoding='utf-8')),
                          ('popstarter/POPSTARTER.ELF', 'elf/build.sh', (repo / 'elf/build.sh').read_text(encoding='utf-8'))):
    if gone in text:
        fail.append('%s: %s is still there (the trim)' % (where, gone))
need(mk, (('neutrino_tgz.o', 'Neutrino stays carried'), ('bible_xlf.o', 'BIBLE stays carried')), 'Makefile')
# build 114: the launch legs call RiptOPL's cueResolveEmber themselves (113's cueEnsureEmber was only its alias)
need(rd('src/bdmsupport.c'), (('if (!cueResolveEmber(ps1Prefix, emberElf, sizeof(emberElf)))', 'a launch uses the drive\'s own Ember'),), 'bdmsupport.c')
if 'cueEnsureEmber' in rd('src/cuesupport.c') + rd('include/cuesupport.h'):
    fail.append('cuesupport: the cueEnsureEmber alias is back')
need(rd('src/ripps2about.c'), (('N_("Ember by Gageformer")', 'Ember stays credited'), ('github.com/Gageformer/Ember/releases', 'with its release page'),
                               ('N_("POPSTARTER by krHACKen")', 'POPSTARTER stays credited')), 'ripps2about.c')
readme = (repo / 'README.md').read_text(encoding='utf-8')
need(readme, (('[Ember](https://github.com/Gageformer/Ember/releases) by Gageformer', 'the README credits Ember'),
              ('[POPSTARTER](https://www.psx-place.com/resources/popstarter.683/) by krHACKen', 'and POPSTARTER')), 'README.md')
for p in ('elf/ember/README.md', 'elf/popstarter/README.md'):
    if not (repo / p).exists():
        fail.append('%s: the credit and where to get it stay in the repo' % p)

lang = Path(__file__).resolve().parents[1] / 'lang'
for p in sorted(lang.glob('[!_]*.yml')):
    t = p.read_text(encoding='utf-8')
    for key in ('\n  Across the Top: ', '\n  Sidebar: ', '\n  RIPPS2_CATEGORY_LAYOUT: ', '\n  HINT_RIPPS2_CATEGORY_LAYOUT: '):
        if key not in t:
            fail.append('%s: %s untranslated' % (p.name, key.strip(' \n:')))

print('\n'.join(fail) or 'build113: the category sidebar (glyphs in the bar, drawers, focus, hints) OK')
sys.exit(1 if fail else 0)
