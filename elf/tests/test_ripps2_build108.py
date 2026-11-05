"""Build 108: RIPSHOT. Step 0: the IOPRP image device is iprp (PCSX2 takes every host*: open for itself, so games
never launched there). Step 1: ee_core reads the shown frame back from GS memory (ripshot.c) and turns its pixels
into the roll's 16 bits. Step 2: the roll's reads and writes, ee_core to CDVDMAN over SIF DMA, BDM first. Step 3 (BDM): the roll at
launch (found, renamed from the blank or made), handed over beside the ISO, its names and counts in ee_core's config.

Static checks on the patched tree, then, when a C compiler is around, the frame geometry and the 16, 24 and 32-bit
pixel paths compiled on the PC against a Python model."""
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
imgdrv, iopmgr, emk, menu = rd('modules/iopcore/imgdrv/imgdrv.c'), rd('ee_core/src/iopmgr.c'), rd('ee_core/Makefile'), rd('ee_core/src/igrmenu.c')
shot, shoth = rd('ee_core/src/ripshot.c'), rd('ee_core/include/ripshot.h')
fail = []

# step 0: UDNL reads the image from imgdrv's device, which must not be called host
if 'const char name[] = "iprp";' not in imgdrv:
    fail.append('imgdrv must register "iprp": PCSX2 serves every host*: open itself')
if iopmgr.count('"iprp0:"') != 2 or '"host0:"' in iopmgr:
    fail.append('the IOP reset must point UDNL at iprp0:')

# step 1: the readback
if 'ripshot.o' not in emk:
    fail.append('ripshot.c must be built into ee_core')
if 'igs_api.h' in shot or 'IGS_' in shot or 'Igs' in shot:
    fail.append('ripshot.c must not use OPL\'s IGS (GPL-3)')
for what, why in (('*RS_VIF1_STAT = VIF_FDR;', 'turn the VIF1 FIFO towards the EE'),
                  ('*RS_GS_BUSDIR = 1;', 'reverse the GS bus'),
                  ('*RS_GS_BUSDIR = 0;', 'give the GS bus back'),
                  ('*RS_VIF1_STAT = 0;', 'give the VIF1 FIFO back'),
                  ('q[9] = 0x61;', 'raise FINISH before the read'),
                  ('q[10] = 1;', 'set TRXDIR to local -> host'),
                  ('GsPutIMR(GsGetIMR() | IMR_FINISH)', 'mask FINISH while ours is raised'),
                  ('if (!finishWas)', 'leave the game\'s FINISH flag as it found it'),
                  ('*RS_D1_CHCR = 0x100;', 'DMA channel 1 into memory')):
    if what not in shot:
        fail.append('rsRead must %s (%s)' % (why, what))
if 'rsFrame(GSMSourceGSRegs, &igrmF)' not in menu:
    fail.append('the in-game menu must find its frame with rsFrame')

# step 2: the roll's I/O over SIF DMA (ripshot_io.h), never SIF RPC while the game is paused
rio, iop, fsv, cdm, bdm = rd('modules/iopcore/common/ripshot_io.h'), rd('modules/iopcore/cdvdman/ripshot_iop.c'), rd('modules/iopcore/cdvdfsv/cdvdfsv.c'), rd('modules/iopcore/cdvdman/cdvdman.c'), rd('modules/iopcore/cdvdman/device-bdm.c')
cfgh, ccfg = rd('modules/iopcore/common/cdvd_config.h'), rd('ee_core/include/coreconfig.h')
for name, text in (('rs_req_t', rio), ('rs_ack_t', rio)):
    body = text.split('} __attribute__((aligned(16))) ' + name)[0].rsplit('{', 1)[1]
    if body.strip().splitlines()[-1].split('//')[0].strip() != 'u32 seq;':
        fail.append('%s must end on seq: a SIF DMA writes in address order' % name)
roll_part = shot.split('// ---- the roll')[1] if '// ---- the roll' in shot else ''
if 'SifCallRpc' in roll_part.split('void rsLinkIop(void)')[1].split('u32 rsRollBytes')[1]:
    fail.append('the roll calls made while paused must not use SIF RPC')
if 'rsLinkIop();' not in iopmgr or 'if (config->IgrMenu && config->GameMode != DISC_MODE)' not in iopmgr:
    fail.append('ee_core must link the mailbox at every IOP reset for every menu game CDVDMAN serves')
if 'int Ripshot;' not in ccfg or ccfg.index('int Ripshot;') < ccfg.index('int RaHuntCount;'):
    fail.append('the Ripshot field must be appended to EECoreConfig_t')
if 'fno == RIPSHOT_RPC_FNO' not in fsv or 'case CDSC_RIPSHOT_INIT:' not in cdm:
    fail.append('the IGR RPC must pass the mailbox address to CDVDMAN')
if 'rsSendEE(rsBuf + r->offset, r->ee_data, r->size); // before the ack' not in iop:
    fail.append('read data must reach the EE before the ack')
if '#define BDM_MAX_FILES 2' not in cfgh or 'fragfile[1]' not in bdm:
    fail.append('BDM must take the roll as fragfile[1]')
