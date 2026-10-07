"""Build 89: BIOS Sounds > Rip also plays the boot and the PS2 logo sequences; Ember's bios.bin from the console's
own ROM; RIPPOPS; Neutrino's automatic -logo after -bsd; the About credits (MCKILLA); the Settings scroll bar and
the right stick's peek.

Static checks on the patched tree; then, with a C compiler, the ripper run on a made-up SNDIMAGE that carries a
one-note sequence on a one-instrument bank (no BIOS needed), which must give 15 sounds."""
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: (root / p).read_text(encoding='utf-8')
rip, ember, vcd, sysc, dia = rd('src/ripps2biossnd.c'), rd('src/ripps2ember.c'), rd('src/vcdsupport.c'), rd('src/system.c'), rd('src/dia.c')
fail = []

# the system music
if '{"SNDBOOTS", "boot.adp"}' not in rip or '{"SNDLOGOS", "launch.adp"}' not in rip:
    fail.append('the boot and the PS2 logo must be ripped into boot.adp and launch.adp')
if 'unsigned long long pos = 0, step' not in rip:
    fail.append('the sequence voices must read their samples in fixed point (float drift detunes them)')

# Ember's BIOS from the ROM, offered where a launch finds none
if '0xBFC00000' not in ember or '"System ROM Version"' not in ember:
    fail.append('the PS1 BIOS must come from the ROM and be checked by its version string')
for f in ('src/bdmsupport.c', 'src/ethsupport.c', 'src/mmcesupport.c', 'src/udpfssupport.c'):
    if '!ripps2EmberBiosOffer(biosPath)' not in rd(f):
        fail.append('%s must offer to make bios.bin' % f)

# RIPPOPS
if 'vcdFindPopsElsewhere(devPrefix)' not in vcd or 'vcdCopyFile(src, path)' not in vcd:
    fail.append('the POPS check must find and copy the user\'s own POPS files from another drive')

# Neutrino: exactly one automatic -logo, after -bsd and before -dvd, in both branches
body = sysc[sysc.index('static int sysRunNeutrinoLaunch('):sysc.index('static int sysRunNeutrinoLaunch(') + 9000]
if body.count('argv[argc++] = "-logo";') != 2 or body.count('if (autoLogo && argc < argvMax)') != 2:
    fail.append('the automatic -logo must be offered in the apa and the bdm branches')
for branch in body[body.index('if (!strcmp(deviceName, "apa"))'):].split('} else {', 1):
    i_logo, i_dvd = branch.find('argv[argc++] = "-logo";'), branch.find('argv[argc++] = filePath;')
    i_bsd = branch.find('argv[argc++] = bsd;')
    if not (0 <= i_bsd < i_logo < i_dvd):
        fail.append('the automatic -logo must come after -bsd and before -dvd')

# the card manager keeps its name on screen; About credits the MCKILLA fork
if '"CARD MANAGER"' not in rd('src/ripps2card.c'):
    fail.append('the card manager keeps its name on screen')
about = rd('src/ripps2about.c')
for credit in ("ORBIT's Neutrino fork by danielnuld", 'Roboto Condensed by Google', 'RIPPS2 Audio Studio', "MCKILLA, RIPPS2's card manager fork"):
    if credit not in about:
        fail.append('About must credit: %s' % credit)

# the Settings scroll bar and the right stick's peek
if 'padGetRightStick(&sx, &sy);' not in dia or 'diaPeek = 0; // build 89: the view follows the cursor again' not in dia:
    fail.append('the right stick must peek a long page and the D-pad bring the view back')
if 'DIA_BAR_X' not in dia or 'thumbH' not in dia:
    fail.append('a long page must show a scroll bar')
peek = dia[dia.index('// build 89: the right stick peeks'):dia.index('if (getKey(KEY_LEFT))', dia.index('// build 89: the right stick peeks'))]
if 'sfxPlay' in peek:
    fail.append('peeking must make no cursor sound')


def lz_literals(data):
    out = bytearray(struct.pack('<I', len(data)))
    for i in range(0, len(data), 30):
        out += b'\0\0\0\0' + data[i:i + 30]
    return bytes(out)


def adpcm_tone(loop=False):
    out = bytearray()
    for b in range(40):
        nibs = [int(round(7 * math.sin(2 * math.pi * (b * 28 + i) / 14))) & 0xF for i in range(28)]
        flags = (4 if loop and b == 0 else 0) | ((3 if loop else 1) if b == 39 else 0)
        out += bytes([0x08, flags]) + bytes(nibs[i] | nibs[i + 1] << 4 for i in range(0, 28, 2))
    return bytes(out)


