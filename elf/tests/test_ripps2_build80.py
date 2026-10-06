"""Build 80: STATUS and the settings moves, Source Name's Pop In, the Coverflow / Grid source button,
YOUR ACCOUNT, and the grid's one-cover tilt.

Static checks on the patched tree; the order of the Colors and More and Network rows is read from the
dialog tables themselves."""
import os, re, sys
from pathlib import Path
root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text()
ms, gui, dia, th, ui = rd('src/menusys.c'), rd('src/gui.c'), rd('src/dialogs.c'), rd('src/themes.c'), rd('src/ripps2ui.c')
ra, net, st = rd('src/ripps2ra.c'), rd('src/ranet.c'), rd('src/ripps2status.c')
fail = []

def table(src, name):
    i = src.index('struct UIItem %s[] = {' % name)
    return src[i:src.index('{UI_TERMINATOR}', i)]

# --- the main menu: STATUS where ACHIEVEMENTS was; ACHIEVEMENTS last of the Settings pages
mm = ms[ms.index('static void menuInitMainMenu(void)'):]
mm = mm[:mm.index('\n}\n')]
if 'MENU_STATUS' not in mm or 'MENU_ACHIEVEMENTS' in mm:
    fail.append('the main menu must offer STATUS in place of ACHIEVEMENTS')
if 'ripps2Status();' not in ms:
    fail.append('MENU_STATUS must open ripps2Status')
idx = gui[gui.index('static int guiSettingsShowIndex(int *page)'):]
idx = idx[:idx.index('\n}\n')]
if '_l(_STR_AUDIO_SETTINGS),\n#ifdef RETROACHIEVEMENTS\n        _l(_STR_RIPPS2_ACHIEVEMENTS)' not in idx or 'ripps2Achievements();' not in idx:
    fail.append('Settings must list Achievements right after Audio and open it')
if 'labels[SETTINGS_PAGE_COUNT + 2]' not in idx:
    fail.append('the Settings index labels must have room for Achievements and Save')
for act in ('ripps2NeutrinoInstallTo(', 'ripps2PopstarterInstall(', 'ripps2EmberInstall(', 'ripps2BibleManage()',
            'guiShowNeutrinoDefaults()', 'guiShowPsEmulationSettings()', 'guiShowPopsNetConfig()'):
    if act not in st:
        fail.append('STATUS must reach %s' % act)

# --- Network: RIPPS2's rows under a header, the RA switches gone (they live on Achievements), a chin
nt = table(dia, 'diaNetConfig')
if 'NETCFG_RA_TELEMETRY' in nt or 'NETCFG_RA_BADGES' in nt:
    fail.append('the Network page must not carry the RA switches any more')
h = nt.find('{.label = {"RIPPS2", -1}}')
if h < 0 or nt.index('NETCFG_NBD_BUTTON') < h or nt.index('NETCFG_POPSTARTER_BUTTON') > h:
    fail.append('NBD and Cover Art sit under the RIPPS2 header, POPSTARTER network above it')
if not re.search(r'\{\.label = \{" ", -1\}\}\},\s*\{UI_BREAK\},\s*//[^\n]*\n\s*\{UI_BUTTON, NETCFG_OK', nt):
    fail.append('a clear chin row must sit right before the OK button')

# --- Colors and More: Source Name under the glyphs, the Color Theme heading the pickers
cm = table(dia, 'diaColorsConfig')
order = [cm.index(k) for k in ('UICFG_RIPPS2_GLYPHS', 'UICFG_RIPPS2_SRCNAME', 'UICFG_RIPPS2_HINTS')]
if order != sorted(order):
    fail.append('Source Name must follow the D-pad glyphs')
split = cm.index('{UI_SPLITTER}', cm.index('UICFG_RIPPS2_RECENTS'))
if not (split < cm.index('UICFG_RIPPS2_PALETTE') < cm.index('UICFG_TXTCOL')):
    fail.append('the Color Theme must head the colour pickers')

# --- Source Name: Pop In, and a theme's source_name=pop for its Shown
if '"Pop In"' not in gui or 'RIPPS2_SRC_COUNT' not in gui:
    fail.append('Source Name must offer Pop In')
if '"source_name"' not in th or 'gTheme->srcNamePop' not in ui:
    fail.append('source_name=pop must make Pop In the theme default')
if 'ripps2SourceToast(' not in th or 'void ripps2SourceToast(' not in ui:  # build 81: it plays as the view word
    fail.append('Pop In must name the source with the view word')

# --- Coverflow / Grid: the cancel button cycles the sources on the game list, not on the info page
main = ms[ms.index('void menuHandleInputMain()'):]
main = main[:main.index('\n}\n')]
c = main.find('menuSourceCycle();')
if c < 0 or c > main.index('getKeyOn(KEY_CROSS)') or 'folderDepth(support->mode) == 0' not in main:
    fail.append('the cancel button must cycle the sources on Coverflow / Grid, folders first')
info = ms[ms.index('void menuHandleInputInfo()'):]
if 'menuSourceCycle' in info[:info.index('\n}\n')]:
    fail.append('the info page keeps the cancel button as Back')
if '_STR_RIPPS2_SOURCE' not in th:
    fail.append('the hint row must say Source on Coverflow / Grid')

# --- YOUR ACCOUNT: what each check learnt is kept, gathered, and let go of on the way out
if 'RA/%s.inf' not in net:
    fail.append('a check must keep its title and counts as RA/<serial>.inf')
acct = ra[ra.index('static void raAccount(void)'):]
if '.inf' not in ra or 'free(games)' not in acct or 'KEY_START' not in acct:
    fail.append('YOUR ACCOUNT must read the .inf files, close with START, and free its list')

# --- the grid: only the chosen cover tips
g = th[th.index('static void drawGrid(struct menu_list'):]
g = g[:g.index('\n}\n')]
if g.count('ripps2TiltBegin(selX, selY') + g.count('ripps2TiltBeginTurn(selX, selY') != 1 or 'ripps2TiltEnd();' not in g:  # build 82: the turn variant
    fail.append('on a Grid only the chosen cover may tilt')

print('\n'.join(fail) or 'build80: STATUS, settings moves, Pop In, source button, account, grid tilt OK')
sys.exit(1 if fail else 0)
