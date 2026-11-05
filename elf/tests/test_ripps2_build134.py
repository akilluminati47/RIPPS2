"""Build 134: Set Metadata with the title and the file name filled in, asking for Write Operations when they are off; a
paste reported in a box (how many and where); General & System without its card scan on every open; and BIBLE (the
akilluminati47 fork of PS2BBL, signed for RIPPS2) installed with the config it reads, mc?:/SYS-CONF/PS2BBL.INI.

Static checks on the patched tree, elf/bible and the languages."""
import hashlib
import os
import sys
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
elf = Path(__file__).resolve().parents[1]
rd = lambda p: (root / p).read_text(encoding='utf-8')
ed, menu, files, boot, gui, hdr = rd('src/ripps2edit.c'), rd('src/menusys.c'), rd('src/ripps2files.c'), rd('src/ripps2boot.c'), rd('src/gui.c'), rd('include/ripps2.h')
fail = []

if '{NULL, N_("FILE NAME"), NULL},' not in ed or 'titleFromList = 1;' not in ed or '_t("GAME LIST")' not in ed:
    fail.append('Set Metadata shows the file name and fills the title from the list')
if ed.count('if (mdFields[i].key == NULL)') < 3:
    fail.append('FILE NAME is never read or written as a detail')
if 'getKeyOn(gSelectButton) && fd->key == NULL' not in ed:
    fail.append('Cross on FILE NAME renames the game')
if 'static int menuAskWrite(void)' not in menu or menu.count('if (menuAskWrite()) {') != 2 or 'saveConfig(CONFIG_OPL, 0);' not in menu:
    fail.append('both Set Metadata rows ask to turn Write Operations on, and keep the answer')
if 'static char fbPop[384];' not in files or 'guiMsgBox(fbPop, 0, NULL);' not in files or '_t("%s in %s")' not in files:
    fail.append('a paste is reported in a box with how many and where')
if 'bootLockWas = ripps2BootLockKnown();' not in gui or 'int ripps2BootLockKnown(void);' not in hdr or boot.count('ripps2BootLockForget();') < 2:
    fail.append('General & System reuses the last BOOT LOCK scan until RIPPS2 changes the lock or runs Manage')
if 'snprintf(sysConf, sizeof(sysConf), "%s/PS2BBL.INI", sys);' not in boot or 'blWriteIcons(sys, "BIBLE ", "Settings");' not in boot:  # build 143: BIBLE's own icon
    fail.append('the card install writes BIBLE\'s mc?:/SYS-CONF/PS2BBL.INI, its folder with an icon')
if 'snprintf(conf, sizeof(conf), "mc%d:/SYS-CONF/PS2BBL.INI", port);' not in boot:
    fail.append('the HDD install\'s card config goes where BIBLE reads it')
for p, s in (('ripps2boot.c', boot), ('ripps2status.c', rd('src/ripps2status.c'))):
    for line in s.split('\n'):
        if ('BBL 1.20' in line or 'PS2BBL 1.2.0' in line) and '_t("' in line:
            fail.append('%s still says the old loader on screen: %s' % (p, line.strip()[:80]))

sums = {'SYSTEM.XLF': '0b251edcf67cf1ff7c9dd4bc7c420e5a33aa7415ecc69d5a9e4da9b13a7e4f52',
        'MX4SIO/SYSTEM.XLF': 'bb927d630e27c4ab00080471bba9d0cce8691dbc3c768ca9209a2d5ef861fef8',
        'HSYSTEM.XLF': '304f78ce6b772a70820d6f0c1c89116b469db5345e79c53136e3c0cc8d339e9c'}
for name, want in sums.items():
    data = (elf / 'bible' / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != want:
        fail.append('elf/bible/%s is not the signed BIBLE build' % name)
    if data[16 + 6:16 + 8] != b'\x00\x01':
        fail.append('elf/bible/%s is not a KELF (system type 0, app type 1)' % name)
readme = (elf / 'bible' / 'README.md').read_text(encoding='utf-8')
for want in sums.values():
    if want not in readme:
        fail.append('elf/bible/README.md lists every file\'s SHA-256')
if 'PS2KEYS' in ''.join(p.name for p in (elf / 'bible').rglob('*')):
    fail.append('no key file in elf/bible')

lang = elf / 'lang'
for yml in sorted(lang.glob('*.yml')):
    if yml.name.startswith('_'):
        continue
    s = yml.read_text(encoding='utf-8')
    for k in ('"FILE NAME":', '"GAME LIST":', '"%s in %s":'):
        if k not in s:
            fail.append('%s lacks %s' % (yml.name, k))
    if 'BBL 1.20' in s or 'PS2BBL 1.2.0' in s:
        fail.append('%s still names the old loader' % yml.name)

print('\n'.join(fail) or 'build134: Set Metadata filled in and asking for writes, the paste box, the BOOT LOCK scan kept, BIBLE signed and configured where it reads OK')
sys.exit(1 if fail else 0)