def romdir(files):
    files = [('RESET', b'\0' * 16), ('ROMDIR', b'')] + files
    for _ in range(2):
        entries = b''.join(struct.pack('<10sHI', n.encode(), 0, len(d)) for n, d in files) + b'\0' * 16
        files[1] = ('ROMDIR', entries)
    img = bytearray()
    for _, d in files:
        img += d + b'\0' * (-len(d) % 16)
    return bytes(img)


def sndimage():
    hd = bytearray(0x80 + 0x20 + 13 * 0x40)
    struct.pack_into('<I', hd, 0x2C, 0x80)
    struct.pack_into('<I', hd, 0x84, 13)
    for k in range(13):
        struct.pack_into('<HHHHHHHHI', hd, 0x80 + 0x20 + k * 0x40, 0x3000, 0x3000, 0x800, 0, 0x00FF, 0x5FCF, 0, 0, 0)
    # one program, one tone: the looping tone at root 60, a fast attack, a sustain that holds, a quick release
    bank = bytearray(0x20 + 4 + 8 + 16)
    struct.pack_into('<I', bank, 0x10, 0x20)
    struct.pack_into('<HH', bank, 0x20, 0, 4)
    p = 0x24
    bank[p:p + 3] = bytes([0, 127, 64])
    t = p + 8
    bank[t + 1], bank[t + 2], bank[t + 3] = 127, 60, 0
    struct.pack_into('<HHH', bank, t + 4, 0, 0x000F, 0x0000)
    bank[t + 10], bank[t + 11], bank[t + 12], bank[t + 15] = 0, 127, 64, 1
    seq = bytearray(0x110)
    struct.pack_into('<HHH', seq, 0, 127, 480, 120)
    for c in range(16):
        seq[0x10 + c * 16 + 1:0x10 + c * 16 + 5] = bytes([c, 0, 100, 64])
    seq += bytes([0x90, 60, 100, 0x83, 0x60, 0x80, 60, 0, 0x00, 0xFF, 0x2F, 0x00])
    return romdir([('SNDOSDDH', lz_literals(bytes(hd))), ('SNDOSDDB', lz_literals(adpcm_tone())),
                   ('SNDBOOTH', lz_literals(bytes(bank))), ('SNDBOOTB', lz_literals(adpcm_tone(loop=True))),
                   ('SNDBOOTS', lz_literals(bytes(seq))), ('SNDLOGOS', lz_literals(bytes(seq)))])


cc = shutil.which('gcc') or shutil.which('cc')
if cc and not fail:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'img.bin').write_bytes(sndimage())
        (td / 't.c').write_text(r'''
#include <stdio.h>
#include <string.h>
#include "include/ripps2biossnd.h"
static int seen, music;
static int put(const char *file, const unsigned char *adp, int size, void *ctx)
{
    (void)ctx;
    if (size < 48 || memcmp(adp, "APCM", 4)) return -1;
    if (!strcmp(file, "boot.adp") || !strcmp(file, "launch.adp")) {
        unsigned int n = adp[12] | adp[13] << 8 | adp[14] << 16 | (unsigned int)adp[15] << 24;
        if ((adp[8] | adp[9] << 8) != 4096 || n < 48000 / 2) { printf("bad %s (%u samples)\n", file, n); return -1; }
        music++;
    }
    seen++;
    return 0;
}
int main(int argc, char **argv)
{
    static unsigned char d[1 << 20];
    FILE *f = fopen(argv[1], "rb");
    int n = (int)fread(d, 1, sizeof(d), f), r;
    fclose(f);
    r = ripps2BiosSoundsFromImage(d, n, put, NULL);
    printf("%d %d %d\n", r, seen, music);
    return r == 15 && music == 2 ? 0 : 2;
}
''')
        exe = td / 't.exe'
        r = subprocess.run([cc, '-DRIPPS2_BIOSSND_HOST_TEST', '-I', str(root), str(td / 't.c'), str(root / 'src/ripps2biossnd.c'),
                            '-o', str(exe), '-lm'], capture_output=True, text=True)
        if r.returncode:
            fail.append('the ripper must build on the PC: ' + r.stderr[-400:])
        else:
            r = subprocess.run([str(exe), str(td / 'img.bin')], capture_output=True, text=True)
            if r.returncode:
                fail.append('the ripper must play a made-up sequence too (%d): %s' % (r.returncode, r.stdout.strip()))

print('\n'.join(fail) or 'build89: boot and launch ripped, Ember BIOS, RIPPOPS, -logo after -bsd, MCKILLA credited, scroll bar and peek OK')
sys.exit(1 if fail else 0)
