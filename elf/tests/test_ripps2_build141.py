"""Build 141: Manage's BIBLE menu as a Settings page with a tip on every row, the cursor kept, changes written once through a
temporary file, Sky Color, Boot Sound, and launch keys chosen with the Memory Files browser.

Static checks on the patched tree."""
import os
import re
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
boot = (root / 'src/ripps2boot.c').read_text(encoding='utf-8')
ed = (root / 'src/ripps2edit.c').read_text(encoding='utf-8')
fb = (root / 'src/ripps2files.c').read_text(encoding='utf-8')
ui = (root / 'src/ripps2ui.c').read_text(encoding='utf-8')
fail = []


def body(text, name):
    a = text.find(name)
    return text[a:text.find('\n}\n', a)] if a >= 0 else ''


# the page: the Set Metadata look, and the tip above the hints
pg = body(ed, 'static void pgDraw(void)')
for want in ('fntRenderString(RIPPS2_DIA_FONT, 20, 16, ALIGN_NONE, 0, 0, pgView.title, gTheme->selTextColor);',
             'rmDrawLine(20, 46, 620, 46, gColWhite);',
             'mdTip(cur->tip, ED_X + 4, tipY + 12, ED_RIGHT - ED_X - 8);'):
    if want not in pg:
        fail.append('the page has %s' % want)
page = body(ed, 'int ripps2Page(')
if '*cursor = c;' not in page or 'c = c > 0 ? c - 1 : count - 1;' not in page:
    fail.append('the page keeps the cursor and goes round as Settings does')

# every setting has a tip
s = boot.find('static const blSet_t blSets[] = {')
keys = re.findall(r'^\s*\{"([A-Z_]+)",', boot[s:boot.find('};', s)], re.M)
t = boot.find('} blTips[] = {')
tips = boot[t:boot.find('};', t)]
for k in keys:
    if k != 'BIBLE_COLOR' and '{"%s", N_("' % k not in tips:
        fail.append('%s has a tip' % k)

menu = body(boot, 'static void blBibleMenu(int boot, int removed)')
for want in ('ripps2Page(_t("BIBLE\'s Settings"), rows, n, &cursor, &action)', 'kind[n] = BLR_SKY;', 'kind[n] = BLR_BOOT;', 'kind[n] = BLR_KEYS;',
             'blBootSoundClose(bootChanged);', '_t("UPDATE BIBLE: SLOT %d HAS AN OLDER ONE")', '_t("SET UP, UPDATE OR RESTORE BIBLE")',
             '_t("EDIT BIBLE\'S SETTINGS FILE")', 'ripps2EditFile(blSetPath);', 'blIniEdit("BIBLE_COLOR", 0, state >= 0 ? text : NULL, NULL)'):
    if want not in menu:
        fail.append('the page has %s' % want)
if 'int cursor = 0' not in menu.replace('cursor = 0', 'int cursor = 0') or 'cursor = 0' in menu[menu.find('while (1) {'):]:
    fail.append('the cursor is set once, before the page\'s loop')

# written once, through a temporary file
fl = body(boot, 'static int blIniFlush(void)')
for want in ('blWrite(tmp, blText, n) == 0', '!memcmp(blOut, blText, n)', 'remove(blSetPath);', 'blMcRename(blSetPath[2] - \'0\', tmp + 5, strrchr(blSetPath, \'/\') + 1)'):
    if want not in fl:
        fail.append('the safe write has %s' % want)
if fl.find('!memcmp(blOut, blText, n)') > fl.find('remove(blSetPath);'):
    fail.append('the temporary file is read back before the old one goes')
if 'blWrite' in body(boot, 'static int blIniEdit('):
    fail.append('a change stays in memory until the page closes')

rc = body(boot, 'static void blIniRecover(void)')
if 'stat(' in rc or 'blRead(blSetPath) >= 0' not in rc or rc.find('blRead(blSetPath) >= 0') > rc.find('blMcRename('):
    fail.append('the recovery opens the files themselves: stat said a missing file on a card was there, and the only copy went')

# launch keys
for want in ('static const char *const blKeyIds[BL_KEYS] =', 'ripps2FilesPick(_t("CHOOSE A PROGRAM"), text, sizeof(text), &bdmType)',
             '"$OSDSYS"', '"$CDVD"', '"$CDVD_NO_PS2LOGO"', '"$CREDITS"', 'static int blPickedPath(', 'static void blArgsMenu(',
             'gOPLPart[0] != \'\\0\' && snprintf(out, size, "%s:pfs:/%s", gOPLPart'):
    if want not in boot:
        fail.append('launch keys have %s' % want)
ps = body(boot, 'static int blPathSet(')
if 'blPathsInFile() <= 1' not in ps:
    fail.append('the last path stays: a file with none sends BIBLE to its rescue mode')
km = body(boot, 'static void blKeyMenu(')
if 'strstr(blText, BL_MARKER) != NULL' not in km or 'rows[0].confirm = locked ? NULL : _t("EDIT");' not in km:
    fail.append('BOOT LOCK\'s lines only show')
if 'blBuildMisses(vals[e])' not in km:
    fail.append('a path this BIBLE cannot reach says so')

# the browser picks
pk = body(fb, 'int ripps2FilesPick(')
for want in ('fbPicking = 1;', 'ripps2RenderFiles();', 'ripps2HandleInputFiles();', 'fbPicking = 0;', 'fbOpenPath(savedPath,', 'bdmSlotDeviceType(out[4] - \'0\')'):
    if want not in pk:
        fail.append('the pick has %s' % want)
hi = body(fb, 'static void fbPickInput(')
if 'fbPickDone = 1;' not in hi or 'fbPickDone = -1;' not in hi or 'fbRunElf' in hi or 'ripps2ShotRolls' in hi:
    fail.append('an ELF is the choice, not a launch')

# the sky
if 'void ripps2ThemeSky(int p, char *out, size_t size)' not in ui or 'skyText(tinted, hue, sat, lift, out, size);' not in body(ui, 'void ripps2BibleSky('):
    fail.append('a Color Theme\'s sky is made as RIPPS2\'s own is')

print('\n'.join(fail) or 'build141: the BIBLE page and its tips, the safe write, Sky Color, launch keys from the browser OK')
sys.exit(1 if fail else 0)
