"""Build 142: Save Settings To stays. A settings file beside RIPPS2.ELF no longer beats the pointer, the row starts the drive it
is asked for, MMCE opens its real root, and Fast Boot's gate names a drive by its type.

Static checks on the patched tree; the behaviour is in the lab table in CHANGELOG.md."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
opl = (root / 'src/opl.c').read_text(encoding='utf-8')
ui = (root / 'src/ripps2ui.c').read_text(encoding='utf-8')
hdr = (root / 'include/opl.h').read_text(encoding='utf-8')
fail = []


def body(text, name):
    a = text.find(name)
    return text[a:text.find('\n}\n', a)] if a >= 0 else ''


# ---- the pointer goes ahead of a file beside the ELF, in the menu and in autolaunch
first = body(opl, 'static int ripps2PointerFirst(')
for want, why in (('bootHomeHasRiptoplMaster(home)', 'only when a file beside the ELF would hide the pointer: otherwise tryAlternateDevice follows it, once'),
                  ('readConfigPathRedirect(redirect, sizeof(redirect))', 'it reads the pointer'),
                  ('gBootHomeApa', 'APA keeps its own ownership chain'),
                  ('!strncmp(home, "hdd", 3)', 'no file open through raw APA space'),
                  ('prepareCustomSettingsPath(redirect, sizeof(redirect)) < 0', "the drive is brought up, and one that does not answer leaves the home alone"),
                  ('snprintf(prevHome, prevSize, "%s", home);', 'the home is copied before configSetMove overwrites it'),
                  ('configSetMove(redirect);', 'and the settings are read from the drive')):
    if want not in first:
        fail.append('ripps2PointerFirst: %s' % why)
if first.find('snprintf(prevHome') > first.find('configSetMove(redirect)'):
    fail.append('ripps2PointerFirst copies the home first')

load = body(opl, 'static void _loadConfig()')
a, b = load.find('ripps2PointerFirst(prevHome, sizeof(prevHome))'), load.find('int result = configReadMulti(lscstatus);')
if a < 0 or b < 0 or a > b:
    fail.append('_loadConfig asks ripps2PointerFirst before its first read')
if 'if (fromCard && !(result & CONFIG_OPL)) {' not in load or 'configSetMove(prevHome);' not in load:
    fail.append('_loadConfig reads the old home when the chosen drive has nothing')
if 'ripps2CardSettingsHome(cardHome, sizeof(cardHome), 1)' not in load:
    fail.append('_loadConfig still reads the card first with no pointer')

mini = body(opl, 'static void miniInit(int mode)')
a, b = mini.find('ripps2PointerFirst(pointerHome, sizeof(pointerHome))'), mini.find('configReadMulti(CONFIG_ALL)')
if a < 0 or b < 0 or a > b or 'configSetMove(pointerHome);' not in mini:
    fail.append('miniInit lands on the same settings as the menu')

# ---- Fast Boot
ready = body(opl, 'static int fastBootHomeReady(')
if 'if (!strncmp(home, "mass", 4))\n        return 0;'.replace('\n', '\r\n' if '\r\n' in ready else '\n') not in ready:
    fail.append("Fast Boot: a gate naming a slot is passed over, so the pointer decides")
if 'isTypedBdmSettingsPath(home)' not in ready or 'prepareCustomSettingsPath(home, size) >= 0' not in ready:
    fail.append('Fast Boot: a typed drive is brought up before it is read')
if 'fastBootHomeReady(fbHome, sizeof(fbHome))' not in load:
    fail.append('_loadConfig asks fastBootHomeReady')
if 'isTypedBdmSettingsPath(gCustomSettingsPath) ? gCustomSettingsPath : configGetHomePath()' not in body(opl, 'static void fastBootWrite(void)'):
    fail.append('the gate names a drive by its type, as config.path does')

# ---- the row
bdm = body(ui, 'static int ripps2SettingsBdmHome(')
if 'bdmResolveBootDir(root, sizeof(root), "", &known) > 0' not in bdm or 'snprintf(root, sizeof(root), "%s:/", typed);' not in bdm:
    fail.append('the row starts a BDM drive through the typed resolver')
hdd = body(ui, 'int ripps2SettingsHddHome(')
if not (0 <= hdd.find('ripps2SettingsBdmMounted(BDM_TYPE_ATA') < hdd.find('pfs:/RIPPS2') < hdd.find('ripps2SettingsBdmHome(BDM_TYPE_ATA')):
    fail.append('Internal HDD: a mounted exFAT drive, then APA, and only then a wait for ATA')
mmce = body(ui, 'static int ripps2SettingsMmceHome(')
if 'prepareMmceSettingsPath(dir) <= 0' not in mmce or 'opendir' in mmce:
    fail.append('MMCE: the driver loads and the card is waited for, as the boot and the save do')
if 'int prepareMmceSettingsPath(const char *path);' not in hdr or 'static int prepareMmceSettingsPath' in opl:
    fail.append('prepareMmceSettingsPath is shared')
if '"mmce%d:", slot' in ui:
    fail.append('no bare mmceN: root in the row')

end = body(ui, 'void ripps2SettingsHomeEnd(')
if 'guiHandleDeferedIO(&ripps2HomeBusy, _t("Starting that drive..."), IO_CUSTOM_SIMPLEACTION, &ripps2HomeWork, OPL_DEFERRED_IO_TIMEOUT_MS);' not in end:
    fail.append('the drive starts on the IO worker, with the wait bounded')
if 'ripps2SettingsDriveHome(' in end:
    fail.append('no driver load on the main thread')
if 'ripps2SettingsHomeOf(gCustomSettingsPath) == mode && strncmp(gCustomSettingsPath, "mass", 4)' not in end:
    fail.append('a row left on its drive does not wait for it')
if 'ripps2HomeBusy = 0;' not in body(ui, 'static void ripps2HomeWork(void)'):
    fail.append('the worker lets the wait end')

if fail:
    print('\n'.join('FAIL: ' + f for f in fail))
    sys.exit(1)
print('build 142 ok')
