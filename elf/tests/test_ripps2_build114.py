"""Build 114: RiptOPL 57c45b4 merged; the launchers RIPPS2 does not carry, found and remembered (ripps2seance.c); STATUS
with the drives first; All Games from a master list; Hide Game and Hidden Games; Delete with everything of a game
behind the APA table check; Neutrino named beside RiptOPL; one RIPPS2.elf (no lite variant); FreeType with the modules
RIPPS2 reads; the compiled-in fonts stripped.

Static checks on the patched tree, then two pieces compiled on the PC: the APA check against synthetic disks (a good
table, one written from a bigger disk, a partition too big for the disk, one off its alignment, a broken link, a
chain that does not close) and the master list's save and load (a round trip; a damaged or short file is not read)."""
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from r2src import unwrap, TR_STUBS  # noqa: E402

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
repo = Path(__file__).resolve().parents[2]
rd = lambda p: unwrap((root / p).read_text(encoding='utf-8').replace('\r\n', '\n'))
raw = lambda p: (root / p).read_text(encoding='utf-8').replace('\r\n', '\n')
fail = []


def need(text, items, where):
    for s, why in items:
        if s not in text:
            fail.append('%s: %s' % (where, why))


def body(text, head):
    i = text.index(head)
    return text[i:text.index('\n}\n', i) + 3]


# ---- the merge
up = (repo / 'elf/RIPTOPL_UPSTREAM').read_text(encoding='utf-8').split()
if up[0] != '57c45b4fcc922ba00fed949c634caea0a2900c63' or up[1] != '4224':
    fail.append('RIPTOPL_UPSTREAM must name rebuild/main 57c45b4 (revision 4224)')
pad = rd('ee_core/src/padhook.c')
thread = pad[pad.index('static void IGR_Thread(void *arg)'):]
need(thread, (('while (Pad_Data.combo_type == 0x00 && !IGR_MenuOpen)', 'the IGR thread waits for the handler\'s latch or the menu'),
              ('choice = IGR_MenuRun(IGR_PadButtons);', 'the in-game menu still runs in it')), 'padhook.c')
if 'IGR_VBLANK_HANDLER' in pad or 'IGR_Poll_Alarm' in pad:
    fail.append('padhook.c: the alarm sampler is gone with upstream (#984): the VBLANK handler in every build')
tex = rd('include/textures.h')
if 'L1_ICON,          // Settings peer-page navigation hint' in tex or 'PSBBN_BACKGROUND' not in tex or 'RIPPS2_SIDEBAR_ICONS' not in tex:
    fail.append('textures.h: one L1/R1, both sides\' entries')
for leg in ('src/bdmsupport.c', 'src/hddsupport.c', 'src/mmcesupport.c', 'src/ethsupport.c', 'src/udpfssupport.c'):
    if 'cueEnsureEmber' in rd(leg):
        fail.append('%s: the launch legs call RiptOPL\'s cueResolveEmber' % leg)

# ---- SEANCE
sh = rd('include/ripps2seance.h')
need(sh, (('int seanceHook(int what, int mode, const char *devPrefix, char *path, int pathSize) __attribute__((weak));',
           'one weak way in, NULL in RiptOPL\'s host harnesses'),), 'ripps2seance.h')
se = rd('src/ripps2seance.c')
need(se, (('launchers.txt', 'remembered beside the settings'),
          ('"usb" : t == BDM_TYPE_ATA ? "ata" : t == BDM_TYPE_SDC ? "mx4sio" : t == BDM_TYPE_ILINK ? "ilink"', 'a drive by its kind, not its slot'),
          ('if (!gSeanceLaunching || what < 0', 'the hook does nothing outside a launch'),
          ('"CD", "DVD", "ART", "CFG", "VMC"', 'the search skips the game and art folders'),
          ('void seancePreLaunch(item_list_t *support, int id)', "Ember's files copied before the launch"),
          ('has[3] || (n >= 6 && !strncasecmp(dir + n - 6, "EMBER/", 6))', 'a bios.bin is Ember\'s only beside ember.elf or in an EMBER folder')), 'ripps2seance.c')
walk = body(se, 'static int seRoots(')
if 'opendir(more[k])' not in walk or 'bdmEnsure' in walk or 'LoadModules' in walk:
    fail.append('seRoots: only drives already started are searched (nothing is loaded to look)')
vcd = rd('src/vcdsupport.c')
res = body(vcd, 'int vcdResolvePopstarter(const char *devPrefix, char *out, int outSize)')
if res.index('vcdResolveCustomPopstarter()') > res.index('SEANCE_MODE_LOOKUP') or res.index('SEANCE_MODE_LOOKUP') > res.index('vcdResolvePopstarterMcElf(out, outSize)'):
    fail.append('POPSTARTER: Settings\' path and the game\'s drive first, then where SEANCE found it, then the cards')
need(vcd, (('seanceHook != NULL && seanceHook(SEANCE_POPS, SEANCE_MODE_LOOKUP', 'RIPPOPS copies from where SEANCE found the POPS files'),
           ('snprintf(src, sizeof(src), "%s%s", from, vcdPopsFiles[i]); // build 114: from is the folder', 'the copy reads the folder found')), 'vcdsupport.c')
sb = rd('src/supportbase.c')
nr = body(sb, 'const char *sbResolveNeutrinoPath(const char *activePrefix)')
if not (nr.index('sbProbeNeutrinoMc()') < nr.index('SEANCE_MODE_LOOKUP') < nr.index('SEANCE_MODE_LAST') < nr.index('ripps2NeutrinoMissing(')):  # build 135
    fail.append('Neutrino: the cards, then where SEANCE found one, then the search, and only then where to put one')
opl = rd('src/opl.c')
need(opl, (('gSeanceLaunching = 1; // build 114', 'a launch is marked for SEANCE'), ('seancePreLaunch(support, launchId);', 'the Ember pre-flight')), 'opl.c')
emb = rd('src/ripps2ember.c')
need(emb, (('in a neutrino folder on the game', 'with no Neutrino, a launch says where to put one (build 135)'),), 'ripps2ember.c')
if raw('src/cuesupport.c').count('seanceHook') or 'seanceHook' in body(raw('src/gui.c'), 'void guiMsgBoxMissing('):
    fail.append('cuesupport.c and guiMsgBoxMissing stay RiptOPL\'s (their harnesses copy them word for word)')

# ---- STATUS and Cache
st = rd('src/ripps2status.c')
if st.index('"DRIVES"') > st.index('"LAUNCHERS"') or st.index('"LAUNCHERS"') > st.index('"BIBLE"'):
    fail.append('STATUS: DRIVES first, then LAUNCHERS, then BIBLE')
need(st, (('"Internal HDD (APA): %s free of %s"', 'the APA drive\'s space'), ('"Memory card %d: %d KB free"', 'the cards\' space'),
          ('ACT_START_DRIVES', 'START EVERY DRIVE'), ('ACT_SEANCE_SEARCH', 'LOOK FOR THEM')), 'ripps2status.c')
