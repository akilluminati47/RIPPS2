"""Build 118 (the user, 10/27): the boot sound read first at boot, so it plays with the towers' first frame; the ART Pack
(Settings > Game Sources > Cache), every started drive's ART folder in one art.tar on the drive picked, fastest first,
read through one sorted index, and answering for the games it was built for; AUDIO and MEDIA README.txt saying where
each belongs.

Static checks on the patched tree, then two programs built on the PC:
  - the key parser and the tar writer of ripps2artpack.c: a pack written by them must be a tar Python reads, byte for
    byte, and each picture's game must come out of its name (OPL Manager's _BG_00 and _SCR_01 included);
  - RiptOPL's own tar.c (the engine the PS2 reads the pack with): that pack and one written out of order, every
    prefix looked up through the sorted index must give what a scan of the archive gives, the first member in archive
    order, before and after the index is read back from art_cache.bin."""
import os
import random
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from r2src import unwrap  # noqa: E402

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
raw = lambda p: (root / p).read_text(encoding='utf-8').replace('\r\n', '\n')
rd = lambda p: unwrap(raw(p))
fail = []


def need(text, items, where):
    for s, why in items:
        if s not in text:
            fail.append('%s: %s' % (where, why))


def body(text, head):
    i = text.index(head)
    return text[i:text.index('\n}\n', i) + 3]


# ---- the boot sound, first at boot
snd = rd('src/sound.c')
need(snd, (('void sfxBootEarlyQueue(int themeID)', 'the boot sound queued with the settings read'),
           ('ioPutRequest(IO_CUSTOM_SIMPLEACTION, &sfxBootEarlyWork);', 'read on the IO worker (never the main thread)'),
           ('int keepBoot = bootSnd && sfxBootEarly == SFX_EARLY_READY && sfxReady[SFX_BOOT];', "the set's load keeps it"),
           ('sfx_files[SFX_BOOT].duration_ms = bootMs;', 'and its length, which times the music after it')), 'sound.c')
init = body(snd, 'int sfxInit(int bootSnd)')
if 'if (!keepBoot) {' not in init or init.index('if (!keepBoot) {') > init.index('audsrv_adpcm_init();'):
    fail.append('sfxInit: no audsrv_adpcm_init under a boot sound that is already playing')
start = body(snd, 'void sfxBootStart(void)')
# build 119: the IO worker sends it (the main thread's send raced a drive's driver load for IOP memory)
upl = '&sfxBootEarlyUpload)'
if upl not in start or start.index('audsrv_adpcm_init();') > start.index(upl):
    fail.append('sfxBootStart: the early boot sound goes to the SPU after audio is up')
opl = rd('src/opl.c')
load = opl[opl.index('static void _loadConfig()'):]
load = load[:load.index('\n}\n')]
if 'sfxBootEarlyQueue(themeID);' not in load or load.index('sfxBootEarlyQueue(themeID);') > load.index('applyConfig(themeID, langID, 0);'):
    fail.append('_loadConfig: the boot sound is queued before applyConfig queues the drives')

# ---- the ART Pack: the engine
tar = rd('src/tar.c')
need(tar, (('static void tarSortIndex(TarKind kind)', 'one sorted order per index'),
           ('return tarFindPrefixSorted(kind, prefix);', 'prefix lookups through it'),
           ('void tarSetPreferredRoot(TarKind kind, const char *mountRoot)', "the pack's drive swept first"),
           ('int tarLoadedPath(TarKind kind, char *out, int outSize)', 'which archive is held'),
           ('TarEntryBase *tarFindLoaded(TarKind kind, const char *name)', 'its list read without a sweep')), 'tar.c')
tc = rd('src/texcache.c')
need(tc, (('result == ART_TAR_MISS && ripps2ArtPackAnswers(req->value)', 'the pack answers for its games'),
          ('texArtAliasNames(req->value, req->cache->suffix, aliasKeys, aliasKinds, 8)', "a PS1 game's other names looked up in the pack"),
          ('if (result < 0 && !packAnswered)', 'and the folder is not asked then'),
          ('texLoadArtFromMemory(texture, buffer, entry->rawSize', 'PNG or JPG out of the pack')), 'texcache.c')
need(rd('src/textures.c'), (('int texLoadArtFromMemory(GSTEXTURE *texture, const void *buf, u32 size, int background)', 'a JPG in a pack'),), 'textures.c')
ap = rd('src/ripps2artpack.c')
need(ap, (('#define AP_LIST      "RIPPS2ART.LST"', "the pack's own list of games"),
          # build 126: a PS1 game is in the list too, its other keys looked up in the pack (texcache.c texArtAliasNames)
          ('if (strlen(startup) >= AP_KEY || apKeyCount >= AP_MAX_KEYS)', 'every game with a key in the list, PS1 ones too'),
          ('setvbuf(out, NULL, _IOFBF, 256 * 1024);', 'whole 256 KB writes'),
          ('qsort(order, n, sizeof(int), apSpeedCmp);', 'the fastest drive first'),
          ('gEnableArtTar = 0;\n    tarInvalidate(TAR_KIND_ART);\n    ioBlockOps(1);', 'nothing reads the pack while it is written'),
          ('remove(pack); // never a pack half written', 'a stopped or failed pack is removed')), 'ripps2artpack.c')