for dev in ('hdd', 'mmce', 'smb', 'http'):
    if 'int DeviceRollIo(' not in rd('modules/iopcore/cdvdman/device-%s.c' % dev):
        fail.append('device-%s.c must define DeviceRollIo' % dev)

# step 3 (BDM): the roll at launch, its handover, the config, the background blank
shot_rp, bsup, sysc, guic, oplc, mk = rd('src/ripps2shot.c'), rd('src/bdmsupport.c'), rd('src/system.c'), rd('src/gui.c'), rd('src/opl.c'), rd('Makefile')
if 'ripps2shot.o' not in mk:
    fail.append('ripps2shot.c must be built into RIPPS2')
call = 'ripps2ShotPrepareBdm(settings, &iTotalFragCount, pDeviceData->bdmDeviceRoot'
if call not in bsup or not (bsup.index('// Add ISO as fragfile[0]') < bsup.index(call) < bsup.index('deinit(NO_EXCEPTION, itemList->mode)')):
    fail.append('the BDM launch must hand the roll over after the ISO and before deinit frees the game')
if 'ripps2ShotFillConfig(config, mode_str);' not in sysc:
    fail.append("the launch must fill ee_core's RIPSHOT fields")
if 'ripps2ShotTick();' not in guic or '"ripps2_ripshot"' not in oplc or '"ripps2_ripshot_develop"' not in oplc:
    fail.append('the background job and the settings keys must be wired')
for what, why in (('rename(blank, path) == 0', "rename the blank to the game's roll at launch"),
                  ('rsCountRolls(dir) >= RS_ROLLS_MAX', 'keep to RS_ROLLS_MAX rolls a drive'),
                  ('lseek(fd, RS_ROLL_BYTES - 1, SEEK_SET)', "take the roll's room without writing 4 MB"),
                  ('if (ok && rename(roll, blank) == 0)', 'turn an unused roll back into the blank'),
                  ('n > BDM_MAX_FRAGS - *fragCount', 'refuse a roll too scattered to fit beside the ISO'),
                  ('if (lseek(fd, 0, SEEK_END) < RS_ROLL_BYTES)', 'never hand over a roll cut short')):
    if what not in shot_rp:
        fail.append('ripps2shot.c must %s' % why)

# the silent menu and the exact frame on RESUME (the user, 10/20)
hush_iop = iop[iop.index('static void rsHush(void)'):iop.index('static s32 rsDo(')]
h, w_ = hush_iop.split('static void rsWake(void)')
if h.index('*SD_P_MVOLL(c) = 0;') > h.index('*SD_VP_PITCH(c, v) = 0;'):
    fail.append('the hush must silence the volumes before it holds the voices')
if 'if (*SD_VP_PITCH(c, v) == 0)' not in w_ or w_.index('*SD_VP_PITCH(c, v) = rsPitch[c][v];') > w_.index('*SD_P_MVOLL(c) = rsMvol[c][0];'):
    fail.append('the wake must give back only the pitches the game left alone, and the volumes last')
run = menu[menu.index('int IGR_MenuRun('):]
if not (run.index('rsHush();') < run.index('rsHoldSave(') < run.index('igrmCompose(&info, sel, armed);')):
    fail.append('the menu must hush, then save the hold, before the panel is first drawn')
resume = run[run.index('if (result == IGR_MENU_RESUME) {'):run.index('done:')]
if not ('igrmHoldBack(pkt);' in resume and 'rsWake();' in resume and resume.index('igrmHoldBack(pkt);') < resume.index('rsWake();')):
    fail.append('RESUME must give the frame back, then the sound')

# step 4: the in-game screens
shoot = menu[menu.index('static void igrmShoot('):menu.index('#ifdef IGR_MENU_TEST', menu.index('static void igrmShoot('))]
for what, why in (('for (igrmMix = 170;; igrmMix -= 85)', 'fade the panel off in steps'),
                  ('saved = rsRollBegin() && igrmWriteFrame(pkt, slot);', 'write the frame once the panel is off it'),
                  ('rsHoldSave(&igrmF, igrmX, igrmStripY,', 'hold the pixels under the KEEP strip'),
                  ('igrmKeep(pkt, in, slot, path)', 'write the slot header only on KEEP'),
                  ('config->RipshotKept = in->shotKept;', 'remember the kept slot for the next menu'),
                  ('igrmHoldPass(pkt, RS_STRIP_AT, SH * igrmSy);', 'give back the pixels under the strip')):
    if what not in shoot:
        fail.append('SAVE must %s' % why)
if shoot.index('igrmWriteFrame') < shoot.index('igrmMix -= 85'):
    fail.append('the frame must be read after the panel faded off it')
if 'rsToRgb555((const u8 *)pkt, igrmF.psm, (u16 *)pkt, sw);' not in menu:
    fail.append('the frame goes to the roll at 16 bits')
if 'info.shot = config->Ripshot == RIPSHOT_READY && !igrmHeld ? RIPSHOT_NOT_HERE : config->Ripshot;' not in menu:
    fail.append('without a hold there is nothing to fade the panel off with: no SCREENSHOT to take')