if 'aside[96]' not in st:
    fail.append('STATUS: a translated note runs to 73 bytes (Lao, Persian): aside[96]')
dlg = rd('src/dialogs.c')
need(dlg, (('RIPPS2_SEANCE_ROW0', 'Cache > Launchers lines'), ('RIPPS2_SEANCE_BUTTON', 'Look now'), ('RIPPS2_HIDDEN_BUTTON', 'Game Sources > Hidden Games')), 'dialogs.c')

# ---- All Games from the master list
mix = rd('src/mixsupport.c')
need(mix, (('#define MIX_MASTER_FILE  "allgames.bin"', 'the master list beside the settings'),
           ('mixAppend(&b, NULL, -1, -1, m->kind, 100 + m->family, m->text, m->startup, m->family);', 'a waiting row: no owner, ranked after live rows'),
           ('if (save && !settling && !recent && page < 0)\n        mixMasterSave(b.arr, kept);', 'saved only once no started source is still to answer (build 115: by All Games only, never by a quiet look; build 116: nor a drive page)'),
           ('itemList->updateDelay = waiting ? MENU_UPD_DELAY_GENREFRESH : MENU_UPD_DELAY_NOUPDATE;', 'polled only while games wait'),
           ('if (ripps2ShroudHas(mode, 0, name)) // build 114: hidden', 'hidden games never reach the master list')), 'mixsupport.c')
upd = body(mix, 'static int mixBuildRows(')  # build 115: the rows are built there
if upd.index('mixMasterSave(') > upd.index('view == LIB_VIEW_PS1'):
    fail.append('mixUpdateItemList: the master list keeps every kind, saved before the view picks its rows')
need(opl, (('mixSourceAnswered(mod->support->mode, mod->support->itemGetCount != NULL ? mod->support->itemGetCount(mod->support) : 1);', 'a source\'s list replaces its saved games (build 116: a list with games in it)'),
           ('if (MODE_IS_MIX(support->mode) && mixIsWaiting(support->mode, curMenu->current->item.id) && !mixWaitForRow(curMenu))', 'Cross on a waiting row starts and waits (build 115: Recent Games too)')), 'opl.c')

# ---- Hide, Hidden Games, Delete
gm = rd('src/ripps2games.c')
need(gm, (('#define SH_FILE "RIPPS2.HID"', 'the hidden list on the game\'s own drive'),
          ('ioBlockOps(1); // nothing else reads the drive while its table changes', 'nothing reads the drive during a remove'),
          ('if (!ripps2ApaCheck(apaWhy, sizeof(apaWhy))) {', 'the APA table is checked before a partition goes'),
          ('guiMsgBoxStartOption("DELETE FOR GOOD");', 'START is the last word, as the HDD MANAGER asks'),
          ('removeFavouriteByIdAndText(r.mode, r.id, r.name, r.kind);', 'the star goes with the game'),
          ('mc0:/RIPPS2/REMOVED.TXT', 'a receipt')), 'ripps2games.c')
lr = body(gm, 'void ripps2LastRites(item_list_t *support, int id)')
if lr.index('fileXioRemove(lrItems[0].path)') > lr.index('for (i = 1; i < lrCount; i++) {'):
    fail.append('LAST RITES: the image (or partition) first, the extras after')
if "g->partition_name[0] == '_' && g->partition_name[1] == '_'" not in lr or 'gOPLPart' not in lr:
    fail.append('LAST RITES: never a __ partition, never the one RIPPS2 keeps its settings on')
need(rd('src/menusys.c'), (('ripps2LastRites(support, id);', 'Delete is LAST RITES'), ('ripps2ShroudHide(support, id);', 'Hide Game'),
                           ('GAME_HIDE_GAME', 'the game options carry Hide Game'), ('APP_HIDE', 'and a PS1 game\'s')), 'menusys.c')
need(opl, (('if (!isFolderRow && ripps2ShroudRow(mdl->support, i))', 'a page leaves hidden games out'),), 'opl.c')
hm = rd('src/ripps2hdd.c')
if 'ripps2ApaCheck(apaWhy, sizeof(apaWhy))' not in hm or hm.index('ripps2ApaCheck(apaWhy') > hm.index('int r = fileXioRemove(path);'):
    fail.append('ripps2hdd.c: the HDD MANAGER walks the APA table before a partition goes, as LAST RITES does')

# ---- credits
ab = rd('src/ripps2about.c')
need(ab, (('"with rickgaiser\'s Neutrino as its second game core,"', 'the opening names Neutrino'),
          ('"BUILT ON RIPTOPL, WITH NEUTRINO"', 'Neutrino beside RiptOPL'), ('"Special thanks to all the YouTube love as well:"', 'the YouTube thanks')), 'ripps2about.c')
if ab.count('{\'H\', "NEUTRINO"}'):
    fail.append('ripps2about.c: Neutrino\'s old mid-page section went to the closing credits')

# ---- no background write runs into a launch (FifthFox, 10/22: damaged card images and a USB stick)
for head in ('void deinitEx(int exception, int modeSelected, int modeSelected2)', 'void deinit(int exception, int modeSelected)'):
    td = body(opl, head)
    if td.find('ioLaunchBegin();') < 0 or td.find('ioLaunchBegin();') > td.find('ioBlockOpsTimed('):
        fail.append('opl.c: %s raises the launch flag before anything else' % head.split('(')[0])
    if td.find('ioWaitWrites(') < td.find('ioBlockOpsTimed('):
        fail.append('opl.c: %s waits for the writes already started, after the drain' % head.split('(')[0])
need(rd('src/ioman.c'), (('int ioWriteBegin(void)', 'the write gate'), ('ok = !gIoLaunching;', 'closed once a launch begins'),
                         ('PollSema(gIoWriteSema) < 0', 'one background write at a time'), ('if (tries >= 150 || gIoLaunching)', 'a bounded wait, then skipped'),
                         ('if (!ok && gIoWriteSema >= 0)\n        SignalSema(gIoWriteSema);', 'given back when a launch closed the gate'),
                         ('gIoWriteSema = CreateSema(&ws);', 'made in ioInit')), 'ioman.c')
fw_ = rd('src/ripps2files.c')
fw_ = fw_[fw_.index('static void fbWorker(void)'):]
fw_ = fw_[:fw_.index('\n}\n')]
if 'ioLaunchBegin();\n    if (fbOp == FB_OP_PASTE)' not in fw_ or 'ioLaunchCancel();\n    if (fbPath[0])' not in fw_:
    fail.append('ripps2files.c: no background write while Memory Files copies, unpacks or deletes (held, then given back)')
io_ = rd('src/ioman.c')
if io_.find('static int gIoWriteSema') < 0 or io_.find('static int gIoWriteSema') > io_.find('gIoWriteSema = CreateSema('):
    fail.append('ioman.c: gIoWriteSema is declared before ioInit makes it')
