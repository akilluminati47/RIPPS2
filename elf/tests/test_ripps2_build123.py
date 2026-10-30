"""Build 123 (the user, 10/28): one ART .tar merged into another. The HDD's art and the MMCE's are packed apart, then one
.tar goes into the other; later a small .tar of only the new games' art goes into the master. Picked from Memory Files
(a .tar under the cursor is the one kept) or from Cache > ART Pack (into the pack in use, or right after a pack is
built). The merged-in .tar's pictures win over the kept one's of the same name; the merge is written beside the kept
.tar and swapped in only when whole; then the merged-in .tar is offered for deletion, the kept one never.

Static checks on the patched tree, then a program built on the PC from the merge engine in ripps2artpack.c, run on tars
Python writes, and RiptOPL's own tar.c reading the result (through the art_cache.bin the merge writes):
  - every member of both comes out once, the merged-in one where a name (PNG or JPG alike) is in both, byte for byte;
  - the two lists of games (RIPPS2ART.LST) become one, each game once;
  - a stop, an archive that is not a tar, and a merge the drive cannot take leave the kept .tar byte for byte as it was,
    with nothing left beside it."""
import hashlib
import io
import os
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


ap = rd('src/ripps2artpack.c')
need(ap, (('return x->from > y->from ? -1 : 1;', 'the merged-in .tar sorts first among names alike: it wins'),
          ('if (dot != NULL && dot != out && apIsPicture(out))', 'a PNG and a JPG of one name are the same picture'),
          ('if (rename(target, old) != 0) {', 'the kept .tar moves aside only once the merge is whole'),
          ('remove(tmp); // never a merge half written', 'a stopped or failed merge leaves nothing'),
          ('ioBlockOps(1);\n    start = tmBegan = clock();', 'nothing reads the archives while the merge swaps in'),
          ('guiMsgBoxStartOption("DELETE IT");', 'deleting the merged-in .tar takes START'),
          ('guiMsgBoxBackLabel("KEEP IT");', 'and Back keeps it'),
          ('Delete the merged-in .tar?\\nDELETE: %s\\nKEEP: %s', 'the box names the file deleted and the file kept'),
          ('if (tmDelete(source)) {', 'only the merged-in .tar is ever deleted'),
          ('ripps2DrawProgress("MERGING THE ART", tmShown, done, total, left, 1);', "RIPPS2's progress bar"),
          ('if (!ripps2AskHold("MERGE .TAR", target, info, when,', 'the long-job panel'),
          ('(long long)vol.freeKb * 1024 < p.outBytes + 1024 * 1024', 'the room on the kept .tar\'s drive, before a byte is written'),
          ('result |= tmOfferAfterBuild(pack);', 'offered right after a pack is built'),
          ("\"MERGE a .tar into the pack in %s\"", 'and from the ART Pack page'),
          ('tmWriteIndex(&p, target);', 'the merged art.tar gets its index beside it'),
          ('artIndexInvalidate();\n        cacheInvalidateFailMemo();', 'and the art caches start over')), 'ripps2artpack.c')
run = body(ap, 'static int tmRun(const char *target, const char *source)')
if 'tmDelete(target)' in run or 'remove(target)' in run:
    fail.append('tmRun: the kept .tar is never deleted')
fb = rd('src/ripps2files.c')
need(fb, (('"MERGE A .TAR INTO THIS"', 'the Triangle menu names it'),
          ('fbList[fbCursor].kind == FB_KIND_TAR)\n        fbMenuItems[fbMenuCount++] = FB_ACT_TARMERGE;', 'on a .tar only (build 125: the blue folder)'),
          ('if (ripps2TarMergeInto(from, fbPath))\n                saveConfig(CONFIG_OPL, 0);', 'a moved pack is saved from Memory Files'),
          ('int ripps2FilesDriveUp(const char *root)', 'only drives Memory Files lists are looked in')), 'ripps2files.c')
need(rd('include/ripps2artpack.h'), (('int ripps2TarMergeInto(const char *target, const char *here);', 'declared'),), 'ripps2artpack.h')
need(rd('include/ripps2.h'), (('int ripps2FilesDriveUp(const char *root);', 'declared'),), 'ripps2.h')

