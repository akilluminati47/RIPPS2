"""RIPPS2 build 129: .pad phase 2. PADEMU reads the block the launcher packs (padprofile.c, the reference decoder built
decode-only), ee_core hands it over after PADEMU's eight bytes with flag 1 << 19, the menu's USB pad driver reads the same
block and lets Set Up A USB Pad see a HID pad's reports, and the setup screen finds a button, a hat, a trigger and a stick
from what moved. On the PC: the wiring, padApplyMap, padfile.c built decode-only, and the setup screen's finder run on a
made-up pad."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
fail = []


def text(rel):
    p = root / rel
    if not p.exists():
        fail.append(rel + ' missing')
        return ''
    return p.read_text(encoding='utf-8', errors='replace')


pademu_mk = text('modules/pademu/Makefile')
pademu = text('modules/pademu/pademu.c')
pademu_usb = text('modules/pademu/ds34usb.c')
prof = text('modules/pademu/padprofile.c')
menu_mk = text('modules/ds34usb/iop/Makefile')
menu = text('modules/ds34usb/iop/ds34usb.c')
menu_ee = text('modules/ds34usb/ee/libds34usb.c')
iopmgr = text('ee_core/src/iopmgr.c')
coreconfig = text('ee_core/include/coreconfig.h')
system = text('src/system.c')
opl = text('src/opl.c')
pads = text('src/ripps2pads.c')
pad = text('src/pad.c')
gui = text('src/gui.c')
dialogs = text('src/dialogs.c')
base = text('lng_tmpl/_base.yml')

checks = [
    ('padprofile.o' in pademu_mk, 'pademu Makefile: padprofile.o'),
    ('PADEMU_PROFILES_FLAG' in pademu and 'padProfilesLoad' in pademu, 'pademu.c: the block read after the settings'),
    ('GENERIC' in pademu_usb and 'padProfileDecode' in pademu_usb and 'padGameMapApply' in pademu_usb,
     'PADEMU ds34usb.c: a profiled pad decoded, the game map applied'),
    ('PADFILE_DECODE_ONLY' in prof and 'PADPROFILE_NO_IMPORTS' in prof, 'padprofile.c: decode-only, shared with the menu driver'),
    ('padprofile.o' in menu_mk, 'menu ds34usb Makefile: padprofile.o'),
    ('DS34USB_GET_RAW' in menu and 'DS34USB_SET_PROFILES' in menu and 'pads_learn' in menu, 'menu ds34usb.c: raw reports, profiles, learn'),
    ('rpcbuf[256]' in menu_ee and 'ds34usb_get_raw' in menu_ee and 'ds34usb_set_profiles' in menu_ee, 'libds34usb: the new calls'),
    ('PadEmuArgs' in coreconfig, 'coreconfig.h: PadEmuArgs'),
    ('(1 << 19)' in iopmgr and '8 + 180' in iopmgr, 'iopmgr.c: PADEMU gets the block and the flag'),
    ('PadEmuArgs' in system and 'ripps2PadsBlock' in system, 'system.c: the block placed for ee_core'),
    ('ripps2PadsPrepare(gameIdStartup)' in opl and 'ripps2PadsMenuLoad()' in opl, 'opl.c: launch and boot read PADS'),
    ('ripps2PadsMenuTick' in pads and 'ripps2PadsMenuLearn' in pads, 'ripps2pads.c: the menu copy'),
    ('ripps2PadsMenuTick();' in pad, 'pad.c: readPads hands profiles to the driver'),
    ('guiSetUpUsbPad' in gui and 'RIPPS2_PAD_SETUP_BUTTON' in dialogs, 'gui.c/dialogs.c: Set Up A USB Pad'),
    ('label: RIPPS2_PAD_SETUP' in base and 'label: HINT_RIPPS2_PAD_SETUP' in base, '_base.yml: the button and its hint'),
]
for ok, what in checks:
    if not ok:
        fail.append(what)


def grab(src, start, end_marker='\n}\n'):
    i = src.find(start)
    if i < 0:
        fail.append('gui.c: ' + start + ' not found')
        return ''
    return src[i:src.index(end_marker, i) + len(end_marker)]


finder = '\n'.join([
    grab(gui, 'typedef struct\n{\n    int port, len, seq;', '} pad_setup_raw_t;\n'),
    grab(gui, 'static int padSetupBits('),
    grab(gui, 'static int padSetupFind('),
    grab(gui, 'static int padSetupAtRest('),
])

PROG = r'''
#include <stdio.h>
#include <string.h>
#include "include/padfile.h"
#define PAD_SETUP_SWING 0x50
''' + finder + r'''
int main(void)
{
    /* a made-up pad: byte 0 face buttons, byte 1 the rest (bit 3 set at rest: pressed is 0), byte 2 a hat (8 = centre),
       bytes 3-6 sticks round 0x80, byte 7 an analog L2, byte 8 a counter */
    unsigned char rest[16] = {0x00, 0x08, 0x08, 0x80, 0x7F, 0x80, 0x81, 0x00, 0x00};
    unsigned char noise[16] = {0, 0, 0, 3, 2, 3, 2, 0, 0xFF};
    unsigned char usedBits[16] = {0}, usedAxis[16] = {0};
    pad_setup_raw_t p;
    unsigned short buttons;
    unsigned char axes[4];
    int at = -1, bit = -1, low = -1;
    unsigned char map[PAD_B_COUNT];
    pad_def_t d;
    char err[96];
    const char *made = "[Device]\nformat=1\ndecoder=generic\n[Buttons]\ncross=b0.1\nselect=!b1.3\nl2=a7\nup=none\n[Axes]\n"
                       "dpad=hat2\nlx=a3\nly=a4-\ndeadzone=12\n";

    memset(&p, 0, sizeof(p));
    p.len = 9;
    memcpy(p.r, rest, 16);
    if (padSetupFind(rest, noise, &p, 0, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 0) return 1; /* nothing moved */
    p.r[0] = 0x02;
    if (padSetupFind(rest, noise, &p, 0, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 1 || at != 0 || bit != 1 || low) return 2;
    if (padSetupAtRest(rest, noise, usedAxis, &p)) return 3;
    usedBits[0] |= 2;
    if (padSetupFind(rest, noise, &p, 0, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 0) return 4; /* a used bit is not found again */
    memcpy(p.r, rest, 16);
    p.r[1] = 0x00;
    if (padSetupFind(rest, noise, &p, 0, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 1 || at != 1 || bit != 3 || !low) return 5;
    memcpy(p.r, rest, 16);
    p.r[2] = 0x00; /* Up on the hat: one bit drops, but on a d-pad step it is the hat */
    if (padSetupFind(rest, noise, &p, 0, 1, 0, usedBits, usedAxis, &at, &bit, &low) != 2 || at != 2) return 6;
    memcpy(p.r, rest, 16);
    p.r[7] = 0xFF; /* L2, an analog trigger */
    if (padSetupFind(rest, noise, &p, 0, 0, 1, usedBits, usedAxis, &at, &bit, &low) != 3 || at != 7) return 7;
    p.r[7] = 0x01; /* its first step down is one bit: not yet anything on a trigger step */
    if (padSetupFind(rest, noise, &p, 0, 0, 1, usedBits, usedAxis, &at, &bit, &low) == 3) return 8;
    memcpy(p.r, rest, 16);
    p.r[3] = 0xFF; /* the left stick to the right */
    if (padSetupFind(rest, noise, &p, 1, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 3 || at != 3 || low) return 9;
    p.r[3] = 0x80;
    p.r[4] = 0x00; /* "down" ran the other way: inverted */
    if (padSetupFind(rest, noise, &p, 1, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 3 || at != 4 || !low) return 10;
    memcpy(p.r, rest, 16);
    p.r[8] = 0x55; /* the counter moved: not a press, and still at rest */
    if (padSetupFind(rest, noise, &p, 0, 0, 0, usedBits, usedAxis, &at, &bit, &low) != 0 || !padSetupAtRest(rest, noise, usedAxis, &p)) return 11;
    usedAxis[3] = 1;
    p.r[3] = 0x90; /* an axis a little off rest is at rest */
    if (!padSetupAtRest(rest, noise, usedAxis, &p)) return 12;
    /* what the screen writes, read back and run */
    if (padDefParse(made, strlen(made), 0x1234, 0x5678, &d, err, sizeof(err))) { printf("%s\n", err); return 13; }
    memcpy(p.r, rest, 16);
    p.r[0] = 0x02; p.r[1] = 0x00; p.r[2] = 0x06; p.r[7] = 0xC0; p.r[4] = 0x00;
    padTranslate(&d, p.r, p.len, &buttons, axes);
    if (buttons != (unsigned short)~(1u << PAD_B_CROSS | 1u << PAD_B_SELECT | 1u << PAD_B_L2 | 1u << PAD_B_LEFT) || axes[PAD_AX_LY] != 255)
        { printf("buttons %04x ly %d\n", buttons, axes[PAD_AX_LY]); return 14; }
    /* the game map: CROSS to CIRCLE, SELECT to nothing, the rest as they were */
    memset(map, PAD_REMAP_SAME, sizeof(map));
    if (!padMapIsSame(map)) return 15;
    map[PAD_B_CROSS] = PAD_B_CIRCLE;
    map[PAD_B_SELECT] = 0xFE;
    if (padMapIsSame(map)) return 16;
    buttons = padApplyMap((unsigned short)~(1u << PAD_B_CROSS | 1u << PAD_B_SELECT | 1u << PAD_B_START), map);
    if (buttons != (unsigned short)~(1u << PAD_B_CIRCLE | 1u << PAD_B_START)) { printf("map %04x\n", buttons); return 17; }
    printf("pad129 ok\n");
    return 0;
}
'''

cc = shutil.which('gcc') or shutil.which('cc')
if cc is None:
    print('\n'.join(fail) or 'build129 pad: no host C compiler, programs skipped')
    sys.exit(1 if fail else 0)

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    src = root / 'src/padfile.c'
    (td / 'only.c').write_text('#include <string.h>\n#define PADFILE_DECODE_ONLY\n#include "src/padfile.c"\nint main(void) { return 0; }\n',
                               encoding='utf-8')
    r = subprocess.run([cc, '-std=gnu99', '-Wall', '-Wextra', '-Werror', '-I', str(root), str(td / 'only.c'), '-o', str(td / 'only.exe')],
                       capture_output=True, text=True)
    if r.returncode:
        fail.append('padfile.c must build decode-only (as PADEMU and the menu driver build it): ' + r.stderr[-600:])
    if finder:
        (td / 't.c').write_text(PROG, encoding='utf-8')
        r = subprocess.run([cc, '-std=gnu99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function', '-I', str(root), str(td / 't.c'), str(src),
                            '-o', str(td / 't.exe')], capture_output=True, text=True)
        if r.returncode:
            fail.append('the setup screen\'s finder must build on the PC: ' + r.stderr[-800:])
        else:
            r = subprocess.run([str(td / 't.exe')], capture_output=True, text=True)
            if r.returncode:
                fail.append('pad129 check %d failed: %s' % (r.returncode, r.stdout.strip()))

print('\n'.join(fail) or 'build129 pad: PADEMU, ee_core, the launcher and the menu driver wired; decode-only build; the setup '
      'screen finds a button, an active-low button, a hat, a trigger and a stick (inverted too), ignores a counter; the game map applies')
sys.exit(1 if fail else 0)