# the progress bar wherever a long job has nothing else on screen: compression, and the launchers copied beside games
gm_ = rd('src/ripps2games.c')
need(gm_, (('void ripps2DrawProgress(const char *head, const char *name, long long done, long long total, const char *left, int cancel)', 'one progress panel'),
           ('ripps2DrawPanelGlass(30, 134, 580, 170, 0);', "on the notch panels' frame"), ('int ripps2CopyFile(const char *src, const char *dst, const char *name)', 'a copy with the bar'),
           ('ripps2DrawProgress("COPYING", name, done, total, NULL, 0);', 'drawn as it copies'), ('j->name, j->done, j->work, left, 1);', 'compression draws the same panel')), 'ripps2games.c progress')
if '(*g)->format != GAME_FORMAT_ISO && (*g)->format != GAME_FORMAT_OLD_ISO' not in gm_:
    fail.append('ripps2games.c: a game named the old way (SCUS_XXX.XX.Name.iso) can be compressed too')
# the lab (10/23, SCPS_150.13.POINIES POIN.zso.part studied on the PC): packed data written in writes of any length came out
# a cluster off now and then inside one write; the new image goes to the drive in whole aligned stage pieces
need(gm_, (('#define ZP_STAGE (256 * 1024)', 'the stage'), ('if ((j.stage = memalign(64, j.stageSize)) == NULL && j.stageSize > ZP_STAGE)', 'an aligned buffer'),
           ('if (rv == 1 && !zpOutFlush(&j)) {', 'the rest written last'), ('if (!zpOut(j, out, o)) {', 'the packed data through it'),
           ('if (!zpOut(j, in, cnt * 2048)) {', 'and the ISO made again')), 'ripps2games.c write stage')
if 'zpWriteAll(j->fdOut, out' in gm_ or 'zpWriteAll(j->fdOut, ent' in gm_ or 'zpWriteAll(j->fdOut, head' in gm_ or 'zpWriteAll(j->fdOut, in,' in gm_:
    fail.append('ripps2games.c: nothing reaches the new image except through the stage')
# (the user, 10/24) the built-in themes together at the top of every theme list; Color Sweep: delete, speed kept on the
# built-in sweep itself; Color Theme greyed and named Sweep under a sweep; BADGES Off by default and greyed without TELEMETRY
gu_ = rd('src/gui.c')
need(gu_, (('static const char **guiCopyThemeNames(void)', 'the list shown, built-ins first'), ("if (copy[i][0] == '<') {", "names in <> first"),
           ('picked = ripps2ThemePanel(names, guiThemeShown(cur));', 'the panel'), ('themeID = guiThemeId(themeID);', 'Interface maps back'),
           ('next = n >= 2 ? guiThemeId((guiThemeShown(thmGetGuiValue()) + 1) % n) : -1;', 'Cycle in the order shown'),
           ('if (k == SWEEP_DELETE) {', 'a sweep deleted'), ('ripps2SweepSetSpeed(from, guiSweepEdit.speed);', 'a speed, no copy'),
           ('static void guiRipps2PaletteSweepRow(void)', 'Color Theme under a sweep'), ('diaSetEnabled(diaColorsConfig, UICFG_RIPPS2_PALETTE, gRipps2Sweep == 0);', 'greyed'),
           ('c[0] = c[1] = c[2] = 0x60;', 'Theme Color a plain grey under a sweep')), 'gui.c 10/24')
if gu_.count('guiCopyThemeNames()') < 4:
    fail.append('gui.c: the panel, both Interface editors and Cycle use the order shown')
ui_ = rd('src/ripps2ui.c')
need(ui_, (('void ripps2SweepSetSpeed(int i, int speed)', 'a built-in sweep at a speed of its own'), ('int ripps2SweepDelete(int i, int cur)', 'delete'),
           ('"ripps2_sweep_speeds"', 'kept in the settings')), 'ripps2ui.c sweeps')
ra_ = rd('src/ripps2ra.c')
need(ra_, (('raWrapLines(RIPPS2_CASE_FONT, RA_X, RA_Y + RA_ROW_COUNT * RA_ROW_H + 40, RA_W, 18,', 'the BADGES note wraps'),
           ('int grey = i == RA_ROW_BADGES && !gRATelemetry;', 'greyed without TELEMETRY'), ('else if (gRATelemetry) // build 114: BADGES only once TELEMETRY is on', 'and cannot be turned on')), 'ripps2ra.c badges')
if 'gRABadges = 0; // build 114' not in rd('src/opl.c'):
    fail.append('opl.c: BADGES starts Off')
# (the user, 10/23) compressing keeps a game visible; Hide and Compress hides it once the work is done and checked
need(gm_, (('static int shAdd(const sh_row_t *rr)', 'one hidden-list write for both'), ('void ripps2PackGame(item_list_t *support, int id, int hideAfter)', 'the job told'),
           ('if (hideAfter && shAdd(&r) == 1) {', 'hidden only when asked, and only after success')), 'ripps2games.c Hide and Compress')
if gm_.find('if (hideAfter && shAdd(&r) == 1) {') < gm_.find('rv = zpCheck(&j, tmp, in, out, cap);'):
    fail.append('ripps2games.c: Hide and Compress hides only after the check')
ms_ = rd('src/menusys.c')
if 'ripps2PackGame(support, id, pick == 2);' not in ms_ or 'ripps2PickList(items, kind == 1 ? 3 : 2)' not in ms_:
    fail.append('menusys.c: Hide Game, Compress to ZSO, Hide and Compress (an ISO); Hide Game, Uncompress to ISO (a ZSO)')
# the same shape elsewhere (a big write starting at an odd place): RIPPS2.LST in one write, RIPDISC's rips staged, the stdio
# writers of big files with 256 KB buffers
sb2_ = rd('src/supportbase.c')
if 'if (write(fd, one, sizeof(h) + bytes) == (int)(sizeof(h) + bytes))' not in sb2_ or 'write(fd, &h, sizeof(h))' in sb2_:
    fail.append('supportbase.c: RIPPS2.LST written in one write from its start')
dc2_ = rd('src/ripps2disc.c')
need(dc2_, (('#define RD_STAGE (256 * 1024)', "RIPDISC's stage"), ('if (!rdPut(p, n))', 'rips through it'), ('static int rdClose(void)', 'flushed on close'),
            ('if (r == RD_OK && rdStageFail)', 'a last piece that could not be written fails the rip')), 'ripps2disc.c stage')
if dc2_.count('close(rdFd);') != 1 or dc2_.count('rdClose()') < 7:  # the one left is rdClose's own
    fail.append('ripps2disc.c: every close of a rip goes through rdClose')
if 'setvbuf(f, NULL, _IOFBF, 256 * 1024);' not in rd('src/ripps2shot.c') or 'setvbuf(w.f, NULL, _IOFBF, 256 * 1024);' not in rd('src/ripps2biossnd.c'):
    fail.append('RIPSHOT and BIOS Music write through 256 KB stdio buffers')
