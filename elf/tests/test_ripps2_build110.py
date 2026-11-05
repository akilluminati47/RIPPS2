"""Build 110: every source quick to list, and Save Settings To on every drive. Build 109's MMCE card list became every
source's (supportbase.c: the list read last time is kept on the source as RIPPS2.LST, shown the moment the source
answers, and the source is read again on its next idle pass): MMCE, every BDM drive (USB, exFAT HDD, MX4SIO, iLink) and
SMB. An MX4SIO scan pauses for the pads as an MMCE one does. The APA HDD's own list cache is on by default (once for
older configs) and checked against the APA table on the next idle pass. Save Settings To: Memory Card, Internal HDD, USB
Drive, MX4SIO, iLink, MMCE, Custom Path.

Static checks on the patched tree."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
sb, sbh, mmce, bdm, bdmh, eth, hdd, opl, ui = (rd('src/supportbase.c'), rd('include/supportbase.h'), rd('src/mmcesupport.c'),
                                              rd('src/bdmsupport.c'), rd('include/bdmsupport.h'), rd('src/ethsupport.c'),
                                              rd('src/hddsupport.c'), rd('src/opl.c'), rd('src/ripps2ui.c'))
fail = []


def need(text, items, where):
    for s, why in items:
        if s not in text:
            fail.append('%s: %s' % (where, why))


def body(text, head):
    i = text.index(head)
    return text[i:text.index('\n}\n', i)]


# ---- the shared list
need(sbh, (('} sb_snap_t;', 'sb_snap_t (tried, shown, sum)'),
           ('int sbSnapShow(sb_snap_t *snap, const char *prefix, base_game_info_t **list, int *gamecount, int *fsize);', 'sbSnapShow'),
           ('void sbSnapScanned(sb_snap_t *snap,', 'sbSnapScanned'), ('void sbSnapForget(sb_snap_t *snap);', 'sbSnapForget'),
           ('void sbSetPadBreath(int on);', 'sbSetPadBreath')), 'supportbase.h')
need(sb, (('#define SB_SNAP_FILE  "RIPPS2.LST"', "the list is RIPPS2.LST, beside the source's CD and DVD folders (build 109's name)"),
          ('#define SB_SNAP_MAGIC "RIPLST01"', "build 109's MMCE lists still read"),
          ('h.itemSize == (int)sizeof(base_game_info_t)', 'a list written by another build (another entry size) is not used'),
          ('if (sum == snap->sum)\n        return;', 'an unchanged list is not written again'),
          ('if (!readOk || !gEnableWrite || !gRipps2FastCache || gamecount > SB_SNAP_MAX)', 'a failed read, Write Operations Off (or Fast Cache off, build 113) writes nothing'),
          ('remove(path);', 'a source with no games left drops its list')), 'supportbase.c')
show = body(sb, 'int sbSnapShow(')
if 'if (snap->tried)\n        return 0;\n    snap->tried = 1;' not in show:
    fail.append('sbSnapShow: a source is looked for once, until it is forgotten')
if 'free(*list);' not in show or 'snap->shown = ok = 1;' not in show:
    fail.append('sbSnapShow: the last list replaces the (empty) one as sbReadList publishes, and is marked shown')
breath = body(sb, 'static void sbPadBreath(')
if 'sbBreathAll ||' not in breath or 'strncmp(path, "mmce", 4)' not in breath:
    fail.append('sbPadBreath: MMCE always, and any scan while sbSetPadBreath is on')

# ---- MMCE on it (build 109's card list)
need(mmce, (('static sb_snap_t mmceSnap;', 'the card list is the shared one'),
            ('sbSnapShow(&mmceSnap, mmcePrefix, &mmceGames, &mmceGameCount, &mmceULSizePrev)', 'shown at once'),
            ('sbSnapScanned(&mmceSnap, mmcePrefix, mmceGames, mmceGameCount, mmceULSizePrev,', 'kept after a read'),
            ('sbSnapForget(&mmceSnap);', 'forgotten with the card'),
            ('        mmceSnap.shown = 0;\n', 'the forced read happens once (a PS1 view no longer rescans on every poll)')), 'mmcesupport.c')
if 'mmceListLoad' in mmce or 'MMCE_LIST_FILE' in mmce:
    fail.append("mmcesupport.c: build 109's own copy of the list code is gone")

# ---- every BDM drive
need(bdmh, (('sb_snap_t bdmSnap;', "each drive's last list"), ('#include "include/supportbase.h"', 'sb_snap_t')), 'bdmsupport.h')
upd = body(bdm, 'static int bdmUpdateGameList(')
need(upd, (("if (sub[0] == '\\0' && sbSnapShow(&pDeviceData->bdmSnap, pDeviceData->bdmPrefix, &pDeviceData->bdmGames,", 'the root list at once'),
           ('sbSetPadBreath(pDeviceData->bdmDeviceType == BDM_TYPE_SDC);', 'an MX4SIO scan pauses for the pads'),
           ('sbSetPadBreath(0);', 'and stops pausing after'),
           ('sbSnapScanned(&pDeviceData->bdmSnap, pDeviceData->bdmPrefix, pDeviceData->bdmGames, pDeviceData->bdmGameCount,', 'kept after a root read')),
     'bdmUpdateGameList')
if upd.index('sbSnapShow(') > upd.index('sbReadList('):
    fail.append('bdmUpdateGameList: the last list comes before the scan')
nu = body(bdm, 'static int bdmNeedsUpdate(')
i_force, i_snap, i_gate = nu.index('pDeviceData->ForceRefresh != 0'), nu.index('if (pDeviceData->bdmSnap.shown) {'), nu.index('pDeviceData->bdmDeviceTick == BdmGeneration &&')
if not i_force < i_snap < i_gate or 'pDeviceData->bdmSnap.shown = 0;\n        return 1;' not in nu:
    fail.append('bdmNeedsUpdate: a list shown from the drive forces one read, ahead of the per-generation gate')
if 'sbSnapForget(&pDeviceData->bdmSnap); // RIPPS2 build 110: the next drive here' not in nu:
    fail.append('bdmNeedsUpdate: a drive taken out forgets its list')
if bdm.count('sbSnapForget(&') < 3:
    fail.append('bdmsupport.c: the list is forgotten at init, on a new games folder and on removal')

# ---- SMB
need(eth, (('static sb_snap_t ethSnap;', "the share's last list"),
           ('if (sbSnapShow(&ethSnap, ethPrefix, &ethGames, &ethGameCount, &ethULSizePrev)) {', 'shown at once'),
           ('ethGameList.updateDelay = MENU_UPD_DELAY_GENREFRESH;', 'the share joins the idle poll until it has been read'),
           ('ethGameList.updateDelay = ETH_MODE_UPDATE_DELAY;', 'and leaves it after'),
           ('sbSnapScanned(&ethSnap, ethPrefix, ethGames, ethGameCount, ethULSizePrev,', 'kept after a read'),
           ('    if (ethSnap.shown) {\n        ethSnap.shown = 0;\n        return 1;\n    }', 'a list shown from the share forces one read')), 'ethsupport.c')
if eth.count('sbSnapForget(&ethSnap);') < 3:
    fail.append('ethsupport.c: the list is forgotten on init, reconnect and a new share')

# ---- the APA HDD
need(hdd, (('static unsigned char hddCacheVerify;', 'the cache-was-shown flag'),
           ('hddCacheVerify = 1;\n        hddGameList.updateDelay = MENU_UPD_DELAY_GENREFRESH;', 'the cache shows at once and joins the idle poll'),
           ('hddCacheVerify = 0;\n            hddGameList.updateDelay = HDD_MODE_UPDATE_DELAY;', 'after one APA read, refreshes are on request again')), 'hddsupport.c')
need(opl, (('gHDDGameListCache = 1; // RIPPS2 build 110', 'the APA cache is on by default'),
           ('if (!configGetInt(configOPL, "ripps2_hddcache_v", &value) || value < 110)\n                gHDDGameListCache = 1;', 'once for older configs'),
           ('configSetInt(configOPL, "ripps2_hddcache_v", 110);', 'the one-time switch is recorded')), 'opl.c')

# ---- Save Settings To on every drive
need(ui, (('RIPPS2_HOME_USB, RIPPS2_HOME_MX4SIO, RIPPS2_HOME_ILINK, RIPPS2_HOME_MMCE, RIPPS2_HOME_CUSTOM', 'the choices, Custom Path last'),
          ('{N_("Memory Card"), N_("Internal HDD"), N_("USB Drive"), "MX4SIO", "iLink", "MMCE", N_("Custom Path"), NULL}', 'their names'),
          ('return ripps2SettingsBdmHome(BDM_TYPE_USB, "usb0", out, size);', 'USB by its type'),
          ('return ripps2SettingsBdmHome(BDM_TYPE_SDC, "mx4sio0", out, size);', 'MX4SIO by its type'),
          ('return ripps2SettingsBdmHome(BDM_TYPE_ILINK, "ilink0", out, size);', 'iLink by its type'),
          ('snprintf(dir, sizeof(dir), "mmce%d:/RIPPS2", slot);', "MMCE: a RIPPS2 folder on the card in either slot"),
          ('THAT DRIVE IS NOT CONNECTED: SETTINGS STAY WHERE THEY ARE', 'a drive not there: say so, change nothing')), 'ripps2ui.c')
hints = ui[ui.index('static const char *ripps2HomeHints[]'):ui.index('NULL};', ui.index('static const char *ripps2HomeHints[]'))]
if hints.count('N_("') != 7:
    fail.append('ripps2ui.c: every choice has its own hint')
for typed, mode in (('usb0', 'USB'), ('mx4sio0', 'MX4SIO'), ('ilink0', 'ILINK')):
    if '!strcmp(path, "%s:/RIPPS2"))\n        return RIPPS2_HOME_%s;' % (typed, mode) not in ui:
        fail.append('ripps2ui.c: %s:/RIPPS2 reads as its choice' % typed)
need(opl, (('int prepareMmceSettingsPath(const char *path)', 'an MMCE settings home'),  # build 142: shared with the row
           # build 115: the root as mmceman opens it (mmce0:/), and up to 8 s while the card says it is busy
           ('mmceLoadModules();\n    for (tries = 0; tries < 40; tries++)', "its driver loaded at boot, with an MMCE boot's wait"),
           ('if (!strncmp(path, "mmce", 4))\n        return prepareMmceSettingsPath(path);', 'used for an mmce path')), 'opl.c')

# ---- the info page: a game reached with the d-pad gets its size
menusys = rd('src/menusys.c')
i_nav = menusys.index('// RIPPS2 build 101 gave RIPFLOW')
nav = menusys[i_nav - 600:menusys.index('ripps2StepCategory(-1); // RIPPS2 build 69', i_nav)]
if nav.count('menuInfoSizeAfterMove();') != 4 or 'static void menuInfoSizeAfterMove(void)' not in menusys:
    fail.append("menusys.c: Up, Down, Left and Right on the info page ask for the new game's size (it read 0 MiB)")

print('\n'.join(fail) or 'build110: every source shows its last list at once and reads again; MX4SIO pauses for the pads; the APA cache '
      'on and checked; Save Settings To on USB, MX4SIO, iLink and MMCE OK')
sys.exit(1 if fail else 0)
