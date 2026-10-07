"""Build 87: the in-game menu. OPL's IGR combo pauses the game under RESUME / ACHIEVEMENTS / EXIT GAME
(ee_core igrmenu.c), drawn on the frame GSM saw the game show (capture-only mode when GSM is off).

Static checks on the patched tree, then, when a C compiler is around, the panel rendered on the PC."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
menu, pad, gsm, eng = rd('ee_core/src/igrmenu.c'), rd('ee_core/src/padhook.c'), rd('ee_core/src/gsm_api.c'), rd('ee_core/src/gsm_engine.S')
cfg, emain, emk, sysc = rd('ee_core/include/coreconfig.h'), rd('ee_core/src/main.c'), rd('ee_core/Makefile'), rd('src/system.c')
fail = []

if 'igrmenu.o' not in emk:
    fail.append('igrmenu.c must be built into ee_core')
# the config fields are appended after the RA block, never inserted
if cfg.index('int IgrMenu;') < cfg.index('void *raWorkArea;'):
    fail.append('the in-game menu fields must come after the RetroAchievements block')
if 'config->IgrMenu = gRipps2IgrMenu;' not in sysc or 'sbGetRaInfo(&config->RaTotal, &config->RaUnlocked)' not in sysc:
    fail.append('the launch must hand ee_core the menu switch and the RA numbers')

# the pause: the combo opens the menu, the power button still leaves at once; RESUME goes back to sleep
if 'Pad_Data.combo_type == IGR_COMBO_START_SELECT && config->IgrMenu && !Power_Button.press' not in pad:
    fail.append('the reset combo must open the menu, and the power button must not')
for what in ('IGR_HoldInterrupts();', 'IGR_PauseThreads();', 'IGR_ResumeGame();', 'choice = IGR_MenuRun(IGR_PadButtons);'):
    if what not in pad:
        fail.append('the IGR thread must pause and resume the game: %s' % what)
if 'ResetEE(0x7E);' not in pad:
    fail.append('leaving from the menu must not reset the DMAC (a SIF transfer would stick)')
if 'i != IGR_INTC_SBUS' not in pad or '{0, 1, 2, 3, 4, 8, 9}' not in pad:
    fail.append('the pause must keep the SIF running: padman fills the pad buffer through it')
if 'DisableGSMCapture();' not in pad:
    fail.append('the way out must take the capture trap down')

# GSM capture only: armed when the menu is on and GSM is not; records and passes through; writes only
if 'EnableGSMCapture();' not in emain or 'config->IgrMenu && !(g_compat_mask & COMPAT_MODE_6)' not in emain:
    fail.append('ee_core must arm the capture trap for the menu (not for games with IGR off)')
if 'GSMCaptureOnly' not in eng or 'gsm_full_write:' not in eng or '0x20280000' not in eng:
    fail.append('gsm_engine.S needs the capture-only path and a write-only trap')
for reg in ('Source_PMODE', 'Source_SMODE2', 'Source_DISPFB1', 'Source_DISPFB2', 'Source_DISPLAY1', 'Source_DISPLAY2'):
    if 'sd      $a1, %s($s0)' % reg not in eng.split('gsm_full_write:')[0]:
        fail.append('capture only must record %s' % reg)
if 'if (!GSMCaptureArmed)' not in gsm:
    fail.append('DisableGSMCapture must be a no-op when nothing was armed')

# the panel: image transfers only, no GS drawing state; static (drawn on open and on a change)
if 'VIF_DIRECT(' not in menu or 'VIF_FLUSHA' not in menu or 'GS_TRXDIR' not in menu:
    fail.append('the panel must go up as VIF1 DIRECT image transfers')
for bad in ('GS_PRIM', 'GS_FRAME_1', 'GS_TEST_1', 'GS_SCISSOR'):
    if bad in menu:
        fail.append('the panel must not touch the GS drawing state (%s)' % bad)
if 'armed = dirty = 1' not in menu:
    fail.append('EXIT GAME must take a second press')
if 'IGR_MENU_TEST' in menu and '#ifdef IGR_MENU_TEST' not in menu:
    fail.append('the PCSX2 frame guess must stay behind IGR_MENU_TEST')
if '#ifdef IGR_MENU_TEST' not in menu or 'RIPPS2_IGR_TEST' not in rd('Makefile'):
    fail.append('the PCSX2 test flavour must exist (RIPPS2_IGR_TEST)')

# the panel on the PC: every page renders, the hint shows the right buttons
cc = shutil.which('gcc') or shutil.which('cc')
if cc and not fail:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'tamtypes.h').write_text('typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;\n')
        (td / 't.c').write_text(r'''
#include <stdio.h>
#include "igrmenu.c"
static u8 buf[320 * 212 * 3];
static int text(void) { int i, n = 0; for (i = 0; i < 320 * 212 * 3; i += 3) n += buf[i] == 255 && buf[i + 1] == 255; return n; }
int main(void)
{
    igrm_info_t a = {0, "SLUS_209.46", "mc0:/BOOT/RIPPS2.ELF", 1, 1, 40, 12, 1, 2};
    int sel, h;
    for (sel = 0; sel < 3; sel++) {
        h = igrmTestRender(&a, sel, 0, 2, 2, buf);
        if (h != 212 || text() == 0) return 10 + sel;
    }
    igrmTestRender(&a, 1, 0, 2, 2, buf);
    if (igrmLine[igrmLines - 1].glyph[0] != G_CIRCLE) return 20;
    if (igrmLine[3].y != ROW_ITEM0 + ITEM_STEP) return 21;
    a.confirmCircle = 1;
    igrmTestRender(&a, 0, 0, 1, 1, buf);
    if (igrmLine[igrmLines - 1].glyph[0] != G_CIRCLE) return 22;
    printf("rendered\n");
    return 0;
}
''')
        exe = td / 't.exe'
        r = subprocess.run([cc, '-DIGR_MENU_HOST_TEST', '-I', str(td), '-I', str(root / 'ee_core/include'),
                            '-I', str(root / 'ee_core/src'), str(td / 't.c'), '-o', str(exe)], capture_output=True, text=True)
        if r.returncode:
            fail.append('the panel renderer must build on the PC: ' + r.stderr[-400:])
        else:
            r = subprocess.run([str(exe)], capture_output=True, text=True)
            if r.returncode:
                fail.append('the panel renderer failed check %d' % r.returncode)

print('\n'.join(fail) or 'build87: in-game menu paused, drawn by image transfers, capture-only GSM, RA page OK')
sys.exit(1 if fail else 0)