# the drive says its free and total space, cluster size and format (the user, 10/23: "detected smart and safe for rips and
# any copy/writes"): the driver RIPPS2 builds answers RIPPS2_DEVCTL_VOLINFO
need(gm_, (('int ripps2VolInfo(const char *path, ripps2_vol_t *v)', 'the drive asked'),
           ('fileXioDevctl(dev, RIPPS2_DEVCTL_VOLINFO, NULL, 0, o, sizeof(o)) != 0', 'through the driver'), ('strncmp(path, "mass", 4) != 0', 'BDM drives only'),
           ('if (known && (long long)vol.freeKb * 1024 < need) {', 'compression: refused before it starts when there is no room'),
           ('if (known && vol.fsType != RIPPS2_FS_EXFAT && (j.pack ?', "compression: FAT's 4 GB"),
           ('j.stageSize = ripps2StageFor(known ? vol.clusterBytes : 0, ZP_STAGE);', 'compression: whole clusters')), 'ripps2games.c drive info')
if gm_.find('known = ripps2VolInfo(prefix, &vol);') > gm_.find('if (!zpAsk('):
    fail.append('ripps2games.c: the room is checked before the panel asks')
sb_ = rd('.github/scripts/install_safe_bdmfs.py')
if 'case RIPPS2_DEVCTL_VOLINFO: {' not in sb_ or 'f_getfree(root, &nclst, &vfs)' not in sb_ or "+ RIPPS2_VOLINFO + source[index:]" not in sb_ or 'o[3] = vfs->fs_type;' not in sb_:
    fail.append('install_safe_bdmfs.py: the driver answers RIPPS2_DEVCTL_VOLINFO (free, total, cluster, format) with f_getfree')
if '#define RIPPS2_DEVCTL_VOLINFO' not in rd('include/vmc_alloc.h'):
    fail.append('vmc_alloc.h: RIPPS2_DEVCTL_VOLINFO, shared by the driver and the EE')
dc3_ = rd('src/ripps2disc.c')
need(dc3_, (("rdBytes > RD_FAT32_MAX && rdSlotType[rdSlotSel] != BDM_TYPE_ATA && !rdIsExfat(prefix)", 'parts only on FAT or a drive that cannot say'),
            ('if (!rdRoomFor(path, rdBytes))', 'room before a game rip'), ('if (!rdRoomFor(base, rdBytes)) {', 'room before a media rip'),
            ('rdStageSize = ripps2StageFor(ripps2VolInfo(path, &v) ? v.clusterBytes : 0, RD_STAGE);', 'the rip stage in whole clusters')), 'ripps2disc.c drive info')
fc3_ = rd('src/ripps2files.c')
need(fc3_, (('u64 copied = 0;', 'a 64-bit count'), ('s64 size = chk >= 0 ? lseek64(chk, 0, SEEK_END) : -1;', 'a 64-bit check'),
            ('if (vol.fsType != RIPPS2_FS_EXFAT && inSize > 0xFFFFFFFFLL)', "FAT's 4 GB before a copy"), ('else if ((s64)vol.freeKb * 1024 < inSize)', 'room before a copy')), 'ripps2files.c drive info')
if 'ripps2VolInfo(dev, &v)' not in rd('src/ripps2status.c'):
    fail.append("ripps2status.c: STATUS shows each BDM drive's format, cluster size and free space")
if "MMCE_PIN=\"${MMCE_PIN:-de28936fdf45fe445554cfa0b8f058b05fa8212f}\"" not in rd('.github/scripts/install_coherent_mmce.sh'):
    fail.append('install_coherent_mmce.sh: mmceman at de28936f (the sio2man hook no longer blocks the second card port)')
# Hidden Games offers compression too (the user, 10/23), its page under the panel and the bar
need(gm_, (('hgRows[i].pack = ripps2PackKind(&view, id);', 'each hidden game knows if it can be compressed'),
           ('pick = ripps2PickList(choices, !gEnableWrite ? 1 : hgRows[sel].pack ? 3 : 2);', 'a third choice for those that can'),
           ('zpUnder = hgDrawUnder; // the page stays under the panel and the bar', 'the page under the panel, without its hints'),
           ('"SHOW AGAIN, DELETE OR UNCOMPRESS"', 'the hint says so'), ('if (zpUnder != NULL) {\n        zpUnder();', 'zpPage draws it')), 'ripps2games.c Hidden Games')
if 'static int seCopy(' in rd('src/ripps2seance.c') or 'ripps2CopyFile(src, dest, what == SEANCE_EMBER' not in rd('src/ripps2seance.c'):
    fail.append('ripps2seance.c: Ember and its BIOS are copied with the progress bar')
if 'ripps2CopyFile != NULL ? ripps2CopyFile(src, path, vcdPopsFiles[i]) : vcdCopyFile(src, path)' not in rd('src/vcdsupport.c'):
    fail.append('vcdsupport.c: the POPS files are copied with the progress bar')
bs_ = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build.sh'), encoding='utf-8').read()
if 'python3 .github/scripts/install_safe_bdmfs.py' not in bs_ or bs_.find('install_safe_bdmfs.py') > bs_.find('make clean'):
    fail.append("elf/build.sh: RiptOPL's guarded exFAT/FAT driver (install_safe_bdmfs.py) is installed before the build, as its releases do")
snapw = body(rd('src/supportbase.c'), 'void sbSnapScanned(')
if snapw.find('ioWriteBegin()') < 0 or snapw.find('ioWriteBegin()') > snapw.find('O_WRONLY'):
    fail.append('supportbase.c: RIPPS2.LST is written only through the write gate')
need(rd('src/supportbase.c'), (('if (ioCacheWriteBegin == NULL || ioCacheWriteBegin())', 'the games list cache through the gate'),), 'supportbase.c')
mw = body(mix, 'static void mixMasterSave(')
if mw.find('ioWriteBegin()') < 0 or mw.find('ioWriteBegin()') > mw.find('O_WRONLY'):
    fail.append('mixsupport.c: allgames.bin is written only through the write gate')
for f, needle in (('src/ripps2shot.c', 'ok = rsPngNow('), ('src/ripps2art.c', 'if (!ioWriteBegin())'), ('src/ripps2seance.c', '!ioWriteBegin()'),
                  ('src/ripps2games.c', 'if (!ioWriteBegin())')):
    if needle not in rd(f):
        fail.append('%s: its background write goes through the gate' % f)

# ---- the launch guard: every light-up has the guard in front of it (the user 10/23)
for f in ('src/opl.c', 'src/system.c', 'src/ripps2.c', 'src/ripps2files.c'):
    src_ = rd(f)
    for m in re.finditer(r'ripps2PlayLaunchSequence\(\);', src_):
        start = src_.rfind('\n{', 0, m.start())  # the function holding this light-up
        if 'ripps2LaunchGuard()' not in src_[start:m.start()]:
            fail.append('%s: a light-up at offset %d has no launch guard before it' % (f, m.start()))
sysd = body(rd('src/system.c'), 'int sysLaunchDisc(')
if sysd.find('ripps2LaunchGuard()') < 0 or sysd.find('ripps2LaunchGuard()') > sysd.find('mmceSendGameID('):
    fail.append("system.c: Launch Disc's guard comes before the MMCE GameID, so backing out leaves the card as it was")
