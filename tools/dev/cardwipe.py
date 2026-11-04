"""Wipe a raw 8 MB PS2 card image (SD2PSX, no ECC) clean of everything deleted: every free cluster zeroed, and every
deleted directory entry (mode without 0x8000) zeroed, so no old file's bytes or name survive. Live files untouched.

    python cardwipe.py <in .mcd> <out .mcd>
"""
import io
import sys

sys.path.insert(0, 'B:/Webpages - Projects/ps2-pillars/tools/dev')
import bible_bootcard as bb  # noqa: E402
from mymcplus import ps2mc  # noqa: E402
import mymcplus.ps2mc as M  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
raw = open(src, 'rb').read()
assert len(raw) == 8 * 1024 * 1024
buf = io.BytesIO(bb.with_ecc(raw))
c = ps2mc.ps2mc(buf)
cs = c.cluster_size
zero = bytes(cs)
free = 0
for n in range(c.allocatable_cluster_end):
    if not (c.lookup_fat(n) & 0x80000000):
        c.write_allocatable_cluster(n, zero)
        free += 1


# deleted directory entries: walk every live directory, zero the entries without DF_EXISTS
def walk(path):
    global dele
    ents = c.dir_open(path)
    names = []
    for i, e in enumerate(ents):
        if i < 2:
            continue
        if not (e[0] & 0x8000):
            continue
        name = e[8].decode('ascii', 'replace').rstrip('\0')
        if e[0] & 0x20:
            names.append(name)
    ents.close()
    for nme in names:
        walk(path.rstrip('/') + '/' + nme)
    # the directory's raw clusters: rewrite deleted entries as zeros
    f = c.dir_open(path, 'r+b')
    cnt = len(f)
    blank = M.unpack_dirent(bytes(M.PS2MC_DIRENT_LENGTH))
    for i in range(2, cnt):
        e = f[i]
        if not (e[0] & 0x8000) and any(e[8]):
            f.write_raw_ent(i, blank, False)
            dele.append((path, e[8].decode('ascii', 'replace').rstrip('\0')))
    f.close()


dele = []
walk('/')
c.check()
c.close()
img = bb.strip_ecc(buf.getvalue())
open(out, 'wb').write(img)
print('zeroed', free, 'free clusters of', cs, 'bytes; deleted entries cleared:', dele)