need(rd('src/ripps2art.c'), (('ripps2ArtPackNoteNew(file);', 'a fetched cover is new to the pack'),), 'ripps2art.c')
need(rd('src/ripps2shot.c'), (('ripps2ArtPackNoteNew(path);', 'a developed shot is new to the pack'),), 'ripps2shot.c')
need(rd('src/dialogs.c'), (('{UI_BUTTON, RIPPS2_ARTPACK_BUTTON, 1, 1, _STR_HINT_RIPPS2_ART_PACK', 'Cache > ART Pack'),
                          ('{UI_LABEL, RIPPS2_ARTPACK_ROW,', 'the pack in use')), 'dialogs.c')
need(rd('src/gui.c'), (('artPack |= ripps2ArtPackDialog();', 'the button opens it'),), 'gui.c')
need(opl, (('configSetStr(configOPL, "ripps2_artpack", gRipps2ArtPack);', 'saved'),
           ('ripps2ArtPackApplySettings();', 'and its drive swept first from boot')), 'opl.c')
if 'ripps2artpack.o' not in raw('Makefile'):
    fail.append('Makefile: ripps2artpack.o')
disc = raw('src/ripps2disc.c')
need(disc, (('"  Beside RIPPS2.ELF, on the drive RIPPS2 starts from: the boot reads it first.\\r\\n"', "AUDIO's README says where it goes"),
            ('"  On your biggest drive. MEDIA holds the large things', "and MEDIA's")), 'ripps2disc.c')

# ---- the programs
cc = shutil.which('gcc') or shutil.which('cc')


def fn(text, head):
    return body(text, head)


SHIM = r'''
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef uint64_t u64;
#define memalign(a, s) malloc(s)
#define lseek64 lseek
#ifdef _WIN32
#include <io.h>
#undef O_RDONLY
#undef O_WRONLY
#define O_RDONLY (_O_RDONLY | _O_BINARY)
#define O_WRONLY (_O_WRONLY | _O_BINARY)
#endif
'''

WRITER = r'''
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
@FUNCS@
int main(int argc, char **argv)
{
    FILE *out = fopen(argv[1], "wb");
    static unsigned char data[3000];
    unsigned char head[512];
    char key[64];
    int i, k;
    for (i = 2; i < argc; i++) {
        int size = 100 + i * 517 % 2500;
        for (k = 0; k < size; k++)
            data[k] = (unsigned char)(k * 7 + i);
        apHeader(head, argv[i], size, 1761600000u);
        fwrite(head, 1, 512, out);
        fwrite(data, 1, size, out);
        for (k = size % 512 ? 512 - size % 512 : 0; k > 0; k--)
            fputc(0, out);
        printf("%s %d %s\n", argv[i], size, ripps2ArtKeyOf(argv[i], key, sizeof(key)) ? key : "-");
    }
    memset(head, 0, 512);
    fwrite(head, 1, 512, out);
    fwrite(head, 1, 512, out);
    fclose(out);
    return 0;
}
'''

READER = r'''
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include "include/tar.h"
/* what tar.c did before build 118: the first member in archive order whose name starts with the prefix */
static int scanFirst(const char *names[], int n, const char *prefix)
{
    for (int i = 0; i < n; i++)
        if (!strncasecmp(names[i], prefix, strlen(prefix)))
            return i;
    return -1;
}
int main(int argc, char **argv)
{
    /* argv[1] the tar, then the member names in archive order */
    const char **names = (const char **)&argv[2];
    int n = argc - 2, bad = 0, pass;
    for (pass = 0; pass < 2; pass++) { /* the second time the index comes from art_cache.bin */
        tarClose(TAR_KIND_ART);
        if (tarLoadFile(TAR_KIND_ART, argv[1]) != 0) {
            printf("FAIL load pass %d\n", pass);
            return 1;
        }
        char held[256];
        if (!tarLoadedPath(TAR_KIND_ART, held, sizeof(held)) || strcmp(held, argv[1])) {
            printf("FAIL loaded path\n");
            return 1;
        }
        for (int i = 0; i < n; i++)
            for (int cut = 1; cut <= (int)strlen(names[i]); cut += 3) {
                char prefix[64];
                snprintf(prefix, sizeof(prefix), "%.*s", cut, names[i]);
                TarEntryBase *e = tarFindPrefixExact(TAR_KIND_ART, prefix);
                int want = scanFirst(names, n, prefix);
                TarEntryArt *a = (TarEntryArt *)e;
                if ((want < 0) != (e == NULL) || (e && strcmp(a->filename, names[want]))) {
                    if (bad++ < 5)
                        printf("FAIL '%s': got %s, wanted %s\n", prefix, e ? a->filename : "none", want >= 0 ? names[want] : "none");
                }
            }
        if (tarFindPrefixExact(TAR_KIND_ART, "ZZZZ_999.99_") != NULL || tarFindLoaded(TAR_KIND_ART, names[n - 1]) == NULL)
            bad++;
    }
    printf("%d members, %d wrong\n", n, bad);
    return bad != 0;
}
'''