need(rd('src/supportbase.c'), (('int ioScanCancelled(void) __attribute__((weak));', "the list read's stop is weak (host harness)"),
                               ('if (ioScanCancelled != NULL && ioScanCancelled())', 'a list read stops when asked')), 'supportbase.c')
lg = body(gm, 'int ripps2LaunchGuard(void)')
# the user 10/23: a RIPDISC-style panel; the launch waits at the end of the queue and goes on by itself; Cross stops the
# work safely and starts, Circle backs out; the notches fill toward the estimate
need(lg, (('ioQueueEstimateMs()', 'the panel estimates the queue'), ('lgDraw(', 'the panel is drawn'),
          ('return 1; // a job that never ends', 'a stop is bounded'), ('if (done > 0.0 && now - done > 0.35)', 'the launch goes on by itself when the queue is done'),
          ('return 0;', 'Circle backs out')), 'ripps2games.c guard')
if not (lg.find('ioLaunchBegin();') < lg.find('getKeyOn(gSelectButton)') < lg.find('ioCancelScans();')):
    fail.append('ripps2games.c: writes stop at the pick; Cross then stops the list read')
if 'guiMsgBox(' in lg:
    fail.append('ripps2games.c: the guard is the panel, not a message box')
need(rd('src/ripps2disc.c'), (('void ripps2NotchRing(int cx, int cy, float p, int a)', "RIPDISC's notches for the guard"),), 'ripps2disc.c')
io = rd('src/ioman.c')
need(io, (('gIoListMs[m] = (int)', 'each list read is timed'), ('int ioQueueEstimateMs(void)', 'the queue estimate')), 'ioman.c')

# ---- the settings audit (the user 10/23)
dia = rd('src/dialogs.c')


def dtab(text, head):
    i = text.index(head)
    return text[i:text.index('{UI_TERMINATOR}};', i)]


need(dia, (('struct UIItem diaBdmDevicesConfig[]', 'BDM Devices has its page'), ('{.label = {"Layout", -1}}', 'Flow and Grid is Layout'),
           ('{.label = {"Colors and Text", -1}}', 'Colors and Text'), ('UICFG_RIPPS2_TEXTWEIGHT', 'Text Weight'),
           ('{.label = {"Screen", -1}}', 'the Screen page'), ('{.label = {"Neutrino Advanced Arguments", -1}}', "the Neutrino page has its row's name"),
           ('{.label = {"POPSTARTER Network", -1}}', 'POPSTARTER Network'), ('{.label = {"HDD POPS partitions", -1}}', 'the short VCD label'),
           ('{.label = {"Missing Covers", -1}}', 'Artwork has Missing Covers'), ('_STR_GENERAL_SYSTEM}}}, // build 114', "General & System's title")), 'dialogs.c')
dev = dtab(dia, 'struct UIItem diaDeviceConfig[]')
for gone in ('CFG_NETPROTOCOL', 'CFG_ENABLEUSB', 'CFG_ENABLEILK'):
    if gone in dev:
        fail.append('dialogs.c: Game Sources keeps %s off its page (the settings audit)' % gone)
uic = dtab(dia, 'struct UIItem diaUIConfig[]')
for gone in ('UICFG_GAME_LIST_BUTTON', 'UICFG_VMODE', 'UICFG_XOFF'):
    if gone in uic:
        fail.append('dialogs.c: Interface keeps %s off its page (the settings audit)' % gone)
if 'UICFG_RIPPS2_CATLAYOUT' in dtab(dia, 'struct UIItem diaColorsConfig[]') or 'UICFG_RIPPS2_CATLAYOUT' not in dtab(dia, 'struct UIItem diaCoverflowConfig[]'):
    fail.append('dialogs.c: the category rows are on Layout')
g = rd('src/gui.c')
need(g, (('const struct UIItem *parts[] = {diaUIConfig};', 'Interface is one part'), ('static void guiShowScreenConfig(void)', 'the Screen page'),
         ('static int guiShowBdmDevicesConfig(void)', 'the BDM Devices page'), ('"PS Emulation", // build 114', 'the hub\'s short names'),
         ('deviceOnOff[0] = _l(_STR_OFF);', "MMCE's On / Off")), 'gui.c')
need(rd('src/menusys.c'), (('GAME_RA_MENU, _STR_RIPPS2_ACHIEVEMENTS', 'one Achievements row'), ('menuID = menuPickAchievements();', 'its three in a list')), 'menusys.c')
need(rd('src/ripps2status.c'), (('"What each card starts; install or repair BIBLE."', "STATUS's BIBLE line fits"),), 'ripps2status.c')

# ---- one HDD (the user 10/23: "on a fat ps2 only one would ever be possible")
need(rd('src/hddsupport.c'), (('hddHideNotApa(); // RIPPS2 build 114', 'an exFAT drive has no APA page'),), 'hddsupport.c')
need(rd('src/opl.c'), (('mod->menuItem.visible = !(mode == HDD_MODE && hddDriveNotApa());', 'a re-enable keeps it hidden'),), 'opl.c')
need(dia, (('{.label = {"HDD Start Mode", -1}}', 'one HDD Start Mode'),), 'dialogs.c')
if 'CFG_ENABLEBDMHDD' in dtab(dia, 'struct UIItem diaBdmDevicesConfig[]'):
    fail.append('dialogs.c: the exFAT HDD follows HDD Start Mode, not a BDM Devices row')
if g.count('gEnableBdmHDD = gHDDStartMode != START_MODE_DISABLED;') != 2:
    fail.append('gui.c: both Game Sources editors set the exFAT HDD from HDD Start Mode')
if 'gEnableBdmHDD = gHDDStartMode != START_MODE_DISABLED; // build 114' not in rd('src/opl.c'):
    fail.append('opl.c: an older config\'s exFAT HDD follows HDD Start Mode at boot')
# the reel's sidebar take: BDM Devices Off took the exFAT HDD Games with it
bdm_ = rd('src/bdmsupport.c')
need(bdm_, (('(type == BDM_TYPE_ATA && gEnableBdmHDD); // build 114: one HDD', 'BDM Devices Off never withholds the internal HDD'),
            ('if (gEnableBdmHDD && gHDDStartMode == START_MODE_AUTO && gBDMStartMode != START_MODE_AUTO)', 'HDD Start Mode Auto reads an exFAT drive')), 'bdmsupport.c')
# the guard: a list request carries &support->mode, a short; read as an int it took the next field too, so no list
# read was ever timed (no notches) and the panel named no drive (the reel's guard takes, 10/23)
for f_ in ('src/ioman.c', 'src/ripps2games.c'):
    if re.search(r'\*\(int \*\)\s*(req->data|data|da)\b', rd(f_)):
        fail.append('%s: a list request\'s mode is a short' % f_)
