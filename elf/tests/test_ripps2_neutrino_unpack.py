"""Build 77: the Neutrino RIPPS2 carries unpacks byte for byte, with config/system.toml written last.

Compiles ripps2NeutrinoUnpack and its helpers out of src/ripps2ember.c with the host gcc (zlib, the
PS2's file calls are the host's), unpacks the bundled tar.gz into a temporary folder and compares
every file with the archive; the write order is recorded to check system.toml comes last."""
import os, re, subprocess, sys, tarfile, tempfile
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
tgz = Path(__file__).resolve().parents[1] / 'neutrino' / 'neutrino-1.8.0.tar.gz'
src = (root / 'src/ripps2ember.c').read_text()
start = src.index('#define NEUTRINO_TAR_SIZE')
end = src.index('// No Neutrino anywhere RIPPS2 looks')
code = src[start:end]
tar_size = int(re.search(r'#define NEUTRINO_TAR_SIZE (\d+)', code).group(1))

with tempfile.TemporaryDirectory() as tmp:
    data = tgz.read_bytes()
    blob = ', '.join(str(b) for b in data)
    c = '''#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <malloc.h>
#include <zlib.h>
#include <sys/stat.h>
#define LOG(...) ((void)0)
static FILE *order;
static void guiRenderTextScreen(const char *m) { if (!strncmp(m, "NEUTRINO: writing ", 18)) fprintf(order, "%s\\n", m + 18); }
static unsigned char neutrino_tgz[] = {''' + blob + '''};
static int size_neutrino_tgz = sizeof(neutrino_tgz);
#define mkdir(p, m) mkdir(p, 0777)
''' + code.replace('(unsigned char *)&neutrino_tgz', 'neutrino_tgz') + '''
int main(int argc, char **argv) { order = fopen(argv[2], "w"); int ok = ripps2NeutrinoUnpack(argv[1]); fclose(order); return ok ? 0 : 1; }
'''
    (Path(tmp) / 'u.c').write_text(c)
    r = subprocess.run(['gcc', '-O1', '-o', tmp + '/u', tmp + '/u.c', '-lz'], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); sys.exit(1)
    out = tmp + '/mc0/neutrino'
    r = subprocess.run([tmp + '/u', out, tmp + '/order.txt'])
    fail = []
    if r.returncode:
        fail.append('ripps2NeutrinoUnpack failed')
    with tarfile.open(tgz) as t:
        members = [m for m in t.getmembers() if m.isfile()]
        if sum((m.size + 511) // 512 * 512 + 512 for m in members) > tar_size:
            fail.append('NEUTRINO_TAR_SIZE is smaller than the archive')
        for m in members:
            p = Path(out) / m.name
            if not p.exists() or p.read_bytes() != t.extractfile(m).read():
                fail.append('%s differs or is missing' % m.name)
    order = Path(tmp + '/order.txt').read_text().split()
    if not order or order[-1] != 'config/system.toml':
        fail.append('config/system.toml must be written last')
    print('\n'.join(fail) or 'neutrino unpack: %d files byte for byte, system.toml last OK' % len(members))
    sys.exit(1 if fail else 0)
