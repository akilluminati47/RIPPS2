"""Build 99: loading and cancel round-up, RiptOPL's identity contract, release.

Static checks on the patched tree (the music path's behaviour is run by RiptOPL's test_bgm_source.py, which compiles
it against a card that loses descriptors)."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from r2src import unwrap, TR_STUBS  # noqa: E402

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
rd = lambda p: unwrap((root / p).read_text(encoding='utf-8').replace('\r\n', '\n'))  # build 104: as before _t
fail = []

# the music's own read path: big pieces into RAM, a short track whole, the old direct reads without the memory
snd = rd('src/sound.c')
for needle, why in (('#define BGM_CACHE_FIRST (64 * 1024)', 'pieces start at 64 KB'),
                    ('#define BGM_CACHE_BLOCK (256 * 1024)', 'and grow to 256 KB'),
                    ('#define BGM_CACHE_WHOLE (512 * 1024)', 'a track up to 512 KB is held whole'),
                    ('static size_t bgmCacheRead(bgm_source_t *src, long off, unsigned char *buf, size_t n)', 'the cache reader'),
                    ('size_t r = bgmCacheRead(src, src->pos, (unsigned char *)ptr, size * nmemb) / size;', 'vorbisfile reads through it'),
                    ('got = bgmCacheRead(src, b, bgmFixBuf, lead + n + OGG_HDR_MAX);', 'the top-bit serial reader too'),
                    ('src->noCache = 1; // no memory for it: straight from the drive, as before', 'without memory the old path'),
                    ('free(src->cache); // build 99', 'the cache goes with the source'),
                    ('memset(src, 0, sizeof(*src)); // build 99', 'a new source starts with no piece in RAM')):
    if needle not in snd:
        fail.append('music read path: %s (%s missing)' % (why, needle))
seek = snd[snd.index('static int bgmSourceSeek('):]
seek = seek[:seek.index('\n}\n')]
if 'fseek(' in seek:
    fail.append('a music seek must only move the position (the next read brings the piece in)')

# drives named by their driver, not their slot: mass0: on the internal exFAT HDD is no USB
bdm, st, ra = rd('src/bdmsupport.c'), rd('src/ripps2status.c'), rd('src/ripps2ra.c')
if 'const char *bdmSlotDriveName(int slot)' not in bdm or 'case BDM_TYPE_ATA:\n            return "HDD";' not in bdm:
    fail.append('bdmSlotDriveName must name a drive by its driver (an exFAT HDD is HDD)')
if 'if ((drive = bdmSlotDriveName(d)) != NULL)' not in ra or '"MMCE 0", "MMCE 1"' not in ra:
    fail.append('YOUR ACCOUNT must say where a game is by the drive\'s driver, and MMCE 0 / 1')
# build 113: the POPS and EMBER install rows went with the copies RIPPS2 carried; build 114: STATUS's DRIVES names every
# drive by its driver, and LAUNCHERS says where SEANCE found Ember; build 135: the Neutrino install row (mass0:/neutrino) went too
for needle in ('t == BDM_TYPE_ATA ? "internal HDD (exFAT)"', 'stLauncher(SEANCE_EMBER, "Ember", p, 1);','LR_ADD("drive      mass%c: is %s\\r\\n"'):
    if needle not in st:
        fail.append('STATUS / the launch report must name mass0: by its driver (%s missing)' % needle)
for gone in ('"USB POPS folder"', '"USB EMBER folder"', '"USB  (mass0:/neutrino)"', 'Not found on USB.'):
    if gone in st:
        fail.append('STATUS still calls mass0: USB whatever it is: %s' % gone)

# Grid's coverless serial: exactly a PS2 startup ID, never a PS1 row's VCD or Ember name
th = rd('src/themes.c')
if 'static int gridRowSerial(item_list_t *src, int id, char *out, int size)' not in th or \
        'libListRowView(src, id) == LIB_VIEW_PS1' not in th or '!gridRowSerial(src, it->item.id, serial, sizeof(serial))' not in th:
    fail.append("a coverless tile's serial must come from a PS2 row only")
cc = shutil.which('gcc') or shutil.which('cc')
if cc:
    fn = th[th.index('static int gridSerial(const char *startup, char *out, int size)'):]
    fn = fn[:fn.index('\n}\n') + 3]
    prog = '#include <stdio.h>\n#include <string.h>\n#include <ctype.h>\n' + fn + r'''
int main(void)
{
    static const char *const in[] = {"SLUS_204.82", "slus_204.82", "SCUS_949.00.Crash Bandicoot", "Crash Bandicoot (USA)",
                                     "SLUS_2O4.82", "ABCD-Game", "SLUS-204.82", "SLUS_20482", "", "SLES_123.4X"};
    char out[24];
    int i;
    for (i = 0; i < (int)(sizeof(in) / sizeof(in[0])); i++) {
        int ok = gridSerial(in[i], out, sizeof(out));
        printf("%s|%s\n", in[i], ok ? out : "-");
    }
    return 0;
}
'''
    with tempfile.TemporaryDirectory() as td:
        open(td + '/g.c', 'w').write(prog)
        r = subprocess.run([cc, '-std=gnu99', '-Wall', td + '/g.c', '-o', td + '/g.exe'], capture_output=True, text=True)
        if r.returncode:
            fail.append('gridSerial did not compile on the PC: ' + r.stderr[-400:])
        else:
            got = subprocess.run([td + '/g.exe'], capture_output=True, text=True).stdout.split('\n')
            want = ['SLUS_204.82|SLUS-20482', 'slus_204.82|SLUS-20482', 'SCUS_949.00.Crash Bandicoot|-', 'Crash Bandicoot (USA)|-',
                    'SLUS_2O4.82|-', 'ABCD-Game|-', 'SLUS-204.82|-', 'SLUS_20482|-', '|-', 'SLES_123.4X|-']
            if got[:len(want)] != want:
                fail.append('gridSerial: %r' % got[:len(want)])

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build99: the music reads the drive in big pieces from RAM, drives named by their driver, coverless serials are PS2 IDs only OK')