# START NOW froze the panel: ioRemoveRequests takes the lock the worker holds for its whole drain. The worker skips the
# queued list reads itself; a launch that comes back gives RIPPS2 its writes and list reads again
guard_ = body(rd('src/ripps2games.c'), 'int ripps2LaunchGuard(void)')
if 'ioRemoveRequests(' in guard_:
    fail.append('ripps2games.c: the guard never takes the worker\'s drain lock (ioRemoveRequests)')
need(rd('src/ioman.c'), (('if (!(gIoCancelScans && req->type == IO_MENU_UPDATE_DEFFERED))', 'the worker skips queued list reads after START NOW'),
                         ('ioLaunchCancel(); // build 114: the menu again', 'ioInit clears the launch flags')), 'ioman.c')
if 'ioLaunchCancel();' not in body(rd('src/ripps2bg.c'), 'void ripps2LaunchAborted(void)'):
    fail.append('ripps2bg.c: a launch that comes back clears the launch flags')
# FifthFox (10/23, MMCE card images and a USB stick): the launch is committed at the pick (no background write starts
# before the MMCE switches cards or the IOP resets); Back gives the writes back; a short wait shows only the loading mark
if guard_.find('ioLaunchBegin();') < 0 or guard_.find('ioLaunchBegin();') > guard_.find('if (!lgBusy())'):
    fail.append('ripps2games.c: the guard commits the launch (ioLaunchBegin) before it looks at the queue')
if 'ioLaunchCancel(); // back where the launch began' not in guard_ or 'lgDrawQuiet();' not in guard_:
    fail.append('ripps2games.c: Back clears the launch; a short wait is quiet (the loading mark, no panel)')
if 'int w = 580, h = 118, x = (640 - w) / 2, y = 134' not in rd('src/ripps2disc.c'):
    fail.append('ripps2disc.c: RIPDISC\'s panel on the launch guard\'s frame (one wheel in one place)')
# the theme list (the user, 10/23): Hold SELECT List (default), Cycle, Off
need(rd('src/ripps2ui.c'), (('int ripps2ThemePanel(const char **names, int cur)', 'the theme panel'),
                            ('"THEMES"', 'its title'), ('"IN USE"', 'the theme in use marked')), 'ripps2ui.c')
need(g, (('int guiPickTheme(void)', 'the list\'s entry'), ('int gRipps2SelectHold = RIPPS2_HOLD_LIST;', 'List by default'),
         ('{"List", "Cycle", "Off", NULL}', 'its three choices')), 'gui.c')
need(dia, (('{.label = {"Hold SELECT", -1}}', 'the Interface row'),), 'dialogs.c')
need(rd('src/menusys.c'), (('if (gRipps2SelectHold == RIPPS2_HOLD_CYCLE)', 'Cycle as before'),
                           ('else if (!guiPickTheme() && !viewPending)', 'the theme in use picked: a refresh')), 'menusys.c')
need(rd('src/opl.c'), (('"ripps2_select_hold"', 'kept in the settings'),), 'opl.c')
# Hide Game and Compression (the user, 10/23): an ISO made a ZSO (OPL's own format) or back, asked twice, every piece
# read back and checked before the original goes (that asked too), the work in <name>.part until then
pk_ = rd('src/ripps2games.c')
need(pk_, (('#define ZP_MAGIC 0x4F53495A', 'the ZISO header'), ('#define ZP_HEAD  24', 'the index right after a 24-byte header'),
           ('raw = n <= 0 || n >= 2048;', 'a block LZ4 cannot shrink stays raw'), ('static int zpLz4(const unsigned char *src, int n, unsigned char *out, int cap)', 'an LZ4 block writer of its own (the EE lz4.c only decodes)'),
           ('mflimit = n - 12, matchlimit = n - 5', 'the end rules of the block format'), ('(sz[k] & 0x8000 ? 0x80000000u : 0)', 'the top bit marks a raw block'),
           ('LZ4_decompress_fast(', 'read back as OPL reads it'), ('crc32(0L, in, cnt * 2048) != j->crcs[b / ZP_RUN]', 'every piece checked'),
           ('snprintf(tmp, sizeof(tmp), "%s.part", dst);', 'the work in a .part file'), ('if (rv == 1 && rename(tmp, dst) != 0)', 'named only once checked'),
           ('if (rv != 1)\n        unlink(tmp);', 'a cancel or failure removes it'), ('if (!zpAsk(', 'the panel: SELECT held'),
           ('if (!guiMsgBox(msg, 1, NULL)) {', 'then a last word'), ('if (guiMsgBox(msg, 1, NULL) && unlink(src) == 0)', 'the original goes only when asked')), 'ripps2games.c compression')
if '(*g)->format != GAME_FORMAT_OLD_ISO) || (*g)->parts != 1' not in pk_:
    fail.append('ripps2games.c: only a whole ISO or ZSO (never a split UL game)')
need(rd('src/menusys.c'), (('packable ? _STR_RIPPS2_HIDE_COMPRESS : _STR_RIPPS2_HIDE_GAME', 'the row says Compression where it applies'),
                           ('ripps2PackGame(support, id, pick == 2);', 'the pick runs it')), 'menusys.c')
# the lab (10/23): ps2sdk's exFAT driver lost whole clusters of a file written at two places or growing beside another.
# A ZSO is written in one straight stream (the sizes first, in a side file that alone grows then), and RIPPS2's own
# background writes are held off while a compression or a RIPDISC rip runs
if 'lseek64(j->fdOut' in pk_ or 'zpPlaceIdx' in pk_:
    fail.append('ripps2games.c: a ZSO is never written at two places (no seek in the file being written)')
need(pk_, (('// pass one: the sizes', 'the sizes first'), ('// pass two: the data, packed again and held to the sizes, straight on', 'then one stream'),
           ('ioLaunchBegin(); // and no background write', 'background writes held off during a job'), ('    ioLaunchCancel();\n    ioBlockOps(0);', 'and given back after')), 'ripps2games.c compression')
dc_ = rd('src/ripps2disc.c')
if 'ioLaunchBegin();\n    rdWhat = what;' not in dc_ or 'ioLaunchCancel(); // build 114: the rip is over' not in dc_:
    fail.append('ripps2disc.c: background writes held off while a rip grows its file')
# and Network Connectivity Off left the SMB page up: Game Sources lost the protocol's re-derive with its Protocol row
if 'guiNetProtocolApplied(netProtocolWas);' not in body(g, 'static void guiSourcesNetRowsRead('):
    fail.append('gui.c: Network Connectivity on Game Sources turns the network page on and off')

# ---- colours (the user 10/23)
ui_ = rd('src/ripps2ui.c')
need(ui_, (('{"Moonlight", 0.0f, 0.10f, 0.55f}, {"Custom", 0.0f, 1.0f, 0.0f}}', 'Moonlight, then Custom, last'),
           ('{"Tangerine",', 'Tangerine'), ('{"Flamingo",', 'Flamingo'), ('{"Turquoise",', 'Turquoise'),
           ('{"Rainbow", {{0xFF, 0x4D, 0x4D}', 'Rainbow is the first sweep'), ('static void tintSolve(', 'Custom and the sweeps are worked out from a colour')), 'ripps2ui.c')