# ---- the program
cc = shutil.which('gcc') or shutil.which('cc')

SHIM = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
#include <time.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef uint64_t u64;
#define memalign(a, s) malloc(s)
#ifdef _WIN32
#include <io.h>
#define lseek64 _lseeki64
#undef O_RDONLY
#undef O_WRONLY
#define O_RDONLY (_O_RDONLY | _O_BINARY)
#define O_WRONLY (_O_WRONLY | _O_BINARY)
#else
#define lseek64 lseek
#endif
'''

MAIN = r'''
#include "include/tar.h"
@DEFS@
@FUNCS@
static int stopAt = -1;
static int stopper(long long done, long long total, int n, int count)
{
    (void)done; (void)total; (void)count;
    return stopAt >= 0 && n > stopAt;
}
/* argv: target source tmp stopAt -> one line: rc out in same pictures0 pictures1 outBytes */
int main(int argc, char **argv)
{
    const char *tars[2] = {argv[1], argv[2]};
    char old[300];
    tm_plan_t p;
    int r = 0;
    memset(&p, 0, sizeof(p));
    stopAt = atoi(argv[4]);
    if (tmScan(&p, tars[0], 0) < 0 || tmScan(&p, tars[1], 1) < 0 || !tmPlan(&p))
        r = -9;
    else {
        r = tmWrite(&p, tars, argv[3], stopper);
        if (r == 1) {
            r = tmSwap(argv[1], argv[3], old, sizeof(old));
            if (r == 1)
                tmWriteIndex(&p, argv[1]);
            else
                r = r == -1 ? -3 : -4;
        }
    }
    printf("%d %d %d %d %d %d %lld\n", r, p.out, p.in, p.same, p.pictures[0], p.pictures[1], p.outBytes);
    tmFree(&p);
    return 0;
}
'''

READER = r'''
#include <stdio.h>
#include <string.h>
#include "include/tar.h"
/* argv[1] the tar, then prefixes: each one's member and its size, as the art worker would get it */
int main(int argc, char **argv)
{
    tarClose(TAR_KIND_ART);
    if (tarLoadFile(TAR_KIND_ART, argv[1]) != 0) {
        printf("LOADFAIL\n");
        return 1;
    }
    for (int i = 2; i < argc; i++) {
        TarEntryArt *e = (TarEntryArt *)tarFindPrefixExact(TAR_KIND_ART, argv[i]);
        printf("%s %s %u\n", argv[i], e ? e->filename : "-", e ? e->base.rawSize : 0u);
    }
    return 0;
}
'''


def blob(tag, n):
    return (hashlib.sha256(tag.encode()).digest() * (n // 32 + 1))[:n]


def write_tar(path, members, prefix=''):
    with tarfile.open(path, 'w', format=tarfile.USTAR_FORMAT) as tf:
        for name, data in members:
            ti = tarfile.TarInfo(prefix + name)
            ti.size = len(data)
            ti.mtime = 1761600000
            tf.addfile(ti, io.BytesIO(data))


def lst(keys):
    return ('RIPPS2 ART PACK 1\r\n' + ''.join(k + '\r\n' for k in keys)).encode()


KEPT = [('SLUS_210.50_COV.png', blob('kept cov', 3000)), ('SLUS_210.50_BG_00.jpg', blob('kept bg', 70000)),
        ('SLES_510.61_COV.png', blob('kept sles', 1200)), ('SCUS_971.99_ICO.png', blob('kept ico', 512)),
        ('SLUS_206.42_COV.png', blob('kept old png', 900)), ('RIPPS2ART.LST', lst(['SLUS_210.50', 'SLES_510.61', 'SCUS_971.99']))]
MERGED = [('SLUS_210.50_COV.png', blob('new cov', 4100)), ('SLUS_206.42_COV.jpg', blob('new jpg', 2000)),
          ('SLPM_650.01_COV.png', blob('new game', 600)), ('slus_216.33_cov.PNG', blob('lower', 10)),
          ('RIPPS2ART.LST', lst(['SLUS_210.50', 'SLPM_650.01', 'slus_216.33']))]
WANT = {'SLUS_210.50_COV.': ('SLUS_210.50_COV.png', 4100), 'SLUS_210.50_BG_00.': ('SLUS_210.50_BG_00.jpg', 70000),
        'SLES_510.61_COV.': ('SLES_510.61_COV.png', 1200), 'SCUS_971.99_ICO.': ('SCUS_971.99_ICO.png', 512),
        'SLUS_206.42_COV.': ('SLUS_206.42_COV.jpg', 2000), 'SLPM_650.01_COV.': ('SLPM_650.01_COV.png', 600),
        'slus_216.33_cov.': ('slus_216.33_cov.PNG', 10)}


def funcs():
    heads = ('static unsigned int apHash(', 'static int apIsPicture(', 'static void apPackDir(', 'static void apHeader(',
             'static int apWriteZeros(', 'static void tmFree(', 'static unsigned long long tmOctal(', 'static int tmHeadOk(',
             'static int tmZero(', 'static void tmClean(', 'static void tmStem(', 'static int tmReadAll(', 'static int tmAdd(',
             'static int tmFromIndex(', 'static int tmScan(', 'static int tmDupCmp(', 'static int tmListMerge(',
             'static int tmPlan(', 'static int tmWrite(', 'static int tmSwap(', 'static void tmWriteIndex(')
    out = []
    for h in heads:
        out.append(body(ap, h))
        if h == 'static int tmZero(':
            out.append('static tm_member_t *tmSortM;\n')
    return '\n'.join(out)


def defs():
    lines = [l for l in ap.split('\n') if l.startswith('#define AP_') or l.startswith('#define TM_')]
    i = ap.index('typedef struct\n{\n    unsigned long long head;')
    j = ap.index('} tm_plan_t;', i) + len('} tm_plan_t;')
    return '\n'.join(lines) + '\n' + ap[i:j] + '\n'


if cc is None:
    print('build123: no host C compiler, the program is skipped')
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
        (t / 'merge.c').write_text(MAIN.replace('@DEFS@', defs()).replace('@FUNCS@', funcs()))
        (t / 'reader.c').write_text(READER)
        flags = ['-std=gnu99', '-Wall', '-Wno-unused-function', '-include', str(t / 'shim.h'), '-I', str(t)]
        r1 = subprocess.run([cc] + flags + [str(t / 'merge.c'), '-o', str(t / 'merge.exe')], capture_output=True, text=True)
        r2 = subprocess.run([cc] + flags + [str(t / 'tar.c'), str(t / 'reader.c'), '-o', str(t / 'reader.exe')], capture_output=True, text=True)
        if r1.returncode or r2.returncode:
            fail.append('the programs do not build:\n' + (r1.stderr + r2.stderr)[-3000:])
        else:
            def merge(target, source, stop=-1):
                tmpf = target + '.tmp'
                r = subprocess.run([str(t / 'merge.exe'), target, source, tmpf, str(stop)], capture_output=True, text=True)
                return [int(x) for x in r.stdout.split()] if r.returncode == 0 and r.stdout.strip() else [-99]

            def members(path):
                with tarfile.open(path) as tf:
                    return {m.name.split('/')[-1]: tf.extractfile(m).read() for m in tf.getmembers() if m.isfile()}

            for case, kept_prefix, index_first in (('plain', '', False), ('ART/ inside, read through its index', 'ART/', True)):
                d = t / case.split()[0]
                (d / 'ART').mkdir(parents=True)
                (d / 'NEW').mkdir()
                target = (d / 'ART' / 'art.tar').as_posix()
                source = (d / 'NEW' / 'new.tar').as_posix()
                write_tar(target, KEPT, kept_prefix)
                write_tar(source, MERGED)
                if index_first:  # tar.c writes art_cache.bin beside it: the merge then reads the kept .tar's list from it
                    subprocess.run([str(t / 'reader.exe'), target], capture_output=True)
                    if not (d / 'ART' / 'art_cache.bin').exists():
                        fail.append('%s: tar.c wrote no index to start from' % case)
                rc = merge(target, source)
                if rc[:6] != [1, 7, 4, 2, 5, 4]:
                    fail.append('%s: merge said %s, wanted rc 1, 7 out, 4 in, 2 in both, 5 and 4 pictures' % (case, rc))
                    continue
                got = members(target)
                if os.path.getsize(target) != rc[6]:
                    fail.append('%s: the merge is %d bytes, it said %d' % (case, os.path.getsize(target), rc[6]))
                if any(p.exists() for p in (d / 'ART' / 'art.tar.tmp', d / 'ART' / 'art.tar.old')):
                    fail.append('%s: something left beside the merge' % case)
                for prefix, (name, size) in WANT.items():
                    src = dict(MERGED) if name in dict(MERGED) else dict(KEPT)
                    if got.get(name) != src[name]:
                        fail.append('%s: %s is not the %s one' % (case, name, 'merged-in' if name in dict(MERGED) else 'kept'))
                if 'SLUS_206.42_COV.png' in got:
                    fail.append('%s: the kept PNG stayed beside the merged-in JPG of the same picture' % case)
                keys = got.get('RIPPS2ART.LST', b'').decode().split('\r\n')
                if keys[0] != 'RIPPS2 ART PACK 1' or sorted(k for k in keys[1:] if k) != sorted(
                        ['SLUS_210.50', 'SLES_510.61', 'SCUS_971.99', 'SLPM_650.01', 'slus_216.33']):
                    fail.append('%s: the list of games is %s' % (case, keys))
                if not (d / 'ART' / 'art_cache.bin').exists():
                    fail.append('%s: no art_cache.bin beside the merged art.tar' % case)
                # tar.c on the merge, its index read from art_cache.bin (checked against the size)
                r = subprocess.run([str(t / 'reader.exe'), target] + list(WANT), capture_output=True, text=True)
                for line in r.stdout.splitlines():
                    prefix, name, size = line.rsplit(' ', 2)
                    if (name.split('/')[-1], int(size)) != WANT[prefix]:
                        fail.append('%s: tar.c finds %s %s for %s, wanted %s' % (case, name, size, prefix, WANT[prefix]))
                if r.returncode or len(r.stdout.splitlines()) != len(WANT):
                    fail.append('%s: tar.c on the merge: %s' % (case, (r.stdout + r.stderr)[-400:]))
                if Path(source).read_bytes() == b'' or members(source) != dict(MERGED):
                    fail.append('%s: the merged-in .tar changed (it is only ever read)' % case)

            # what must leave the kept .tar as it was: a stop, a source that is not a tar, a drive that takes nothing
            d = t / 'safe'
            d.mkdir()
            target = (d / 'art.tar').as_posix()
            write_tar(target, KEPT)
            before = Path(target).read_bytes()
            source = (d / 'new.tar').as_posix()
            write_tar(source, MERGED)
            if merge(target, source, stop=3)[0] != 0:
                fail.append('a stop at the third picture: not reported as stopped')
            bad = (d / 'bad.tar')
            data = bytearray(Path(source).read_bytes())
            data[600:610] = b'XXXXXXXXXX'
            data[148:156] = b'0000000\0'
            bad.write_bytes(bytes(data))
            if merge(target, bad.as_posix())[0] != -9:
                fail.append('a source with a broken header was taken for a tar')
            r = subprocess.run([str(t / 'merge.exe'), target, source, (d / 'no' / 'such' / 'dir.tmp').as_posix(), '-1'],
                               capture_output=True, text=True)
            if not r.stdout.startswith('-1 '):
                fail.append('a merge the drive cannot take: %s' % r.stdout.strip())
            if Path(target).read_bytes() != before:
                fail.append('the kept .tar changed after a stop or a failure')
            left = sorted(p.name for p in d.iterdir())
            if left != ['art.tar', 'bad.tar', 'new.tar']:
                fail.append('left beside the kept .tar: %s' % left)
            if not fail:
                print('build123: 2 merges read back by tar.c, 3 failures leave the kept .tar as it was')

if fail:
    print('\n'.join(fail))
    sys.exit(1)
print('build123: a .tar merged into another, the merged-in pictures winning, written beside and swapped in whole; offered '
      'for deletion only the merged-in one OK')