NAMES = ['SLUS_210.50_COV.png', 'SLUS_210.50_COV2.png', 'SLUS_210.50_BG_00.jpg', 'SLES_510.61_SCR_01.png', 'SCUS_971.99_ICO.png',
         'SLUS_206.42_LGO.png', 'SLUS_206.42_SCR2.png', 'SLUS_206.42_SCR3.png', 'slus_216.33_cov.PNG', 'SCPS_150.13_LAB.jpg',
         'SLUS_210.08_BG.png', 'SCUS_972.68_COV.jpg', 'SCUS_972.68_COV.png', 'Free McBoot.png', 'RIPPS2ART.LST']
KEYS = {'SLUS_210.50_COV.png': 'SLUS_210.50', 'SLUS_210.50_BG_00.jpg': 'SLUS_210.50', 'SLES_510.61_SCR_01.png': 'SLES_510.61',
        'SLUS_206.42_SCR3.png': 'SLUS_206.42', 'slus_216.33_cov.PNG': 'slus_216.33', 'Free McBoot.png': '-', 'RIPPS2ART.LST': '-'}

if cc is None:
    print('build118: no host C compiler, programs skipped')
elif not fail:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / 'include').mkdir()
        (t / 'shim.h').write_text(SHIM)
        (t / 'ps2sdkapi.h').write_text('')
        (t / 'tamtypes.h').write_text('')
        (t / 'include' / 'tar.h').write_text(raw('include/tar.h'))
        (t / 'include' / 'ioman.h').write_text('#define LOG(...) ((void)0)\n')
        (t / 'tar.c').write_text(raw('src/tar.c'))
        funcs = '\n'.join(fn(ap, h) for h in ('static unsigned int apHash(', 'static int apIsKind(', 'int ripps2ArtKeyOf(',
                                              'static void apHeader('))
        (t / 'writer.c').write_text(WRITER.replace('@FUNCS@', funcs))
        (t / 'reader.c').write_text(READER)
        flags = ['-std=gnu99', '-Wall', '-Wno-unused-function', '-include', str(t / 'shim.h'), '-I', str(t)]
        r1 = subprocess.run([cc] + flags + [str(t / 'writer.c'), '-o', str(t / 'writer.exe')], capture_output=True, text=True)
        r2 = subprocess.run([cc] + flags + [str(t / 'tar.c'), str(t / 'reader.c'), '-o', str(t / 'reader.exe')], capture_output=True, text=True)
        if r1.returncode or r2.returncode:
            fail.append('the programs do not build:\n' + (r1.stderr + r2.stderr)[-2500:])
        else:
            pack = (t / 'ART' / 'art.tar').as_posix() # tar.c finds art_cache.bin's folder by the last '/'
            (t / 'ART').mkdir()
            w = subprocess.run([str(t / 'writer.exe'), pack] + NAMES, capture_output=True, text=True)
            got = {}
            for line in w.stdout.splitlines(): # "<name> <size> <key>" (a name may hold spaces)
                name, size, key = line.rsplit(' ', 2)
                got[name] = (int(size), key)
            for name, key in KEYS.items():
                if got.get(name, (0, None))[1] != key:
                    fail.append('ripps2ArtKeyOf(%s): %s, wanted %s' % (name, got.get(name, (0, None))[1], key))
            with tarfile.open(pack) as tf:
                members = tf.getmembers()
                if [m.name for m in members] != NAMES:
                    fail.append('the pack as Python reads it: %s' % [m.name for m in members])
                for m in members:
                    data = tf.extractfile(m).read()
                    i = NAMES.index(m.name) + 2
                    if len(data) != got[m.name][0] or data != bytes(((k * 7 + i) & 0xFF) for k in range(len(data))):
                        fail.append('the pack: %s holds other bytes' % m.name)
            # tar.c on the PS2's pack, then on one written in another order by Python (a pack made on a PC)
            r = subprocess.run([str(t / 'reader.exe'), pack] + NAMES, capture_output=True, text=True)
            if r.returncode:
                fail.append("tar.c on RIPPS2's pack: " + (r.stdout + r.stderr)[-600:])
            shuffled = NAMES[:]
            random.Random(118).shuffle(shuffled)
            other = t / 'PC' / 'ART'
            other.mkdir(parents=True)
            with tarfile.open(other / 'art.tar', 'w', format=tarfile.USTAR_FORMAT) as tf:
                for name in shuffled:
                    src = t / 'one'
                    src.write_bytes(name.encode() * 3)
                    tf.add(src, arcname=name)
            r = subprocess.run([str(t / 'reader.exe'), (other / 'art.tar').as_posix()] + shuffled, capture_output=True, text=True)
            if r.returncode:
                fail.append("tar.c on a PC's pack: " + (r.stdout + r.stderr)[-600:])
            else:
                print(r.stdout.strip())

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build118: the boot sound first at boot; the ART Pack built as a plain tar, read through a sorted index that finds what a scan finds, answering for its games; AUDIO and MEDIA say where they belong OK')
