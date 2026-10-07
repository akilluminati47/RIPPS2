"""Build 88: Audio settings > BIOS Sounds > RIP (src/ripps2biossnd.c) and the Music row playing the track
called Menu when none is picked.

Static checks on the patched tree; then, with a C compiler, the ripper run on a made-up SNDIMAGE (no BIOS
is ever needed or shipped: a ROM directory, a 13-entry bank and one ADPCM tone, LZ-packed as literals)."""
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
rip, gui, snd, mk, dia = rd('src/ripps2biossnd.c'), rd('src/gui.c'), rd('src/sound.c'), rd('Makefile'), rd('src/dialogs.c')
fail = []

if 'ripps2biossnd.o' not in mk:
    fail.append('ripps2biossnd.c must be built')
if 'RIPPS2_RIP_BIOS_BUTTON' not in dia or 'ripps2RipBiosSoundsDialog();' not in gui:
    fail.append('Audio settings must have the BIOS Sounds > RIP button')
if '"rom0:SNDIMAGE"' not in rip:
    fail.append('the ripper must read the console\'s own BIOS (rom0:SNDIMAGE)')
for ev in ('cursor', 'confirm', 'cancel', 'page_in', 'page_out', 'transition', 'message', 'disc', 'error', 'save',
           'bd_connect', 'bd_disconnect', 'random'):
    if '"%s.adp"' % ev not in rip:
        fail.append('the ripper must write %s.adp' % ev)
for ev in ('"boot.adp"', '"launch.adp"'):
    if ev in rip:
        fail.append('boot and launch are system music, not menu sounds: %s must not be ripped' % ev)
if 'guiMsgBoxStartOption("RIP")' not in rip:
    fail.append('the rip must ask first (START), it replaces files')
if 'int bgmMusicDefault(' not in snd or 'bgmMusicDefault(musicFiles, musicCount)' not in gui or 'pick = bgmMusicDefault(names, n);' not in snd:
    fail.append('the Music row must default to the track called Menu')


def lz_literals(data):
    """The BIOS LZ format with every token a literal: a zero flag word before each 30 bytes."""
    out = bytearray(struct.pack('<I', len(data)))
    for i in range(0, len(data), 30):
        out += b'\0\0\0\0' + data[i:i + 30]
    return bytes(out)


def adpcm_tone():
    """A short tone as SPU2 ADPCM, filter 0 (each nibble is the sample): 40 blocks, the last one ends it."""
    out = bytearray()
    for b in range(40):
        nibs = [int(round(7 * math.sin(2 * math.pi * (b * 28 + i) / 14))) & 0xF for i in range(28)]
        out += bytes([0x00 | 8, 1 if b == 39 else 0]) + bytes(nibs[i] | nibs[i + 1] << 4 for i in range(0, 28, 2))
    return bytes(out)


def sndimage():
    bd = adpcm_tone()
    hd = bytearray(0x80 + 0x20 + 13 * 0x40)
    struct.pack_into('<I', hd, 0x2C, 0x80)
    struct.pack_into('<I', hd, 0x84, 13)
    for k in range(13):
        struct.pack_into('<HHHHHHHHI', hd, 0x80 + 0x20 + k * 0x40, 0x3000, 0x3000, 0x800, 0, 0x00FF, 0x5FCF, 0, 0, 0)
    files = [('RESET', b'\0' * 16), ('ROMDIR', b''), ('SNDOSDDH', lz_literals(bytes(hd))), ('SNDOSDDB', lz_literals(bd))]
    entries = b''.join(struct.pack('<10sHI', n.encode(), 0, len(d)) for n, d in files) + b'\0' * 16
    files[1] = ('ROMDIR', entries)
    entries = b''.join(struct.pack('<10sHI', n.encode(), 0, len(d)) for n, d in files) + b'\0' * 16
    img = bytearray()
    for n, d in files:
        d = entries if n == 'ROMDIR' else d
        img += d + b'\0' * (-len(d) % 16)
    return bytes(img)


cc = shutil.which('gcc') or shutil.which('cc')
if cc and not fail:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'img.bin').write_bytes(sndimage())
        (td / 't.c').write_text(r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "include/ripps2biossnd.h"
static int seen;
static int put(const char *file, const unsigned char *adp, int size, void *ctx)
{
    int i, loud = 0;
    (void)ctx;
    if (size < 48 || memcmp(adp, "APCM", 4) || adp[4] != 1 || adp[5] != 1) { printf("bad header %s\n", file); exit(3); }
    if ((adp[8] | adp[9] << 8) != 0x800) { printf("pitch %s\n", file); exit(4); }
    for (i = 16; i < size; i += 16) loud |= adp[i] & 0xF0 || memcmp(adp + i + 2, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0", 14);
    if (!loud) { printf("silent %s\n", file); exit(5); }
    seen++;
    return 0;
}
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    static unsigned char d[1 << 20];
    int n = (int)fread(d, 1, sizeof(d), f), r;
    fclose(f);
    r = ripps2BiosSoundsFromImage(d, n, put, NULL);
    printf("%d %d\n", r, seen);
    return r == 13 && seen == 13 ? 0 : 2;
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
                fail.append('the ripper failed on a made-up SNDIMAGE (%d): %s' % (r.returncode, r.stdout.strip()))

print('\n'.join(fail) or 'build88: BIOS Sounds > RIP writes all 13 menu events; Music defaults to Menu OK')
sys.exit(1 if fail else 0)