m_ = re.search(r'static const float sweepSecs\[3\] = \{([0-9.f, ]+)\}', ui_)
if m_ is None or min(float(x.strip().rstrip('f')) for x in m_.group(1).split(',')) < 3.0:
    fail.append('ripps2ui.c: a sweep colour lasts 3 s at the quickest (the user: never flashy)')
if '#define RIPPS2_PALETTE_COUNT 11' not in rd('include/ripps2.h') or 'if (!gRipps2TintOn)' not in rd('include/ripps2tint.h'):
    fail.append('ripps2.h / ripps2tint.h: eleven Color Themes, the tint on whenever a theme, Custom or a sweep draws')
need(dia, (('struct UIItem diaSweepConfig[]', 'the sweep page'), ('UICFG_RIPPS2_PALETTE_COLOR', 'the Theme Color picker')), 'dialogs.c')
# the reel's take: the Name row said "Rainbow 2" before anything was changed; the copy's name comes at the save
sw_ = body(g, 'static void guiShowSweepConfig(void)')
if '"%s 2", _t(was.name)); // the copy' not in sw_ or 'from <= RIPPS2_SWEEP_BUILTIN ? _t(was.name) : was.name' not in sw_:
    fail.append("gui.c: Sweep Colors shows the sweep's own name; a changed built-in is saved as '<name> 2'")

# ---- fonts (the font audit's answers)
need(rd('src/fntsys.c'), (('void fntSetWeight(int id, int weight)', 'a weight for any font'), ('FT_Set_Var_Design_Coordinates(', 'a variable face takes it'),
           ('FT_Outline_EmboldenXY(', 'a static face is grown'), ('"builtin:roboto"', 'builtin:roboto')), 'fntsys.c')
th = rd('src/themes.c')
need(th, (('"font%d_weight"', 'the theme key'), ('fntLoadFile("builtin:ripflowbold", 18)', 'Settings rows at 18 px'),
          ('void ripps2ApplyTextWeight(void)', 'Text Weight')), 'themes.c')
if 'ripflow.o' in rd('Makefile') or 'ripps2roboto.o' not in rd('Makefile'):
    fail.append('Makefile: the one variable Roboto')
if not (repo / 'elf/theme/fonts/ripps2_roboto.ttf').exists() or (repo / 'elf/theme/fonts/ripflow.ttf').exists():
    fail.append('elf/theme/fonts: ripps2_roboto.ttf replaces ripflow.ttf and ripflow_bold.ttf')

# ---- the full ELF (the user 10/23: no lite ELF; 10/31: a lite one beside it), FreeType, fonts
mk = rd('Makefile')
need(mk, (('bible_xlf.o bible_mx4sio_xlf.o bible_mmce_xlf.o bible_hdd_xlf.o', 'BIBLE is carried'),), 'Makefile')  # build 135: Neutrino found
# build 135 (the user, 11/02: "no more lite tag just the one ripps2 with bible"): one ELF again (builds 126-134 had a lite one)
if 'RIPPS2_LITE' in raw('Makefile') or (root / 'src/ripps2lite.c').exists():
    fail.append('Makefile: one ELF, no lite build')
if '{INCEBTION_PICTURE, "incebtion", &incebtion_png}' not in rd('src/textures.c'):
    fail.append('textures.c: OPL\'s background is carried for its built-in look')
fnt = rd('src/fntsys.c')
if 'FT_Init_FreeType(' in fnt or 'static FT_Error fntNewLibrary(FT_Library *library)' not in fnt:
    fail.append('fntsys.c: FreeType starts with RIPPS2\'s own module list (FT_Init_FreeType links every module)')
for cls in ('tt_driver_class', 'sfnt_module_class', 'autofit_module_class', 'ft_smooth_renderer_class'):
    if '&%s' % cls not in fnt:
        fail.append('fntsys.c: %s is one RIPPS2 reads' % cls)
for gone in ('t1_driver_class', 'bdf_driver_class', 'pcf_driver_class', 'pfr_driver_class', 'winfnt_driver_class', 't42_driver_class'):
    if gone in fnt:
        fail.append('fntsys.c: %s stays out' % gone)
bsh = (repo / 'elf/build.sh').read_text(encoding='utf-8')
need(bsh, (('strip_fonts.py', 'the compiled-in fonts are stripped'),), 'build.sh')
wf = (repo / '.github/workflows/build-elf.yml').read_text(encoding='utf-8')
if 'cp -f "$ELF" "$OUT/RIPPS2.elf"' not in bsh or 'RIPPS2-lite.elf' in bsh or 'RIPPS2-lite.elf' in wf:
    fail.append('build.sh / build-elf.yml: RIPPS2.elf only (build 135)')

# ---- compiled: the APA check against synthetic disks
cc = shutil.which('gcc') or shutil.which('cc')
if cc is None:
    print('build114: no host C compiler, the compiled checks are skipped')
