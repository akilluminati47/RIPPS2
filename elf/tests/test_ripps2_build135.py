"""Build 135: Neutrino found, never carried, and one ELF. RIPPS2.elf carries BIBLE and no Neutrino and installs none; a
launch that finds none says where to put it; STATUS has no install row; About and the APA message say so; the credits
stay; the lite ELF (builds 126-134) is gone.

Static checks on the patched tree, elf/build.sh, the workflow and elf/neutrino."""
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
repo = elf.parent
rd = lambda p: (root / p).read_text(encoding='utf-8')
fail = []

mk, emb, st, sb, ab, hdr = rd('Makefile'), rd('src/ripps2ember.c'), rd('src/ripps2status.c'), rd('src/supportbase.c'), rd('src/ripps2about.c'), rd('include/ripps2.h')
bsh = (elf / 'build.sh').read_text(encoding='utf-8')
wf = (repo / '.github/workflows/build-elf.yml').read_text(encoding='utf-8')
for gone, where, text in (('neutrino_tgz', 'Makefile', mk), ('neutrino_tgz', 'ripps2ember.c', emb), ('ripps2NeutrinoUnpack', 'ripps2ember.c', emb),
                          ('ripps2NeutrinoInstallTo', 'ripps2.h', hdr), ('ripps2NeutrinoOffer', 'ripps2.h', hdr),
                          ('ACT_NT_INSTALL', 'ripps2status.c', st), ('stInstallNeutrino', 'ripps2status.c', st), ('ripps2NeutrinoOffer', 'supportbase.c', sb),
                          ('neutrino.tar.gz', 'elf/build.sh', bsh), ('the one RIPPS2 carries', 'system.c', rd('src/system.c')),
                          ('carried unmodified', 'ripps2about.c', ab), ('RIPPS2_LITE', 'Makefile', mk), ('RIPPS2_LITE', 'gui.c', rd('src/gui.c')),
                          ('RIPPS2_LITE', 'ripps2boot.c', rd('src/ripps2boot.c')), ('RIPPS2-lite.elf', 'elf/build.sh', bsh),
                          ('RIPPS2-lite.elf', 'build-elf.yml', wf)):
    if gone in text:
        fail.append('%s: %s is still there' % (where, gone))
if (root / 'src/ripps2lite.c').exists():
    fail.append('src/ripps2lite.c: one ELF, no lite stand-ins')
if list((elf / 'neutrino').glob('*.tar.gz')):
    fail.append('elf/neutrino: no Neutrino tar is carried')
if 'void ripps2NeutrinoMissing(void)' not in emb or 'github.com/rickgaiser/neutrino) in a neutrino folder' not in emb:
    fail.append('a launch with no Neutrino says where to get it and where to put it')
if 'ripps2NeutrinoMissing();' not in sb:
    fail.append('sbResolveNeutrinoPath says where to put one when it finds none')
if 'stLauncher(SEANCE_NEUTRINO, "Neutrino", p, 4);' not in st or 'github.com/rickgaiser/neutrino' not in st:
    fail.append('STATUS still shows where Neutrino was found, and NEUTRINO SETTINGS says where to get it')
for credit in ('"Neutrino by rickgaiser"', '"ORBIT\'s Neutrino fork by danielnuld"', '"github.com/rickgaiser/neutrino"'):
    if credit not in ab:
        fail.append('About keeps the credit %s' % credit)
if 'bible_xlf.o bible_mx4sio_xlf.o bible_mmce_xlf.o bible_hdd_xlf.o' not in mk:
    fail.append('RIPPS2.elf carries BIBLE')

if fail:
    print('\n'.join('FAIL: ' + f for f in fail))
    sys.exit(1)
print('build 135: ok')
