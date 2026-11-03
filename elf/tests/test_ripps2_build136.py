"""Build 136: Manage counts the slots 0 and 1 (as mc0: and mc1:), says an SD2PSX or MMCE card cannot be bound before the I/O
processor restarts (and offers BOOT LOCK for its own PS2BBL), and asks for a power cycle after a refused bind; BIBLE's
MMCE build, signed 11/03, starts RIPPS2 from an SD2PSX or MMCE card; STATUS's RIP THIS CONSOLE'S AUDIO opens Audio
settings on BIOS Sounds and BIOS Music, and the boot sound line names its file.

Static checks on the patched tree, elf/build.sh, elf/bible and the languages."""
import hashlib
import os
import sys
from pathlib import Path

import yaml

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
boot, st, gui, snd, mk = rd('src/ripps2boot.c'), rd('src/ripps2status.c'), rd('src/gui.c'), rd('src/sound.c'), rd('Makefile')
bsh = (elf / 'build.sh').read_text(encoding='utf-8')
fail = []

# slots 0 and 1, as mc0: and mc1:
for line in boot.split('\n') + st.split('\n'):
    if ('port + 1' in line or 'boot + 1' in line or 'i + 1, kb' in line) and ('slot' in line.lower() or 'SLOT' in line or 'card' in line.lower()):
        fail.append('a slot still counted from 1: %s' % line.strip()[:90])
if '_t("SLOT 0: %s\\nSLOT 1: %s\\n%s\\n"' not in boot:
    fail.append('the Manage screen heads its cards SLOT 0 and SLOT 1')
if "reads slot 1's config before slot 0's" not in boot or 'SD2PSX or MMCE BOOT card' in boot:
    fail.append('the confirm screen says an SD2PSX or MMCE card cannot be bound, slots 0 and 1')

# an SD2PSX or MMCE card: said before the restart, BOOT LOCK offered; a refused bind asks for a power cycle
i, j = boot.find('if (port == 4 || port == 5) {'), boot.find('// where RIPPS2 starts from: where it is now')
mm = boot[i:j]
if 'fileXioDevctl(dev, 0x1, NULL, 0, NULL, 0) >= 0' not in mm or 'ripps2BootLockApply(1);' not in mm or 'nothing was tried' not in mm:
    fail.append('Manage checks the slot for an SD2PSX or MMCE card before it restarts the I/O processor, and offers BOOT LOCK')
k = boot.find('if (SecrDownloadFile(2 + port, 0, buf) == NULL) {')
if k < 0 or 'stop answering after a refused bind' not in boot[k:k + 1200]:
    fail.append('a refused bind says to turn the console off and on')

# BIBLE's MMCE build, carried and picked for an MMCE start
mmce = (elf / 'bible' / 'MMCE' / 'SYSTEM.XLF')
want = '20074daa0cc6c8a6bff95c3725ba36f58dc96ca2f22bb033d65a413d0edcf8c9'
if not mmce.exists() or hashlib.sha256(mmce.read_bytes()).hexdigest() != want:
    fail.append('elf/bible/MMCE/SYSTEM.XLF is the signed BIBLE MMCE build')
elif mmce.read_bytes()[16 + 6:16 + 8] != b'\x00\x01':
    fail.append('elf/bible/MMCE/SYSTEM.XLF is a KELF (system type 0, app type 1)')
if want not in (elf / 'bible' / 'README.md').read_text(encoding='utf-8'):
    fail.append('elf/bible/README.md lists the MMCE build\'s SHA-256')
if '"$HERE/bible/MMCE/SYSTEM.XLF" "$SRC/misc/bible_mmce_system.xlf"' not in bsh or 'bible_mmce_xlf.o' not in mk:
    fail.append('build.sh and the Makefile carry the MMCE build')
if 'w->mmce ? bible_mmce_xlf' not in boot or 'where[count].mmce = 1;' not in boot:
    fail.append('RIPPS2 started from MMCE installs BIBLE\'s MMCE build')

# STATUS: Audio settings on its rip rows, and the boot sound's file
if 'guiShowAudioFromStatus()' not in st or 'ripps2RipBiosSoundsDialog();' in st.split('case ACT_SOUNDS_RIP')[1][:200]:
    fail.append('RIP THIS CONSOLE\'S AUDIO opens Audio settings')
if 'guiShowAudioConfigAt(RIPPS2_RIP_BIOS_BUTTON);' not in gui:
    fail.append('Audio settings opens on BIOS Sounds from STATUS')
if 'int sfxBootSoundWhere(char *out, int size)' not in snd or 'sfxBootSoundWhere(card, sizeof(card));' not in st:
    fail.append('STATUS names the boot sound file, and a memory card\'s as one')

# the languages: every new line, and the VMC slot labels from 0
tpl = set(e['en'] for e in yaml.safe_load((elf / 'lang' / '_strings.yml').read_text(encoding='utf-8'))['strings'])
new = [k for k in tpl if k.startswith(('RIP THIS CONSOLE\'S AUDIO', 'Boot sound On (fast): %s on the memory card', 'An SD2PSX or MMCE card can stop answering', 'SLOT 0: %s'))]
if len(new) != 4:
    fail.append('the template has build 136\'s lines (%d of 4)' % len(new))
for yml in sorted((elf / 'lang').glob('*.yml')):
    if yml.name.startswith('_'):
        continue
    d = yaml.safe_load(yml.read_text(encoding='utf-8'))
    miss = [k[:30] for k in new if k not in d['strings']]
    if miss:
        fail.append('%s lacks %s' % (yml.name, miss))
    lab = d.get('labels') or {}
    if 'VMC_SLOT2' in lab and '2' in lab['VMC_SLOT2']:
        fail.append('%s: VMC_SLOT2 still says 2' % yml.name)

print('\n'.join(fail) or 'build136: slots 0 and 1, no bind tried on an SD2PSX or MMCE card, BIBLE MMCE carried, STATUS opens Audio settings and names the boot sound OK')
sys.exit(1 if fail else 0)