else:
    games = (root / 'src/ripps2games.c').read_text(encoding='utf-8').replace('\r\n', '\n')
    apa = body(games, 'static u32 lrLe32(') + body(games, 'static u32 lrApaMax(') + body(games, 'int ripps2ApaCheck(')
    harness = r'''
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef unsigned char u8;
typedef unsigned int u32;
#define LR_APA_MAGIC 0x00415041
static u8 *disk; static long diskBytes; static u32 diskSectors;
static u32 hddGetTotalSectors(void) { return diskSectors; }
/* the synthetic disk is sparse: records of a sector number and the two sectors of a header found there */
static int hddReadSectors(u32 lba, u32 n, void *buf)
{
    long at;
    for (at = 0; at + 1028 <= diskBytes; at += 1028)
        if (*(u32 *)(disk + at) == lba && n <= 2) {
            memcpy(buf, disk + at + 4, n * 512);
            return 0;
        }
    return -1;
}
''' + TR_STUBS + apa + r'''
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb"); long size; char why[200];
    fseek(f, 0, SEEK_END); size = ftell(f); fseek(f, 0, SEEK_SET);
    disk = malloc(size); fread(disk, 1, size, f); fclose(f);
    diskBytes = size; diskSectors = strtoul(argv[2], NULL, 0);
    printf("%d %s\n", ripps2ApaCheck(why, sizeof(why)), why);
    return 0;
}
'''

    def header(start, length, nxt, prev, name):
        h = bytearray(1024)
        struct.pack_into('<IIII', h, 4, 0x00415041, nxt, prev, 0)
        h[16:16 + len(name)] = name.encode()
        struct.pack_into('<II', h, 64, start, length)
        s = sum(struct.unpack_from('<255I', h, 4)) & 0xFFFFFFFF
        struct.pack_into('<I', h, 0, s)
        return bytes(h)

    def table(parts):
        # parts: [(start, length, name)]; the chain in order, the last one's next 0, __mbr's prev the last one
        img = bytearray()
        for i, (s, l, n) in enumerate(parts):
            nxt = parts[i + 1][0] if i + 1 < len(parts) else 0
            prev = parts[i - 1][0] if i > 0 else parts[-1][0]
            img += struct.pack('<I', s) + header(s, l, nxt, prev, n)
        return bytes(img)

    M = 0x40000  # 128 MB
    good = [(0, M, '__mbr'), (M, M, '__net'), (2 * M, 2 * M, '__system'), (4 * M, 4 * M, 'PP.GAME')]
    disk40 = 0x04ffffff
    cases = [('a good table', good, disk40, 1),
             ('written from a bigger disk', good + [(8 * M, 8 * M, 'PP.BIG')], 12 * M, 0),
             ('a partition too big for the disk', [(0, M, '__mbr'), (0x2000000, 0x2000000, 'PP.HUGE')], disk40, 0),
             ('off its alignment', [(0, M, '__mbr'), (M, 2 * M, 'PP.ODD')], disk40, 0)]
    def patch(img, rec, off, value):  # rec: the record's index; its header starts 4 bytes in
        base = rec * 1028 + 4
        struct.pack_into('<I', img, base + off, value)
        struct.pack_into('<I', img, base, sum(struct.unpack_from('<255I', img, base + 4)) & 0xFFFFFFFF)
    broken = bytearray(table(good))
    patch(broken, 3, 12, 3 * M)  # PP.GAME's prev points nowhere
    open_chain = bytearray(table(good))
    patch(open_chain, 0, 12, 2 * M)  # __mbr's prev is not the last partition
    with tempfile.TemporaryDirectory() as tmp:
        src, exe = os.path.join(tmp, 'apa.c'), os.path.join(tmp, 'apa.exe')
        open(src, 'w').write(harness)
        cr = subprocess.run([cc, '-std=gnu99', '-Wall', '-Werror', '-Wno-unused-function', src, '-o', exe], capture_output=True, text=True)
        if cr.returncode != 0:
            fail.append('the APA check does not compile on its own:\n' + cr.stderr[-1500:])
        else:
            runs = [(n, table(p), d, want) for n, p, d, want in cases] + [('a broken link', bytes(broken), disk40, 0), ('a chain that does not close', bytes(open_chain), disk40, 0)]
            for name, img, sectors, want in runs:
                path = os.path.join(tmp, 'disk.bin')
                open(path, 'wb').write(img)
                out = subprocess.run([exe, path, str(sectors)], capture_output=True, text=True).stdout.strip()
                if not out.startswith('%d ' % want):
                    fail.append('APA check, %s: wanted %d, got "%s"' % (name, want, out))

    # ---- compiled: the master list, saved and read back; a damaged or short file is not read
    m = (root / 'src/mixsupport.c').read_text(encoding='utf-8').replace('\r\n', '\n')
    pick = ''.join(body(m, h) for h in ('static unsigned int mixLe32(', 'static void mixPutLe32(', 'static unsigned int mixFnv(',
                                        'static void mixMasterLoad(', 'static void mixMasterSave('))
    harness = r'''
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#ifndef O_BINARY
#define O_BINARY 0
#endif
#define open(p, f, ...) open((p), (f) | O_BINARY, ##__VA_ARGS__)
#define LOG(...) ((void)0)
enum { MIX_FAM_APA = 0, MIX_FAM_ATA, MIX_FAM_USB, MIX_FAM_MX4SIO, MIX_FAM_ILINK, MIX_FAM_BDM, MIX_FAM_MMCE, MIX_FAM_SMB, MIX_FAM_UDPFS, MIX_FAM_HTTP, MIX_FAM_COUNT };
#define MIX_MASTER_FILE  "allgames.bin"
#define MIX_MASTER_MAGIC "RIPALL01"
#define MIX_MASTER_MAX   8192
typedef struct { void *owner; int mode, id, kind, rank; char *text, *startup; int family; } mix_rec_t;
typedef struct { unsigned char kind, family; char *text, *startup; } mix_master_t;
static mix_master_t *mixMaster; static int mixMasterCount, mixMasterLoaded, mixMasterSaved = -1; static unsigned int mixMasterSum;
static int gRipps2FastCache = 1, gEnableWrite = 1;
static int ioWriteBegin(void) { return 1; } /* build 114's write gate: open, no launch here */
static void ioWriteEnd(void) {}
static char gPath[512];
static void mixMasterPath(char *out, int size) { snprintf(out, size, "%s", gPath); }
''' + pick + r'''
int main(int argc, char **argv)
{
    char *t[3] = {"Aqua Teen Hunger Force", "Burnout 3 - Takedown", "Spyro the Dragon"}, *s[3] = {"SLUS_216.56", "SLUS_210.50", "Spyro the Dragon"};
    mix_rec_t r[3]; int i;
    snprintf(gPath, sizeof(gPath), "%s", argv[1]);
    for (i = 0; i < 3; i++) { memset(&r[i], 0, sizeof(r[i])); r[i].text = t[i]; r[i].startup = s[i]; r[i].kind = i == 2 ? 2 : 0; r[i].family = i; }
    if (argc > 2) { mixMasterLoad(); printf("%d\n", mixMasterCount); return 0; }
    mixMasterSave(r, 3);
    mixMasterLoaded = 0; mixMasterCount = 0;
    mixMasterLoad();
    if (mixMasterCount != 3) { printf("read %d\n", mixMasterCount); return 1; }
    for (i = 0; i < 3; i++)
        if (strcmp(mixMaster[i].text, t[i]) || strcmp(mixMaster[i].startup, s[i]) || mixMaster[i].family != i || mixMaster[i].kind != (i == 2 ? 2 : 0)) { printf("row %d\n", i); return 1; }
    printf("ok\n");
    return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        src, exe, path = os.path.join(tmp, 'mix.c'), os.path.join(tmp, 'mix.exe'), os.path.join(tmp, 'allgames.bin')
        open(src, 'w').write(harness)
        cr = subprocess.run([cc, '-std=gnu99', '-Wall', '-Wno-unused-function', '-Wno-unused-variable', src, '-o', exe], capture_output=True, text=True)
        if cr.returncode != 0:
            fail.append('the master list does not compile on its own:\n' + cr.stderr[-1500:])
        else:
            out = subprocess.run([exe, path], capture_output=True, text=True).stdout.strip()
            if out != 'ok':
                fail.append('master list round trip: %s' % out)
            data = bytearray(open(path, 'rb').read())
            data[30] ^= 0x55
            open(path, 'wb').write(data)
            if subprocess.run([exe, path, 'load'], capture_output=True, text=True).stdout.strip() != '0':
                fail.append('master list: a damaged file must not be read')
            open(path, 'wb').write(bytes(data[:40]))
            if subprocess.run([exe, path, 'load'], capture_output=True, text=True).stdout.strip() != '0':
                fail.append('master list: a short file must not be read')

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build114: the merge, the launcher search, STATUS, the master list, hide and delete with the APA check, credits, launch write safety, the launch guard, one ELF, FreeType OK')
