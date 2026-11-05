"""Build 143: BIBLE f5705eb carried (signed by akilluminati47 on 11/04), with BIBLE's own icon; BIBLE 3282396 is an older build, so
Manage offers the update that carries the hang fix; ROM 2.30 and up is warned, not refused; a plain BIBLE at mc?:/BOOT/BOOT.ELF is
recognised and never treated as something to write over.

Static checks on the patched tree and on elf/bible."""
import hashlib
import os
import sys
import zlib
from pathlib import Path

root = Path(os.environ.get('RIPTOPL_DIR', '.'))
here = Path(__file__).resolve().parents[1]
boot = (root / 'src/ripps2boot.c').read_text(encoding='utf-8').replace('\r\n', '\n')
mk = (root / 'Makefile').read_text(encoding='utf-8').replace('\r\n', '\n')
build = (here / 'build.sh').read_text(encoding='utf-8').replace('\r\n', '\n')
readme = (here / 'bible' / 'README.md').read_text(encoding='utf-8')
fail = []


def body(text, name):
    a = text.find(name)
    return text[a:text.find('\n}\n', a)] if a >= 0 else ''


# ---- the four signed files, and what they were signed from
sums = {'SYSTEM.XLF': ('0b251edcf67cf1ff7c9dd4bc7c420e5a33aa7415ecc69d5a9e4da9b13a7e4f52', 116584),
        'MMCE/SYSTEM.XLF': ('6a0e8364cec382c8cdd6da580de1f82a21edebc0ba1738a13b800c83b9d6e216', 169576),
        'MX4SIO/SYSTEM.XLF': ('bb927d630e27c4ab00080471bba9d0cce8691dbc3c768ca9209a2d5ef861fef8', 166840),
        'HSYSTEM.XLF': ('304f78ce6b772a70820d6f0c1c89116b469db5345e79c53136e3c0cc8d339e9c', 160184)}
for name, (want, size) in sums.items():
    d = (here / 'bible' / name).read_bytes()
    if hashlib.sha256(d).hexdigest() != want or len(d) != size:
        fail.append('elf/bible/%s is BIBLE f5705eb, signed 11/04' % name)
    if want not in readme:
        fail.append('elf/bible/README.md names %s' % name)
if 'f5705eb' not in readme:
    fail.append('elf/bible/README.md names the commit')

# ---- BIBLE's icon
icn = (here / 'bible' / 'bible.icn').read_bytes()
sys_ = (here / 'bible' / 'icon.sys').read_bytes()
if len(icn) != 37564 or icn[:4] != b'\0\0\1\0':
    fail.append('elf/bible/bible.icn is icon v2, 37,564 bytes, a PS2 icon')
if len(sys_) != 964 or sys_[:4] != b'PS2D':
    fail.append('elf/bible/icon.sys is BIBLE\'s')
for want, why in (('cp -f "$HERE/bible/bible.icn" "$SRC/misc/bible.icn"', 'the build takes the icon'),
                  ('cp -f "$HERE/bible/icon.sys" "$SRC/misc/bible_icon.sys"', 'and its icon.sys')):
    if want not in build:
        fail.append('elf/build.sh: %s' % why)
if 'bible_icn.o bible_icon_sys.o' not in mk or '$(EE_ASM_DIR)bible_icn.c: misc/bible.icn' not in mk:
    fail.append('Makefile embeds them')
icons = body(boot, 'static int blWriteIcons(const char *dir, const char *first, const char *second)\n{')
if 'bible_icn, size_bible_icn' not in icons or 'memcpy(sys + 0x10, bible_icon_sys + 0x10, 0xC0 - 0x10);' not in icons:
    fail.append("BIBLE's folders wear BIBLE's icon, under its colours and light")
named = body(boot, 'int ripps2CardFolderIconNamed(')
if 'save_icn, size_save_icn' not in named or 'bible_icn' in named:
    fail.append("a folder that is not BIBLE's keeps the plain icon")
if 'size_bible_icn + 1023' not in boot:
    fail.append('the room asked for on the card counts the bigger icon')

# ---- 3282396 is an older build: told by size and CRC, as elf/bible had it
older = boot[boot.index('} blBibleOlder[] = {'):boot.index('};', boot.index('} blBibleOlder[] = {'))]
for want in ('{179176, 0xEB932B45u, "MMCE"}', '{176456, 0xA2BF1298u, "MX4SIO"}', '{117160, 0x7B820870u, "memory card"}'):
    if want not in older:
        fail.append('blBibleOlder has %s (3282396)' % want)