# the menu's thread stack lives after the modules (ee_core's own region is the main thread's alone)
pad = rd('ee_core/src/padhook.c')
if 'thread_param.stack = config->IgrStack;' not in pad or 'thread_param.stack = (void *)&_stack;' not in pad:
    fail.append("the IGR thread must run on the menu's stack after the modules, else on ee_core's own region")
if 'igrStack = (u8 *)ModuleStorage + ModuleStorageSize;' not in sysc or 'ModuleStorageSize + igrBytes <= 0xD0000' not in sysc:
    fail.append("the launch must place the menu's stack after the modules, below 0xD0000")
if 'memcpy(igrFont, igrmFontData, sizeof(igrmFontData));' not in sysc or 'config->IgrFont = igrFont;' not in sysc:
    fail.append("the menu's font must follow its stack (ee_core has no room for it)")
if 'static const u8 igrmFont[' in menu or 'igrmFont = (const u8(*)[7])config->IgrFont;' not in menu:
    fail.append("the menu must read its font from module storage, not carry it in ee_core")
if 'static SifRpcClientData_t rsCd' not in shot:
    fail.append("rsLinkIop's RPC buffers must be static: the first IOP reset runs near ee_core's 3 KB stack floor")
if sysc.index('igrStack = (u8 *)ModuleStorage') > sysc.index('ModuleStorageEnd = (void *)((u8 *)ModuleStorage + ModuleStorageSize);'):
    fail.append("the menu's stack must be inside ModuleStorageEnd, so nothing erases it")

# GSM's data breakpoint is off while the menu runs (its own GS stores must not trap), and BPC goes back as it was
if run.index('bpc = igrmBpcOff();') > run.index('rsHush();') or 'igrmBpcBack(bpc);' not in run[run.index('done:'):]:
    fail.append('the menu must switch the GS data breakpoint off before its first GS store and put it back on the way out')

cc = shutil.which('gcc') or shutil.which('cc')
if cc is None and Path('C:/msys64/mingw64/bin/gcc.exe').exists():
    cc = 'C:/msys64/mingw64/bin/gcc.exe'


def model555(px, psm):
    if psm in (2, 10):
        return (px[0] | px[1] << 8) | 0x8000
    return (px[0] >> 3) | (px[1] >> 3) << 5 | (px[2] >> 3) << 10 | 0x8000


if cc and not fail:
    rnd = random.Random(108)
    cases = []
    for psm, bpp in ((0, 4), (1, 3), (2, 2), (10, 2)):
        data = bytes(rnd.randrange(256) for _ in range(64 * bpp))
        want = [model555(data[i * bpp:i * bpp + bpp], psm) for i in range(64)]
        cases.append((psm, data, want))
    arrays = []
    for k, (psm, data, want) in enumerate(cases):
        arrays.append('static const u8 src%d[] = {%s};' % (k, ','.join(map(str, data))))
        arrays.append('static const u16 want%d[] = {%s};' % (k, ','.join(map(str, want))))
    calls = '\n'.join('    rsToRgb555(src%d, %d, out, 64); if (memcmp(out, want%d, sizeof(out))) return 30 + %d;' % (k, c[0], k, k)
                      for k, c in enumerate(cases))
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')
        (td / 't.c').write_text(r'''
#include <stdio.h>
#include <string.h>
#include "ripshot.c"
#define DISPFB(fbp, fbw, psm, dbx, dby) ((u64)(fbp) | (u64)(fbw) << 9 | (u64)(psm) << 15 | (u64)(dbx) << 32 | (u64)(dby) << 43)
#define DISPLAY(dx, dy, magh, magv, dw, dh) ((u64)(dx) | (u64)(dy) << 12 | (u64)(magh) << 23 | (u64)(magv) << 27 | (u64)((dw) - 1) << 32 | (u64)((dh) - 1) << 44)
''' + '\n'.join(arrays) + r'''
int main(void)
{
    u64 r[11];
    rs_frame_t f;
    u16 out[64];

    /* nothing seen, a Z buffer format, no width: no frame */
    memset(r, 0, sizeof(r));
    if (rsFrame(r, &f)) return 1;
    r[7] = DISPFB(0, 10, 0x30, 0, 0);
    if (rsFrame(r, &f)) return 2;
    r[7] = DISPFB(0, 0, 0, 0, 0) | 1;
    if (rsFrame(r, &f)) return 3;

    /* NTSC interlaced FRAME mode (INT 1, FFMD 1): a 640 wide CT32 buffer holding one field */
    memset(r, 0, sizeof(r));
    r[0] = 1;
    r[2] = 3;
    r[7] = DISPFB(70, 10, 0, 0, 0);
    r[8] = DISPLAY(636, 50, 3, 0, 2560, 448);
    if (!rsFrame(r, &f) || f.bp != 70 * 32 || f.bw != 10 || f.bpp != 4 || f.w != 640 || f.h != 224 || !f.field) return 4;

    /* a DH past the TV's raster (POINIES POIN writes DH 959 in NTSC FRAME mode): 480 lines shown, one field of 240 */
    r[8] = DISPLAY(636, 50, 3, 0, 2560, 960);
    if (!rsFrame(r, &f) || f.h != 240 || !f.field) return 40;
    r[8] = DISPLAY(652, 72, 3, 0, 2560, 1024); /* PAL starts lower: 576 shown */
    if (!rsFrame(r, &f) || f.h != 288) return 41;
    r[8] = DISPLAY(636, 50, 3, 0, 2560, 448);

    /* FIELD mode (INT 1, FFMD 0): the buffer holds the whole frame */
    r[2] = 1;
    if (!rsFrame(r, &f) || f.h != 448 || f.field) return 5;

    /* 480p CT24 */
    r[2] = 0;
    r[7] = DISPFB(0, 10, 1, 0, 0);
    r[8] = DISPLAY(318, 50, 1, 0, 1280, 480);
    if (!rsFrame(r, &f) || f.psm != 1 || f.bpp != 3 || f.w != 640 || f.h != 480) return 6;

    /* PAL 512 wide CT16S with MAGH 4, MAGV 1 (a 1024 line raster at half), offset in a bigger buffer */
    r[7] = DISPFB(140, 8, 10, 16, 32);
    r[8] = DISPLAY(652, 72, 4, 1, 2560, 1024);
    if (!rsFrame(r, &f) || f.bpp != 2 || f.w != 512 || f.h != 512 || f.x != 16 || f.y != 32) return 7;

    /* circuit 2 when circuit 1 is off and 2 is on */
    memset(r, 0, sizeof(r));
    r[0] = 2;
    r[7] = DISPFB(1, 10, 0, 0, 0);
    r[9] = DISPFB(2, 10, 2, 0, 0);
    if (!rsFrame(r, &f) || f.bp != 2 * 32 || f.bpp != 2 || f.h != 224) return 8;

    /* transfer widths are whole quadwords in every format */
    if (RS_READ_W(640) != 640 || RS_READ_W(1) != 16 || RS_READ_W(513) != 528) return 9;
    {
        u32 w, b;
        for (w = 1; w <= 720; w++)
            for (b = 2; b <= 4; b++)
                if (RS_READ_W(w) * b % 16) return 10;
    }
''' + calls + r'''
    printf("frames and pixels OK\n");
    return 0;
}
''')
        exe = td / 't.exe'
        env = dict(os.environ)
        if cc.startswith('C:/msys64'):
            env['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + env.get('PATH', '')
        r = subprocess.run([cc, '-std=gnu99', '-Wall', '-Wextra', '-Werror', '-DRIPSHOT_HOST_TEST', '-I', str(td),
                            '-I', str(root / 'ee_core/include'), '-I', str(root / 'ee_core/src'), str(td / 't.c'),
                            '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append('ripshot.c must build on the PC: ' + r.stderr[-600:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the frame / pixel paths failed check %d' % r.returncode)

# the BDM roll walk on the PC: a fake block device, a roll in three fragments
ROLL_TEST = r"""
#include <stdio.h>
#include <string.h>
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;
typedef struct { u64 sector; u32 count; } __attribute__((packed)) bd_fragment_t;
struct cdvdman_fragfile { u8 frag_start, frag_count; };
struct block_device { u32 sectorSize; int (*read)(struct block_device *, u64, void *, u16); int (*write)(struct block_device *, u64, const void *, u16); };
static struct { struct cdvdman_fragfile fragfile[2]; bd_fragment_t frags[64]; } cdvdman_settings;
static u8 disk[64 * 512];
static int fails;
static int rd_(struct block_device *b, u64 s, void *p, u16 n) { (void)b; if (fails) return -1; memcpy(p, disk + s * 512, n * 512); return n; }
static int wr_(struct block_device *b, u64 s, const void *p, u16 n) { (void)b; memcpy(disk + s * 512, p, n * 512); return n; }
static struct block_device bd0 = {512, rd_, wr_}, *g_bd = &bd0;
static int bdm_io_sema;
static void WaitSema(int s) { (void)s; }
static void SignalSema(int s) { (void)s; }
@BODY@
int main(void)
{
    static u8 in[8 * 512], out[8 * 512];
    u32 i;
    /* the ISO owns frags 0-1; the roll is frags 2-4: 2 sectors at 40, 3 at 10, 4 at 50 (9 sectors) */
    cdvdman_settings.fragfile[1].frag_start = 2;
    cdvdman_settings.fragfile[1].frag_count = 3;
    cdvdman_settings.frags[2].sector = 40; cdvdman_settings.frags[2].count = 2;
    cdvdman_settings.frags[3].sector = 10; cdvdman_settings.frags[3].count = 3;
    cdvdman_settings.frags[4].sector = 50; cdvdman_settings.frags[4].count = 4;
    if (DeviceRollBytes() != 9 * 512) return 1;
    for (i = 0; i < sizeof(in); i++) in[i] = (u8)(i * 7 + 3);
    /* 6 sectors from roll sector 1: 1 at 41, 3 at 10-12, 2 at 50-51 */
    if (DeviceRollIo(1, 512, in, 6 * 512) != 6 * 512) return 2;
    if (memcmp(disk + 41 * 512, in, 512) || memcmp(disk + 10 * 512, in + 512, 3 * 512) || memcmp(disk + 50 * 512, in + 4 * 512, 2 * 512)) return 3;
    if (DeviceRollIo(0, 512, out, 6 * 512) != 6 * 512 || memcmp(in, out, 6 * 512)) return 4;
    if (DeviceRollIo(0, 8 * 512, out, 2 * 512) != -1) return 5; /* past the end */
    if (DeviceRollIo(0, 100, out, 512) != -1) return 6;        /* not a whole sector */
    fails = 1;
    if (DeviceRollIo(0, 0, out, 512) != -1) return 7;          /* the drive failed */
    fails = 0;
    cdvdman_settings.fragfile[1].frag_count = 0;
    if (DeviceRollBytes() != 0 || DeviceRollIo(0, 0, out, 512) != -1) return 8; /* no roll */
    printf("roll walk OK\n");
    return 0;
}
"""
if cc and not fail:
    env = dict(os.environ)
    if cc.startswith('C:/msys64'):
        env['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'r.c').write_text(ROLL_TEST.replace('@BODY@', bdm[bdm.index('u32 DeviceRollBytes(void)'):]))
        exe = td / 'r.exe'
        r = subprocess.run([cc, '-std=gnu99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable', str(td / 'r.c'),
                            '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append('the BDM roll walk must build on the PC: ' + r.stderr[-600:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the BDM roll walk failed check %d' % r.returncode)

SHOT_TEST = r"""
#include <stdio.h>
#include <string.h>
#include "ripshot_roll.h"
#include "ripps2shot.c"
#include "ripshot.c"
static int folder(const char *title, const char *id, const char *want)
{
    char out[32];
    ripps2ShotFolder(title, id, out, sizeof(out));
    if (strcmp(out, want) != 0) { printf("folder [%s] want [%s]\n", out, want); return 0; }
    return 1;
}
int main(void)
{
    rs_slot_hdr_t h[RS_SLOTS];
    int kept, art, media;
    u32 lb, w, b;

    /* the layout: whole 4 KB pieces, room for the biggest hold, and the sizes the drive and ee_core agree on */
    if (sizeof(rs_roll_hdr_t) != 64 || sizeof(rs_slot_hdr_t) != 136) return 1;
    if (RS_SLOT_AT(0) % 4096 || RS_SLOT_BYTES % 4096 || RS_HOLD_AT % 4096 || RS_STRIP_AT % 4096 || RS_ROLL_BYTES % 4096) return 2;
    if (RS_HOLD_PANEL < 320 * 252 * 4 + 511 || RS_HOLD_STRIP < 320 * 32 * 4) return 3;
    if (RS_ROLL_BYTES != 4329472) return 4;

    /* staged writes land on whole sectors and fit the IOP buffer, for every panel line */
    for (w = 160; w <= 640; w += 16)
        for (b = 2; b <= 4; b++) {
            lb = w * b;
            if (rsLinesPerWrite(lb) == 0 || rsLinesPerWrite(lb) * lb > 8192) return 5;
            if ((w == 160 || w == 320) && rsLinesPerWrite(lb) * lb % 512) return 6;
        }
    if (rsLinesPerWrite(1280) != 6 || rsLinesPerWrite(0) != 0 || rsLinesPerWrite(9000) != 0) return 7;

    /* folder names */
    if (!folder("Aqua Teen Hunger Force: Zombie Ninja Pro-Am", "SLUS_216.33", "Aqua Teen Hunger Force Zombie N")) return 10;
    if (!folder("  ..Ratchet & Clank?.. ", "SCUS_971.99", "Ratchet & Clank")) return 11;
    if (!folder("", "SLUS_209.46", "SLUS_209.46")) return 12;
    if (!folder("???", "SLUS_209.46", "SLUS_209.46")) return 13;
    if (!folder(NULL, "SLES_123.45", "SLES_123.45")) return 14;

    /* slot counting: only kept slots with the magic count */
    memset(h, 0, sizeof(h));
    memcpy(h[0].magic, RS_SLOT_MAGIC, 8); h[0].state = 1; h[0].path = RS_PATH_ART;
    memcpy(h[2].magic, RS_SLOT_MAGIC, 8); h[2].state = 1; h[2].path = RS_PATH_BOTH;
    memcpy(h[3].magic, RS_SLOT_MAGIC, 8); h[3].state = 0; h[3].path = RS_PATH_MEDIA; /* deleted */
    h[4].state = 1; h[4].path = RS_PATH_MEDIA;                                         /* no magic: a blank's leftovers */
    ripps2ShotCount(h, &kept, &art, &media);
    if (kept != 5 || art != 2 || media != 1) return 20; /* slots 0 and 2 */
    /* step 5: the quantizer. 256 colours or fewer: exact */
    {
        static unsigned short px[640 * 240], small[250 * 188];
        static unsigned char idx[640 * 240], pal[768];
        int i, nc, x, y;
        long err = 0;
        for (i = 0; i < 640 * 240; i++) px[i] = (i % 64) | ((i / 64) % 4) << 10 | 0x8000; /* 256 colours */
        nc = ripps2ShotQuantize(px, 640 * 240, idx, pal);
        if (nc <= 0 || nc > 256) return 30;
        for (i = 0; i < 640 * 240; i++) {
            int c = px[i];
            if (pal[idx[i] * 3] != rsX8(c & 31) || pal[idx[i] * 3 + 1] != rsX8((c >> 5) & 31) || pal[idx[i] * 3 + 2] != rsX8((c >> 10) & 31)) return 31;
        }
        /* a busy gradient (thousands of 15-bit colours): 256 colours, a small mean error */
        for (y = 0; y < 240; y++)
            for (x = 0; x < 640; x++)
                px[y * 640 + x] = ((x * 31) / 639) | (((y * 31) / 239) << 5) | ((((x + y) * 31) / 878) << 10) | 0x8000;
        nc = ripps2ShotQuantize(px, 640 * 240, idx, pal);
        if (nc != 256) return 32;
        for (i = 0; i < 640 * 240; i++) {
            int c = px[i], k;
            for (k = 0; k < 3; k++) {
                int d = pal[idx[i] * 3 + k] - rsX8((c >> (k * 5)) & 31);
                err += d < 0 ? -d : d;
            }
        }
        if (err / (640 * 240 * 3) > 6) { printf("mean error %ld\n", err / (640 * 240 * 3)); return 33; }
        /* the shrink: one colour stays that colour; a field frame is read line-doubled */
        for (i = 0; i < 640 * 240; i++) px[i] = 7 | 19 << 5 | 25 << 10 | 0x8000;
        ripps2ShotShrink(px, 640, 240, 1, small, 250, 188);
        for (i = 0; i < 250 * 188; i++) if (small[i] != (7 | 19 << 5 | 25 << 10 | 0x8000)) return 34;
        for (y = 0; y < 240; y++) for (x = 0; x < 640; x++) px[y * 640 + x] = (y < 120 ? 31 : 0) | 0x8000; /* red top half */
        ripps2ShotShrink(px, 640, 240, 1, small, 250, 188);
        if ((small[0] & 31) != 31 || (small[187 * 250] & 31) != 0) return 35;
    }
    printf("roll layout, chunks, folders, counts, quantizer, shrink OK\n");
    return 0;
}
"""
if cc and not fail:
    env = dict(os.environ)
    if cc.startswith('C:/msys64'):
        env['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')
        (td / 's.c').write_text(SHOT_TEST)
        exe = td / 's.exe'
        r = subprocess.run([cc, '-std=gnu99', '-Wall', '-Wextra', '-Werror', '-DRIPSHOT_HOST_TEST', '-DRIPPS2_SHOT_HOST_TEST',
                            '-I', str(td), '-I', str(root), '-I', str(root / 'src'), '-I', str(root / 'ee_core/src'),
                            '-I', str(root / 'modules/iopcore/common'), '-I', str(root / 'ee_core/include'),
                            str(td / 's.c'), '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append("ripps2shot.c's host half must build on the PC: " + r.stderr[-600:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the roll layout / names failed check %d %s' % (r.returncode, r.stdout))

PAGES_TEST = r"""
#include <stdio.h>
#include <string.h>
#include "igrmenu.c"
static u8 buf[320 * 252 * 3];
static char txt[IGRM_LINES][40];
static void texts(void)
{
    int i, k;
    for (i = 0; i < igrmLines; i++) {
        for (k = 0; k < igrmLine[i].len; k++) {
            int g = igrmLine[i].glyph[k];
            txt[i][k] = g < 64 ? g + 32 : g == G_CROSS ? 'X' : g == G_CIRCLE ? 'O' : g == G_TILDE ? '~' : '>';
        }
        txt[i][k] = 0;
    }
}
static int has(const char *s)
{
    int i;
    texts();
    for (i = 0; i < igrmLines; i++)
        if (strcmp(txt[i], s) == 0) return 1;
    printf("missing [%s]; the page:", s);
    for (i = 0; i < igrmLines; i++) printf(" [%s]", txt[i]);
    printf("\n");
    return 0;
}
static int fits(void)
{
    int i;
    for (i = 0; i < igrmLines; i++)
        if (igrmLine[i].x + igrmLine[i].len * 6 - 1 > PW - 4 || igrmLine[i].y + 7 > igrmH - 2) return 0;
    return 1;
}
int main(void)
{
    igrm_info_t a = {0, "SLUS_209.46", "", 1, 1, 40, 12, 1, 2, NULL, 0, 1,
                     RIPSHOT_READY, 3, 3, 3, -1, 640, 448, "SLUS_209.46", "USB", "Aqua Teen Hunger Force"};

    /* the menu with SCREENSHOT third */
    if (igrmTestPage(&a, 0, 2, 0, 2, 2, "", buf) != 252 || igrmItems != 5) return 1;
    if (!has("SCREENSHOT") || !has("SAVE THIS FRAME") || !has("4 OF 6 LEFT") || !has("X SELECT   O RESUME") || !fits()) return 2;
    igrmTestPage(&a, 0, 3, 0, 2, 2, "", buf);
    if (!has("SPIRIT OF RA")) return 3; /* ACHIEVEMENTS after it */
    a.shotKept = 0x3f;
    igrmTestPage(&a, 0, 2, 0, 2, 2, "", buf);
    if (!has("ROLL FULL") || !has("DEVELOP IN MEMORY FILES")) return 4;
    a.shot = RIPSHOT_DRIVE_FULL;
    igrmTestPage(&a, 0, 2, 0, 2, 2, "", buf);
    if (!has("NO ROLL: SEE DIAG.TXT")) return 5;
    a.shot = RIPSHOT_NOT_HERE;
    igrmTestPage(&a, 0, 2, 0, 2, 2, "", buf);
    if (!has("NOT FOR THIS GAME")) return 6;
    a.shot = RIPSHOT_OFF;
    igrmTestPage(&a, 0, 2, 0, 2, 2, "", buf);
    if (igrmItems != 4 || !has("SPIRIT OF RA")) return 7; /* no SCREENSHOT: ACHIEVEMENTS is third again */

    /* the path step */
    a.shot = RIPSHOT_READY;
    a.shotKept = 3;
    igrmTestPage(&a, 1, 0, 0, 2, 2, "", buf);
    if (!has("ART") || !has("MEDIA") || !has("BOTH") || !has("SLUS_209.46_SCR3.PNG") || !has("250X188  ~20 KB") ||
        !has("USB: ART") || !has("3 LEFT") || !has("X SAVE   O BACK") || !fits()) return 10;
    igrmTestPage(&a, 1, 1, 0, 2, 2, "", buf);
    if (!has("SHOT 03.PNG") || !has("640X448  ~140 KB") || !has("USB: MEDIA/AQUA TEEN HUN") || !fits()) return 11;
    a.freeMB = 12 * 1024;
    a.scrNext = 1;
    a.shotNext = 12;
    igrmTestPage(&a, 1, 2, 0, 2, 2, "", buf);
    if (!has("SCR + SHOT 12") || !has("~160 KB") || !has("USB: ART + MEDIA") || !has("3 LEFT  12 GB FREE") || !fits()) return 12;
    igrmTestPage(&a, 1, 0, 0, 1, 1, "", buf);
    if (!has("SLUS_209.46_SCR.PNG")) return 13;

    /* the strip */
    if (igrmTestPage(&a, 2, 0, 0, 2, 2, "X KEEP   O DELETE", buf) != SH * 2 || !fits()) return 20;
    if (igrmTestPage(&a, 2, 0, 0, 1, 1, "KEPT  3 LEFT", buf) != SH || !has("KEPT  3 LEFT")) return 21;
    printf("pages OK\n");
    return 0;
}
"""
if cc and not fail:
    env = dict(os.environ)
    if cc.startswith('C:/msys64'):
        env['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')
        (td / 'p.c').write_text(PAGES_TEST.replace('"X KEEP', '"\\x01 KEEP').replace('O DELETE"', '\\x02 DELETE"'))
        exe = td / 'p.exe'
        r = subprocess.run([cc, '-DIGR_MENU_HOST_TEST', '-I', str(td), '-I', str(root / 'ee_core/include'),
                            '-I', str(root / 'ee_core/src'), str(td / 'p.c'), '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append('the in-game pages must build on the PC: ' + r.stderr[-600:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the in-game pages failed check %d %s' % (r.returncode, r.stdout[-400:]))

# MEDIA's README.txt says what RIPSHOT is (written with the roll's folder), and an older RIPPS2 README is written again
disc = rd('src/ripps2disc.c')
if 'RIPSHOT: screenshots from the in-game menu' not in disc or 'ripps2WriteReadme(root, 1)' not in rd('src/ripps2shot.c'):
    fail.append("MEDIA's README.txt must explain RIPSHOT, written when MEDIA/RIPSHOT is made")
if 'memcmp(head, media ? rdReadmeMedia : rdReadmeAudio, sizeof(head))' not in disc:
    fail.append("an older RIPPS2 README must be brought up to date (one the user made left alone)")

# step 6 in the lab: every choice's hint (an enum row's intvalue.max stays 0), the hint again on a new choice, dim disabled rows
dia = rd('src/dia.c')
if 'item->intvalue.current <= item->intvalue.max' in dia or 'float tipA = diaTipAlpha(item, text);' not in dia:
    fail.append("an enum row shows the hint of whichever choice it is on, coming in again when the choice changes")
if 'static int diaRowDisabled(const struct UIItem *item)' not in dia or 'if (diaRowDisabled(item))' not in dia:
    fail.append('a row that cannot be changed now (RIPSHOT with the menu off) must read dimmed, its label too')

# developing, from the reel takes: a PNG is checked on the drive after it is closed and written once more if it did not
# hold; an empty file left by a failed write counts as free, so its number is written over
shotc = rd('src/ripps2shot.c')
if 'rsSize(path) != want' not in shotc or 'static int rsPngSure(' not in shotc or shotc.count('rsPngSure(file') != 2:
    fail.append('a developed PNG must be checked on the drive (its size) and written again when it did not hold')
if 'cacheInvalidateFailMemo(); // new ART' not in shotc:
    fail.append("developing ART must re-open the art cache's absent answers, or a theme never shows the new shots this session")
if 'return rsSize(path) > 0;' not in shotc or 'if (!rsTaken(path))' not in shotc:
    fail.append('an empty PNG left by a failed write must not hold its shot number')

# step 7: the SCRn theme key, every shot in turn, in the engine and the built-in themes
import re
themes = rd('src/themes.c')
ripps2_theme = (Path(__file__).resolve().parents[1] / 'theme' / 'conf_theme.cfg').read_text(encoding='utf-8')  # build.sh copies it in
for cfg, c in (('RIPPS2 (elf/theme/conf_theme.cfg)', ripps2_theme), ('RIPFLOW', rd('misc/theme_coverflow.cfg')), ('RIPGRID', rd('misc/theme_ripgrid.cfg'))):
    if c.count('pattern=SCRn') != 2 or re.search(r'pattern=SCR2?\s*$', c, re.M):
        fail.append('%s: both screenshot boxes (slides on RIPPS2) must be pattern=SCRn' % cfg)
for need, why in (('!strcmp(cachePattern, "SCRn")', 'SCRn makes a cache for each shot (thmShotCaches)'),
                  ('#define SCRN_MAX   9', 'SCRn shows _SCR to _SCR9'),
                  ('drawGameImageArt(menu, item, drawElem, gameImage, over, slideW * overW)', 'the next shot crossfades in over the one on show'),
                  ('gameImage->shots ? (const void *)gameImage->shots : texture', 'a new shot crossfades; it does not fade in again from nothing'),
                  ('if (mutableImage->shots && !mutableImage->shotsLinked)', "the shots' caches are freed with the theme, once"),
                  ('scrShowShot(turn * shotSlides, scrShowOrder(e))', 'an SCRn slide shows the next shot each time the show comes round'),
                  ('int turn = slideShow.pass + (e->slide < slideShow.cur);', 'a slide shown this round fades in on its next shot, never pops to it'),
                  ('scrShowTex(menu, item, img, k, 0);', 'the shots are found in order, the first unknown one asked for'),
                  ('infoGroupFrame(thmItemKey(item));', 'a rescan rebuilding the list under the info page must not fade it in again (the game, not its row)'),
                  ('slideShow.item = key;', "a rescan must not start the slideshow over"),
                  ('if (slideShow.cur <= was) // round again', 'the show counts its rounds')):
    if need not in themes:
        fail.append('themes.c: ' + why)
SCRN_TEST = """
#include <stdio.h>
#define SCRN_MAX 9
static struct { signed char st[SCRN_MAX]; } scrShow;
""" + re.search(r'static int scrShowKnown\(int \*all\)\n\{.*?\n\}\n', themes, re.S).group(0) + \
    re.search(r'static int scrShowShot\(int b, int o\)\n\{.*?\n\}\n', themes, re.S).group(0) + """
static void set(const char *s) { int i; for (i = 0; i < SCRN_MAX; i++) scrShow.st[i] = s[i] == '1' ? 1 : s[i] == 'x' ? -1 : 0; }
int main(void)
{
    set("000000000"); /* nothing known yet: no box shows anything (the probe asks for _SCR) */
    if (scrShowShot(0, 0) != -1 || scrShowShot(0, 1) != -1) return 1;
    set("111x00000"); /* three shots: two boxes never show the same one, and wrap */
    if (scrShowShot(0, 0) != 0 || scrShowShot(0, 1) != 1 || scrShowShot(2, 0) != 2 || scrShowShot(2, 1) != 0) return 2;
    set("1x0000000"); /* one shot: the second box shows its default */
    if (scrShowShot(0, 0) != 0 || scrShowShot(0, 1) != -1 || scrShowShot(1, 0) != 0) return 3;
    set("x00000000"); /* none */
    if (scrShowShot(0, 0) != -1) return 4;
    set("111111111"); /* all nine: that is every one */
    if (scrShowShot(8, 0) != 8 || scrShowShot(8, 1) != 0) return 5;
    set("11x111000"); /* a gap ends the run: _SCR4 on is never shown */
    if (scrShowShot(1, 1) != 0 || scrShowShot(2, 0) != 0) return 6;
    set("110000000"); /* still finding them: a shot known shows, one past them waits */
    if (scrShowShot(0, 1) != 1 || scrShowShot(1, 1) != -1) return 7;
    set("011000000"); /* _SCR2 and _SCR3 came back first: nothing past an unknown _SCR shows (the lab's case) */
    if (scrShowShot(0, 0) != -1 || scrShowShot(2, 0) != -1) return 8;
    printf("scrn OK\\n");
    return 0;
}
"""
if cc and not fail:
    env = dict(os.environ)
    if cc.startswith('C:/msys64'):
        env['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 's.c').write_text(SCRN_TEST)
        exe = td / 's.exe'
        r = subprocess.run([cc, str(td / 's.c'), '-o', str(exe)], capture_output=True, text=True, env=env)
        if r.returncode:
            fail.append('the SCRn show must build on the PC: ' + r.stderr[-600:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True, env=env)
            if r.returncode:
                fail.append('the SCRn show failed check %d' % r.returncode)

print('\n'.join(fail) or 'build108: iprp IOPRP device, GS readback steps, frame geometry and RGB555 paths, roll mailbox, BDM walk, roll layout, launch handover, silent menu and exact frame, the in-game screens, SCRn OK')
sys.exit(1 if fail else 0)