# ---- the plain ELFs: the table holds the real files' size and CRC where the tree has them
plain = boot[boot.index('} blBiblePlain[] = {'):boot.index('};', boot.index('} blBiblePlain[] = {'))]
for size, crc, name in ((169428, 0xFA50666C, 'MMCE'), (166692, 0x79D0611C, 'MX4SIO'), (116436, 0x6930956A, 'memory card'), (160036, 0x9510BFF7, 'HDD'),
                        (179060, 0x3ABBDFB0, 'MMCE'), (176404, 0x7B0DCE86, 'MX4SIO'), (117028, 0x93D37D70, 'memory card')):
    if '{%d, 0x%08Xu, "%s"}' % (size, crc, name) not in plain:
        fail.append('blBiblePlain has %s %d' % (name, size))
for name, f in (('MMCE', 'MMCE/SYSTEM.XLF'), ('MX4SIO', 'MX4SIO/SYSTEM.XLF'), ('memory card', 'SYSTEM.XLF')):
    d = (here / 'bible' / f).read_bytes()
    if len(d) - 148 not in (169428, 166692, 116436):
        fail.append('%s: the signed file is its plain ELF plus 148 bytes' % name)
fn = body(boot, 'static const char *blPlainBibleOf(int port)')
if 'mc%d:/BOOT/BOOT.ELF' not in fn or 'crc32(0L, buf, size)' not in fn:
    fail.append('a plain BIBLE is mc?:/BOOT/BOOT.ELF, told by the whole file')
scan = body(boot, 'static void blScanCard(int port)\n{')
if '!c->folder[0] && c->kind == BL_NONE' not in scan or 'c->plain = 1;' not in scan:
    fail.append('a card with a system update is that loader\'s: plain is only looked for without one')

# ---- a plain BIBLE is never written over as if it were bound: the folder moves aside, whole
if boot.count('!(c->bible && !c->plain && !strcmp(c->folder, blSysFolder))') != 2 or '!(c->bible && !strcmp(c->folder, blSysFolder))' in boot:
    fail.append('a system folder beside a plain BIBLE still moves aside, in the work and in what the screen says')
what = body(boot, 'static void blCardWhat(int port, int boot, char *out, int size)')
if 'plain ELF' not in what or what.find('c->plain') > what.find('c->bibleOld'):
    fail.append('the card list says plain ELF, and nothing about power on')
if 'strcmp(b, "HDD") ? b : NULL' not in body(boot, 'static const char *blBuildMisses(const char *path)'):
    fail.append('a plain HDD build reads the HDD')

# ---- ROM 2.30 and up: warned, then the same screen as ever
rom = body(boot, 'static int blConsoleUpdate(void)')
if 'blRom = rom;' not in rom or '#ifdef RIPPS2_TEST_ROM' not in rom or 'blRom = 0;' not in rom:
    fail.append('blConsoleUpdate keeps the ROM, and a lab build can name one')
if 'RIPPS2_TEST_ROM' not in mk:
    fail.append('Makefile: the lab flag')
inst = body(boot, 'static void blInstall(void)\n{')
a, b, c = inst.find('if (blRom >= 230) {'), inst.find('guiMsgBox(msg, 0, NULL);', inst.find('if (blRom >= 230) {')), inst.find('guiMsgBoxStartOption(_t("SET UP BIBLE"));')
if a < 0 or not a < b < c:
    fail.append('blInstall warns on ROM 2.30 and up, then still asks')
if 'return;' in inst[a:b]:
    fail.append('the warning does not refuse')
if 'rows[n].tip = blRom >= 230 ?' not in boot:
    fail.append("the page's tip says it too")

# ---- the boot sound is not read by this BIBLE
if 'A boot sound beside BIBLE is read first' in boot:
    fail.append('the wait tip no longer says BIBLE reads a boot sound')
if '"How long BIBLE waits for a button before the Auto path. At 0 ms a button held from power on still works."' not in boot:
    fail.append('the wait tip')
if 'ripps2BibleArgs' not in (root / 'src/opl.c').read_text(encoding='utf-8'):
    fail.append('RIPPS2 still takes a RAM copy from a card on an older BIBLE')

if fail:
    print('\n'.join('FAIL: ' + f for f in fail))
    sys.exit(1)
print('build 143 ok')
